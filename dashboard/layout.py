"""
Dashboard Layout — Main layout with sidebar navigation and page container.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_sidebar():
    """Create the sidebar navigation."""
    return html.Div(
        [
            html.Div(
                [
                    html.H4("🏛️ Smart Panchayat", className="sidebar-title"),
                    html.P("AI Planner", className="sidebar-subtitle"),
                ],
                className="sidebar-header",
            ),
            html.Hr(style={"borderColor": "rgba(255,255,255,0.1)"}),
            dbc.Nav(
                [
                    dbc.NavLink([html.I(className="nav-icon"), "🏠 Overview"],
                                href="/dashboard/", active="exact", id="nav-overview"),
                    dbc.NavLink([html.I(className="nav-icon"), "📊 Vulnerability"],
                                href="/dashboard/vulnerability", active="exact", id="nav-vulnerability"),
                    dbc.NavLink([html.I(className="nav-icon"), "💰 Budget"],
                                href="/dashboard/budget", active="exact", id="nav-budget"),
                    dbc.NavLink([html.I(className="nav-icon"), "🔍 AI Explain"],
                                href="/dashboard/explanations", active="exact", id="nav-explanations"),
                    dbc.NavLink([html.I(className="nav-icon"), "📋 Compare"],
                                href="/dashboard/compare", active="exact", id="nav-compare"),
                ],
                vertical=True,
                pills=True,
                className="sidebar-nav",
            ),
            html.Div(
                [
                    html.P("Manjeshwar Grama Panchayat", className="sidebar-footer-text"),
                    html.P("Kasaragod, Kerala", className="sidebar-footer-sub"),
                ],
                className="sidebar-footer",
            ),
        ],
        className="sidebar",
    )


def create_layout():
    """Create the main application layout."""
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="engine-data", storage_type="memory"),
            create_sidebar(),
            html.Div(id="page-content", className="main-content"),
        ],
        className="app-container",
    )
