"""
Overview Page — Panchayat overview with key stats, ward rankings, and summary.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go


def create_stat_card(title, value, subtitle="", icon="", color="#26A69A"):
    """Create a glassmorphism stat card."""
    return dbc.Col(
        html.Div(
            [
                html.Div(icon, className="stat-icon"),
                html.H3(value, className="stat-value", style={"color": color}),
                html.P(title, className="stat-title"),
                html.Small(subtitle, className="stat-subtitle"),
            ],
            className="stat-card glass-card",
        ),
        md=3, sm=6, xs=12,
    )


def create_overview_layout(engine):
    """Create the overview page layout."""
    summary = engine.get_all_wards_summary()
    df = engine.df_processed

    # Stats
    total_pop = int(df["population"].sum())
    avg_vuln = df["vulnerability_index"].mean()
    top_ward = summary.iloc[0]["ward_name"] if len(summary) > 0 else "N/A"
    top_sector = df["priority_sector_1"].mode().iloc[0] if "priority_sector_1" in df.columns else "N/A"
    high_vuln_count = len(df[df["vulnerability_category"] == "High"])

    # Vulnerability distribution bar chart
    vuln_fig = go.Figure()
    sorted_df = df.sort_values("vulnerability_index", ascending=True)
    colors = ["#4CAF50" if v == "Low" else "#FF9800" if v == "Medium" else "#F44336"
              for v in sorted_df["vulnerability_category"]]
    vuln_fig.add_trace(go.Bar(
        y=sorted_df["ward_name"], x=sorted_df["vulnerability_index"],
        orientation="h", marker_color=colors,
        text=[f"{v:.2f}" for v in sorted_df["vulnerability_index"]],
        textposition="outside",
    ))
    vuln_fig.update_layout(
        title="Ward Vulnerability Index Rankings",
        xaxis_title="Vulnerability Index", yaxis_title="",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=700,
        font=dict(family="Inter", color="#E7E9EA"),
        margin=dict(l=150),
    )

    # Category distribution pie
    cat_counts = df["vulnerability_category"].value_counts()
    pie_fig = go.Figure(data=[go.Pie(
        labels=cat_counts.index, values=cat_counts.values,
        hole=0.5, marker_colors=["#4CAF50", "#FF9800", "#F44336"],
        textinfo="label+value",
        textposition="inside",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    )])
    pie_fig.update_layout(
        title="Vulnerability Distribution",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=350,
        font=dict(family="Inter", color="#E7E9EA"),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.15,
            xanchor="center", x=0.5,
            font=dict(size=11, color="#E7E9EA"),
        ),
        margin=dict(t=50, b=60),
    )

    return html.Div([
        # Header
        html.Div([
            html.H1("Manjeshwar Grama Panchayat", className="page-title"),
            html.P("AI-Enabled Local Development Assistance Planner • Kasaragod District, Kerala",
                   className="page-subtitle"),
        ], className="page-header"),

        # Stat Cards
        dbc.Row([
            create_stat_card("Total Population", f"{total_pop:,}", "2011 Census", "👥", "#26A69A"),
            create_stat_card("Avg Vulnerability", f"{avg_vuln:.3f}", f"{high_vuln_count} wards high-risk", "⚡", "#FF9800"),
            create_stat_card("Most Vulnerable Ward", top_ward, "Needs urgent attention", "🔴", "#F44336"),
            create_stat_card("Top Priority Sector", top_sector, "Across all wards", "🎯", "#42A5F5"),
        ], className="stat-row"),

        # Charts
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=vuln_fig, id="overview-vuln-chart"), className="glass-card chart-card"), md=8),
            dbc.Col(html.Div(dcc.Graph(figure=pie_fig, id="overview-pie-chart"), className="glass-card chart-card"), md=4),
        ], className="chart-row"),

        # Ward Table
        html.Div([
            html.H4("📋 Ward Summary Table", className="section-title"),
            dbc.Table.from_dataframe(
                summary.round(3), striped=True, bordered=True, hover=True,
                responsive=True, className="ward-table",
            ),
        ], className="glass-card table-card"),
    ])
