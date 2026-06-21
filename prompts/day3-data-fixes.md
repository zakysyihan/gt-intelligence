Read SPEC.md Section 3 (Dataset) and src/pipeline/cleaner.py. Make 4 changes:

1. Remove Java Island geo filter — keep all shop locations (the data is already Java anyway, 13 outside-Java products are actually East Java cities our filter missed)

2. Add `category` field — it exists in staging JSON (e.g., "Makanan & Minuman"). Carry it through cleaning into cleaned CSV and SQLite. Add it to the 14-field schema in SPEC.md.

3. Add location normalization — "Jakarta Barat" → "Jakarta", "Kab. Bandung" → "Bandung", "Kab. Tangerang" → "Tangerang", "Tangerang Selatan" → "Tangerang Selatan". Create a province-level field `shop_province` by extracting the province from location names (e.g., "Kab. Malang" → "Jawa Timur", "Jakarta Selatan" → "DKI Jakarta"). This enables province-level analytics.

4. After making changes, run the cleaning step on VPS (skip scraping) and verify: python3 -m src.pipeline.run_pipeline --skip-scrape

Read CLAUDE.md for VPS connection details. Work on a feature branch.
