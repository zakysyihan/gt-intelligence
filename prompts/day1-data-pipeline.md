# Claude Code Prompt — Data Pipeline

> Single prompt for Claude Code. Implements the full data pipeline per SPEC.md.
> Runs on VPS: ubuntu@43.133.140.154 at /home/ubuntu/gt-intelligence/

---

## Prompt

```
Read SPEC.md sections 3 and 4 for full context. Read research/marketplace-scraping.md for API details.

Build the complete data pipeline for this project. ALL work happens on VPS.

**SCOPE:** Food & beverage on Java Island only. Target ~1,000 products.
**SUBCATEGORIES:** chocolate, candy, snacks, sweets

**STEP 1: Scraper (src/pipeline/scraper.py)**

Build a Tokopedia scraper using httpx.
- GraphQL endpoint: https://gql.tokopedia.com/graphql/SearchProductQueryV4
- Search keywords: "cokelat", "permen", "snack", "camilan", "keripik", "biskuit", "wafer", "chocolate", "candy"
- Collect these fields: timestamp, product_name, category, price, rating, review_count, sold_count, shop_name, shop_location (city and province), shop_rating, product_url
- Rate limit: 2 seconds between requests, rotate User-Agent headers
- Save raw JSON to data/raw/tokopedia_{keyword}_{date}.json
- Filter: only Java Island shop_locations (Jakarta, Jawa Barat, Jawa Tengah, Jawa Timur, Banten, Yogyakarta, Jawa)
- If Tokopedia fails, fall back to Shopee API scraping or BPS data download

**STEP 2: Staging**

After scraping, copy all raw JSON files from data/raw/ to data/staging/ as a backup.

**STEP 3: Cleaner (src/pipeline/cleaner.py)**

Read data/staging/*.json. Clean and transform:
- Map API fields to our 14-field schema (see SPEC.md Section 3)
- Deduplicate by product_url (keep first occurrence)
- Remove rows with missing price or sold_count
- Normalize price: remove "Rp" prefix, remove dots, convert to int
- Normalize sold_count: "1rb+" → 1000, "10rb+" → 10000, "100rb+" → 100000
- Parse product_name to extract: flavor (keyword matching), weight (regex for \d+g/\d+gr/\d+ml), variant (keyword matching)
- Add computed columns: price_bucket (cheap/mid/expensive based on subcategory median), rating_category (low/medium/high)
- Save to data/cleaned/products_clean.csv

**STEP 4: Validator (src/pipeline/validator.py)**

Read data/cleaned/products_clean.csv. Run these checks:
- Schema: all 14 fields present
- Types: price is int, rating is float, sold_count is int
- Nulls: 0 nulls in price, sold_count, subcategory, shop_location
- Range: price > 0, rating between 1-5, sold_count >= 0
- Dedup: unique product_url
- Geography: shop_location in Java Island list
- Print pass/fail for each check. Print row count.

**STEP 5: Curated (write to SQLite)**

Read data/cleaned/products_clean.csv. Write to data/analytics/products.db:
- Table: products (14 fields + computed columns)
- Add index on subcategory and shop_location for fast queries
- Print final row count and summary stats

**STEP 6: Main entry point**

Create src/pipeline/run_pipeline.py that runs steps 1-5 in sequence.
Add: pip install httpx pandas pytest to requirements.txt

**VERIFY:** Run the full pipeline. Check:
- Raw JSON files exist in data/raw/
- Staging backup exists in data/staging/
- Cleaned CSV has ~1000 rows
- Validation passes all checks
- SQLite database has data
```
