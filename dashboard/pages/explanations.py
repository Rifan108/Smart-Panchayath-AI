"""
Explanations Page — SHAP-based AI explanations with plots and natural language.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np


def create_explanations_layout(engine):
    """Create the AI explanations page."""
    df = engine.df_processed
    ward_names = sorted(df["ward_name"].tolist())

    return html.Div([
        html.Div([
            html.H1("🔍 AI Explanations (Explainable AI)", className="page-title"),
            html.P("Understand WHY the AI prioritized specific sectors using SHAP analysis",
                   className="page-subtitle"),
        ], className="page-header"),

        # Ward selector
        html.Div([
            html.Label("Select Ward to Explain:", className="control-label"),
            dcc.Dropdown(
                id="explain-ward-selector",
                options=[{"label": w, "value": w} for w in ward_names],
                value=ward_names[0] if ward_names else None,
                className="dark-dropdown",
                style={"maxWidth": "400px"},
            ),
        ], className="controls-card", style={"padding": "20px", "marginBottom": "20px"}),

        # Explanation content (updated by callback)
        html.Div(id="explanation-content-container", style={"position": "relative", "zIndex": 1}),

        # Global feature importance (static)
        html.Div([
            html.H4("🌍 Global Feature Importance", className="section-title"),
            html.P("Which indicators matter most across ALL wards for sector prioritization?"),
            dcc.Graph(figure=create_global_importance_chart(engine), id="global-importance"),
        ], className="glass-card chart-card"),
    ])


def create_ward_explanation(engine, ward_name):
    """Create ward-specific explanation content."""
    ward_data = engine.get_ward_data(ward_name)
    if not ward_data:
        return html.P("No data available.")

    # Get explanation text
    explanation_text = engine.get_ward_explanation(ward_name)

    # Priority sectors
    p1 = ward_data.get("priority_sector_1", "N/A")
    p2 = ward_data.get("priority_sector_2", "N/A")
    p3 = ward_data.get("priority_sector_3", "N/A")
    conf = ward_data.get("priority_confidence_1", 0)

    # SHAP feature importance for this ward
    shap_chart = create_ward_shap_chart(engine, ward_name)

    return html.Div([
        # Priority sectors cards
        dbc.Row([
            dbc.Col(html.Div([
                html.H5("🥇 Priority #1", className="priority-rank"),
                html.H3(p1, style={"color": "#F44336"}),
                html.P(f"Confidence: {conf:.1%}"),
            ], className="glass-card priority-card"), md=4),
            dbc.Col(html.Div([
                html.H5("🥈 Priority #2", className="priority-rank"),
                html.H3(p2, style={"color": "#FF9800"}),
            ], className="glass-card priority-card"), md=4),
            dbc.Col(html.Div([
                html.H5("🥉 Priority #3", className="priority-rank"),
                html.H3(p3, style={"color": "#42A5F5"}),
            ], className="glass-card priority-card"), md=4),
        ], style={"marginBottom": "20px"}),

        # Natural language explanation
        html.Div([
            html.H4("💬 AI Explanation", className="section-title"),
            dcc.Markdown(explanation_text, className="explanation-text"),
        ], className="glass-card", style={"padding": "25px", "marginBottom": "20px", "position": "relative", "zIndex": 100, "overflow": "visible"}),

        # SHAP chart
        html.Div([
            html.H4("📊 SHAP Feature Contributions", className="section-title"),
            html.P("Top indicators influencing the AI decision for this ward:"),
            dcc.Graph(figure=shap_chart),
        ], className="glass-card chart-card"),
    ])


def create_ward_shap_chart(engine, ward_name):
    """Create a waterfall-style SHAP chart for a ward."""
    if engine.shap_values is None:
        fig = go.Figure()
        fig.add_annotation(text="SHAP analysis not available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font_size=16)
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=400)
        return fig

    from models.explainer import get_feature_shap_for_ward
    ward_idx = engine.df_processed[engine.df_processed["ward_name"] == ward_name].index
    if len(ward_idx) == 0:
        return go.Figure()
    ward_idx = ward_idx[0]

    contributions = get_feature_shap_for_ward(
        engine.shap_values, ward_idx, engine.feature_cols, top_n=15
    )

    features = [c[0].replace("_", " ").title() for c in contributions]
    values = [c[1] for c in contributions]
    colors = ["#F44336" if v > 0 else "#4CAF50" for v in values]

    fig = go.Figure(data=[go.Bar(
        y=features[::-1], x=values[::-1], orientation="h",
        marker_color=colors[::-1],
        text=[f"{v:+.3f}" for v in values[::-1]], textposition="outside",
    )])
    fig.update_layout(
        title=f"SHAP Feature Impact — {ward_name}",
        xaxis_title="SHAP Value (Impact on Prediction)",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=500,
        font=dict(family="Inter", color="#E7E9EA"), margin=dict(l=200),
    )
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    return fig


def create_global_importance_chart(engine):
    """Create global feature importance bar chart."""
    importance = engine.get_feature_importance()
    top_15 = dict(list(importance.items())[:15])

    features = [k.replace("_", " ").title() for k in top_15.keys()]
    values = list(top_15.values())

    fig = go.Figure(data=[go.Bar(
        y=features[::-1], x=values[::-1], orientation="h",
        marker=dict(color=values[::-1], colorscale=[[0, "#004D40"], [1, "#26A69A"]]),
        text=[f"{v:.4f}" for v in values[::-1]], textposition="outside",
    )])
    fig.update_layout(
        title="Global Feature Importance (XGBoost + Random Forest Combined)",
        xaxis_title="Importance Score", template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=500, font=dict(family="Inter", color="#E7E9EA"),
        margin=dict(l=200),
    )
    return fig
