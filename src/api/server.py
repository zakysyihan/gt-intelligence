"""FastAPI backend for GT Intelligence.

Serves the custom UI and provides REST API for:
- Dashboard data (metrics + charts)
- Chat (agentic AI with multi-step reasoning)
- Sessions (create, switch, list)
- Google Trends data

Port: 8000 (Streamlit moves to 8501)
"""

import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm.data_loader import load_sqlite_to_duckdb
from llm.agent import GTAgent

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="GT Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Agent init
# ---------------------------------------------------------------------------

_agent: Optional[GTAgent] = None


def get_agent() -> GTAgent:
    global _agent
    if _agent is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
        sqlite_path = PROJECT_ROOT / "data" / "analytics" / "products.db"
        con = load_sqlite_to_duckdb(sqlite_path)
        _agent = GTAgent(duckdb_con=con, openai_api_key=api_key)
    return _agent


# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

sessions: dict = {
    "session_1": {
        "id": "session_1",
        "title": "Sesi Baru",
        "messages": [],
    }
}
session_counter = 1


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class SessionCreate(BaseModel):
    title: Optional[str] = "Sesi Baru"


class TitleUpdate(BaseModel):
    session_id: str
    title: str


# ---------------------------------------------------------------------------
# Static files + SPA fallback
# ---------------------------------------------------------------------------

static_dir = PROJECT_ROOT / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def serve_index():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "Frontend not built yet"}


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

def _build_filter_clause(subcategories: str = None, province: str = None) -> tuple[str, list]:
    """Build SQL WHERE clause from filter params. Returns (clause, params)."""
    conditions = []
    params = []
    if subcategories:
        cats = [c.strip() for c in subcategories.split(",") if c.strip()]
        if cats:
            placeholders = ",".join(["?" for _ in cats])
            conditions.append(f"subcategory IN ({placeholders})")
            params.extend(cats)
    if province:
        # Filter by shop_location containing the province name
        conditions.append("shop_location LIKE ?")
        params.append(f"%{province}%")
    if conditions:
        return "WHERE " + " AND ".join(conditions), params
    return "", params


@app.get("/api/dashboard/filters")
async def get_filter_options():
    """Return available filter values (subcategories, provinces)."""
    agent = get_agent()
    subcats = [r[0] for r in agent.con.execute(
        "SELECT DISTINCT subcategory FROM products ORDER BY subcategory"
    ).fetchall()]
    provinces = [r[0] for r in agent.con.execute(
        "SELECT DISTINCT shop_location FROM products ORDER BY shop_location"
    ).fetchall()]
    return {"subcategories": subcats, "provinces": provinces}


@app.get("/api/dashboard")
async def get_dashboard(subcategories: str = None, province: str = None):
    """Return dashboard data (metrics + chart data), optionally filtered."""
    agent = get_agent()
    where, params = _build_filter_clause(subcategories, province)

    def q(sql):
        return agent.con.execute(sql, params).fetchall()

    def q1(sql):
        return agent.con.execute(sql, params).fetchone()

    total = q1("SELECT COUNT(*) FROM products " + where)[0]
    top_sub = q1(
        f"SELECT subcategory, SUM(sold_count) as total FROM products {where} GROUP BY subcategory ORDER BY total DESC LIMIT 1"
    )
    harga = q1(
        f"""SELECT price_range, total_sold FROM (
            SELECT CASE
                WHEN price < 5000 THEN '< 5K'
                WHEN price < 15000 THEN '5K-15K'
                WHEN price < 30000 THEN '15K-30K'
                WHEN price < 75000 THEN '30K-75K'
                WHEN price < 150000 THEN '75K-150K'
                ELSE '150K+'
            END as price_range, SUM(sold_count) as total_sold
            FROM products {where} GROUP BY price_range
        ) ORDER BY total_sold DESC LIMIT 1"""
    )
    total_shops = q1("SELECT COUNT(DISTINCT shop_name) FROM products " + where)[0]
    total_cities = q1("SELECT COUNT(DISTINCT shop_location) FROM products " + where)[0]

    subcat_demand = [list(r) for r in q(
        "SELECT subcategory, SUM(sold_count), COUNT(*) FROM products " + where + " GROUP BY subcategory ORDER BY SUM(sold_count) DESC"
    )]
    price_demand = [list(r) for r in q(
        """SELECT CASE
            WHEN price < 5000 THEN '< 5K'
            WHEN price < 15000 THEN '5K-15K'
            WHEN price < 30000 THEN '15K-30K'
            WHEN price < 75000 THEN '30K-75K'
            WHEN price < 150000 THEN '75K-150K'
            ELSE '150K+'
        END as price_range, SUM(sold_count), COUNT(*)
        FROM products """ + where + """ GROUP BY price_range ORDER BY MIN(price)"""
    )]
    geo_dist = [list(r) for r in q(
        "SELECT shop_location, COUNT(*), SUM(sold_count) FROM products " + where + " GROUP BY shop_location ORDER BY COUNT(*) DESC LIMIT 15"
    )]

    return {
        "total_products": total,
        "top_subcategory": list(top_sub) if top_sub else ["-", 0],
        "harga_diminati": list(harga) if harga else ["-", 0],
        "total_shops": total_shops,
        "total_cities": total_cities,
        "subcategory_demand": subcat_demand,
        "price_demand": price_demand,
        "geo_distribution": geo_dist,
    }


@app.get("/api/dashboard/quadrant")
async def get_quadrant_data(subcategories: str = None, province: str = None):
    """Return per-product data for the opportunity quadrant (demand vs rating)."""
    agent = get_agent()
    where, params = _build_filter_clause(subcategories, province)
    extra = " AND rating > 0" if where else "WHERE rating > 0"
    rows = agent.con.execute(
        "SELECT product_name, subcategory, sold_count, rating, price "
        "FROM products " + where + extra + " ORDER BY sold_count DESC LIMIT 200",
        params
    ).fetchall()
    return {
        "products": [
            {"name": r[0], "subcategory": r[1], "sold_count": r[2], "rating": r[3], "price": r[4]}
            for r in rows
        ]
    }


@app.get("/api/dashboard/quadrant-store")
async def get_quadrant_store_data(subcategories: str = None, province: str = None):
    """Return per-product data for distribution quadrant (demand vs store_count).

    Normalizes product names to identify the same product across sellers.
    store_count = number of distinct sellers listing the same product.
    """
    agent = get_agent()
    where, params = _build_filter_clause(subcategories, province)
    extra = " AND rating > 0" if where else "WHERE rating > 0"
    rows = agent.con.execute("""
        SELECT
            LOWER(TRIM(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(product_name, '\\*\\*\\s*', ''),
                        '\\s*\\[.*?\\]\\s*', ''
                    ),
                    '\\s+', ' '
                )
            )) as normalized_name,
            subcategory,
            SUM(sold_count) as total_sold,
            COUNT(DISTINCT shop_name) as store_count,
            AVG(rating) as avg_rating
        FROM products
        """ + where + extra + """
        GROUP BY normalized_name, subcategory
        HAVING store_count >= 1
        ORDER BY total_sold DESC
        LIMIT 200
    """, params).fetchall()
    return {
        "products": [
            {"name": r[0], "subcategory": r[1], "sold_count": r[2], "store_count": r[3], "rating": round(r[4], 2)}
            for r in rows
        ]
    }


@app.get("/api/dashboard/geo-map")
async def get_geo_map(subcategories: str = None, province: str = None):
    """Return geo data with lat/lng for mapbox visualization."""
    agent = get_agent()
    where, params = _build_filter_clause(subcategories, province)
    rows = agent.con.execute(
        "SELECT shop_location, COUNT(*) as seller_count, SUM(sold_count) as total_sold "
        "FROM products " + where + " GROUP BY shop_location ORDER BY seller_count DESC",
        params
    ).fetchall()

    CITY_COORDS = {
        "Surabaya": (-7.2575, 112.7521),
        "Kab. Bandung": (-6.9175, 107.6191),
        "Bandung": (-6.9175, 107.6191),
        "Jakarta Barat": (-6.1681, 106.7589),
        "Jakarta Utara": (-6.1219, 106.8748),
        "Jakarta Selatan": (-6.2615, 106.8106),
        "Jakarta Timur": (-6.2250, 106.9006),
        "Jakarta Pusat": (-6.1862, 106.8341),
        "Kab. Tangerang": (-6.1781, 106.6319),
        "Tangerang": (-6.1781, 106.6319),
        "Kab. Bekasi": (-6.2349, 106.9896),
        "Bekasi": (-6.2349, 106.9896),
        "Depok": (-6.4025, 106.7942),
        "Bogor": (-6.5971, 106.8060),
        "Malang": (-7.9666, 112.6326),
        "Semarang": (-6.9666, 110.4196),
        "Solo": (-7.5755, 110.8243),
        "Yogyakarta": (-7.7956, 110.3695),
        "Cirebon": (-6.7320, 108.5523),
        "Tasikmalaya": (-7.3466, 108.2090),
        "Purwokerto": (-7.4278, 109.2418),
        "Kediri": (-7.8490, 112.0068),
        "Madiun": (-7.5583, 111.5317),
        "Jember": (-8.1845, 113.6965),
        "Probolinggo": (-7.7543, 113.2159),
        "Garut": (-7.2175, 107.9038),
        "Sumedang": (-6.8361, 107.9225),
        "Karawang": (-6.3203, 107.3139),
        "Purwakarta": (-6.5569, 107.4431),
        "Sukabumi": (-6.9175, 106.9271),
        "Cianjur": (-6.8172, 107.1373),
        "Magelang": (-7.4704, 110.2178),
    }

    # Map cities to provinces
    CITY_TO_PROVINCE = {
        'Jakarta Barat': 'DKI Jakarta', 'Jakarta Utara': 'DKI Jakarta',
        'Jakarta Selatan': 'DKI Jakarta', 'Jakarta Timur': 'DKI Jakarta',
        'Jakarta Pusat': 'DKI Jakarta',
        'Tangerang': 'Banten', 'Kab. Tangerang': 'Banten', 'Serang': 'Banten',
        'Kab. Tangerang': 'Banten',
        'Bandung': 'Jawa Barat', 'Kab. Bandung': 'Jawa Barat',
        'Bekasi': 'Jawa Barat', 'Kab. Bekasi': 'Jawa Barat',
        'Depok': 'Jawa Barat', 'Bogor': 'Jawa Barat',
        'Karawang': 'Jawa Barat', 'Purwakarta': 'Jawa Barat',
        'Sumedang': 'Jawa Barat', 'Garut': 'Jawa Barat',
        'Tasikmalaya': 'Jawa Barat', 'Cirebon': 'Jawa Barat',
        'Sukabumi': 'Jawa Barat', 'Cianjur': 'Jawa Barat',
        'Semarang': 'Jawa Tengah', 'Solo': 'Jawa Tengah',
        'Purwokerto': 'Jawa Tengah', 'Cirebon': 'Jawa Tengah',
        'Magelang': 'Jawa Tengah',
        'Yogyakarta': 'DI Yogyakarta',
        'Surabaya': 'Jawa Timur', 'Malang': 'Jawa Timur',
        'Kediri': 'Jawa Timur', 'Madiun': 'Jawa Timur',
        'Jember': 'Jawa Timur', 'Probolinggo': 'Jawa Timur',
    }

    # Aggregate by province
    province_data = {}
    for r in rows:
        city = r[0]
        # Try exact match first, then partial
        prov = CITY_TO_PROVINCE.get(city)
        if not prov:
            for known_city, p in CITY_TO_PROVINCE.items():
                if known_city in city or city in known_city:
                    prov = p
                    break
        if not prov:
            prov = 'Lainnya'
        if prov not in province_data:
            province_data[prov] = {'seller_count': 0, 'total_sold': 0, 'cities': []}
        province_data[prov]['seller_count'] += r[1]
        province_data[prov]['total_sold'] += r[2]
        province_data[prov]['cities'].append(city)

    # Convert to list for Plotly choropleth
    result = [
        {'province': p, 'seller_count': d['seller_count'], 'total_sold': d['total_sold']}
        for p, d in province_data.items()
    ]

    return {"provinces": result}


@app.get("/api/dashboard/revenue")
async def get_revenue_data():
    """Return per-product data for revenue proxy chart (price vs demand)."""
    agent = get_agent()
    rows = agent.con.execute(
        "SELECT product_name, subcategory, price, sold_count, "
        "(price * sold_count) as estimated_revenue "
        "FROM products ORDER BY estimated_revenue DESC LIMIT 200"
    ).fetchall()
    return {
        "products": [
            {"name": r[0], "subcategory": r[1], "price": r[2], "sold_count": r[3], "estimated_revenue": r[4]}
            for r in rows
        ]
    }


@app.get("/api/dashboard/specs")
async def get_spec_signals():
    """Return top product specs (flavor/weight) by subcategory."""
    agent = get_agent()
    rows = agent.con.execute(
        "SELECT subcategory, flavor, weight, SUM(sold_count) as total_sold, COUNT(*) as count "
        "FROM products WHERE flavor IS NOT NULL AND flavor != '' "
        "GROUP BY subcategory, flavor, weight "
        "HAVING count >= 3 "
        "ORDER BY subcategory, total_sold DESC"
    ).fetchall()
    return {
        "specs": [
            {"subcategory": r[0], "flavor": r[1], "weight": r[2], "total_sold": r[3], "count": r[4]}
            for r in rows
        ]
    }


@app.get("/api/trends")
async def get_trends():
    """Return Google Trends data (cached)."""
    try:
        from llm.trends import get_trends_data
        data = get_trends_data()
        if data is None:
            return {"error": "Google Trends data not available", "data": None}
        return {"data": data}
    except ImportError:
        return {"error": "pytrends not installed", "data": None}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Process a chat message through the agentic AI."""
    agent = get_agent()

    # Get or create session
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[req.session_id]
    session["messages"].append({"role": "user", "content": req.message})

    # Run agent
    response = agent.ask(req.message)

    # Build assistant message
    assistant_msg = {"role": "assistant", "content": req.message}
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

    session["messages"].append(assistant_msg)

    # Generate title after first exchange
    if len(session["messages"]) == 2:
        try:
            title = agent.generate_title(session["messages"])
            session["title"] = title
        except Exception:
            pass

    return {
        "session_id": req.session_id,
        "title": session["title"],
        "message": assistant_msg,
        "history": session["messages"],
    }


@app.get("/api/sessions")
async def list_sessions():
    """List all chat sessions."""
    return {
        "sessions": [
            {"id": s["id"], "title": s["title"], "message_count": len(s["messages"])}
            for s in sessions.values()
        ]
    }


@app.post("/api/sessions")
async def create_session(req: SessionCreate):
    """Create a new chat session."""
    global session_counter
    session_counter += 1
    sid = f"session_{session_counter}"
    sessions[sid] = {"id": sid, "title": req.title, "messages": []}
    return {"session_id": sid, "title": req.title}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a session's full message history."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    s = sessions[session_id]
    return {"id": s["id"], "title": s["title"], "messages": s["messages"]}


@app.put("/api/sessions/{session_id}/title")
async def update_title(session_id: str, req: TitleUpdate):
    """Update session title."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    sessions[session_id]["title"] = req.title
    return {"ok": True}
