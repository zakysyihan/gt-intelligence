Read SPEC.md, CLAUDE.md, and research/llm-selection.md. Work on branch feat/streamlit-ui.

Rewrite the UI from Chainlit to Streamlit. The data pipeline, agent logic, and LLM research are done — reuse src/llm/agent.py and src/llm/data_loader.py. Only rewrite the UI layer.

**Layout:** Dashboard is the main view (75% width). Analyst Agent chat is a collapsible side panel (25% width). When collapsed, dashboard takes full width. When expanded, side panel shows chat with multi-session history.

**Dashboard tab:** 4 metric cards (st.metric with delta), 4 Plotly charts in 2x2 grid (demand, price, geo, revenue proxy). Live data from SQLite via DuckDB. Reuse charts from src/app/charts.py.

**Side panel:** Collapsible via button toggle. Shows list of past analysis sessions. User can create new analysis or revisit previous. Each session preserves full chat history (SQL, table, chart, insight, follow-ups). Agent queries DuckDB, returns grounded answer with chart. Clicking a chart in chat opens it in a full-screen modal dialog.

**Agent:** Reuse GTAgent from src/llm/agent.py. Connect to SumoPod DeepSeek (OPENAI_API_KEY + OPENAI_BASE_URL from .env).

**Verify:** Run `streamlit run src/app/app.py` on VPS. Dashboard loads with live data. Side panel opens/closes. Ask a question, get SQL + table + chart + insight. Click chart to expand.
