"""Chart generation helpers for GT Intelligence.

Returns Plotly Figure objects for the FastAPI dashboard.
All charts use a consistent color palette and Indonesian labels.

ponytail: Simple functions returning go.Figure — no chart class hierarchy,
no abstract base, no registry.
"""

import plotly.graph_objects as go

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

LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, system-ui, sans-serif", size=12),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=40, r=20, t=40, b=40),
)


def _apply_layout(fig: go.Figure, title: str, **kwargs) -> go.Figure:
    """Apply consistent layout to a figure."""
    layout = {**LAYOUT_DEFAULTS, "title": dict(text=title, font=dict(size=14))}
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig


def subcategory_demand_chart(data: list) -> go.Figure:
    """Bar chart: demand by subcategory."""
    subcategories = [r[0] for r in data]
    totals = [r[1] for r in data]
    colors = [SUBCATEGORY_COLORS.get(s, COLORS["primary"]) for s in subcategories]

    fig = go.Figure(
        data=[
            go.Bar(
                x=subcategories,
                y=totals,
                marker_color=colors,
                text=[f"{t:,.0f}" for t in totals],
                textposition="outside",
            )
        ]
    )
    return _apply_layout(
        fig,
        "Total Penjualan per Subkategori",
        yaxis=dict(title="Total Terjual", gridcolor=COLORS["grid"]),
        xaxis=dict(title=""),
        showlegend=False,
    )


def price_distribution_chart(data: list) -> go.Figure:
    """Bar chart: price distribution histogram."""
    ranges = [r[0] for r in data]
    counts = [r[1] for r in data]

    fig = go.Figure(
        data=[
            go.Bar(
                x=ranges,
                y=counts,
                marker_color=COLORS["primary"],
                text=counts,
                textposition="outside",
            )
        ]
    )
    return _apply_layout(
        fig,
        "Distribusi Harga Produk",
        yaxis=dict(title="Jumlah Produk", gridcolor=COLORS["grid"]),
        xaxis=dict(title="Rentang Harga (IDR)"),
        showlegend=False,
    )


def geo_distribution_chart(data: list) -> go.Figure:
    """Horizontal bar chart: geographic distribution."""
    cities = [r[0] for r in data][::-1]
    counts = [r[1] for r in data][::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                y=cities,
                x=counts,
                orientation="h",
                marker_color=COLORS["accent"],
                text=counts,
                textposition="outside",
            )
        ]
    )
    return _apply_layout(
        fig,
        "Distribusi Penjual per Kota",
        xaxis=dict(title="Jumlah Penjual", gridcolor=COLORS["grid"]),
        yaxis=dict(title=""),
        height=500,
        margin=dict(l=120, r=20, t=40, b=40),
    )


def agent_result_chart(
    data: list[dict], columns: list[str], chart_type: str, question: str
) -> go.Figure | None:
    """Generate a chart from agent query results."""
    if not data or len(columns) < 2:
        return None

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
    y_title = y_col.replace("_", " ").title()

    if chart_type == "bar":
        fig = go.Figure(
            data=[
                go.Bar(
                    x=x_vals,
                    y=y_vals,
                    marker_color=COLORS["primary"],
                    text=[f"{v:,.0f}" for v in y_vals],
                    textposition="outside",
                )
            ]
        )
        return _apply_layout(
            fig,
            question[:60],
            yaxis=dict(title=y_title, gridcolor=COLORS["grid"]),
            xaxis=dict(title=""),
        )

    elif chart_type == "line":
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode="lines+markers",
                    line=dict(color=COLORS["primary"], width=2),
                    marker=dict(size=6),
                )
            ]
        )
        return _apply_layout(
            fig,
            question[:60],
            yaxis=dict(title=y_title, gridcolor=COLORS["grid"]),
            xaxis=dict(title=""),
        )

    elif chart_type == "pie":
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=x_vals,
                    values=y_vals,
                    marker_colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["warning"]],
                    textinfo="label+percent",
                )
            ]
        )
        return _apply_layout(fig, question[:60])

    elif chart_type == "scatter" and len(columns) >= 3:
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
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=y_vals,
                        y=z_vals,
                        mode="markers",
                        marker=dict(color=COLORS["primary"], size=8),
                        text=x_vals,
                    )
                ]
            )
            return _apply_layout(
                fig,
                question[:60],
                xaxis=dict(title=y_title),
                yaxis=dict(title=z_col.replace("_", " ").title()),
            )

    # Default: bar chart
    fig = go.Figure(
        data=[
            go.Bar(
                x=x_vals[:20],
                y=y_vals[:20],
                marker_color=COLORS["primary"],
            )
        ]
    )
    return _apply_layout(fig, question[:60])
