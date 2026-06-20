"""GT Intelligence — Chainlit Chat Interface.

Market intelligence agent for general trade businesses.
Powered by WrenAI MDL grounding + OpenAI gpt-4o-mini.

User flow (per SPEC.md Section 7):
1. User opens system → sees dashboard (summary metrics + charts)
2. Clicks "Chat" to ask deeper questions
3. Agent answers with data, charts, follow-up suggestions
4. User can start new chat for different analysis

ponytail: Single file for the Chainlit app. Dashboard rendering and
chat logic live together because they share the same agent instance.
No separate routes, no API layer — Chainlit handles the UI.
"""

import os
from pathlib import Path

import chainlit as cl
import orjson

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm.data_loader import load_sqlite_to_duckdb
from llm.agent import GTAgent
from app.charts import (
    subcategory_demand_chart,
    price_distribution_chart,
    geo_distribution_chart,
    agent_result_chart,
    COLORS,
)

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

_agent: GTAgent | None = None


def _get_agent() -> GTAgent:
    """Lazy-initialize the agent (first request)."""
    global _agent
    if _agent is not None:
        return _agent

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    sqlite_path = PROJECT_ROOT / "data" / "analytics" / "products.db"
    con = load_sqlite_to_duckdb(sqlite_path)
    _agent = GTAgent(duckdb_con=con, openai_api_key=api_key)
    return _agent


# ---------------------------------------------------------------------------
# Quick Action Buttons
# ---------------------------------------------------------------------------

QUICK_ACTIONS = [
    {
        "label": "🏆 Produk Terlaris",
        "category": "Cat 1: Demand",
        "prompt": "Produk mana yang paling banyak terjual bulan ini? Top 10 berdasarkan sold_count",
    },
    {
        "label": "📈 Tren Demand",
        "category": "Cat 1: Demand",
        "prompt": "Bagaimana tren penjualan per subkategori? Subkategori mana yang paling tinggi total penjualannya?",
    },
    {
        "label": "💰 Estimasi Pendapatan",
        "category": "Cat 2: Profitability",
        "prompt": "Produk mana yang menghasilkan estimasi pendapatan tertinggi (harga × terjual)? Top 10.",
    },
    {
        "label": "🗺️ Analisis Regional",
        "category": "Cat 3: Geographic",
        "prompt": "Bagaimana distribusi penjualan di berbagai kota di Jawa? Kota mana yang paling banyak penjualnya?",
    },
    {
        "label": "📊 Analisis Harga",
        "category": "Cat 2: Profitability",
        "prompt": "Bagaimana distribusi harga produk? Berapa harga rata-rata di tiap subkategori?",
    },
    {
        "label": "🍫 Sinyal Sukses Produk",
        "category": "Cat 5: Product Dev",
        "prompt": "Apa spesifikasi produk (rasa, berat) yang paling laris di tiap subkategori? Produk seperti apa yang sebaiknya kami kembangkan?",
    },
]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


async def render_dashboard():
    """Render the dashboard with metric cards and charts."""
    agent = _get_agent()
    dash = agent.get_dashboard_data()

    # Header
    await cl.Message(
        content="## 🏢 GT Intelligence — Market Analyst\n\nDashboard data dari "
        f"**{dash['total_products']}** produk Tokopedia di Jawa Island.",
    ).send()

    # Metric cards
    top_sub = dash["top_subcategory"]
    avg_price = dash["avg_price"]

    import pandas as pd

    metrics_df = pd.DataFrame([
        {"Metrik": "📦 Total Produk", "Nilai": f"{dash['total_products']:,}"},
        {"Metrik": "🏆 Subkategori Terlaris", "Nilai": f"{top_sub[0]} ({top_sub[1]:,} terjual)"},
        {"Metrik": "💵 Harga Rata-rata", "Nilai": f"Rp {avg_price:,.0f}"},
        {"Metrik": "📍 Produk di Jawa", "Nilai": f"{dash['java_products']:,}"},
    ])

    elements = [
        cl.Dataframe(
            name="metrics",
            data=metrics_df,
            display="inline",
        ),
    ]

    # Charts
    chart_configs = [
        ("📊 Demand per Subkategori", subcategory_demand_chart(dash["subcategory_demand"])),
        ("💰 Distribusi Harga", price_distribution_chart(dash["price_distribution"])),
        ("🗺️ Distribusi Geografis", geo_distribution_chart(dash["geo_distribution"])),
    ]

    for chart_name, chart_data in chart_configs:
        elements.append(
            cl.Plotly(name=chart_name, figure=chart_data, display="inline")
        )

    await cl.Message(content="### 📊 Dashboard", elements=elements).send()

    # Quick action buttons
    actions = [
        cl.Action(
            name="quick_action",
            label=a["label"],
            payload={"prompt": a["prompt"]},
            description=a["category"],
        )
        for a in QUICK_ACTIONS
    ]

    await cl.Message(
        content="### 💬 Ajukan Pertanyaan\n\n"
        "Gunakan tombol di bawah atau ketik pertanyaan Anda sendiri:",
        actions=actions,
    ).send()


# ---------------------------------------------------------------------------
# Chainlit Event Handlers
# ---------------------------------------------------------------------------


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session and show dashboard."""
    try:
        _get_agent()
        await render_dashboard()
    except Exception as e:
        await cl.Message(
            content=f"⚠️ Gagal memulai aplikasi: {e}\n\nPastikan OPENAI_API_KEY sudah di-set."
        ).send()


@cl.action_callback("quick_action")
async def on_quick_action(action: cl.Action):
    """Handle quick action button clicks."""
    prompt = action.payload.get("prompt", "")
    if prompt:
        await handle_question(prompt)


@cl.on_message
async def on_message(message: cl.Message):
    """Handle user messages."""
    await handle_question(message.content)


async def handle_question(question: str):
    """Process a question through the agent and render results."""
    agent = _get_agent()

    # Show thinking indicator
    msg = cl.Message(content="🔍 Menganalisis data...")
    await msg.send()

    # Get agent response
    response = agent.ask(question)

    # Handle errors
    if response.error and not response.data:
        if response.is_unanswerable:
            msg.content = f"❌ **Tidak Dapat Dijawab**\n\n{response.error}"
        else:
            msg.content = f"⚠️ **Error:** {response.error}"
        await msg.update()
        return

    # Build response content
    content_parts = []

    # SQL transparency
    if response.sql:
        content_parts.append(f"```sql\n{response.sql}\n```")

    # Data table
    if response.data:
        # Format as markdown table for readability
        if len(response.data) <= 20:
            cols = response.columns
            header = " | ".join(c.replace("_", " ").title() for c in cols)
            separator = " | ".join("---" for _ in cols)
            rows = []
            for row in response.data:
                cells = []
                for c in cols:
                    val = row.get(c, "")
                    if isinstance(val, float):
                        val = f"{val:,.2f}"
                    elif isinstance(val, int):
                        val = f"{val:,}"
                    cells.append(str(val)[:40])
                rows.append(" | ".join(cells))

            table_md = f"| {header} |\n| {separator} |\n" + "\n".join(
                f"| {r} |" for r in rows
            )
            content_parts.append(table_md)
        else:
            content_parts.append(
                f"*{len(response.data)} baris data ditemukan (menampilkan 20 teratas)*"
            )

    # Insight
    if response.insight:
        content_parts.append(f"\n### 💡 Insight\n{response.insight}")

    # Follow-ups
    if response.follow_ups:
        follow_up_text = "\n".join(f"- {fu}" for fu in response.follow_ups)
        content_parts.append(f"\n### 🔍 Lanjutkan Analisis\n{follow_up_text}")

    # Update message
    msg.content = f"### 📊 {question}\n\n" + "\n\n".join(content_parts)
    await msg.update()

    # Render chart if applicable
    if response.data and response.chart_type and response.chart_type != "table":
        chart = agent_result_chart(
            response.data, response.columns, response.chart_type, question
        )
        if chart:
            chart_msg = cl.Message(
                content="",
                elements=[cl.Plotly(name="result_chart", figure=chart, display="inline")],
            )
            await chart_msg.send()

    # Send follow-up action buttons
    if response.follow_ups:
        actions = [
            cl.Action(
                name="quick_action",
                label=f"➡️ {fu[:50]}",
                payload={"prompt": fu},
            )
            for fu in response.follow_ups[:3]
        ]
        await cl.Message(content="*", actions=actions).send()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # This is handled by: chainlit run src/app/app.py
    pass
