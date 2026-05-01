"""
Dashboard Callbacks — Page routing and interactive callbacks.
"""

from dash import Input, Output, callback, html, dcc
from dashboard.pages.overview import create_overview_layout
from dashboard.pages.vulnerability import create_vulnerability_layout, create_radar_chart
from dashboard.pages.budget import create_budget_layout, create_budget_charts
from dashboard.pages.explanations import create_explanations_layout, create_ward_explanation
from dashboard.pages.comparison import create_comparison_layout, create_comparison_content


def register_callbacks(app, engine):
    """Register all dashboard callbacks."""

    # ─── Page Routing ──────────────────────────────────────────────
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname):
        if pathname == "/dashboard/" or pathname == "/dashboard":
            return create_overview_layout(engine)
        elif pathname == "/dashboard/vulnerability":
            return create_vulnerability_layout(engine)
        elif pathname == "/dashboard/budget":
            return create_budget_layout(engine)
        elif pathname == "/dashboard/explanations":
            return create_explanations_layout(engine)
        elif pathname == "/dashboard/compare":
            return create_comparison_layout(engine)
        else:
            return create_overview_layout(engine)

    # ─── Vulnerability Radar ───────────────────────────────────────
    @app.callback(
        Output("vulnerability-radar-container", "children"),
        Input("vulnerability-ward-selector", "value"),
    )
    def update_vulnerability_radar(ward_name):
        if not ward_name:
            return html.P("Select a ward to view its radar chart.")
        fig = create_radar_chart(engine, ward_name)
        return dcc.Graph(figure=fig)

    # ─── Budget Charts ─────────────────────────────────────────────
    @app.callback(
        Output("budget-charts-container", "children"),
        Input("budget-ward-selector", "value"),
        Input("budget-input", "value"),
    )
    def update_budget(ward_name, budget_lakhs):
        if not ward_name:
            return html.P("Select a ward.")
        if budget_lakhs is None or budget_lakhs < 1:
            budget_lakhs = 50
        return create_budget_charts(engine, ward_name, budget_lakhs)

    # ─── AI Explanations ──────────────────────────────────────────
    @app.callback(
        Output("explanation-content-container", "children"),
        Input("explain-ward-selector", "value"),
    )
    def update_explanation(ward_name):
        if not ward_name:
            return html.P("Select a ward.")
        return create_ward_explanation(engine, ward_name)

    # ─── Ward Comparison ──────────────────────────────────────────
    @app.callback(
        Output("comparison-content-container", "children"),
        Input("compare-ward-a", "value"),
        Input("compare-ward-b", "value"),
    )
    def update_comparison(ward_a, ward_b):
        if not ward_a or not ward_b:
            return html.P("Select two wards to compare.")
        if ward_a == ward_b:
            return html.P("Please select two different wards.", className="warning-text")
        return create_comparison_content(engine, ward_a, ward_b)
