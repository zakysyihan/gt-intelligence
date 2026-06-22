# GT Intelligence — Market Intelligence for General Trade

> LLM-powered market intelligence system that helps general trade businesses identify winning products to develop. Scrapes marketplace data, analyzes trends and pricing patterns, and provides a natural-language interface for data-driven product decisions.

**Live demo:** https://gt-intelligence.biz.id

---

## Quick Start

```bash
# Clone
git clone git@github.com:zakysyihan/gt-intelligence.git
cd gt-intelligence

# Setup
cp .env.example .env
# Edit .env — add your OpenAI-compatible API key

# Run (Docker)
docker compose up --build

# Run (local)
pip install -r requirements.txt
python -m src.pipeline.run_pipeline
uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

---

## What This Does

**Problem:** In general trade businesses, defining the right product to develop is difficult. Data is scattered across marketplaces, not centralized, and hard for non-technical teams to collect.

**Solution:** GT Intelligence scrapes product data from Indonesian marketplaces, analyzes demand patterns, pricing, and geographic distribution, and lets users ask questions in natural language (Indonesian).

### Dashboard

- Market overview: total products, total shops, total cities, top subcategory
- Demand distribution: per subcategory, per price bucket
- Product Mapping — Demand vs Rating quadrant (identifies market gaps)
- Product Mapping — Demand vs Price quadrant (pricing intelligence)
- Filters: subcategory, province, city/kabupaten

**Dashboard vs Analysis Categories:**

| Category | Dashboard Feature |
|----------|------------------|
| 1. Demand & Trend | Subcategory demand chart, Product Mapping quadrant |
| 2. Profitability | Price × Demand quadrant, price distribution chart |
| 3. Geographic | Province/city filters (chat agent for city-level analysis) |
| 4. Temporal | Limited (snapshot data) — chat agent can query timestamp patterns |
| 5. Product Success | Product Mapping quadrant (demand vs rating), chat agent for spec analysis |

### AI Analyst Agent

- Ask questions in Indonesian (e.g., "Produk cokelat apa yang paling laku di Bandung?")
- Agent generates SQL, queries the database, returns data + chart + insight
- Follow-up suggestions after each answer
- Handles unanswerable questions gracefully (e.g., profit margins — no cost data)
- Multi-step reasoning: exploration queries, chain queries, clarifying questions

---

## Dataset Reference

| Property | Value |
|----------|-------|
| Source | Tokopedia (via `tokopaedi` library) |
| Category | Food & Beverage (Makanan & Minuman) |
| Subcategories | Chocolate, Candy, Snacks |
| Total products | 1,317 |
| Total sellers | 530 |
| Total cities | 33 (across 5 provinces in Java) |
| Collection date | June 2026 |
| Method | API scraping (mobile spoofing, bypasses Akamai) |
| Fields | 19 columns (product info, seller info, location, parsed specs, computed) |

---

## Project Structure

```
gt-intelligence/
├── src/
│   ├── api/               # FastAPI backend (primary UI server)
│   ├── pipeline/          # Data scraping, cleaning, validation
│   ├── llm/               # Agent, data loader
│   └── app/               # Chart helpers (Plotly)
├── static/                # Frontend assets (HTML, CSS, JS, GeoJSON)
├── data/
│   ├── raw/               # Scraped JSON
│   ├── staging/           # Backup before transformation
│   ├── cleaned/           # Cleaned CSV
│   └── analytics/         # SQLite database (products.db)
├── research/              # Technical research & decisions
├── docs/                  # Architecture document
├── submission/            # Presentation, demo video
├── SPEC.md                # Technical specification
├── Dockerfile
└── docker-compose.yml
```

---

## Data Pipeline

```
Tokopedia API → Raw JSON → Staging → Clean → LLM Parse → Validate → SQLite
```

- **Scraping:** `tokopaedi` library (mobile API spoofing, bypasses Akamai)
- **Cleaning:** Dedup, normalize prices, parse flavor/weight/variant, map provinces
- **LLM Parse:** DeepSeek V4 Flash extracts product specs from titles (~$0.01 for 1,317 products)
- **Validation:** 8 checks (schema, types, nulls, ranges, dedup, geography, category, row count)
- **Storage:** SQLite (1 table, 19 fields, 1,317 products, indexed on subcategory/province)

---

## AI Model & Prompt Engineering

### System Prompt Structure

The agent uses a structured system prompt with four layers ([src/llm/agent.py](src/llm/agent.py)):

1. **Business context** — Indonesian term → SQL mapping (e.g., "terlaris" → `ORDER BY sold_count DESC`, "menguntungkan" → `ORDER BY (price * sold_count) DESC`). Defines the business domain: general trade, food & beverage, Tokopedia, Java Island.
2. **Data dictionary** — Column definitions with business meaning (e.g., `sold_count` = monthly sales volume, `estimated_revenue` = virtual column computed at query time).
3. **SQL rules** — DuckDB syntax, single table, no `review_count`, ILIKE for text matching, handle NULLs on parsed specs.
4. **Unanswerable question rules** — Explicit list of out-of-scope topics (profit margins, buyer demographics, forecasting, external data). Returns structured error in Indonesian.

### Grounding Strategy

The LLM **never answers freely**. Every response is grounded in data:

1. LLM generates SQL query (structured JSON output)
2. DuckDB executes the SQL against the actual dataset
3. LLM generates insight from the query results (not from memory)

This two-step grounding eliminates hallucination — the LLM cannot invent data that doesn't exist in the database.

### Intent Classification

The agent classifies each question into one of four intents:

| Intent | Behavior |
|--------|----------|
| `direct_answer` | Generate SQL, execute, return result |
| `needs_exploration` | Run discovery query first (e.g., `SELECT DISTINCT subcategory`), then answer |
| `needs_clarification` | Ask user to refine ambiguous question |
| `chain_queries` | Execute multiple SQL queries, compare results |

### Token Optimization

| Stage | Strategy | Cost |
|-------|----------|------|
| LLM Parse (offline) | Batch processing (10 products per API call) | ~$0.01 for 1,317 products |
| Query-time (online) | Schema is 1 table / 19 columns — minimal prompt size, no JOIN context needed | Negligible |
| SQL generation | `temperature=0` for deterministic, reproducible queries | — |

**Total LLM cost:** ~Rp 2,000–5,000/day. Optimizable — reduce prompt size, cache repeated queries, switch to cheaper models for simple tasks.

### Error Handling

| Failure Mode | Mitigation |
|--------------|------------|
| SQL syntax error | Auto-retry: max 3 iterations, LLM sees error message and fixes query |
| Out-of-scope question | `is_unanswerable=true` detection — returns structured error in Indonesian |
| Hallucination | SQL grounding — LLM generates SQL, DuckDB executes (never free-form) |
| LLM failure | Fallback: structured error message in Indonesian |

---

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture document including:

- System architecture diagram (Mermaid)
- Data flow (offline pipeline + online query flow)
- Technology choices and trade-offs
- Data schema (19 fields)
- Security & privacy
- MVP vs production comparison

---

## Assumptions

1. Tokopedia data represents general trade market for food & beverage
2. `sold_count` reflects monthly sales volume (demand proxy)
3. `price × sold_count` is a revenue proxy (not actual profit — cost data unavailable)
4. `rating` (1-5) reflects customer satisfaction
5. Product title parsing (flavor/weight/variant) is best-effort (~60% accuracy)
6. Seller location is used as geographic proxy (buyer location unavailable)

---

## Known Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Data scraped at one point in time | No real sales trends | Periodic scraping planned for time-series |
| Only Tokopedia (Shopee/Blibli blocked by Akamai) | Single marketplace view | Multi-marketplace is future improvement |
| No profit margin data | Can't assess true profitability | Revenue proxy (price × demand) documented |
| review_count = 0 for all products | No engagement/loyalty signal | Rating used instead |
| Product spec parsing ~60% accuracy | Some flavor/weight/variant fields null | Best-effort extraction documented |
| Seller location, not buyer | Geographic proxy only | Documented as limitation |

---

## Technology Choices

| Choice | Alternative | Why This |
|--------|------------|---------|
| SQLite | PostgreSQL | 1,317 rows, single user — PostgreSQL overkill |
| DeepSeek V4 Flash | GPT-4o-mini, Claude, Qwen | Free on SumoPod, 94%+ SQL accuracy for simple schema |
| FastAPI + HTML/CSS/JS | React/Next.js | Full UX control, fast to build, no framework overhead |
| Python + Pandas | Polars | More common, easier to explain |
| Docker | Manual deploy | One command to run, reproducible |

### Why DeepSeek V4 Flash?

**Benchmark context (TokenMix, 2026):** On simple SQL tasks with single-table schemas, all major LLMs score 94%+ accuracy. The bottleneck is not model capability — it's cost and availability.

| Model | SQL Accuracy | Cost | Availability |
|-------|-------------|------|--------------|
| DeepSeek V4 Flash | 94%+ | Free (SumoPod platform) | Self-hosted |
| GPT-4o-mini | 95%+ | $0.15/1M input tokens | API (OpenAI) |
| Claude Haiku | 94%+ | $0.25/1M input tokens | API (Anthropic) |
| Qwen 2.5 | 94%+ | Free (self-hosted) | Requires GPU |

**Decision:** DeepSeek V4 Flash is free on SumoPod (the deployment platform), has comparable SQL accuracy for our simple 1-table schema. For a dataset of 1,317 products with 19 columns, the schema fits in ~200 tokens — well within any model's context window.

**Switching cost:** One environment variable change (`LLM_MODEL=gpt-4o-mini`). The agent code is model-agnostic via the OpenAI-compatible API.

---

## License

Private — PT Bangunindo Teknusa Jaya.
