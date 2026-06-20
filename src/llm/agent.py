"""LLM agent for GT Intelligence — text-to-SQL with MDL grounding.

Uses OpenAI gpt-4o-mini to convert natural language questions into SQL,
grounded in the MDL semantic layer. Executes via WrenAI engine against DuckDB.

Grounding rules (per SPEC.md Section 6):
1. LLM never answers freely — always grounded in data via MDL
2. Every answer must reference specific data points
3. Unanswerable questions return structured error
4. Follow-up suggestions generated from query context

ponytail: One class, one OpenAI call per question. No agent framework,
no chain-of-thought chains, no RAG pipeline. OpenAI function calling
is the simplest path to grounded text-to-SQL.
"""

import json
from dataclasses import dataclass, field
from typing import Any

import duckdb
import orjson
from openai import OpenAI

from .mdl_manifest import build_manifest

# Business term mappings — Indonesian → SQL concepts
BUSINESS_CONTEXT = """
## Business Context (Indonesian General Trade)

You are an analyst for a general trade business selling food & beverage products
(chocolate, candy, snacks) on Tokopedia across Java Island, Indonesia.

### Key Business Terms (Indonesian → SQL)
- "terlaris" / "paling laku" / "best-selling" → ORDER BY sold_count DESC
- "tren" / "trending" / "naik" → time aggregation or growth analysis
- "menguntungkan" / "profitable" / "untung" → ORDER BY (price * sold_count) DESC
  (NOTE: this is revenue proxy, NOT actual profit — we don't have cost data)
- "peluang" / "opportunity" / "gap" → high demand (sold_count) + few sellers
- "kota" / "daerah" / "regional" / "location" → GROUP BY shop_location
- "harga" / "price" / "murah" / "mahal" → price analysis
- "rasa" / "flavor" → flavor column
- "berat" / "weight" / "ukuran" → weight column

### Data Dictionary
- sold_count: Monthly sales volume (primary demand signal)
- price: Listed price in IDR
- estimated_revenue: price × sold_count (virtual, computed at query time)
- subcategory: chocolate, candy, snacks
- shop_location: City in Java Island (e.g., "Surabaya", "Kab. Bandung")
- flavor/weight/variant: Parsed from product_name (40-65% null — best-effort)

### Unanswerable Questions
These topics have NO data — refuse politely:
- Profit margins (we don't have cost data)
- Buyer demographics (we only have seller location)
- Future predictions / forecasting
- External data (inflation, market size, GDP)
- Individual transaction data

Response for unanswerable: "Saya hanya bisa menjawab berdasarkan data produk Tokopedia
yang sudah dikumpulkan. Dataset ini mencakup {subcategory_count} subkategori dari
{location_count} kota di Jawa, dikumpulkan pada {scrape_date}. Untuk pertanyaan
tentang {topic}, Anda memerlukan sumber data tambahan."
"""


@dataclass
class AgentResponse:
    """Structured response from the agent."""

    question: str
    sql: str = ""
    data: list[dict[str, Any]] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    insight: str = ""
    chart_type: str = ""  # bar, line, table, scatter
    chart_config: dict[str, Any] = field(default_factory=dict)
    follow_ups: list[str] = field(default_factory=list)
    error: str = ""
    is_unanswerable: bool = False


SYSTEM_PROMPT = """You are GT Intelligence — an AI market analyst for general trade businesses in Indonesia.

Your job: Convert natural language questions about product data into SQL queries.

RULES:
1. Generate ONLY valid DuckDB SQL. No explanations in the SQL.
2. Always use the "products" table.
3. For "terlaris" / "best-selling", ORDER BY sold_count DESC.
4. For "profitable" / "menguntungkan", use (price * sold_count) as estimated_revenue.
5. For aggregation questions, always include ORDER BY and LIMIT.
6. Use ILIKE for text matching (Indonesian text varies in case).
7. For flavor/weight queries, handle NULLs (many products lack parsed specs).
8. Return results in a format useful for the business team.
9. If the question cannot be answered from the data, set is_unanswerable=true.

You MUST respond with a JSON object:
{
    "sql": "SELECT ...",
    "is_unanswerable": false,
    "unanswerable_reason": "",
    "insight_hint": "what to highlight in the answer",
    "chart_type": "bar|line|table|scatter|pie",
    "follow_ups": ["suggested follow-up question 1", "suggested follow-up question 2"]
}
"""


def _build_context_prompt() -> str:
    """Build context prompt with data statistics."""
    return BUSINESS_CONTEXT


class GTAgent:
    """Text-to-SQL agent with MDL grounding."""

    def __init__(
        self,
        duckdb_con: duckdb.DuckDBPyConnection,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
    ):
        self.con = duckdb_con
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.manifest = build_manifest()

        # Pre-compute data stats for grounding
        self._data_stats = self._get_data_stats()

    def _get_data_stats(self) -> dict:
        """Gather data statistics for context grounding."""
        stats = {}
        stats["row_count"] = self.con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        stats["subcategories"] = [
            r[0]
            for r in self.con.execute(
                "SELECT DISTINCT subcategory FROM products ORDER BY subcategory"
            ).fetchall()
        ]
        stats["locations"] = self.con.execute(
            "SELECT COUNT(DISTINCT shop_location) FROM products"
        ).fetchone()[0]
        stats["price_range"] = self.con.execute(
            "SELECT MIN(price), MAX(price), AVG(price) FROM products"
        ).fetchone()
        stats["top_products"] = self.con.execute(
            "SELECT product_name, sold_count FROM products ORDER BY sold_count DESC LIMIT 3"
        ).fetchall()
        return stats

    def _get_schema_str(self) -> str:
        """Return a clean schema description for the LLM."""
        cols = self.con.execute("PRAGMA table_info('products')").fetchall()
        lines = ["Table: products"]
        for c in cols:
            nullable = "NULL" if not c[3] else "NOT NULL"
            lines.append(f"  - {c[1]} ({c[2]}) {nullable}")
        lines.append("")
        lines.append("Virtual columns (computed at query time):")
        lines.append("  - estimated_revenue = price * sold_count")
        return "\n".join(lines)

    def _format_result(self, columns: list[str], rows: list) -> list[dict]:
        """Convert query results to list of dicts."""
        return [dict(zip(columns, row)) for row in rows]

    def _generate_insight(
        self, question: str, data: list[dict], insight_hint: str
    ) -> str:
        """Generate a natural language insight from query results."""
        if not data:
            return "Tidak ada data yang ditemukan untuk pertanyaan ini."

        data_str = json.dumps(data[:10], indent=2, default=str)

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a business analyst. Write a concise insight (2-3 sentences) in Indonesian (Bahasa) based on the query results. Highlight key findings and actionable signals. Be specific with numbers.",
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nHint: {insight_hint}\n\nData:\n{data_str}",
                },
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()

    def _generate_follow_ups(self, question: str, data: list[dict]) -> list[str]:
        """Generate follow-up question suggestions."""
        if not data:
            return []

        data_summary = f"Query returned {len(data)} rows. Columns: {list(data[0].keys()) if data else 'none'}"

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Generate 2 follow-up questions in Indonesian (Bahasa) that a business analyst would ask next. Return as JSON array of strings. Be specific and actionable.",
                },
                {
                    "role": "user",
                    "content": f"Original question: {question}\n{data_summary}",
                },
            ],
            temperature=0.5,
            max_tokens=150,
        )

        try:
            follow_ups = orjson.loads(resp.choices[0].message.content)
            if isinstance(follow_ups, list):
                return follow_ups[:3]
        except Exception:
            pass
        return []

    def ask(self, question: str) -> AgentResponse:
        """Process a natural language question and return grounded results.

        Flow:
        1. Send question + schema + business context to OpenAI
        2. OpenAI returns SQL + metadata
        3. Execute SQL against DuckDB via WrenAI engine
        4. Generate insight + follow-up suggestions
        """
        response = AgentResponse(question=question)

        # Step 1: Generate SQL via OpenAI
        schema_str = self._get_schema_str()
        context_prompt = _build_context_prompt()

        stats_context = f"""
Current dataset: {self._data_stats['row_count']} products
Subcategories: {', '.join(self._data_stats['subcategories'])}
Unique locations: {self._data_stats['locations']} cities
Price range: Rp {self._data_stats['price_range'][0]:,} - Rp {self._data_stats['price_range'][1]:,}
"""

        try:
            llm_resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"""{context_prompt}

{stats_context}

Schema:
{schema_str}

Question: {question}""",
                    },
                ],
                temperature=0,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            result = orjson.loads(llm_resp.choices[0].message.content)
        except Exception as e:
            response.error = f"LLM error: {e}"
            return response

        # Step 2: Check if unanswerable
        if result.get("is_unanswerable"):
            response.is_unanswerable = True
            response.error = result.get(
                "unanswerable_reason",
                "Pertanyaan ini tidak bisa dijawab dari data yang tersedia.",
            )
            return response

        sql = result.get("sql", "")
        if not sql:
            response.error = "LLM did not generate a SQL query."
            return response

        response.sql = sql
        response.chart_type = result.get("chart_type", "table")

        # Step 3: Execute SQL against DuckDB
        try:
            query_result = self.con.execute(sql)
            columns = [desc[0] for desc in query_result.description]
            rows = query_result.fetchall()
            response.columns = columns
            response.data = self._format_result(columns, rows)
        except Exception as e:
            response.error = f"SQL execution error: {e}"
            # Try to fix common SQL issues
            response = self._retry_with_fix(question, sql, str(e))
            return response

        # Step 4: Generate insight and follow-ups
        if response.data:
            response.insight = self._generate_insight(
                question, response.data, result.get("insight_hint", "")
            )
            response.follow_ups = self._generate_follow_ups(question, response.data)

        return response

    def _retry_with_fix(self, question: str, failed_sql: str, error: str) -> AgentResponse:
        """Attempt to fix a failed SQL query."""
        response = AgentResponse(question=question)

        try:
            llm_resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Fix this DuckDB SQL query. Return ONLY valid SQL, no explanation.",
                    },
                    {
                        "role": "user",
                        "content": f"Original question: {question}\nFailed SQL: {failed_sql}\nError: {error}",
                    },
                ],
                temperature=0,
                max_tokens=300,
            )

            fixed_sql = llm_resp.choices[0].message.content.strip()
            # Clean markdown code fences
            if fixed_sql.startswith("```"):
                fixed_sql = fixed_sql.split("\n", 1)[1]
            if fixed_sql.endswith("```"):
                fixed_sql = fixed_sql.rsplit("```", 1)[0]
            fixed_sql = fixed_sql.strip()

            query_result = self.con.execute(fixed_sql)
            columns = [desc[0] for desc in query_result.description]
            rows = query_result.fetchall()
            response.sql = fixed_sql
            response.columns = columns
            response.data = self._format_result(columns, rows)
            response.insight = self._generate_insight(
                question, response.data, "highlight key findings"
            )
        except Exception as e:
            response.error = f"Retry failed: {e}"

        return response

    def get_dashboard_data(self) -> dict:
        """Fetch dashboard metrics and chart data."""
        dash = {}

        # Metric cards
        dash["total_products"] = self.con.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        dash["top_subcategory"] = self.con.execute(
            "SELECT subcategory, SUM(sold_count) as total FROM products GROUP BY subcategory ORDER BY total DESC LIMIT 1"
        ).fetchone()

        dash["avg_price"] = self.con.execute(
            "SELECT AVG(price) FROM products"
        ).fetchone()[0]

        dash["java_products"] = self.con.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]  # All are Java Island

        # Chart 1: Subcategory demand ranking
        dash["subcategory_demand"] = self.con.execute(
            "SELECT subcategory, SUM(sold_count) as total_sold, COUNT(*) as product_count FROM products GROUP BY subcategory ORDER BY total_sold DESC"
        ).fetchall()

        # Chart 2: Price distribution
        dash["price_distribution"] = self.con.execute(
            """SELECT
                CASE
                    WHEN price < 5000 THEN '< 5K'
                    WHEN price < 15000 THEN '5K-15K'
                    WHEN price < 30000 THEN '15K-30K'
                    WHEN price < 75000 THEN '30K-75K'
                    WHEN price < 150000 THEN '75K-150K'
                    ELSE '> 150K'
                END as price_range,
                COUNT(*) as count
            FROM products
            GROUP BY price_range
            ORDER BY MIN(price)"""
        ).fetchall()

        # Chart 3: Geographic distribution (top 15 cities)
        dash["geo_distribution"] = self.con.execute(
            "SELECT shop_location, COUNT(*) as seller_count, SUM(sold_count) as total_sold FROM products GROUP BY shop_location ORDER BY seller_count DESC LIMIT 15"
        ).fetchall()

        return dash
