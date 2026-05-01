"""
Comparison Page — Side-by-side ward comparison with dual radar and tables.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go


def create_comparison_layout(engine):
    """Create the ward comparison page."""
    df = engine.df_processed
    ward_names = sorted(df["ward_name"].tolist())

    return html.Div([
        html.Div([
            html.H1("📋 Ward Comparison Tool", className="page-title"),
            html.P("Compare any two wards side-by-side across all sectors",
                   className="page-subtitle"),
        ], className="page-header"),

        # Dual selectors
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("Ward A:", className="control-label"),
                    dcc.Dropdown(
                        id="compare-ward-a",
                        options=[{"label": w, "value": w} for w in ward_names],
                        value=ward_names[0] if ward_names else None,
                        className="dark-dropdown",
                    ),
                ], md=5),
                dbc.Col(html.Div(
                    html.H3("VS", style={"textAlign": "center", "color": "#26A69A", "marginTop": "30px"}),
                ), md=2),
                dbc.Col([
                    html.Label("Ward B:", className="control-label"),
                    dcc.Dropdown(
                        id="compare-ward-b",
                        options=[{"label": w, "value": w} for w in ward_names],
                        value=ward_names[1] if len(ward_names) > 1 else None,
                        className="dark-dropdown",
                    ),
                ], md=5),
            ]),
        ], className="controls-card", style={"padding": "25px", "marginBottom": "20px"}),

        # Comparison content (updated by callback)
        html.Div(id="comparison-content-container", style={"position": "relative", "zIndex": 1}),
    ])


def create_comparison_content(engine, ward_a, ward_b):
    """Create comparison visualizations for two wards."""
    df = engine.df_processed
    row_a = df[df["ward_name"] == ward_a]
    row_b = df[df["ward_name"] == ward_b]

    if row_a.empty or row_b.empty:
        return html.P("Please select two valid wards.")

    score_cols = [c for c in df.columns if c.startswith("score_")]
    labels = [c.replace("score_", "").replace("_", " ").title() for c in score_cols]

    vals_a = row_a[score_cols].values[0].tolist()
    vals_b = row_b[score_cols].values[0].tolist()

    # Dual radar chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(38,166,154,0.3)",
        line_color="#26A69A", name=ward_a,
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(239,83,80,0.3)",
        line_color="#EF5350", name=ward_b,
    ))
    fig.update_layout(
        title=f"Vulnerability Comparison: {ward_a} vs {ward_b}",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
                   bgcolor="rgba(0,0,0,0)"),
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=500, font=dict(family="Inter", color="#E7E9EA"),
    )

    # Bar comparison
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=labels, y=vals_a, name=ward_a, marker_color="#26A69A"))
    bar_fig.add_trace(go.Bar(x=labels, y=vals_b, name=ward_b, marker_color="#EF5350"))
    bar_fig.update_layout(
        title="Sector-wise Vulnerability Comparison", barmode="group",
        yaxis_title="Vulnerability Score", template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=400, font=dict(family="Inter", color="#E7E9EA"),
        xaxis_tickangle=-30,
    )

    # Comparison table
    table_rows = []
    for label, col, va, vb in zip(labels, score_cols, vals_a, vals_b):
        diff = va - vb
        indicator = "🔴" if diff > 0.05 else "🟢" if diff < -0.05 else "🟡"
        winner = ward_a if va > vb else ward_b if vb > va else "Tie"
        table_rows.append(html.Tr([
            html.Td(label), html.Td(f"{va:.3f}"), html.Td(f"{vb:.3f}"),
            html.Td(f"{diff:+.3f}"), html.Td(indicator),
            html.Td(f"More vulnerable: {winner}"),
        ]))

    # Overall comparison
    vi_a = float(row_a["vulnerability_index"].values[0])
    vi_b = float(row_b["vulnerability_index"].values[0])

    return html.Div([
        # Summary cards
        dbc.Row([
            dbc.Col(html.Div([
                html.H4(ward_a, style={"color": "#26A69A"}),
                html.H2(f"{vi_a:.3f}", style={"color": "#26A69A"}),
                html.P(f"Category: {row_a['vulnerability_category'].values[0]}"),
                html.P(f"Priority: {row_a['priority_sector_1'].values[0]}" if "priority_sector_1" in row_a.columns else ""),
            ], className="glass-card priority-card", style={"textAlign": "center"}), md=5),
            dbc.Col(html.Div(
                html.H2("⚔️", style={"textAlign": "center", "fontSize": "3rem", "marginTop": "30px"}),
            ), md=2),
            dbc.Col(html.Div([
                html.H4(ward_b, style={"color": "#EF5350"}),
                html.H2(f"{vi_b:.3f}", style={"color": "#EF5350"}),
                html.P(f"Category: {row_b['vulnerability_category'].values[0]}"),
                html.P(f"Priority: {row_b['priority_sector_1'].values[0]}" if "priority_sector_1" in row_b.columns else ""),
            ], className="glass-card priority-card", style={"textAlign": "center"}), md=5),
        ], style={"marginBottom": "20px"}),

        # Charts
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig), className="glass-card chart-card"), md=6),
            dbc.Col(html.Div(dcc.Graph(figure=bar_fig), className="glass-card chart-card"), md=6),
        ]),

        # Table
        html.Div([
            html.H4("📊 Detailed Sector Comparison", className="section-title"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Sector"), html.Th(ward_a), html.Th(ward_b),
                    html.Th("Difference"), html.Th(""), html.Th("Analysis"),
                ])),
                html.Tbody(table_rows),
            ], bordered=True, hover=True, striped=True, responsive=True),
        ], className="glass-card table-card"),
    ])
