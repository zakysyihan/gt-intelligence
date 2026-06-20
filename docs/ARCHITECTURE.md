# ARCHITECTURE.md — GT Intelligence

> Architecture document (3-5 pages). Required deliverable per test case.

---

## 1. Problem Statement

In general trade businesses, defining the right product to develop is difficult in the initial phase. Product type, specification, pricing, and variance are hard to determine without data. The data needed is scattered across marketplaces, not centralized, and difficult for non-technical people to collect.

**Solution:** GT Intelligence — an LLM-powered market intelligence system that scrapes product data from Indonesian marketplaces, analyzes trends, and provides a natural-language interface for the business team to identify winning products.

**User persona:** Business team or product development team in a general trade business who wants to develop a product aimed at winning the market.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User (Browser)                       │
│                    http://43.133.140.154:8000                │
├─────────────────────┬───────────────────────────────────────┤
│   Streamlit UI      │   Analyst Agent (Side Panel)          │
│   - Dashboard       │   - Multi-session chat                │
│   - Metric cards    │   - Text-to-SQL via DeepSeek V4 Flash │
│   - Plotly charts   │   - Grounded answers + charts         │
│   - Quick actions   │   - Follow-up suggestions             │
├─────────────────────┴───────────────────────────────────────┤
│                     GTAgent (Python)                         │
│   - OpenAI-compatible API (SumoPod DeepSeek V4 Flash)       │
│   - Function calling for SQL generation                     │
│   - Business context (Indonesian terms → SQL mapping)       │
├─────────────────────────────────────────────────────────────┤
│                    DuckDB (in-memory)                        │
│   - SQLite bridge (data_loader.py)                          │
│   - Query execution                                         │
├─────────────────────────────────────────────────────────────┤
│              SQLite (products.db, 672 rows)                  │
│   - 14 fields + computed columns                            │
│   - Indexed on subcategory, shop_location                   │
├─────────────────────────────────────────────────────────────┤
│                 Data Pipeline (Python)                       │
│   Scrape (tokopaedi) → Stage → Clean → LLM Parse →         │
│   Validate → SQLite                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow

### 3.1 Data Ingestion (Offline)

```
Tokopedia API (tokopaedi library)
  ↓ Mobile API spoofing (bypasses Akamai)
  ↓ Search by keyword: cokelat, permen, snack, etc.
  ↓ Filter: Java Island locations only
  ↓
Raw JSON (data/raw/)
  ↓
Staging backup (data/staging/)
  ↓
Cleaning (cleaner.py):
  - Deduplicate by product_url
  - Normalize price (remove "Rp", dots → int)
  - Normalize sold_count ("1rb+" → 1000)
  - Parse flavor/weight/variant from product_name
  - Filter Java Island locations
  ↓
LLM Parse (llm_parser.py):
  - DeepSeek V4 Flash extracts product specs
  - flavor, weight, variant fields
  ↓
Validation (validator.py):
  - Schema, types, nulls, ranges, dedup, geography, row count
  - 7 checks, all must pass
  ↓
SQLite (data/analytics/products.db)
```

### 3.2 Query Flow (Online)

```
User question (Indonesian)
  ↓
GTAgent.ask(question)
  ↓
OpenAI function calling (SumoPod DeepSeek V4 Flash)
  - System prompt: business context, data dictionary, unanswerable rules
  - Schema manifest: table name, columns, types
  - Function: run_sql(query)
  ↓
Generated SQL → DuckDB executes against SQLite
  ↓
Results → Agent interprets → Insight (Indonesian)
  ↓
Follow-up suggestions
  ↓
Streamlit renders: SQL, data table, Plotly chart, insight text
```

---

## 4. Technology Choices

| Layer | Tool | Why |
|-------|------|-----|
| Data scraping | Python + tokopaedi | Mobile API spoofing bypasses Akamai bot protection |
| Data storage | SQLite | File-based, zero setup, 1000 rows, portable |
| Data processing | Pandas | Industry standard, easy to explain |
| LLM Agent | SumoPod DeepSeek V4 Flash | Free, OpenAI-compatible, adequate for simple SQL |
| Fallback LLM | O3-Mini ($0.06/task) | Best value if DeepSeek quality insufficient |
| Interface | Streamlit | Dashboard-first UI, built-in charts, multi-session support |
| Visualization | Plotly | Interactive charts, st.dialog modal for expansion |
| Containerization | Docker + Docker Compose | Single container, simple deployment |
| Deployment | SumoPod VPS (Jakarta) | 2vCPU/2GB/40GB, Rp 60k/month |

### Why Streamlit Over Alternatives

- **Not Chainlit:** Chainlit is chat-first by design. Our UX needs dashboard-first with chat as side panel.
- **Not Dash (Plotly):** Dash is more complex, steeper learning curve. Streamlit is simpler for an MVP.
- **Not custom React:** Too much work for 3-day sprint. Streamlit handles both dashboard and chat.
- **Not Metabase:** Adds another service. We need dashboard + LLM chat in one app.

### Why SQLite Over PostgreSQL

- MVP scope: 1000 rows, single user, no concurrent writes
- Zero setup: file-based, no server needed
- Portable: ship the .db file
- PostgreSQL would be the production choice — documented in MVP vs Production table

### Why DeepSeek Over GPT-4o

- Free on SumoPod (zero cost)
- Our schema is trivial: 1 table, 14 columns, no JOINs
- TokenMix benchmark: all models score 94%+ on simple SQL
- WrenAI compensates: dry-plan validates SQL, guided mode forces workflow
- Switching cost: one env var change

---

## 5. Data Schema

```sql
CREATE TABLE products (
    timestamp TEXT,          -- When scraped
    product_name TEXT,       -- Full product title
    subcategory TEXT,        -- chocolate, candy, snacks
    price INTEGER,           -- Price in IDR
    sold_count INTEGER,      -- Monthly sales
    rating REAL,             -- Average rating (0-5)
    review_count INTEGER,    -- Number of reviews
    shop_name TEXT,          -- Seller name
    shop_location TEXT,      -- City in Java Island
    product_url TEXT,        -- Product link (unique)
    flavor TEXT,             -- Parsed from product_name (best-effort)
    weight TEXT,             -- Parsed from product_name (best-effort)
    variant TEXT,            -- Parsed from product_name (best-effort)
    price_bucket TEXT,       -- cheap/mid/expensive (computed)
    rating_category TEXT,    -- low/medium/high (computed)
    estimated_revenue REAL   -- price × sold_count (computed)
);
```

---

## 6. Security & Privacy

| Risk | Mitigation |
|------|-----------|
| API keys exposed | .env file, never committed, gitignored |
| LLM hallucination | SQL grounding — LLM only queries data, never free-form answers |
| Unanswerable questions | Structured refusal with explanation |
| No PII in data | Public product listings only, no user data |
| VPS access | SSH key-based auth only, no passwords |

---

## 7. MVP vs Production

| Concern | MVP (This Project) | Production (Future) |
|---------|-------------------|---------------------|
| Database | SQLite (file-based) | PostgreSQL (concurrent, millions of rows) |
| UI | Streamlit (single container) | Custom frontend (React/Next.js) |
| LLM | SumoPod DeepSeek V4 Flash (API) | Self-hosted LLM or fine-tuned SLM |
| Scraping | Manual run, tokopaedi library | Scheduled (Airflow), proxy rotation, multi-marketplace |
| Auth | None (single user) | Multi-user, RBAC |
| Monitoring | Logs only | Prometheus + Grafana |
| Cost | ~Rp 60k/month (VPS only) | VPS + DB + LLM API costs |

---

## 8. Known Limitations

1. **Data freshness:** Scraped at one point in time, not real-time
2. **Single marketplace:** Only Tokopedia, not Shopee/Bukalapak (Akamai blocks server-side scraping)
3. **No profit margin:** Revenue proxy (price × demand), not true profitability
4. **Product spec parsing:** 40-65% null for flavor/weight/variant (best-effort from titles)
5. **Seller location, not buyer:** Demand signals from seller geography
6. **Missing sweets subcategory:** Tokopedia didn't return results
7. **No shop_rating:** Tokopedia API doesn't expose this field

---

## 9. Future Improvements

1. Scrape multiple marketplaces (Shopee with residential proxy)
2. Time-series analysis (periodic scraping for real trends)
3. Profit margin estimation (with cost data input)
4. Demand forecasting model
5. Multi-language support (Indonesian/English)
6. Fine-tuned SLM for SQL generation (Qwen3-6B)
7. Multi-user auth and RBAC
