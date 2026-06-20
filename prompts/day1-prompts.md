# Claude Code Prompts — Day 1

> Ready-to-use prompts for Claude Code sessions. Follow AGENTS.md prompt rules.

---

## Prompt 1: Build Tokopedia Scraper

```
Build a Tokopedia scraper per SPEC.md section 2 (Dataset) and section 3 (Data Pipeline).

Read research/marketplace-scraping.md for API details. The GraphQL endpoint is
https://gql.tokopedia.com/graphql/SearchProductQueryV4.

Scope: Food & beverage products on Java Island only.
Search keywords: "cokelat", "permen", "snack", "camilan", "keripik", "biskuit",
"wafer", "chocolate", "candy", "snack". Filter results to Java Island locations.

Collect: timestamp, product_name, subcategory, price, rating, review_count,
sold_count, shop_name, shop_location, shop_rating, product_url.

Use httpx, rate limit 2 seconds between requests, rotate User-Agent headers.
Target: 500-1000 products total across keywords.

Save raw JSON to data/raw/. Save cleaned CSV to data/cleaned/products.csv.

Verify: run the scraper, check data quality (no nulls in price/rating,
correct types, Java Island locations only).
```

---

## Prompt 2: Data Cleaning Pipeline

```
Build data cleaning pipeline per SPEC.md section 3 (Transformation Logic).

Read data/raw/ for scraped JSON files. Clean and transform:
- Deduplicate by product_url
- Remove products with missing price or rating
- Normalize price: remove "Rp" prefix, dots → int
- Convert sold_count: "1rb+" → 1000, "10rb+" → 10000
- Add price_bucket (cheap/mid/expensive) based on subcategory median
- Add rating_category (low/medium/high) based on 1-5 scale
- Ensure timestamp field is present for trend analysis

Save to data/cleaned/products_clean.csv and data/analytics/products.db (SQLite).

Verify: schema check (all columns present, correct types), null check (0 nulls
in critical fields), Java Island locations only.
```

---

## Prompt 3: Analytics Layer

```
Build analytics layer per SPEC.md section 4 (Analytics Layer).

Read data/analytics/products.db. Answer these 7 business questions scoped to
food & beverage on Java Island:
1. Price distribution by subcategory (chocolate, candy, snacks, sweets)
2. Subcategory demand ranking (by total sold count)
3. Regional pricing across Java Island cities
4. Price vs rating correlation
5. Top cities by seller count and rating
6. Market gaps (high demand subcategories, few sellers)
7. Trend analysis over time (how sold counts change)

Save results to data/analytics/insights.json. Each answer must include:
the question, the data/method used, the result, and a brief insight.

Verify: all 7 questions answered, results are non-empty, insights are
meaningful (not just "the average is X").
```
