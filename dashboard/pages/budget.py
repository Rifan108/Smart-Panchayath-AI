"""
Budget Page — Interactive budget allocation with input field and visualizations.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
from models.budget_allocator import compute_allocation
from models.vulnerability_index import get_sector_rankings


def create_budget_layout(engine):
    """Create the budget allocation page."""
    df = engine.df_processed
    ward_names = sorted(df["ward_name"].tolist())

    return html.Div([
        html.Div([
            html.H1("💰 Budget Allocation Optimizer", className="page-title"),
            html.P("AI-recommended budget distribution based on sector vulnerability",
                   className="page-subtitle"),
        ], className="page-header"),

        # Controls
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Ward:", className="control-label"),
                    dcc.Dropdown(
                        id="budget-ward-selector",
                        options=[{"label": w, "value": w} for w in ward_names],
                        value=ward_names[0] if ward_names else None,
                        className="dark-dropdown",
                    ),
                ], md=5),
                dbc.Col([
                    html.Label("Total Budget (₹ Lakhs):", className="control-label"),
                    dbc.InputGroup([
                        dbc.InputGroupText("₹", style={
                            "background": "rgba(38,166,154,0.2)",
                            "color": "#26A69A",
                            "border": "1px solid rgba(255,255,255,0.15)",
                            "fontWeight": "700",
                            "fontSize": "1.1rem",
                        }),
                        dbc.Input(
                            id="budget-input",
                            type="number",
                            min=1,
                            max=1000,
                            step=1,
                            value=50,
                            placeholder="Enter amount in Lakhs",
                            style={
                                "background": "rgba(255,255,255,0.08)",
                                "color": "#E7E9EA",
                                "border": "1px solid rgba(255,255,255,0.15)",
                                "fontSize": "1.1rem",
                                "fontWeight": "600",
                            },
                        ),
                        dbc.InputGroupText("Lakhs", style={
                            "background": "rgba(255,255,255,0.05)",
                            "color": "#8B98A5",
                            "border": "1px solid rgba(255,255,255,0.15)",
                            "fontSize": "0.9rem",
                        }),
                    ], style={"maxWidth": "320px"}),
                    html.Small(
                        "Enter any amount between ₹1L and ₹1000L",
                        style={"color": "#8B98A5", "marginTop": "6px", "display": "block"},
                    ),
                ], md=5),
            ], className="align-items-end"),
        ], className="controls-card", style={"padding": "25px", "marginBottom": "20px"}),

        # Charts container (updated by callback) — low z-index so dropdown overlays above
        html.Div(id="budget-charts-container", style={"position": "relative", "zIndex": 1}),
    ])


def create_budget_charts(engine, ward_name, total_budget_lakhs):
    """Create budget allocation charts for a ward."""
    if total_budget_lakhs is None or total_budget_lakhs < 1:
        total_budget_lakhs = 50

    total_budget = total_budget_lakhs * 100000  # Convert lakhs to rupees
    rankings = get_sector_rankings(engine.df_processed, ward_name)
    if not rankings:
        return html.P("No data available for this ward.")

    result = compute_allocation(rankings, total_budget)
    allocs = result["allocations"]

    # Donut chart — text INSIDE to avoid overlap, legend shows full names
    labels = [a["sector"] for a in allocs]
    values = [a["allocation_pct"] for a in allocs]
    colors_list = ["#26A69A", "#EF5350", "#AB47BC", "#42A5F5",
                   "#66BB6A", "#FFA726", "#EC407A", "#78909C"]
    donut = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.55,
        marker_colors=colors_list[:len(labels)],
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>Allocation: %{value:.1f}%<br>Amount: ₹%{customdata:,.0f}<extra></extra>",
        customdata=[a["allocation_amount"] for a in allocs],
        pull=[0.04 if a["is_priority"] else 0 for a in allocs],
    )])
    donut.update_layout(
        title=f"Budget Allocation — {ward_name} (₹{total_budget_lakhs} Lakhs)",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=480, font=dict(family="Inter", color="#E7E9EA"),
        legend=dict(
            orientation="v", yanchor="middle", y=0.5,
            xanchor="left", x=1.05,
            font=dict(size=11, color="#E7E9EA"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=20, r=180, t=50, b=20),
        annotations=[dict(text=f"₹{total_budget_lakhs}L", x=0.45, y=0.5,
                          font_size=22, showarrow=False, font_color="#26A69A")],
    )

    # Bar chart — amount view
    bar = go.Figure(data=[go.Bar(
        x=[a["sector"] for a in allocs],
        y=[a["allocation_amount"] for a in allocs],
        marker_color=[
            "#26A69A" if a["is_priority"] else "#78909C" for a in allocs
        ],
        text=[f"₹{a['allocation_amount']:,.0f}" for a in allocs],
        textposition="outside",
        textfont=dict(size=10),
    )])
    bar.update_layout(
        title="Allocation Amounts (₹)", yaxis_title="Amount (₹)",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=400,
        font=dict(family="Inter", color="#E7E9EA"), xaxis_tickangle=-30,
    )

    # Table
    table_rows = []
    for a in allocs:
        priority_badge = html.Span("⭐ PRIORITY", className="priority-badge") if a["is_priority"] else ""
        table_rows.append(html.Tr([
            html.Td(a["rank"]),
            html.Td(a["sector"]),
            html.Td(f"{a['vulnerability_score']:.3f}"),
            html.Td(f"{a['allocation_pct']:.1f}%"),
            html.Td(f"₹{a['allocation_amount']:,.0f}"),
            html.Td(priority_badge),
        ]))

    table = dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Rank"), html.Th("Sector"), html.Th("Vuln Score"),
            html.Th("Allocation %"), html.Th("Amount (₹)"), html.Th("Status"),
        ]))] + [html.Tbody(table_rows)],
        bordered=True, hover=True, striped=True, responsive=True,
    )

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=donut), className="glass-card chart-card"), md=6),
            dbc.Col(html.Div(dcc.Graph(figure=bar), className="glass-card chart-card"), md=6),
        ]),
        html.Div([
            html.H4("📋 Detailed Allocation Table", className="section-title"),
            html.P(f"Min: {result['constraints']['min_pct']}% | "
                   f"Max: {result['constraints']['max_pct']}% | "
                   f"Priority Boost: {result['constraints']['boost_factor']}x",
                   className="constraint-info"),
            table,
        ], className="glass-card table-card"),
    ])
