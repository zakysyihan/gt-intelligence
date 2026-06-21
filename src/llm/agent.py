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
    is_clarifying: bool = False
    clarifying_question: str = ""
    intermediate_steps: list[dict[str, Any]] = field(default_factory=list)


REACT_SYSTEM_PROMPT = """You are GT Intelligence — an AI market analyst for general trade businesses in Indonesia.

Your job: Convert natural language questions about product data into SQL queries.

You operate in a ReAct (Reason-Act-Observe) loop. For each step, you must:

1. REASON: Analyze what the user needs. Classify the intent:
   - "direct_answer" — question is clear, proceed with SQL
   - "needs_exploration" — need to check data structure first (e.g., what subcategories exist)
   - "needs_clarification" — question is ambiguous, ask the user to clarify
   - "chain_queries" — question requires multiple SQL queries and a comparison

2. ACT: Based on classification:
   - For direct_answer: generate the SQL query
   - For needs_exploration: generate a discovery query (e.g., SELECT DISTINCT subcategory FROM products)
   - For needs_clarification: generate a clarifying question for the user
   - For chain_queries: generate the first SQL query in the chain

3. OBSERVE: After execution, assess if the answer is complete.

RULES:
- Generate ONLY valid DuckDB SQL. No explanations in the SQL.
- Always use the "products" table.
- For "terlaris" / "best-selling", ORDER BY sold_count DESC.
- For "profitable" / "menguntungkan", use (price * sold_count) as estimated_revenue.
- For aggregation questions, always include ORDER BY and LIMIT.
- Use ILIKE for text matching (Indonesian text varies in case).
- For flavor/weight queries, handle NULLs (many products lack parsed specs).
- NEVER use review_count in SQL (it's all zeros).
- Return results in a format useful for the business team.

RESPOND WITH A JSON OBJECT:
{
    "intent": "direct_answer|needs_exploration|needs_clarification|chain_queries|answer_complete",
    "sql": "SELECT ...",
    "clarifying_question": "question to ask user (only if intent is needs_clarification)",
    "exploration_query": "SELECT DISTINCT ... (only if intent is needs_exploration)",
    "chain_sql": ["query1", "query2"] (only if intent is chain_queries),
    "chain_comparison_hint": "what to compare in chain results",
    "is_unanswerable": false,
    "unanswerable_reason": "",
    "insight_hint": "what to highlight in the answer",
    "chart_type": "bar|line|table|scatter|pie",
    "follow_ups": ["suggested follow-up question 1", "suggested follow-up question 2"],
    "answer_ready": false,
    "final_answer": "if answer_ready is true, put the final insight here"
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

    def _execute_sql(self, sql: str) -> tuple[list[str], list[dict[str, Any]], str]:
        """Execute SQL and return (columns, data, error)."""
        try:
            query_result = self.con.execute(sql)
            columns = [desc[0] for desc in query_result.description]
            rows = query_result.fetchall()
            return columns, self._format_result(columns, rows), ""
        except Exception as e:
            return [], [], str(e)

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

    def generate_title(self, messages: list[dict]) -> str:
        """Generate a short, descriptive session title from conversation content.

        Args:
            messages: List of {"role": "user"|"assistant", "content": str} dicts.

        Returns:
            A short title string (max 6 words, Indonesian). Returns "Sesi Baru" on failure.
        """
        if not messages:
            return "Sesi Baru"

        # Build a compact summary of the conversation for the LLM
        conversation_text = "\n".join(
            f"{m['role']}: {m['content'][:200]}" for m in messages[-6:]
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Generate a short session title (max 6 words, in Indonesian) "
                            f"for this data analysis conversation:\n{conversation_text}\n\n"
                            "Return ONLY the title, no quotes, no explanation."
                        ),
                    },
                ],
                temperature=0.3,
                max_tokens=30,
            )
            title = resp.choices[0].message.content.strip().strip('"').strip("'")
            return title if title else "Sesi Baru"
        except Exception:
            return "Sesi Baru"

    def ask(self, question: str) -> AgentResponse:
        """Process a natural language question and return grounded results.

        Uses a ReAct (Reason-Act-Observe) loop:
        1. Classify intent (direct_answer, needs_exploration, needs_clarification, chain_queries)
        2. Execute appropriate action (SQL, exploration, clarifying question, chain query)
        3. Observe if result is complete
        4. Repeat until answer is ready or max 3 iterations
        """
        response = AgentResponse(question=question)

        # Build context
        schema_str = self._get_schema_str()
        context_prompt = _build_context_prompt()

        stats_context = f"""
Current dataset: {self._data_stats['row_count']} products
Subcategories: {', '.join(self._data_stats['subcategories'])}
Unique locations: {self._data_stats['locations']} cities
Price range: Rp {self._data_stats['price_range'][0]:,} - Rp {self._data_stats['price_range'][1]:,}
"""

        # ReAct loop setup (max 3 iterations)
        conversation_history = [
            {"role": "system", "content": REACT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""{context_prompt}

{stats_context}

Schema:
{schema_str}

Question: {question}""",
            },
        ]

        max_iterations = 3
        all_data: list[dict[str, Any]] = []
        result = {}

        for iteration in range(max_iterations):
            try:
                llm_resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation_history,
                    temperature=0,
                    max_tokens=500,
                    response_format={"type": "json_object"},
                )

                result = orjson.loads(llm_resp.choices[0].message.content)
            except Exception as e:
                response.error = f"LLM error: {e}"
                return response

            intent = result.get("intent", "direct_answer")

            # --- Check if unanswerable ---
            if result.get("is_unanswerable"):
                response.is_unanswerable = True
                response.error = result.get(
                    "unanswerable_reason",
                    "Pertanyaan ini tidak bisa dijawab dari data yang tersedia.",
                )
                return response

            # --- Intent: needs_clarification ---
            if intent == "needs_clarification":
                response.is_clarifying = True
                response.clarifying_question = result.get(
                    "clarifying_question",
                    "Bisa jelaskan lebih spesifik tentang apa yang ingin Anda ketahui?",
                )
                return response

            # --- Intent: needs_exploration ---
            if intent == "needs_exploration":
                exploration_query = result.get("exploration_query", "")
                if exploration_query:
                    columns, data, error = self._execute_sql(exploration_query)
                    if error:
                        response.error = f"Exploration query failed: {error}"
                        return response

                    response.intermediate_steps.append({
                        "step": iteration + 1,
                        "intent": "exploration",
                        "sql": exploration_query,
                        "data": data,
                    })
                    all_data.extend(data)

                    # Feed exploration result back to LLM for the actual answer
                    exploration_context = json.dumps(data[:10], indent=2, default=str)
                    conversation_history.append({"role": "assistant", "content": json.dumps(result)})
                    conversation_history.append({
                        "role": "user",
                        "content": (
                            f"Exploration query returned:\n{exploration_context}\n\n"
                            "Now generate the actual answer based on this exploration."
                        ),
                    })
                    continue

            # --- Intent: chain_queries ---
            if intent == "chain_queries":
                chain_sql_list = result.get("chain_sql", [])
                chain_comparison = result.get("chain_comparison_hint", "")

                for sql in chain_sql_list:
                    columns, data, error = self._execute_sql(sql)
                    if error:
                        response.error = f"Chain query failed: {error}"
                        return response

                    response.intermediate_steps.append({
                        "step": len(response.intermediate_steps) + 1,
                        "intent": "chain_query",
                        "sql": sql,
                        "data": data,
                    })
                    all_data.extend(data)

                # Feed chain results back to LLM for comparison analysis
                chain_summary = []
                for i, step in enumerate(response.intermediate_steps):
                    chain_summary.append(
                        f"Step {i+1} ({step['intent']}):\n"
                        f"SQL: {step['sql']}\n"
                        f"Data: {json.dumps(step['data'][:5], indent=2, default=str)}"
                    )

                conversation_history.append({"role": "assistant", "content": json.dumps(result)})
                conversation_history.append({
                    "role": "user",
                    "content": (
                        f"Chain query results:\n{chr(10).join(chain_summary)}\n\n"
                        f"Comparison hint: {chain_comparison}\n\n"
                        "Now provide the final comparison analysis."
                    ),
                })
                continue

            # --- Intent: direct_answer or answer_complete ---
            sql = result.get("sql", "")
            if not sql and intent != "answer_complete":
                response.error = "LLM did not generate a SQL query."
                return response

            if sql:
                columns, data, error = self._execute_sql(sql)
                if error:
                    # Try to fix common SQL issues
                    fix_response = self._retry_with_fix(question, sql, error)
                    fix_response.intermediate_steps = response.intermediate_steps
                    return fix_response

                response.sql = sql
                response.columns = columns
                response.data = data
                response.chart_type = result.get("chart_type", "table")

                response.intermediate_steps.append({
                    "step": iteration + 1,
                    "intent": intent,
                    "sql": sql,
                    "data": data,
                })
                all_data.extend(data)

            # Check if answer is ready
            if result.get("answer_ready", False):
                final_answer = result.get("final_answer", "")
                if final_answer:
                    response.insight = final_answer
                break

            # Feed result back to LLM to observe if complete
            observation = (
                f"Query result:\nSQL: {sql}\n"
                f"Data: {json.dumps(response.data[:10], indent=2, default=str)}"
            )
            conversation_history.append({"role": "assistant", "content": json.dumps(result)})
            conversation_history.append({
                "role": "user",
                "content": (
                    f"{observation}\n\n"
                    "Is this answer complete? If yes, set answer_ready=true and provide "
                    "the final insight. If not, continue reasoning."
                ),
            })

        # Generate insight if not already provided
        if not response.insight and all_data:
            insight_hint = result.get("insight_hint", "")
            response.insight = self._generate_insight(question, all_data[:15], insight_hint)

        # Generate follow-ups
        if all_data:
            response.follow_ups = self._generate_follow_ups(question, all_data[:10])

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

        dash["total_shops"] = self.con.execute(
            "SELECT COUNT(DISTINCT shop_name) FROM products"
        ).fetchone()[0]

        dash["total_cities"] = self.con.execute(
            "SELECT COUNT(DISTINCT shop_location) FROM products"
        ).fetchone()[0]

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
