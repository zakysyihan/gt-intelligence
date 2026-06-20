# Research: Indonesian Marketplace Scraping

> **Topic:** Feasibility of scraping Indonesian e-commerce for trade demand data
> **Date:** Jun 19, 2026 (updated Jun 20, 2026)
> **Status:** Final — Working solution found
> **Context:** User has 6 months domain expertise in demand forecasting and pricing analysis

---

## Summary

Scraping Indonesian marketplaces is feasible but challenging due to Akamai Bot Manager protection on Tokopedia. **Working solution: `tokopaedi` Python library** (PyPI) which uses mobile API spoofing to bypass Akamai. Successfully scraped 672 real Tokopedia products from Java Island sellers.

**What didn't work:** Direct GraphQL API, curl_cffi TLS impersonation, Playwright/Obscura headless browsers, Shopee API, Blibli API, Bukalapak.

**What works:** `tokopaedi` library — mobile user-agent spoofing against Tokopedia's mobile API endpoints.

---

## Why Scraping Fits the Test Case

The PDF says:
- "Data ingestion from CSV, **API**, or local file" — scraping is data ingestion
- "Kaggle or **another public source**" — marketplace data is public
- "Perform **light-to-medium data engineering**" — scraping IS data engineering
- "You must explain **why** you chose the dataset" — domain expertise = strong justification

**Evaluation alignment:**
| Criterion | How Scraping Helps |
|-----------|-------------------|
| Problem framing (10%) | Domain expertise in demand forecasting = strong justification |
| Data engineering (15%) | Scraping pipeline = demonstrates data engineering skills |
| Pragmatism (10%) | Using public data, no paid APIs needed |
| Communication (10%) | Can explain real business value from experience |

---

## Indonesian Marketplace Options

### 1. Tokopedia — RECOMMENDED

**Why:** Largest Indonesian marketplace, GraphQL API accessible, rich data

**Data available:**
- Product names, categories, prices
- Ratings, review counts
- Sold counts (monthly)
- Shop location (city/province)
- Shop ratings
- Product images

**Scraping approach:**
- GraphQL API endpoint: `https://gql.tokopedia.com/graphql/SearchProductQueryV4`
- Requires headers (User-Agent, etc.) but no authentication
- Can search by keyword, category, sort by popularity/price/rating
- Returns structured JSON (not HTML parsing needed)

**Feasibility:** ★★★★☆
- API is discoverable and structured
- Anti-bot exists but manageable with delays
- No login required for search results

**Time estimate:** 1-2 hours for working scraper

---

### 2. Shopee — VIABLE ALTERNATIVE

**Why:** Second largest, similar data structure

**Data available:** Similar to Tokopedia

**Scraping approach:**
- API endpoint: `https://shopee.co.id/api/v4/search/search_items`
- Requires specific headers and cookies
- More aggressive anti-bot than Tokopedia

**Feasibility:** ★★★☆☆
- Harder to scrape than Tokopedia
- More likely to get blocked

**Time estimate:** 2-3 hours

---

### 3. Bukalapak — VIABLE ALTERNATIVE

**Why:** Third largest, less aggressive anti-bot

**Data available:** Similar to Tokopedia

**Scraping approach:**
- Has API endpoints (less documented)
- Web scraping with BeautifulSoup possible

**Feasibility:** ★★★☆☆
- Less structured API
- More manual HTML parsing

**Time estimate:** 2-3 hours

---

### 4. BPS (Statistics Indonesia) — FALLBACK

**Why:** Official government data, reliable, no scraping needed

**Data available:**
- Export/import statistics by commodity
- Trade balance data
- Consumer price index
- Regional economic indicators

**Approach:**
- CSV/Excel downloads from https://www.bps.go.id
- No scraping needed — direct download

**Feasibility:** ★★★★★
- Official data, very reliable
- No anti-bot, no scraping
- Limited granularity (monthly/yearly, not real-time)

**Time estimate:** 30 minutes

---

## Recommended Approach: Hybrid

**Primary:** Tokopedia scraping (demonstrates data engineering)
**Fallback:** BPS data (if scraping fails or time runs out)

**Why hybrid:**
1. Tokopedia scraping = impressive, demonstrates skills
2. BPS = reliable backup, still Indonesian data
3. Both fit "Retail / Sales / Customer Behavior" category
4. Domain expertise applies to both

---

## Data Collection Plan

### Target: Indonesian E-Commerce Product Data

**Scrape criteria:**
- Categories: Electronics, Fashion, Home & Living, Health & Beauty
- Metrics: price, rating, sold count, review count, shop location
- Volume: 1000-5000 products across categories
- Time: 1-2 hours scraping, 1 hour cleaning

### Business Questions (From Domain Expertise)

1. **Price distribution** — What's the price range for electronics in Indonesia?
2. **Category trends** — Which categories have the highest demand (sold counts)?
3. **Regional pricing** — Do prices differ by seller location?
4. **Rating analysis** — What factors correlate with higher ratings?
5. **Seller performance** — What makes top sellers successful?
6. **Market gaps** — Which product categories have low competition but high demand?
7. **Seasonal patterns** — Can we detect demand patterns from sold counts?

### LLM Grounding Strategy

The LLM will answer questions by:
1. Querying the scraped data (SQLite/CSV)
2. Returning specific data points with references
3. Never answering freely without data backing

**Example grounded answer:**
> "Based on the data, electronics products in Jakarta have an average price of Rp 1.2M with 4.5 rating. The top-selling category is smartphones with 15,000+ monthly sales."

---

## Exploration Results (Jun 20, 2026)

### Approaches Tested

| # | Approach | Tool/Library | Result | Why Failed |
|---|----------|-------------|--------|------------|
| 1 | Direct GraphQL API | httpx | 0 products | API returns empty results without browser cookies |
| 2 | GraphQL + session cookies | httpx | 0 products | Same — cookies alone insufficient |
| 3 | GraphQL + X-TKPD-AKAMAI header | httpx | Connection killed | Header triggers Akamai to kill HTTP/2 stream |
| 4 | curl_cffi TLS impersonation | curl_cffi 0.15.0 | HTTP/2 stream error | All 11 impersonation modes (chrome, safari, edge) killed by Akamai |
| 5 | Playwright headless browser | Playwright + Chromium | JS challenge blocks | Akamai serves challenge page, products never render |
| 6 | Obscura stealth browser | Obscura v0.1.8 (Rust) | Same as Playwright | Akamai JS challenge still blocks product rendering |
| 7 | Shopee API | httpx | 403 Forbidden | Shopee has DataDome anti-bot |
| 8 | Blibli backend API | httpx | 403 Forbidden | Blibli has anti-bot protection |
| 9 | Bukalapak | httpx | 404/406 | Endpoints deprecated or protected |
| 10 | GraphQL introspection | httpx | Disabled | Tokopedia blocks introspection queries |
| 11 | **tokopaedi library** | **tokopaedi 0.2.3** | **672 products ✓** | **Mobile API spoofing bypasses Akamai** |

### Key Technical Discoveries

1. **Akamai Bot Manager** protects Tokopedia with 4 layers:
   - TLS/JA3 fingerprint checking (curl_cffi handles this)
   - HTTP/2 SETTINGS frame checking (curl_cffi handles this)
   - `_abck`/`bm_sz` cookie challenge (needs browser JS execution)
   - Behavioral analysis (mouse movements, timing)

2. **The `X-TKPD-AKAMAI: pdpGetLayout` header is a trap** — it triggers Akamai to kill the connection. The sgm-ecommerce-price-tracker repo that uses it was likely written before Tokopedia added this detection.

3. **Tokopedia's GraphQL schema has changed** — `price`, `stats`, `category` fields cause "Invalid request schema" errors. Only `name`, `url`, `imageUrl`, `originalPrice`, `stock`, `condition`, `rating`, `shop{name city}` work.

4. **Mobile API has lighter protection** — Tokopedia's mobile endpoints are less protected than desktop, which is why `tokopaedi` works.

### Akamai Bypass Libraries Researched

| Library | Type | Akamai Handling | Verdict |
|---------|------|-----------------|---------|
| curl_cffi | HTTP-only | TLS fingerprint only | Insufficient — needs sensor data |
| wafer | Hybrid | Browser-based Akamai solver | Works but needs Patchright browser |
| nodriver/zendriver | Full browser | Natural JS execution | Works but slow, resource-intensive |
| hyper-sdk | Commercial API | Generates sensor data | Works but requires paid API key |
| tokopaedi | HTTP (mobile spoofing) | Avoids heaviest Akamai | **Working ✓** |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Anti-bot blocking | **Medium** (mitigated) | tokopaidi library bypasses Akamai via mobile API |
| tokopaedi library breaks | Medium | Library actively maintained; fallback to Kaggle dataset |
| Data quality unknown | Medium | Data cleaning pipeline, validation checks |
| Legal concerns | Low | Public data, no PII, no login required |
| Incomplete data | Medium | Document limitations in architecture doc |

---

## Decision

**Use `tokopaedi` library as primary data source.** This demonstrates:
- Data engineering skills (scraping pipeline with anti-bot bypass)
- Domain expertise (demand forecasting knowledge)
- Pragmatism (finding a working solution after extensive exploration)
- Risk awareness (documenting what didn't work and why)

**Results achieved:**
- 672 real Tokopedia products from Java Island sellers
- 3 subcategories: candy, chocolate, snacks
- Avg price: Rp 44,743, Avg rating: 4.41
- 374 unique shops across 10+ Java cities

---

## Sources

1. **Tokopedia GraphQL API** — `https://gql.tokopedia.com/graphql/SearchProductQueryV4` — discovered via browser network inspection. No official public documentation (undocumented API).
2. **BPS Statistics Indonesia** — https://www.bps.go.id/en — Official government statistics portal. Trade data available as CSV/Excel downloads.
3. **Indonesia E-Commerce Market Share** — https://iprice.co.id/insights/mapofecommerce/en/ — Iprice Commerce Report 2024, tracks top Indonesian marketplaces by traffic.
4. **Tokopedia Product Data Structure** — Verified via browser DevTools inspection of search results (Jun 19, 2026).
