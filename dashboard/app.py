"""
Dash App Initialization — Creates and configures the Plotly Dash application.
"""

import os
import dash
import dash_bootstrap_components as dbc

# Resolve assets folder relative to project root (parent of dashboard/)
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

def create_dash_app(server=None):
    """Create and configure the Dash application."""
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/dashboard/",
        assets_folder=ASSETS_DIR,
        external_stylesheets=[
            dbc.themes.DARKLY,
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        ],
        suppress_callback_exceptions=True,
        title="Kerala Smart Panchayat AI Planner",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {"name": "description", "content": "AI-enabled development planning for Manjeshwar Grama Panchayat"},
        ],
    )
    return app
