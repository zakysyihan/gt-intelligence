# Plan: Analytics Dashboard Upgrade

## Changes

### 1. Metric Cards
- Remove avg_price card
- Add "Harga Diminati" — price bucket with highest total sold_count
- Backend: new SQL query in `get_dashboard_data()`

### 2. Price Chart Rename + Data Change
- Rename to "Distribusi Demand per Harga"
- Y-axis: sold_count grouped by price bucket (not product count)
- Backend: modify price_distribution query to SUM(sold_count) instead of COUNT(*)

### 3. Geographic Map (scatter_mapbox)
- Replace bar chart with Plotly scatter_mapbox
- OpenStreetMap tiles (free, no API key)
- Hardcoded lat/lng dict for ~32 Java Island cities
- Bubble size = seller_count, label top cities
- Backend: add lat/lng to geo_distribution response

### 4. Quadrant 1 — Quality (dynamic thresholds)
- X: sold_count, Y: rating
- Thresholds: median of each (not maxX/2 and 3.5)
- Labels: Winning Formula, Hidden Gem, Volume Only, Avoid

### 5. Quadrant 2 — Distribution (new)
- X: sold_count, Y: store_count (sellers listing same product)
- Normalize product names to identify same product across sellers
- Thresholds: median of each
- Labels: Mass Market, Niche Centralized, Wide but Weak, Avoid

### 6. Future improvements doc

## Files to Modify
- `src/llm/agent.py` — get_dashboard_data() + new queries
- `src/api/server.py` — new endpoints, updated responses
- `static/app.js` — new chart renderers, updated metrics
- `static/index.html` — layout updates
- `SPEC.md` — document changes
- `HISTORY.md` — session notes
