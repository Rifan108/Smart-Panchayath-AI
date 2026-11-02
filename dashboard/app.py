"""
Dash App Initialization — Creates and configures the Plotly Dash application.
"""

import os
import dash
import dash_bootstrap_components as dbc

# Resolve assets folder relative to project root (parent of dashboard/)
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

def create_dash_app(server=None):
    """Create and configure the Dash application for Indian Government Digital Portal standard."""
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/dashboard/",
        assets_folder=ASSETS_DIR,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap",
        ],
        external_scripts=[
            "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js",
            "https://unpkg.com/lenis@1.1.18/dist/lenis.min.js",
        ],
        suppress_callback_exceptions=True,
        title="Smart AI Panchayat – Local Development Assistance Planner (LSGI)",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {"name": "description", "content": "Official AI-Enabled Local Development Assistance Planner (LSGI) for Panchayati Raj Institutions across Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, and Maharashtra."},
            {"name": "theme-color", "content": "#142D4E"},
        ],
    )
    return app

