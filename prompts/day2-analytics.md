Read SPEC.md sections 2 and 5. The data is at data/analytics/products.db on VPS (672 products, 1 table, 14 columns).

Write 5 analytics scripts that answer the business questions from SPEC.md Section 2. Each script queries DuckDB/SQLite and produces a structured result (JSON or dict) suitable for dashboard rendering. Save results to data/analytics/insights.json.

Category 1: Top products by sold_count + subcategory demand ranking + trend over time
Category 2: Revenue proxy (price × sold_count) per product + price distribution by subcategory
Category 3: Geographic distribution across Java Island cities + regional pricing comparison
Category 4: Weekly sold_count pattern
Category 5: Price vs sold_count correlation + top flavors/weights per subcategory

Each result must include: question, data (table/chart), insight (1-2 sentence Indonesian summary).
