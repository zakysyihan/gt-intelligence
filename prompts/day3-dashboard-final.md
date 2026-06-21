Read SPEC.md Section 7, the app code on VPS, and the existing dashboard implementation. Update the analytics dashboard with these changes:

**Metric cards (top row, 4 cards):**
- Total Produk, Total Toko, Total Kota (keep as-is)
- Rename "Harga Rata-rata" to "Harga Diminati" — show the price range or price point with highest demand, not just average

**Demand distribution section (below cards):**
- Demand per Subkategori (existing bar chart — keep)
- Demand per Price Point (histogram of sold_count grouped by price buckets — keep existing price distribution chart but rename to "Distribusi Demand per Harga")

**Geographic section:**
- Replace Top 10 Kota bar chart with a Plotly scatter_mapbox visualization
- Use OpenStreetMap tiles (free, no API token needed)
- Plot each city as a bubble sized by seller count, positioned by approximate lat/lng
- Create a hardcoded lookup dict of ~32 Java Island cities → coordinates (no scraping, no API)
- Kab/kota level — each city/region is a separate data point
- Keep it readable — label top cities

**Advanced Analytics section:**
- Quadrant 1: Customer Quality — sold_count (x) vs rating (y)
  - Dynamic thresholds: median of sold_count for x-split, median of rating for y-split
  - Labels: Winning Formula (high demand + high quality), Hidden Gem (low demand + high quality), Volume Only (high demand + low quality), Avoid (low demand + low quality)
  - Data point per product (each dot = one product, colored by subcategory)

- Quadrant 2: Distribution Level — sold_count (x) vs store_count (y)
  - "store_count" = number of sellers selling the same product (requires product name normalization)
  - Simple normalization: lowercase, remove punctuation, standardize weights (68g, 100gr → 68g), group by normalized name, count unique shop_name per group
  - Dynamic thresholds: median of sold_count for x-split, median of store_count for y-split
  - Labels: Mass Market (high demand + high distribution), Niche Centralized (low demand + high distribution), Wide but Weak (high demand + low distribution), Avoid (low demand + low distribution)
  - Data point per product

**Future improvements to note in docs (don't implement now):**
- review_count for engagement rate quadrant (not available from tokopaedi)
- Dynamic thresholding with percentile-based or cluster-based splits
- Fuzzy matching for better product name normalization
- Real map with GeoJSON boundaries (admin level 2)

Update any relevant docs before merging to main. Read CLAUDE.md for VPS details. Work on a feature branch. Merge when done.
