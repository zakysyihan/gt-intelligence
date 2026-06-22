# GT Intelligence — Market Intelligence for General Trade

> LLM-powered market intelligence system that helps general trade businesses identify winning products to develop. Scrapes marketplace data, analyzes trends, and provides a natural-language interface for data-driven product decisions.

**Built for:** General trade businesses that need data-driven product development.
**Dataset:** 672 food & beverage products from Tokopedia (Java Island)  
**Stack:** Python, DeepSeek V4 Flash, DuckDB, FastAPI + HTML/CSS/JS, Docker  
**Live demo:** http://43.133.140.154:8000

---

## Quick Start

```bash
# Clone
git clone git@github.com:zakysyihan/gt-intelligence.git
cd gt-intelligence

# Setup
cp .env.example .env
# Edit .env — add your SumoPod AI API key

# Run (Docker)
docker compose up --build

# Run (local)
pip install -r requirements.txt
python -m src.pipeline.run_pipeline
uvicorn src.app.app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

---

## What This Does

**Problem:** In general trade businesses, defining the right product to develop is difficult. Data is scattered across marketplaces, not centralized, and hard for non-technical teams to collect.

**Solution:** GT Intelligence scrapes product data from Indonesian marketplaces, analyzes demand patterns, pricing, and geographic distribution, and lets users ask questions in natural language (Indonesian).

### Dashboard

- Market overview: total products, demand volume, avg price, avg rating
- Subcategory comparison (chocolate, candy, snacks)
- Price distribution analysis
- Geographic distribution across Java Island
- Opportunity quadrant: demand vs quality (identifies market gaps)
- Product spec signals: top flavors, weights, variants

### AI Analyst Agent

- Ask questions in Indonesian (e.g., "Produk cokelat apa yang paling laku di Bandung?")
- Agent generates SQL, queries the database, returns data + chart + insight
- Follow-up suggestions after each answer
- Handles unanswerable questions gracefully (e.g., profit margins — no cost data)

---

## Project Structure

```
gt-intelligence/
├── src/
│   ├── pipeline/          # Data scraping, cleaning, validation
│   ├── llm/               # Agent, MDL manifest, data loader
│   └── app/               # FastAPI backend + HTML/CSS/JS frontend
├── data/
│   ├── raw/               # Scraped JSON
│   ├── staging/           # Backup before transformation
│   ├── cleaned/           # Cleaned CSV
│   └── analytics/         # SQLite database (products.db)
├── research/              # Technical research & decisions
├── docs/                  # Architecture document
├── submission/            # Presentation, demo video
├── SPEC.md                # Technical specification
└── Dockerfile
```

---

## Data Pipeline

```
Tokopedia API → Raw JSON → Staging → Clean → LLM Parse → Validate → SQLite
```

- **Scraping:** `tokopaedi` library (mobile API spoofing, bypasses Akamai)
- **Cleaning:** Dedup, normalize prices, parse flavor/weight/variant from product names
- **Validation:** 7 checks (schema, types, nulls, ranges, dedup, geography, row count)
- **Storage:** SQLite (1 table, 14 columns, 672 products)

---

## Assumptions

1. Tokopedia data represents general trade market for food & beverage
2. `sold_count` reflects monthly sales volume (demand proxy)
3. `price × sold_count` is a revenue proxy (not actual profit — cost data unavailable)
4. `rating` (1-5) reflects customer satisfaction
5. Google Trends search interest correlates with market demand
6. Product title parsing (flavor/weight/variant) is best-effort (~60% accuracy)

---

## Known Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Data scraped at one point in time | No real sales trends | Google Trends provides 12-month search interest as proxy |
| Only Tokopedia (Shopee/Blibli blocked by Akamai) | Single marketplace view | Documented; multi-marketplace is a future improvement |
| No profit margin data | Can't assess true profitability | Revenue proxy (price × demand) documented as limitation |
| review_count = 0 for all products | No engagement/loyalty signal | Rating used instead; review data requires page-level scraping |
| Product spec parsing ~60% accuracy | Some flavor/weight/variant fields null | Documented as best-effort; regex + LLM extraction |
| No buyer location data | Only seller location available | Seller location used as geographic proxy |
| Missing "sweets" subcategory | Tokopedia didn't return results | Documented; scope limited to chocolate, candy, snacks |

---

## Technology Choices

| Choice | Alternative | Why This |
|--------|------------|---------|
| SQLite | PostgreSQL | 672 rows, single user — PostgreSQL overkill |
| DeepSeek V4 Flash | GPT-5 | Free on SumoPod, 94%+ SQL accuracy for our simple schema |
| Streamlit + Custom UI | React/Next.js | 3-day sprint — Streamlit fastest for dashboard + chat |
| Python + Pandas | Polars | More common, easier to explain |
| Docker | Manual deploy | One command to run, reproducible |

---

## Deliverables

| Deliverable | Location | Status |
|------------|----------|--------|
| Source code | This repository | ✅ |
| Architecture document | `docs/ARCHITECTURE.md` | ✅ |
| Presentation | `submission/presentation-outline.md` | ✅ |
| Demo video | `submission/demo-video.mp4` | ⏳ |

---

## License

Private — PT Bangunindo Teknusa Jaya.
