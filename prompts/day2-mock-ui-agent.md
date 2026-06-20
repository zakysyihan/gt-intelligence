# Claude Code Prompt — Mock Data + WrenAI Agent + Chainlit UI

> Second Claude terminal. Works on feat/ui-agent branch.
> Depends on: SPEC.md (read only), does NOT depend on real data.

---

## Prompt

```
Read SPEC.md sections 6, 7, and 8 for full context. Work on branch feat/ui-agent.

Build the WrenAI agent + Chainlit interface with mock data.

**STEP 1: Mock Data**

Create data/mock/ directory. Generate a realistic mock SQLite database
at data/mock/products_mock.db that matches our exact schema (14 fields + computed).
Use Python to generate ~500 rows with realistic Indonesian food & beverage data:
- Subcategories: chocolate, candy, snacks, sweets
- Locations: Jakarta, Bandung, Surabaya, Semarang, Yogyakarta, Tangerang, Bekasi
- Prices: realistic IDR ranges per subcategory (chocolate Rp 5k-50k, snacks Rp 3k-20k)
- Sold counts: realistic distribution (some high sellers, many mid, some low)
- Ratings: mostly 4.0-5.0 with some 3.0-4.0
- Product names: realistic Indonesian product names (Silverqueen, Chitato, Indomie, etc.)
- Include timestamps from June 2026

Create src/pipeline/mock_data.py to generate this.

**STEP 2: WrenAI Setup**

Install WrenAI: pip install wrenai

Create MDL configuration:
- mdl/models.yml: Define products table with all 14 fields + relationships
- mdl/instructions.yml: Business context for the LLM (what each field means,
  business terms mapping like "terlaris" = sold_count DESC, "opportunity" =
  high demand + few sellers)

Configure WrenAI to connect to the mock SQLite database.

**STEP 3: Chainlit Chat Interface**

Create src/app/app.py — Chainlit app with:
- Chat interface for natural language questions
- WrenAI agent as the backend (query data, generate SQL, return results)
- Each conversation is a separate analysis session
- Follow-up suggestions after each answer
- "How was this answer generated?" context shown

**STEP 4: Dashboard Welcome Screen**

When user opens the app, show summary metrics + charts before chat:
- 4 metric cards: total products, top subcategory, avg price, java island count
- 3 charts: subcategory demand bar, price distribution, geographic distribution
- 6 quick action buttons mapped to analysis categories (see SPEC.md Section 7)
- Metrics query from SQLite (live data from mock DB for now)

**STEP 5: Requirements**

Update requirements.txt with: wrenai, chainlit, httpx, pandas, plotly

**VERIFY:** Run the Chainlit app. Check:
- Dashboard loads with mock data metrics and charts
- Chat accepts questions and WrenAI generates SQL
- Agent returns grounded answers with data references
- Follow-up suggestions appear
- Quick action buttons send predefined questions
```
