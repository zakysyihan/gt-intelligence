# SPEC.md — Bangunindo Analytics MVP

> Technical specification. Source of truth for all implementation.
> Last updated: Jun 20, 2026

---

## 1. What This MVP Is

This is an LLM-powered market intelligence system for a **general trade business**. The system scrapes product data from Indonesian marketplaces (Tokopedia, Shopee), analyzes demand trends and pricing patterns, and provides a natural-language interface where the business team can ask market questions and get data-backed answers.

**The goal:** Enable a product development team to identify winning products to develop — fast, data-driven, without needing to manually browse marketplaces.

**The context:** In general trade businesses, defining the right product to develop is difficult in the initial phase. Product type, specification, pricing, and variance are hard to determine without data. The data needed for these decisions is scattered across marketplaces, not centralized, and difficult for non-technical people to collect.

**User persona:** Business team or product development team in a general trade business who wants to start developing a product aimed at winning the market.

**Why this MVP matters:** It demonstrates how data engineering + LLM can replace weeks of manual market research with hours of automated analysis.

---

## 2. What This MVP Aims to Answer

The business team needs to answer 5 categories of analysis. Each category maps to specific data fields we must scrape. If a field isn't needed for these questions, we don't scrape it.

### Category 1: Demand & Trend Analysis

> "What product is winning right now? What's trending?"

| # | Business Question | What We Need |
|---|-------------------|-------------|
| 1.1 | Which products have the highest total demand (sold count)? | subcategory, sold_count |
| 1.2 | Which products are trending right now (growth in sold count)? | subcategory, sold_count, timestamp |
| 1.3 | How is demand changing over time — accelerating, stable, declining? | subcategory, sold_count, timestamp |
| 1.4 | Which subcategories (chocolate, candy, snacks, sweets) have the strongest demand? | subcategory, sold_count |

### Category 2: Profitability Proxy (Price × Demand)

> "Which products generate the highest estimated revenue?"

| # | Business Question | What We Need |
|---|-------------------|-------------|
| 2.1 | Which products generate the highest estimated revenue (price × sold count)? | price, sold_count |
| 2.2 | Which price points sell best per subcategory? | price, sold_count, subcategory |
| 2.3 | What's the sweet spot — high volume low price vs low volume high price? | price, sold_count, subcategory |

**Limitation:** This is a revenue proxy (price × demand), NOT actual profit margin. Cost data is not available from marketplace scraping. We document this clearly.

### Category 3: Geographic Distribution

> "Where is demand concentrated? Where are the gaps?"

| # | Business Question | What We Need |
|---|-------------------|-------------|
| 3.1 | Which products are concentrated in specific cities vs widely distributed? | shop_location, sold_count, product_name |
| 3.2 | How fast is product distribution spreading across Java Island? | shop_location, sold_count, timestamp |
| 3.3 | Which cities are underserved (high demand signals, few sellers)? | shop_location, sold_count |
| 3.4 | Does pricing vary significantly by region? | price, shop_location, subcategory |

### Category 4: Temporal Pattern

> "How does demand change over time?"

| # | Business Question | What We Need |
|---|-------------------|-------------|
| 4.1 | How do weekly sales patterns change? | sold_count, timestamp |
| 4.2 | Are there seasonal signals in the collection period? | sold_count, timestamp, subcategory |
| 4.3 | Which products gained or lost traction fastest? | sold_count, timestamp, product_name |

### Category 5: Product Success Signals (Product Development)

> "What product specs correlate with winning? What should we develop?"

| # | Business Question | What We Need |
|---|-------------------|-------------|
| 5.1 | What product attributes correlate with high sales? | price, rating, review_count, sold_count, subcategory |
| 5.2 | Which underserved niches have demand but low seller count? | subcategory, sold_count, shop_name |
| 5.3 | What flavor/weight/variant sells best per subcategory? | parsed from product_name (flavor, weight, variant) |
| 5.4 | What's the optimal product spec to enter a winning subcategory? | all fields above |

**Note on Category 5:** Flavor, weight, and variant data are parsed from product titles (e.g., "Chitato Sapi Panggang 68g" → flavor: sapi panggang, weight: 68g). Extraction accuracy is a known limitation — not all titles contain structured specs.

---

## 3. Dataset

**Scope:** Food & beverage products targeting younger/teenager audience
**Subcategories:** Chocolate, candy, snacks, sweets
**Location scope:** Java Island only
**Volume target:** ~1,000 products (realistic for 3-day MVP)
**Category:** Retail / Sales / Customer Behavior

### Data Sources (Layered)

| Layer | Source | Method | Priority |
|-------|--------|--------|----------|
| 1 (Primary) | Tokopedia | Mobile API via `tokopaedi` library (user-agent spoofing) | Working ✓ |
| 2 (Secondary) | Shopee | curl_cffi TLS impersonation | Blocked (403) |
| 3 (Tertiary) | Blibli | Backend JSON API | Blocked (403) |
| 4 (Fallback) | Kaggle | `salmanabdu/tokopedia-product-reviews-2025` (65K reviews) | Requires credentials |

**Why tokopaedi works:** Tokopedia's Akamai Bot Manager blocks server-side GraphQL API access and headless browsers. The `tokopaedi` library bypasses this by spoofing mobile user-agents against Tokopedia's mobile API endpoints, which have lighter anti-bot protection than the desktop web interface.

**What we tried that didn't work:**
- Direct GraphQL API (`gql.tokopedia.com/graphql/SearchProductQueryV4`) — returns empty results without browser cookies
- `curl_cffi` with TLS fingerprint impersonation — HTTP/2 stream killed by Akamai
- `X-TKPD-AKAMAI: pdpGetLayout` header — triggers Akamai to kill the connection
- Playwright/Obscura headless browsers — Akamai JS challenge blocks product rendering
- Shopee API — 403 Forbidden
- Blibli backend API — 403 Forbidden
- Bukalapak — 404/406

### Data Fields

Every field maps to at least one analysis category above.

| # | Field | Type | Description | Maps To |
|---|-------|------|-------------|---------|
| 1 | timestamp | datetime | When data was collected (scrape time) | Cat 1, 2, 3, 4 |
| 2 | shop_location | string | Seller city/province (Java Island only) | Cat 3, 4 |
| 3 | product_name | string | Full product title (used to parse flavor/weight/variant) | Cat 1, 5 |
| 4 | subcategory | string | chocolate, candy, snacks, sweets | Cat 1, 2, 4, 5 |
| 5 | price | int | Price in IDR (normalized) | Cat 2, 3, 5 |
| 6 | rating | float | Average rating (1-5) | Cat 5 |
| 7 | sold_count | int | Monthly sales (normalized) | Cat 1, 2, 3, 4, 5 |
| 8 | review_count | int | Number of reviews | Cat 5 |
| 9 | shop_name | string | Seller name | Cat 3, 5 |
| 10 | shop_rating | float | Seller rating (set to 0 — not available from tokopaedi API) | Cat 3 |
| 11 | product_url | string | Product link (for deduplication) | Dedup |
| 12 | flavor | string | Parsed from product_name (e.g., "sapi panggang") | Cat 5 |
| 13 | weight | string | Parsed from product_name (e.g., "68g") | Cat 5 |
| 14 | variant | string | Parsed from product_name (e.g., "large", "pack") | Cat 5 |

**Field 12-14 are derived** — extracted from product_name during cleaning, not scraped directly.

---

## 4. Data Pipeline

### Flow

```
Raw Data (API) → Staging Layer (JSON) → Transformation Layer → Curated Analytics Layer (SQLite)
```

### Pipeline Steps

| Step | Layer | Input | Output | What Happens |
|------|-------|-------|--------|-------------|
| 1. Ingestion | Raw | Tokopedia mobile API (tokopaedi) | `data/raw/*.json` | Scrape by keyword via mobile API spoofing, store as JSON |
| 2. Staging | Staging | Raw JSON | `data/staging/*.json` | Copy raw to staging (backup before transformation) |
| 3. Cleaning | Transformation | Staging JSON | `data/cleaned/products_clean.csv` | Dedup, normalize, filter Java Island |
| 4. LLM Parse | Transformation | Cleaned CSV | Cleaned CSV (enriched) | LLM extracts flavor/weight/variant from product names (DeepSeek v4 Flash) |
| 5. Validation | Transformation | Cleaned CSV | Pass/Fail | Schema check, null check, range check, dedup check |
| 6. Curated | Curated | Cleaned CSV | `data/analytics/products.db` | Write to SQLite, add computed columns |

**Why staging matters:** If transformation has a bug, you re-run from staging without re-scraping. The raw data is preserved.

### Transformation Logic

- Deduplicate by product_url
- Remove products with missing price or rating
- Normalize price to numeric (remove "Rp" prefix, dots)
- Convert sold_count to numeric ("1rb+" → 1000, "10rb+" → 10000)
- **Parse product_name** → extract flavor, weight/netto, variant using regex + keyword matching
- Filter to Java Island locations only
- Add computed columns: price_bucket, rating_category

### Product Spec Parsing Rules

| Field | Parsing Logic | Example |
|-------|--------------|---------|
| flavor | Match known flavor keywords from title | "Sapi Panggang" → sapi_panggang |
| weight | Match regex for weight patterns | "68g", "100gr", "250ml" → 68g |
| variant | Match known variant keywords | "Large", "Pack", "Box" → large/pack/box |

**Accuracy:** Best-effort. Product titles vary widely. Document extraction rate as a limitation.

### Validation Rules

| Check | Rule | Fail Action |
|-------|------|-------------|
| Schema | All 14 fields present | Stop pipeline, log missing fields |
| Type | price is int, rating is float, sold_count is int | Coerce or drop row |
| Null | 0 nulls in price, sold_count, subcategory, shop_location | Drop row |
| Range | price > 0, rating 1-5, sold_count >= 0 | Drop row |
| Dedup | Unique product_url | Keep first occurrence |
| Geography | shop_location must be Java Island cities | Drop row |
| Row count | At least 500 rows after cleaning | Warn, continue with what we have |

---

## 5. Analytics Layer

Analytics output maps directly to the 5 analysis categories from Section 2.

### Category 1: Demand & Trend
- Top products by total sold count
- Subcategory demand ranking
- Demand trend over time (line chart)

### Category 2: Profitability Proxy
- Estimated revenue per product (price × sold count)
- Price distribution by subcategory
- Sweet spot analysis (volume vs price scatter)

### Category 3: Geographic Distribution
- Seller concentration by city (bar chart)
- Geographic heatmap across Java Island
- Regional pricing comparison

### Category 4: Temporal Pattern
- Weekly sales trend (line chart)
- Time-series decomposition (trend, seasonality)
- Fastest growing products

### Category 5: Product Success Signals
- Correlation: price vs sold_count, rating vs sold_count
- Top flavor/weight/variant by subcategory
- Market gap analysis (high demand, few sellers)

---

## 6. LLM Grounding Strategy

### How It Works

WrenAI provides the grounding through its MDL (Modeling Definition Language) semantic layer.

```
User Question → WrenAI MDL Context → Governed SQL → Results + Chart + Insight
```

### MDL Layer (Business Context)

The MDL encodes business logic so the LLM understands what data means:

| Business Term | MDL Maps To | Example |
|--------------|-------------|---------|
| "terlaris" (best-selling) | sold_count DESC | Sort by sold_count |
| "profitable" | price × sold_count | Revenue proxy |
| "opportunity" | high demand + few sellers | Market gap |
| "tren" (trend) | time-series aggregation | Weekly/monthly pattern |
| "region" | shop_location (Java Island) | Geographic filter |

### Grounding Rules

1. LLM never answers freely — always grounded in data via MDL
2. Every answer must reference specific data points
3. MDL handles unanswerable questions — WrenAI returns structured errors
4. Follow-up suggestions generated from query context

### Why MDL > Prompt Engineering

| Approach | How It Works | Limitation |
|----------|-------------|------------|
| **Prompt engineering** | System prompt tells LLM about data | LLM may forget or ignore instructions |
| **MDL (WrenAI)** | Semantic layer defines data relationships | Deterministic — LLM always has correct context |

### Unanswerable Questions

- Questions about profit margins (cost data not available)
- Questions requiring external data (inflation rate, market size)
- Questions about future predictions (prices next month)
- Questions about buyers (we only have seller location, not buyer)

**Response:** "I can only answer questions based on the scraped product data. This dataset covers [X subcategories] from [Y locations] collected on [Z date]. For questions about [topic], you would need additional data sources."

---

## 7. MVP Interface

### User Flow

```
1. User opens system → sees dashboard (8 widgets + metrics)
2. Clicks "Buka Chat" to open analyst side panel
3. Agent answers with multi-step reasoning, data, charts, insights
4. Agent can ask clarifying questions mid-conversation
5. User can create/switch between analysis sessions
6. Dynamic session titles auto-generated from conversation
```

### Layout

```
┌──────────────────────────────────────────┬──────────────────┐
│  GT Intelligence — Market Analyst        │  [💬 Tutup Chat] │
├──────────────────────────────────────────┼──────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │  🤖 Analis Pasar │
│  │ 📦  │ │ 🏆  │ │ 🏪  │ │ 📍  │       │  Sesi: [▼] [➕]  │
│  │672  │ │snack│ │374  │ │32   │       │                  │
│  └─────┘ └─────┘ └─────┘ └─────┘       │  ⚡ Quick Actions │
│                                          │  [🏆] [📈] [💰]  │
│  📊 Demand  │  💰 Harga                  │  [🗺️] [📊] [🍫]  │
│  🗺️ Top 10 Kota                         │                  │
│  📈 Quadrant │ 💵 Revenue │ 🍫 Specs     │  💬 chat history  │
└──────────────────────────────────────────┴──────────────────┘
```

### Dashboard (8 Widgets)

The dashboard loads on open with 4 metric cards + 4 chart rows (8 widgets total).
Every element queries live data from DuckDB on each load.

| # | Widget | What It Shows | Data Source |
|---|--------|--------------|-------------|
| 1 | Market Snapshot | Total products, top subcategory, total shops, total cities | `COUNT(*)`, `GROUP BY` |
| 2 | Subcategory Comparison | Demand ranking by subcategory (bar chart) | `SUM(sold_count) GROUP BY subcategory` |
| 3 | Price Sweet Spot | Price distribution histogram | `CASE WHEN price...` |
| 4 | Top 10 Cities | Geographic distribution (horizontal bar) | `GROUP BY shop_location` |
| 5 | Product Spec Signals | Top flavor/weight per subcategory (table) | `GROUP BY subcategory, flavor, weight` |
| 6 | Trend Analysis | Google Trends interest over 12 months (line chart) | pytrends API (cached) |
| 7 | Opportunity Quadrant | Demand vs Quality scatter (4 quadrants) | `sold_count vs rating` scatter |
| 8 | Revenue Proxy | Price vs Demand scatter | `price vs sold_count` scatter |

**Opportunity Quadrant Interpretation (from brand owner / product creator perspective):**

| Quadrant | Signal | Action |
|----------|--------|--------|
| High Demand + High Quality | ⭐ Winning Formula | Study and replicate |
| Low Demand + High Quality | 💎 Hidden Gem (Opportunity) | Develop and promote |
| High Demand + Low Quality | ⚠️ Volume Only | Improve quality |
| Low Demand + Low Quality | ❌ Avoid | Don't enter |

**Quick action buttons (map to analysis categories):**

| Button | Category | Predefined Prompt |
|--------|----------|------------------|
| 🏆 Terlaris | Cat 1: Demand | Top 10 produk terlaris bulan ini |
| 📈 Tren | Cat 1: Demand | Tren penjualan per subkategori |
| 💰 Pendapatan | Cat 2: Profitability | Estimasi pendapatan tertinggi (harga × terjual) |
| 🗺️ Regional | Cat 3: Geographic | Distribusi penjualan per kota di Jawa |
| 📊 Harga | Cat 2: Profitability | Harga rata-rata per subkategori |
| 🍫 Specs | Cat 5: Product Dev | Spesifikasi produk paling laris (rasa, berat) |

### Chat (Agentic AI)

- Multi-step ReAct (Reason-Act-Observe) loop — not just single-shot SQL
- Agent can ask clarifying questions mid-conversation
- Agent can chain multiple SQL queries in one answer
- Agent can explore data before answering (discovery queries)
- Dynamic session titles auto-generated by LLM
- All answers grounded in data via MDL semantic layer
- Follow-up suggestions after each answer
- Unanswerable questions handled gracefully (profit margins, buyer data, etc.)

**Agent Response Format:**
```
[SQL Query] → [Data Table] → [Insight] → [Chart] → [Follow-up Suggestions]
```

**Agentic Capabilities:**
- Intent classification: direct_answer, needs_exploration, needs_clarification, chain_queries
- Max 3 iterations per question (prevent infinite loops)
- SQL error retry with auto-fix
- Intermediate steps recorded for transparency

### Interface Tiers (Target: "Excellent") ✅ ACHIEVED

**Minimum (must have):** ✅
- Dashboard with summary metrics
- Chat prompt box
- Clear LLM output with data reference

**Better (target):** ✅
- Suggested questions as quick action buttons
- Data/metric references in answers
- Error handling for unanswerable questions

**Excellent (target):** ✅
- Agentic AI with multi-step reasoning
- Generates charts inline (Plotly)
- Suggests follow-up analysis
- Dynamic session titles
- Opportunity quadrant analysis
- Google Trends integration

---

## 8. Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Scraping | Python + `tokopaedi` (PyPI) | Mobile API spoofing bypasses Akamai; actively maintained |
| Data storage | SQLite | File-based, no server needed |
| Data processing | Pandas | Industry standard, easy to explain |
| Spec parsing | DeepSeek v4 Flash (SumoPod AI) | LLM extracts flavor/weight/variant from product names (80%+ accuracy) |
| Analytics + LLM Agent | OpenAI gpt-4o-mini + ReAct loop | Multi-step reasoning, grounded in MDL semantic layer |
| Custom UI | FastAPI + HTML/CSS/JS | Production-smooth, modern design |
| Backup UI | Streamlit | Dashboard-first layout, backup/prototype |
| Google Trends | pytrends | Search interest data (24hr cache, rate-limit aware) |
| Containerization | Docker + Docker Compose | Dual-service container (FastAPI + Streamlit) |
| Deployment | Single VPS (43.133.140.154) | All services on one machine |
| Testing | Python assert + pytest | Simple verification |

### Data Limitations

| Field | Status | Impact |
|-------|--------|--------|
| review_count | ⚠️ ALL ZERO (tokopaedi doesn't expose) | Cannot use for quality signals |
| rating | ✅ 616/672 have rating > 0 | Used as quality signal |
| flavor/weight/variant | ⚠️ 40-65% null | Best-effort extraction from titles |
| Google Trends | ⚠️ search interest ≠ actual sales | Supplementary signal only |

### MVP vs Production

| Concern | MVP (This Project) | Production (Future) |
|---------|-------------------|---------------------|
| Database | SQLite (file-based) | PostgreSQL (concurrent access, millions of rows) |
| UI | Custom HTML/CSS/JS + Streamlit backup | React/Vue SPA with auth |
| LLM Agent | OpenAI gpt-4o-mini + ReAct | Self-hosted LLM + RAG pipeline |
| Deployment | Single VPS, Docker Compose | Kubernetes, load balancer |
| Scraping | Manual run, tokopaedi mobile API | Scheduled (cron/Airflow), proxy rotation |
| Google Trends | pytrends (unofficial) | Official API or SerpAPI |
| Authentication | None (single user) | Multi-user auth, RBAC |
| Data pipeline | Batch (scrape → clean → serve) | Streaming (real-time updates) |
| Deployment | Single VPS (43.133.140.154) | All services on one machine |
| Testing | Python assert + pytest | Simple verification |

### Why WrenAI Over Vanna.ai

- **MDL (Modeling Definition Language):** Encodes business logic so the LLM understands what data MEANS, not just how to query it
- **Semantic layer:** "terlaris" = sold_count, "opportunity" = high demand + few sellers — business terms mapped to data
- **Follow-up suggestions:** Agent can suggest next questions based on context
- **Apache 2.0 license:** Permissive, no restrictions
- **Agent-native:** Built for AI agent workflows, not just a library

### Why Chainlit Over Streamlit

- **Built for conversational AI:** Chat UI, tool calls, actions out of the box
- **Agent-native:** Designed for LLM agents, not general-purpose dashboards
- **Pairs with WrenAI:** Both are agent-focused, natural fit

### MVP vs Production

This section documents what's POC/MVP and what would change in production.

| Concern | MVP (This Project) | Production (Future) |
|---------|-------------------|---------------------|
| Database | SQLite (file-based) | PostgreSQL (concurrent access, millions of rows) |
| UI | Chainlit (conversational) | Chainlit + custom dashboard for non-chat users |
| LLM Agent | WrenAI + OpenAI | WrenAI + self-hosted LLM option |
| Deployment | Single VPS, Docker Compose | Kubernetes, load balancer, auto-scaling |
| Scraping | Manual run, tokopaedi mobile API | Scheduled (cron/Airflow), retry logic, distributed, proxy rotation |
| Scheduling | Manual | Cron job or cloud scheduler |
| Monitoring | Logs only | Prometheus + Grafana |
| Authentication | None (single user) | Multi-user auth, RBAC |
| Data pipeline | Batch (scrape → clean → serve) | Streaming (real-time updates) |
| Cost | ~$0 (local) | VPS + DB hosting + LLM API costs |

**The test case explicitly asks:** "what's included in the POC/MVP" and "what's not production-ready". This table answers both.

---

## 9. Acceptance Criteria

### Data Pipeline
- [ ] Scraper collects ~1,000 products from Tokopedia/Shopee
- [ ] Data filtered to Java Island locations only
- [ ] Food & beverage subcategories only (chocolate, candy, snacks, sweets)
- [ ] All 14 data fields present (including parsed flavor/weight/variant)
- [ ] Duplicates removed
- [ ] Missing values handled explicitly
- [ ] Data passes schema validation
- [ ] Transformation logic documented

### Analytics Layer
- [ ] All 5 analysis categories covered
- [ ] At least 5 business questions answered with data
- [ ] Analytics results are meaningful (not just charts)
- [ ] Each answer includes insight/recommendation

### LLM Interface
- [ ] WrenAI integrated with SQLite database
- [ ] MDL configured with business context (models.yml + instructions.yml)
- [ ] LLM answers grounded in data via MDL (never free-form)
- [ ] Unanswerable questions handled gracefully
- [ ] Follow-up suggestions present
- [ ] Security/privacy risks documented

### MVP Interface
- [ ] Chainlit chat UI functional
- [ ] Prompt box accepts natural language
- [ ] LLM output is clear and readable with charts
- [ ] "How was this answer generated?" shown (MDL context)

### Documentation
- [ ] README with setup instructions
- [ ] Architecture doc (3-5 pages) — includes MVP vs Production table
- [ ] Known limitations documented
- [ ] Assumptions documented

### Deployment
- [ ] Dockerfile builds successfully
- [ ] docker-compose.yml runs all services
- [ ] App accessible via VPS IP/port
- [ ] .env.example with all required variables

---

## 10. File Structure

```
gt-intelligence/
├── SPEC.md                    # This file
├── AGENTS.md                  # Agent rules
├── CLAUDE.md                  # Claude Code context
├── HISTORY.md                 # Session tracking
├── README.md                  # Project overview
├── Dockerfile                 # Single container for all services
├── docker-compose.yml         # Service orchestration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template (never commit .env)
├── wren.yml                   # WrenAI MDL configuration
├── data/
│   ├── raw/                   # Scraped JSON (staging layer)
│   ├── staging/               # Backup of raw before transformation
│   ├── cleaned/               # Cleaned CSV
│   └── analytics/             # SQLite database
├── src/
│   ├── pipeline/              # Scraping + cleaning + validation
│   │   ├── scraper.py         # Tokopedia/Shopee scraper
│   │   ├── cleaner.py         # Data cleaning + spec parsing
│   │   └── validator.py       # Data quality checks
│   ├── llm/                   # WrenAI integration
│   │   └── agent.py           # WrenAI setup + MDL configuration
│   └── app/                   # Chainlit UI
│       └── app.py             # Main app
├── mdl/                       # WrenAI Modeling Definition Language
│   ├── models.yml             # Table definitions + relationships
│   └── instructions.yml       # Business context for LLM
├── prompts/                   # LLM prompt templates
├── notebooks/                 # Exploratory analysis
├── tests/                     # Data quality tests
├── docs/
│   └── ARCHITECTURE.md        # 3-5 page architecture doc
└── submission/                # Final deliverables
    ├── architecture.pdf
    ├── presentation.pdf
    └── demo-video.mp4
```

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tokopedia/Shopee anti-bot blocks scraper | High | Rate limiting, user-agent rotation, fallback to BPS |
| Product spec parsing accuracy | Medium | Document extraction rate, treat as best-effort |
| Data quality issues | Medium | Validation pipeline, document limitations |
| LLM hallucination | High | Strict grounding, data-first prompting |
| Time overrun | High | 2-hour timebox for scraping, MVP scope control |
| Legal concerns | Low | Public data, no PII, no login required |

---

## 12. Assumptions

1. Tokopedia/Shopee GraphQL API is accessible without authentication
2. Product data (prices, ratings, sold counts) is publicly available
3. ~1,000 products can be scraped in under 2 hours
4. OpenAI API key is available (user provides)
5. Product titles contain enough info to parse flavor/weight/variant
6. Docker and VPS deployment configured (SumoPod Jakarta)

---

## 13. Known Limitations

1. **Data freshness:** Scraped at one point in time, not real-time
2. **Sample bias:** Only Tokopedia/Shopee, not all Indonesian marketplaces
3. **No transaction data:** We have listing data, not actual sales
4. **No profit margin:** Revenue proxy (price × demand), not true profitability
5. **Product spec parsing:** Best-effort extraction from titles, not guaranteed accuracy
6. **Seller location, not buyer:** Demand signals are from seller location, not actual buyer geography
7. **Language:** Product names may be in Indonesian (mixed with English)
8. **Scope:** Food & beverage on Java Island only — not generalizable to all product categories

---

## 14. Future Improvements (If More Time)

1. Scrape additional marketplaces (Bukalapak, Blibli)
2. Add time-series analysis (scrape periodically for real trends)
3. Add actual competitor analysis
4. Add profit margin estimation (with cost data)
5. Add demand forecasting model
6. Expand to other product categories
7. Multi-language support (Indonesian/English)
