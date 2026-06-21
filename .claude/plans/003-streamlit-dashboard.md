# Plan: Dashboard-First UI with Streamlit

## Context

The current UI is Chainlit (chat-first). User needs dashboard-first: main area is dashboard with metric cards + charts + filters, collapsible side panel on right for analyst agent chat with multiple sessions. Charts in chat expandable full-screen. Reuse agent + charts modules, only rewrite UI layer.

**Decision: Streamlit** — satisfies all layout requirements, fast to implement, `go.Figure` charts work directly. Trade-off: less polished than custom HTML/CSS/JS, but adequate for MVP.

## Architecture

```
┌─────────────────────────────────────────────┬──────────────┐
│  Main Area (dashboard)                      │  Sidebar     │
│                                             │  (collapsible)│
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │              │
│  │ Total   │ │ Top Sub │ │ Avg     │       │  🤖 Analyst  │
│  │ 672     │ │ snacks  │ │ Rp 44K  │       │              │
│  └─────────┘ └─────────┘ └─────────┘       │  [New Chat]  │
│                                             │  [Session 1] │
│  ┌── Filters ──────────────────────────┐    │  [Session 2] │
│  │ Subcategory ▼ │ Location ▼ │ Price ▼│    │              │
│  └─────────────────────────────────────┘    │  💬 chat...  │
│                                             │              │
│  ┌── Chart 1 ──┐ ┌── Chart 2 ──┐           │  SQL shown   │
│  │  Demand     │ │  Price      │           │  Insight     │
│  │  by Subcat  │ │  Dist       │           │  Chart       │
│  └─────────────┘ └─────────────┘           │  Follow-ups  │
│                                             │              │
│  ┌── Chart 3 ───────────────────────┐       │              │
│  │  Geographic Distribution         │       │              │
│  └──────────────────────────────────┘       │              │
└─────────────────────────────────────────────┴──────────────┘
```

## Implementation Steps

### Step 1: Create feature branch
```bash
git checkout -b feat/streamlit-dashboard
```

### Step 2: Update dependencies
**`requirements.txt`:** Replace `chainlit>=1.0` with `streamlit>=1.37`

### Step 3: Create Streamlit app
**File:** `src/app/app.py` (rewrite)

**Layout:**
- `st.set_page_config(layout="wide", page_title="GT Intelligence")`
- Custom CSS for polished look (metric cards, sidebar styling)
- Sidebar: chat panel with session management
- Main: dashboard with filters + metrics + charts

**Dashboard section:**
- 4 `st.metric()` cards in a row
- 3 filter widgets in sidebar or above charts
- 3 Plotly charts via `st.plotly_chart(use_container_width=True)`
- Data auto-refreshes when filters change

**Chat section (sidebar):**
- `st.session_state` manages multiple chat sessions
- Session selector dropdown
- "New Chat" button
- `st.chat_input()` at bottom of sidebar
- Agent responses rendered with `st.chat_message()`
- Charts in chat are expandable via `st.expander()` or modal

**Filter logic:**
- Subcategory multiselect (chocolate, candy, snacks)
- Location multiselect (32 cities)
- Price range slider
- Filters create a filtered DuckDB view passed to agent

### Step 4: Update Dockerfile
Change CMD from `chainlit run` to `streamlit run`

### Step 5: Deploy and verify on VPS

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| UI framework | Streamlit | Dashboard-first layout, sidebar for chat, fast to build |
| Chart expand | `st.expander()` | Pseudo-fullscreen, simple to implement |
| Chat sessions | `st.session_state` dict | Native Streamlit pattern |
| Filters | Sidebar widgets | Standard Streamlit UX |
| Chart format | `go.Figure` (unchanged) | Both Streamlit and Chainlit accept it |

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/app/app.py` | Rewrite | Streamlit dashboard + chat |
| `requirements.txt` | Modify | Replace chainlit with streamlit |
| `Dockerfile` | Modify | Change CMD to streamlit |
| `.streamlit/config.toml` | Create | Streamlit theme config |

## Verification

1. App loads at http://43.133.140.154:8000
2. Dashboard shows 4 metric cards + 3 charts
3. Filters work (subcategory, location, price)
4. Chat in sidebar works
5. Multiple chat sessions work
6. Charts in chat are expandable
7. Agent responses include SQL, data, insight, follow-ups
