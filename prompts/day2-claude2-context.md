Before you proceed with the 4 items, here is context from discussions you may not have:

**Analytics / Dashboard data:**
- review_count is 0 for ALL 672 products (tokopaedi does not expose it). Do not use review_count in any queries or charts.
- rating IS available (616/672 have rating > 0, 56 have rating=0 = new products). Use rating for quality signals.
- Google Trends API (pytrends) is now in the tech stack for temporal/trend data. Scrape interest for keywords: "snack Indonesia", "cokelat Indonesia", "permen Indonesia" over 12 months.
- SPEC.md Section 4 now includes Google Trends as the trend data source. Limitation: search interest ≠ actual sales.

**Quadrant analysis (new dashboard widget):**
- SPEC.md Section 2 Category 5.5 now has a quadrant: Demand (sold_count) vs Quality (rating).
- Four quadrants: Quality Gap (opportunity), Winning Formula (study), Hidden Gem (niche), Failing (avoid).
- Interpretation is from brand owner / product creator perspective.

**Dashboard widgets (8 total, per updated SPEC.md Section 7):**
1. Market snapshot (4 metric cards)
2. Subcategory comparison (grouped bar)
3. Price sweet spot (histogram)
4. Top 10 cities (horizontal bar)
5. Product spec signals (table)
6. Trend analysis (Google Trends line chart)
7. Opportunity quadrant (scatter: demand vs rating)
8. Revenue proxy (scatter: price vs demand)

**SPEC.md has been updated** with all of this. Read Section 7 and Section 8 before proceeding.
