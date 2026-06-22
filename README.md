# GT Intelligence — Market Intelligence for General Trade

> LLM-powered market intelligence system that helps general trade businesses identify winning products to develop. Scrapes marketplace data, analyzes trends and pricing patterns, and provides a natural-language interface for data-driven product decisions.

**Live demo:** http://43.133.140.154:8000

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
- Customer Quality quadrant: Demand vs Rating (identifies market gaps)
- Price × Demand quadrant: Sales vs Pricing (pricing intelligence)
- Geographic distribution: top 15 cities by seller count
- Filters: subcategory, province, city/kabupaten

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
│   ├── llm/               # Agent, data loader, Google Trends
│   └── app/               # Streamlit backup UI
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
| DeepSeek V4 Flash | GPT-5 | Free on SumoPod, 94%+ SQL accuracy for simple schema |
| FastAPI + HTML/CSS/JS | React/Next.js | Full UX control, fast to build, no framework overhead |
| Python + Pandas | Polars | More common, easier to explain |
| Docker | Manual deploy | One command to run, reproducible |

---

## License

Private — PT Bangunindo Teknusa Jaya.
