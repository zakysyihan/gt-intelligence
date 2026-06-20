"""GT Intelligence — Streamlit Dashboard + Analyst Chat.

Dashboard-first layout with toggleable chat panel:
- Main area: metric cards + charts + "Buka Chat" button
- Right panel: analyst agent chat (toggle via st.session_state)

Reuses: agent.py (GTAgent), data_loader.py, charts.py
Only this file is Streamlit-specific.
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
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.8rem; font-weight: 700; color: #1e293b;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-size: 0.85rem; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #334155;
        margin: 1rem 0 0.5rem 0; padding-bottom: 0.3rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .insight-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #2563eb; border-radius: 0 8px 8px 0;
        padding: 12px 16px; margin: 8px 0;
        font-size: 0.9rem; line-height: 1.5;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stChatMessage"] { padding: 8px 12px; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Agent initialization (cached)
# ---------------------------------------------------------------------------

@st.cache_resource
def get_agent():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    sqlite_path = PROJECT_ROOT / "data" / "analytics" / "products.db"
    con = load_sqlite_to_duckdb(sqlite_path)
    return GTAgent(duckdb_con=con, openai_api_key=api_key)


@st.cache_data
def get_dashboard_data():
    agent = get_agent()
    if agent is None:
        return None
    return agent.get_dashboard_data()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def init_session_state():
    if "sessions" not in st.session_state:
        st.session_state.sessions = {"Session 1": {"messages": []}}
    if "active_session" not in st.session_state:
        st.session_state.active_session = "Session 1"
    if "session_counter" not in st.session_state:
        st.session_state.session_counter = 1
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = True


# ---------------------------------------------------------------------------
# Dashboard (left panel)
# ---------------------------------------------------------------------------

def render_dashboard():
    dash = get_dashboard_data()
    if dash is None:
        st.error("Agent tidak tersedia. Pastikan OPENAI_API_KEY sudah di-set.")
        return

    top_sub = dash["top_subcategory"]
    avg_price = dash["avg_price"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📦 Total Produk", f"{dash['total_products']:,}")
    with c2: st.metric("🏆 Subkategori Terlaris", top_sub[0], f"{top_sub[1]:,} terjual")
    with c3: st.metric("💵 Harga Rata-rata", f"Rp {avg_price:,.0f}")
    with c4: st.metric("📍 Kota di Jawa", f"{dash['java_products']:,}")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<p class="section-header">📊 Demand per Subkategori</p>', unsafe_allow_html=True)
        st.plotly_chart(subcategory_demand_chart(dash["subcategory_demand"]),
                        use_container_width=True, key="chart_demand")
    with col_r:
        st.markdown('<p class="section-header">💰 Distribusi Harga</p>', unsafe_allow_html=True)
        st.plotly_chart(price_distribution_chart(dash["price_distribution"]),
                        use_container_width=True, key="chart_price")

    st.markdown('<p class="section-header">🗺️ Distribusi Geografis (Top 15 Kota)</p>',
                unsafe_allow_html=True)
    st.plotly_chart(geo_distribution_chart(dash["geo_distribution"]),
                    use_container_width=True, key="chart_geo")


# ---------------------------------------------------------------------------
# Chat panel (right column)
# ---------------------------------------------------------------------------

def render_chat_panel():
    st.markdown("### 🤖 Analis Pasar")

    sessions = st.session_state.sessions
    session_names = list(sessions.keys())

    col1, col2 = st.columns([3, 1])
    with col1:
        active = st.selectbox("Sesi", session_names,
                              index=session_names.index(st.session_state.active_session),
                              key="session_select", label_visibility="collapsed")
        st.session_state.active_session = active
    with col2:
        if st.button("➕", key="new_session", help="Sesi baru"):
            st.session_state.session_counter += 1
            new_name = f"Session {st.session_state.session_counter}"
            sessions[new_name] = {"messages": []}
            st.session_state.active_session = new_name
            st.rerun()

    st.divider()

    st.markdown("**⚡ Quick Actions**")
    quick_actions = [
        ("🏆", "Top 10 produk terlaris bulan ini"),
        ("📈", "Tren penjualan per subkategori"),
        ("💰", "Estimasi pendapatan tertinggi"),
        ("🗺️", "Distribusi per kota di Jawa"),
        ("📊", "Harga rata-rata per subkategori"),
        ("🍫", "Spesifikasi paling laris"),
    ]
    qa_cols = st.columns(2)
    for i, (emoji, prompt) in enumerate(quick_actions):
        with qa_cols[i % 2]:
            if st.button(f"{emoji} {prompt}", key=f"qa_{i}", use_container_width=True):
                _process_question(prompt)

    st.divider()

    active_msgs = sessions[st.session_state.active_session]["messages"]
    for msg in active_msgs:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑‍💼" if role == "user" else "🤖"):
            if role == "user":
                st.markdown(msg["content"])
            else:
                _render_assistant_message(msg)

    if question := st.chat_input("Tanya tentang data pasar...", key="chat_input"):
        _process_question(question)


def _process_question(question: str):
    agent = get_agent()
    if agent is None:
        st.error("Agent tidak tersedia.")
        return

    msgs = st.session_state.sessions[st.session_state.active_session]["messages"]
    msgs.append({"role": "user", "content": question})

    with st.spinner("🔍 Menganalisis data..."):
        response = agent.ask(question)

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
    if msg.get("error"):
        st.error(f"{'❌ **Tidak Dapat Dijawab**' if msg.get('is_unanswerable') else '⚠️ Error'}: {msg['error']}")
        return

    if msg.get("sql"):
        with st.expander("🔍 Lihat SQL", expanded=False):
            st.code(msg["sql"], language="sql")

    if msg.get("data"):
        df = pd.DataFrame(msg["data"])
        st.dataframe(df, use_container_width=True, height=min(200, 40 + len(df) * 35))

    if msg.get("insight"):
        st.markdown(f'<div class="insight-box">💡 {msg["insight"]}</div>', unsafe_allow_html=True)

    if msg.get("data") and msg.get("chart_type") and msg["chart_type"] != "table":
        fig = agent_result_chart(msg["data"], msg["columns"], msg["chart_type"], msg.get("content", ""))
        if fig:
            with st.expander("📊 Lihat Chart", expanded=False):
                st.plotly_chart(fig, use_container_width=True)

    if msg.get("follow_ups"):
        st.markdown("**🔍 Lanjutkan analisis:**")
        for fu in msg["follow_ups"]:
            if st.button(f"➡️ {fu[:60]}", key=f"fu_{hash(fu)}"):
                _process_question(fu)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    init_session_state()

    agent = get_agent()
    if agent is None:
        st.title("🏢 GT Intelligence")
        st.error("⚠️ OPENAI_API_KEY belum di-set. Tambahkan ke file `.env`.")
        st.stop()

    # --- Two-column layout with toggle ---
    if st.session_state.chat_open:
        # Dashboard (left, wide) + Chat (right, narrow)
        dash_col, chat_col = st.columns([2, 1])

        with dash_col:
            st.markdown("# 🏢 GT Intelligence — Market Analyst")
            st.markdown("*LLM-powered market intelligence untuk bisnis general trade*")

            if st.button("💬 Tutup Chat", key="toggle_close"):
                st.session_state.chat_open = False
                st.rerun()

            render_dashboard()

        with chat_col:
            render_chat_panel()
    else:
        # Dashboard full width + "Buka Chat" button
        st.markdown("# 🏢 GT Intelligence — Market Analyst")
        st.markdown("*LLM-powered market intelligence untuk bisnis general trade*")

        if st.button("💬 Buka Chat", key="toggle_open", type="primary"):
            st.session_state.chat_open = True
            st.rerun()

        render_dashboard()


if __name__ == "__main__":
    main()
