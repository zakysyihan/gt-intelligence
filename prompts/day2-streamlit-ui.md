Read SPEC.md, CLAUDE.md, research/llm-selection.md, and the existing src/llm/agent.py, src/llm/data_loader.py, src/app/charts.py.

The current UI is Chainlit (chat-first). The user needs dashboard-first: main area is a dashboard with metric cards + charts, and a collapsible side panel on the right for the analyst agent chat. The side panel supports multiple analysis sessions (create new, revisit previous). Charts in the chat can be clicked to expand full-screen. The dashboard should have filters (subcategory, location, price range). Reuse the agent logic and chart modules — only rewrite the UI layer in Streamlit.

If Streamlit can't achieve the desired UX, consider a custom HTML/CSS/JS solution with a Python backend. The user cares about smooth, polished UX — not just functionality.

Work on a feature branch. Verify on VPS at http://43.133.140.154.
