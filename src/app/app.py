"""GT Intelligence — Streamlit Dashboard + Analyst Chat.

Dashboard-first layout:
- Main area: metric cards + filters + charts
- Sidebar (collapsible): analyst agent chat with multiple sessions

Reuses: agent.py (GTAgent), data_loader.py, charts.py
Only this file is Streamlit-specific.

ponytail: Single file for the Streamlit app. Dashboard and chat share
the same agent instance via st.session_state.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm.data_loader import load_sqlite_to_duckdb
from llm.agent import GTAgent, AgentResponse
from app.charts import (
    subcategory_demand_chart,
    price_distribution_chart,
    geo_distribution_chart,
    agent_result_chart,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="GT Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    /* Sidebar chat */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-left: 1px solid #e2e8f0;
    }
    /* Chat message bubbles */
    .chat-msg-user {
        background: #2563eb;
        color: white;
        border-radius: 16px 16px 4px 16px;
        padding: 10px 16px;
        margin: 4px 0;
        max-width: 90%;
        float: right;
        clear: both;
    }
    .chat-msg-assistant {
        background: #f1f5f9;
        color: #1e293b;
        border-radius: 16px 16px 16px 4px;
        padding: 10px 16px;
        margin: 4px 0;
        max-width: 90%;
        float: left;
        clear: both;
    }
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #334155;
        margin: 1rem 0 0.5rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #e2e8f0;
    }
    /* SQL code block */
    .sql-block {
        background: #1e293b;
        color: #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.82rem;
        overflow-x: auto;
        margin: 8px 0;
    }
    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #2563eb;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    /* Follow-up chips */
    .followup-chip {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 2px 4px;
        font-size: 0.8rem;
        color: #475569;
        cursor: pointer;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Agent initialization (cached)
# ---------------------------------------------------------------------------

@st.cache_resource
def get_agent():
    """Initialize agent (cached across reruns)."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    sqlite_path = PROJECT_ROOT / "data" / "analytics" / "products.db"
    con = load_sqlite_to_duckdb(sqlite_path)
    return GTAgent(duckdb_con=con, openai_api_key=api_key)


@st.cache_data
def get_dashboard_data():
    """Fetch dashboard data (cached)."""
    agent = get_agent()
    if agent is None:
        return None
    return agent.get_dashboard_data()


@st.cache_data
def get_filter_options():
    """Get unique values for filter widgets."""
    agent = get_agent()
    if agent is None:
        return [], [], (0, 1500000)
    con = agent.con
    subcats = [r[0] for r in con.execute("SELECT DISTINCT subcategory FROM products ORDER BY subcategory").fetchall()]
    locations = [r[0] for r in con.execute("SELECT DISTINCT shop_location FROM products ORDER BY shop_location").fetchall()]
    price_range = con.execute("SELECT MIN(price), MAX(price) FROM products").fetchone()
    return subcats, locations, (int(price_range[0]), int(price_range[1]))


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

def init_session_state():
    """Initialize session state variables."""
    if "sessions" not in st.session_state:
        st.session_state.sessions = {
            "Session 1": {"messages": [], "created": "Baru"}
        }
    if "active_session" not in st.session_state:
        st.session_state.active_session = "Session 1"
    if "session_counter" not in st.session_state:
        st.session_state.session_counter = 1
    if "sidebar_open" not in st.session_state:
        st.session_state.sidebar_open = True


# ---------------------------------------------------------------------------
# Dashboard rendering
# ---------------------------------------------------------------------------

def render_dashboard(filters: dict):
    """Render the main dashboard area with metrics, filters, and charts."""
    dash = get_dashboard_data()
    if dash is None:
        st.error("Agent tidak tersedia. Pastikan OPENAI_API_KEY sudah di-set.")
        return

    # --- Metric cards ---
    top_sub = dash["top_subcategory"]
    avg_price = dash["avg_price"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📦 Total Produk", f"{dash['total_products']:,}")
    with c2:
        st.metric("🏆 Subkategori Terlaris", top_sub[0], f"{top_sub[1]:,} terjual")
    with c3:
        st.metric("💵 Harga Rata-rata", f"Rp {avg_price:,.0f}")
    with c4:
        st.metric("📍 Kota di Jawa", f"{dash['java_products']:,}")

    st.divider()

    # --- Charts ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<p class="section-header">📊 Demand per Subkategori</p>', unsafe_allow_html=True)
        fig1 = subcategory_demand_chart(dash["subcategory_demand"])
        st.plotly_chart(fig1, use_container_width=True, key="chart_demand")

    with col_right:
        st.markdown('<p class="section-header">💰 Distribusi Harga</p>', unsafe_allow_html=True)
        fig2 = price_distribution_chart(dash["price_distribution"])
        st.plotly_chart(fig2, use_container_width=True, key="chart_price")

    st.markdown('<p class="section-header">🗺️ Distribusi Geografis (Top 15 Kota)</p>', unsafe_allow_html=True)
    fig3 = geo_distribution_chart(dash["geo_distribution"])
    st.plotly_chart(fig3, use_container_width=True, key="chart_geo")


# ---------------------------------------------------------------------------
# Chat rendering (in sidebar)
# ---------------------------------------------------------------------------

def render_chat_sidebar():
    """Render the analyst chat in the sidebar."""
    with st.sidebar:
        st.markdown("## 🤖 Analis Pasar")

        # --- Session management ---
        sessions = st.session_state.sessions
        session_names = list(sessions.keys())

        col1, col2 = st.columns([3, 1])
        with col1:
            active = st.selectbox(
                "Sesi",
                session_names,
                index=session_names.index(st.session_state.active_session),
                key="session_select",
                label_visibility="collapsed",
            )
            st.session_state.active_session = active
        with col2:
            if st.button("➕", key="new_session", help="Sesi baru"):
                st.session_state.session_counter += 1
                new_name = f"Session {st.session_state.session_counter}"
                sessions[new_name] = {"messages": [], "created": "Baru"}
                st.session_state.active_session = new_name
                st.rerun()

        st.divider()

        # --- Quick actions ---
        st.markdown("**⚡ Quick Actions**")
        quick_actions = [
            ("🏆", "Top 10 produk terlaris bulan ini"),
            ("📈", "Tren penjualan per subkategori"),
            ("💰", "Estimasi pendapatan tertinggi (harga × terjual)"),
            ("🗺️", "Distribusi penjualan per kota di Jawa"),
            ("📊", "Distribusi harga rata-rata per subkategori"),
            ("🍫", "Spesifikasi produk paling laris (rasa, berat)"),
        ]

        for emoji, prompt in quick_actions:
            if st.button(f"{emoji} {prompt[:35]}...", key=f"qa_{prompt[:20]}"):
                _process_question(prompt)

        st.divider()

        # --- Chat history ---
        active_msgs = sessions[st.session_state.active_session]["messages"]
        for msg in active_msgs:
            role = msg["role"]
            with st.chat_message(role, avatar="🧑‍💼" if role == "user" else "🤖"):
                if role == "user":
                    st.markdown(msg["content"])
                else:
                    _render_assistant_message(msg)

        # Chat input moved to main area for accessibility


def _process_question(question: str):
    """Process a question and add to active session."""
    agent = get_agent()
    if agent is None:
        st.error("Agent tidak tersedia.")
        return

    sessions = st.session_state.sessions
    active = st.session_state.active_session
    msgs = sessions[active]["messages"]

    # Add user message
    msgs.append({"role": "user", "content": question})

    # Get agent response
    with st.spinner("🔍 Menganalisis data..."):
        response = agent.ask(question)

    # Build assistant message
    assistant_msg = {"role": "assistant", "content": question}
    if response.error and not response.data:
        assistant_msg["error"] = response.error
        assistant_msg["is_unanswerable"] = response.is_unanswerable
    else:
        assistant_msg["sql"] = response.sql
        assistant_msg["data"] = response.data
        assistant_msg["columns"] = response.columns
        assistant_msg["insight"] = response.insight
        assistant_msg["chart_type"] = response.chart_type
        assistant_msg["follow_ups"] = response.follow_ups

    msgs.append(assistant_msg)
    st.rerun()


def _render_assistant_message(msg: dict):
    """Render an assistant message in the sidebar chat."""
    # Error handling
    if msg.get("error"):
        if msg.get("is_unanswerable"):
            st.error(f"❌ **Tidak Dapat Dijawab**\n\n{msg['error']}")
        else:
            st.error(f"⚠️ Error: {msg['error']}")
        return

    # SQL (collapsible)
    if msg.get("sql"):
        with st.expander("🔍 Lihat SQL", expanded=False):
            st.code(msg["sql"], language="sql")

    # Data table
    if msg.get("data"):
        df = pd.DataFrame(msg["data"])
        st.dataframe(df, use_container_width=True, height=min(200, 40 + len(df) * 35))

    # Insight
    if msg.get("insight"):
        st.markdown(f'<div class="insight-box">💡 {msg["insight"]}</div>', unsafe_allow_html=True)

    # Chart (expandable)
    if msg.get("data") and msg.get("chart_type") and msg["chart_type"] != "table":
        fig = agent_result_chart(
            msg["data"], msg["columns"], msg["chart_type"], msg.get("content", "")
        )
        if fig:
            with st.expander("📊 Lihat Chart", expanded=False):
                st.plotly_chart(fig, use_container_width=True)

    # Follow-ups
    if msg.get("follow_ups"):
        st.markdown("**🔍 Lanjutkan analisis:**")
        for fu in msg["follow_ups"]:
            if st.button(f"➡️ {fu[:60]}", key=f"fu_{fu[:30]}_{hash(fu)}"):
                _process_question(fu)


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

def main():
    init_session_state()

    # Check agent
    agent = get_agent()
    if agent is None:
        st.title("🏢 GT Intelligence")
        st.error("⚠️ OPENAI_API_KEY belum di-set. Tambahkan ke file `.env`.")
        st.stop()

    # --- Header ---
    st.markdown("# 🏢 GT Intelligence — Market Analyst")
    st.markdown("*LLM-powered market intelligence untuk bisnis general trade*")

    # --- Sidebar (session history + quick actions only) ---
    render_chat_sidebar()

    # --- Main dashboard ---
    render_dashboard({})

    # --- Chat section (always visible in main area) ---
    st.divider()
    st.markdown("## 💬 Analis Pasar")

    # Session selector in main area too
    sessions = st.session_state.sessions
    session_names = list(sessions.keys())
    col_sel, col_new = st.columns([4, 1])
    with col_sel:
        active = st.selectbox(
            "Sesi Aktif",
            session_names,
            index=session_names.index(st.session_state.active_session),
            key="main_session_select",
        )
        st.session_state.active_session = active
    with col_new:
        if st.button("➕ Sesi Baru", key="main_new_session"):
            st.session_state.session_counter += 1
            new_name = f"Session {st.session_state.session_counter}"
            sessions[new_name] = {"messages": [], "created": "Baru"}
            st.session_state.active_session = new_name
            st.rerun()

    # Quick actions in main area
    qa_cols = st.columns(3)
    quick_actions = [
        ("🏆", "Top 10 produk terlaris bulan ini"),
        ("📈", "Tren penjualan per subkategori"),
        ("💰", "Estimasi pendapatan tertinggi (harga × terjual)"),
        ("🗺️", "Distribusi penjualan per kota di Jawa"),
        ("📊", "Distribusi harga rata-rata per subkategori"),
        ("🍫", "Spesifikasi produk paling laris (rasa, berat)"),
    ]
    for i, (emoji, prompt) in enumerate(quick_actions):
        with qa_cols[i % 3]:
            if st.button(f"{emoji} {prompt[:40]}...", key=f"main_qa_{i}", use_container_width=True):
                _process_question(prompt)

    # Chat history in main area
    active_msgs = sessions[st.session_state.active_session]["messages"]
    for msg in active_msgs:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑‍💼" if role == "user" else "🤖"):
            if role == "user":
                st.markdown(msg["content"])
            else:
                _render_assistant_message(msg)

    # Chat input in main area (always visible)
    if question := st.chat_input("Tanya tentang data pasar..."):
        _process_question(question)


if __name__ == "__main__":
    main()
