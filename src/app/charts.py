"""Chart generation helpers for GT Intelligence.

Returns Plotly figure dicts that Chainlit can render inline.
All charts use a consistent color palette and Indonesian labels.

ponytail: Simple functions returning dicts — no chart class hierarchy,
no abstract base, no registry. Just functions that produce Plotly JSON.
"""

# Color palette — muted, professional
COLORS = {
    "primary": "#2563EB",
    "secondary": "#7C3AED",
    "accent": "#059669",
    "warning": "#D97706",
    "bg": "#F8FAFC",
    "text": "#1E293B",
    "grid": "#E2E8F0",
}

SUBCATEGORY_COLORS = {
    "chocolate": "#7C3AED",
    "candy": "#EC4899",
    "snacks": "#F59E0B",
    "sweets": "#10B981",
}

LAYOUT_DEFAULTS = {
    "font": {"family": "Inter, system-ui, sans-serif", "size": 12},
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
}


def _base_layout(title: str, **kwargs) -> dict:
    """Base layout with consistent styling."""
    layout = {**LAYOUT_DEFAULTS, "title": {"text": title, "font": {"size": 14}}}
    layout.update(kwargs)
    return layout


def subcategory_demand_chart(data: list) -> dict:
    """Bar chart: demand by subcategory."""
    subcategories = [r[0] for r in data]
    totals = [r[1] for r in data]
    colors = [SUBCATEGORY_COLORS.get(s, COLORS["primary"]) for s in subcategories]

    return {
        "data": [
            {
                "type": "bar",
                "x": subcategories,
                "y": totals,
                "marker": {"color": colors},
                "text": [f"{t:,.0f}" for t in totals],
                "textposition": "outside",
            }
        ],
        "layout": _base_layout(
            "Total Penjualan per Subkategori",
            yaxis={"title": "Total Terjual", "gridcolor": COLORS["grid"]},
            xaxis={"title": ""},
            showlegend=False,
        ),
    }


def price_distribution_chart(data: list) -> dict:
    """Bar chart: price distribution histogram."""
    ranges = [r[0] for r in data]
    counts = [r[1] for r in data]

    return {
        "data": [
            {
                "type": "bar",
                "x": ranges,
                "y": counts,
                "marker": {"color": COLORS["primary"]},
                "text": counts,
                "textposition": "outside",
            }
        ],
        "layout": _base_layout(
            "Distribusi Harga Produk",
            yaxis={"title": "Jumlah Produk", "gridcolor": COLORS["grid"]},
            xaxis={"title": "Rentang Harga (IDR)"},
            showlegend=False,
        ),
    }


def geo_distribution_chart(data: list) -> dict:
    """Horizontal bar chart: geographic distribution."""
    cities = [r[0] for r in data][::-1]
    counts = [r[1] for r in data][::-1]

    return {
        "data": [
            {
                "type": "bar",
                "y": cities,
                "x": counts,
                "orientation": "h",
                "marker": {"color": COLORS["accent"]},
                "text": counts,
                "textposition": "outside",
            }
        ],
        "layout": _base_layout(
            "Distribusi Penjual per Kota",
            xaxis={"title": "Jumlah Penjual", "gridcolor": COLORS["grid"]},
            yaxis={"title": ""},
            height=500,
            margin={"l": 120, "r": 20, "t": 40, "b": 40},
        ),
    }


def agent_result_chart(
    data: list[dict], columns: list[str], chart_type: str, question: str
) -> dict | None:
    """Generate a chart from agent query results.

    Picks chart config based on chart_type hint from the agent and
    the shape of the data returned.
    """
    if not data or len(columns) < 2:
        return None

    # Use first non-text column as x, second numeric column as y
    x_vals = [str(row.get(columns[0], "")) for row in data]
    y_col = None
    for col in columns[1:]:
        try:
            float(data[0].get(col, 0))
            y_col = col
            break
        except (ValueError, TypeError):
            continue

    if not y_col:
        return None

    y_vals = [float(row.get(y_col, 0)) for row in data]

    if chart_type == "bar":
        return {
            "data": [
                {
                    "type": "bar",
                    "x": x_vals,
                    "y": y_vals,
                    "marker": {"color": COLORS["primary"]},
                    "text": [f"{v:,.0f}" for v in y_vals],
                    "textposition": "outside",
                }
            ],
            "layout": _base_layout(
                question[:60],
                yaxis={"title": y_col.replace("_", " ").title(), "gridcolor": COLORS["grid"]},
                xaxis={"title": ""},
            ),
        }

    elif chart_type == "line":
        return {
            "data": [
                {
                    "type": "scatter",
                    "x": x_vals,
                    "y": y_vals,
                    "mode": "lines+markers",
                    "line": {"color": COLORS["primary"], "width": 2},
                    "marker": {"size": 6},
                }
            ],
            "layout": _base_layout(
                question[:60],
                yaxis={"title": y_col.replace("_", " ").title(), "gridcolor": COLORS["grid"]},
                xaxis={"title": ""},
            ),
        }

    elif chart_type == "pie":
        return {
            "data": [
                {
                    "type": "pie",
                    "labels": x_vals,
                    "values": y_vals,
                    "marker": {
                        "colors": [COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["warning"]]
                    },
                    "textinfo": "label+percent",
                }
            ],
            "layout": _base_layout(question[:60]),
        }

    elif chart_type == "scatter" and len(columns) >= 3:
        # Use third column as second numeric axis
        z_col = None
        for col in columns[2:]:
            try:
                float(data[0].get(col, 0))
                z_col = col
                break
            except (ValueError, TypeError):
                continue

        if z_col:
            z_vals = [float(row.get(z_col, 0)) for row in data]
            return {
                "data": [
                    {
                        "type": "scatter",
                        "x": y_vals,
                        "y": z_vals,
                        "mode": "markers",
                        "marker": {"color": COLORS["primary"], "size": 8},
                        "text": x_vals,
                    }
                ],
                "layout": _base_layout(
                    question[:60],
                    xaxis={"title": y_col.replace("_", " ").title()},
                    yaxis={"title": z_col.replace("_", " ").title()},
                ),
            }

    # Default: bar chart
    return {
        "data": [
            {
                "type": "bar",
                "x": x_vals[:20],
                "y": y_vals[:20],
                "marker": {"color": COLORS["primary"]},
            }
        ],
        "layout": _base_layout(question[:60]),
    }
