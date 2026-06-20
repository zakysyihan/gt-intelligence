# Plan: WrenAI Agent + Chainlit Interface

## Context

Data pipeline is complete — 672 real Tokopedia products in SQLite at `data/analytics/products.db` on the VPS. Need to:
1. Validate data against SPEC.md schema
2. Build WrenAI agent + Chainlit interface per SPEC.md Sections 6 & 7

**Critical discovery:** WrenAI has two architectures:
- **Legacy v1** (Docker): 6 Java/Python/Node containers, ~4GB RAM — **won't fit on 2GB VPS**
- **Current v2** (pip): `wrenai` Python package, in-process Rust engine (DataFusion), LanceDB for semantic memory — **single Python process, fits 2GB**

**Decision: Use WrenAI v2 (`pip install wrenai`)**. Same MDL semantic layer concept, runs in-process. Document the tradeoff in architecture doc.

## Data Validation (Step 0)

Run validation against SPEC.md Section 4 rules on VPS:
- Schema: all columns present
- Types: price=int, rating=float, sold_count=int
- Nulls: 0 nulls in price, sold_count, subcategory, shop_location
- Range: price > 0, rating 1-5, sold_count >= 0
- Dedup: unique product_url
- Geography: Java Island cities
- Row count: >= 500

**Known discrepancies vs SPEC.md:**
- SPEC says 14 fields; actual DB has 16 (includes `price_bucket`, `rating_category` computed columns — acceptable)
- SPEC lists `sweets` subcategory; data has only `chocolate`, `candy`, `snacks` (no `sweets` found — document as limitation)
- `flavor`/`weight`/`variant` are 40-65% null (document as known limitation per SPEC)

## Architecture

```
┌─────────────────────────────────────────────┐
│  Docker Container (single)                  │
│                                             │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │  Chainlit   │  │  Agent (OpenAI)      │  │
│  │  :8000      │──│  MDL grounding       │  │
│  │  Dashboard  │  │  Text-to-SQL         │  │
│  │  Chat       │  │  via WrenAI Engine   │  │
│  └─────────────┘  └────────┬─────────────┘  │
│                            │                │
│                     ┌──────┴───────┐        │
│                     │  DuckDB      │        │
│                     │  (in-process)│        │
│                     │  ← SQLite    │        │
│                     │    data load │        │
│                     └──────────────┘        │
└─────────────────────────────────────────────┘
         ↑
    VPS 43.133.140.154:8000
```

**Flow:**
1. On startup, load `data/analytics/products.db` → DuckDB in-memory
2. WrenAI engine compiles MDL manifest (business semantics)
3. User asks question → Agent classifies intent → generates SQL via MDL context → executes on DuckDB → returns result + chart + insight
4. All answers grounded in data (never free-form)

## Implementation Steps

### Step 1: Data Validation Script
**File:** `src/pipeline/validate_for_agent.py`
- Run all 7 SPEC.md validation checks against VPS SQLite
- Output pass/fail report
- Log any discrepancies

### Step 2: DuckDB Data Loader
**File:** `src/llm/data_loader.py`
- On app startup: `ATTACH 'data/analytics/products.db' AS sqlite_db; CREATE TABLE products AS SELECT * FROM sqlite_db.products;`
- Verify row count matches expected (672)
- Make DuckDB available to WrenAI engine

### Step 3: MDL Manifest
**File:** `src/llm/mdl_manifest.py`
- Define `products` model with all 16 columns
- Add calculated columns:
  - `estimated_revenue` = price * sold_count
  - `demand_score` = sold_count normalized
- Add cubes for common aggregations:
  - `demand_by_subcategory`: SUM(sold_count) by subcategory
  - `revenue_by_subcategory`: SUM(price * sold_count) by subcategory
  - `geographic_distribution`: COUNT by shop_location
- Business term mappings (Indonesian → SQL):
  - "terlaris" → sold_count DESC
  - "profitable" / "menguntungkan" → price * sold_count DESC
  - "tren" / "trending" → time-series aggregation
  - "opportunity" / "peluang" → high demand + few sellers
  - "region" / "kota" / "daerah" → shop_location

### Step 4: LLM Agent
**File:** `src/llm/agent.py`
- OpenAI gpt-4o-mini (per CLAUDE.md tech stack)
- System prompt with MDL context (business terms, data schema, grounding rules)
- Intent classification: data question vs. unanswerable
- Text-to-SQL generation with MDL context
- SQL execution via WrenAI engine
- Result formatting: table, chart spec, insight text
- Follow-up suggestion generation
- Unanswerable question handling (per SPEC.md Section 6)

### Step 5: Chainlit App
**File:** `src/app/app.py`

**Dashboard (on_open):**
- 4 metric cards (live SQL queries):
  - Total products: `SELECT COUNT(*)`
  - Top subcategory: `SELECT subcategory, SUM(sold_count) GROUP BY subcategory ORDER BY 2 DESC LIMIT 1`
  - Average price: `SELECT AVG(price)`
  - Java Island products: `SELECT COUNT(*) WHERE shop_location IS NOT NULL`
- 3 charts:
  - Subcategory demand ranking (bar)
  - Price distribution (histogram)
  - Geographic distribution by city (bar)

**Chat:**
- 6 quick action buttons (per SPEC.md Section 7)
- Agent responds with: SQL query, data table, chart, insight
- Follow-up suggestions after each answer
- "How was this answer generated?" section

**Files:**
- `src/app/app.py` — main Chainlit app
- `src/app/dashboard.py` — dashboard components
- `src/app/charts.py` — chart generation helpers

### Step 6: Requirements + Config
**File:** `requirements.txt` (update)
- Add: `wrenai`, `chainlit`, `openai`, `duckdb`, `plotly`, `orjson`

**File:** `.env.example`
- `OPENAI_API_KEY=sk-...`
- `WREN_ENGINE_PORT=8080`

### Step 7: Dockerfile + docker-compose.yml
**Single container** (Chainlit + WrenAI in-process):
- Base: `python:3.12-slim`
- Install deps, copy code + data
- Expose port 8000 (Chainlit)
- CMD: `chainlit run src/app/app.py`

**docker-compose.yml:**
- Single service: `gt-intelligence`
- Volume mount: `data/` (SQLite database)
- Port: `8000:8000`
- Env file: `.env`

### Step 8: Deploy to VPS
```bash
git add -A && git commit -m "feat: WrenAI agent + Chainlit interface"
git push origin main
ssh -i ~/.ssh/gt-intelligence ubuntu@43.133.140.154 \
  "cd /home/ubuntu/gt-intelligence && git pull && docker compose up -d --build"
```

## Key Files to Create

| File | Purpose |
|------|---------|
| `src/llm/__init__.py` | Package init |
| `src/llm/data_loader.py` | SQLite → DuckDB loader |
| `src/llm/mdl_manifest.py` | MDL manifest definition |
| `src/llm/agent.py` | LLM agent (OpenAI + WrenAI) |
| `src/app/__init__.py` | Package init |
| `src/app/app.py` | Main Chainlit app |
| `src/app/dashboard.py` | Dashboard metrics + charts |
| `src/app/charts.py` | Chart generation (Plotly) |
| `src/pipeline/validate_for_agent.py` | Data validation script |
| `requirements.txt` | Updated dependencies |
| `.env.example` | Environment template |
| `Dockerfile` | Container definition |
| `docker-compose.yml` | Service orchestration |
| `mdl/models.yml` | MDL model definitions (YAML) |
| `mdl/instructions.yml` | Business context instructions |

## Trade-offs to Document

| Decision | Why | Trade-off |
|----------|-----|-----------|
| WrenAI v2 (pip) over v1 (Docker) | 2GB VPS constraint | No web UI from WrenAI; we build our own in Chainlit |
| DuckDB as query engine | WrenAI default, in-process | Data must be loaded from SQLite on startup (~1s) |
| OpenAI gpt-4o-mini | Per CLAUDE.md, cost-effective | Requires API key, not self-hosted |
| Single container | MVP simplicity, 2GB RAM limit | No service isolation; all-in-one |
| SQLite → DuckDB load | WrenAI doesn't support SQLite natively | Tiny startup overhead |

## Verification

1. **Data validation:** Run `validate_for_agent.py` on VPS — all 7 checks pass
2. **WrenAI engine:** Query DuckDB via WrenAI SDK — returns correct results
3. **Agent:** Ask "produk terlaris apa?" — returns ranked table with sold_count
4. **Dashboard:** Open `http://43.133.140.154:8000` — 4 cards + 3 charts render
5. **Chat:** Ask all 6 quick action questions — each returns data + chart + insight
6. **Unanswerable:** Ask "berapa profit margin?" — returns structured error
7. **Docker:** `docker compose up -d` on VPS — container healthy, port 8000 accessible
