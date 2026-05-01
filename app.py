"""
Kerala Smart Panchayat AI Planner
Main Application Entry Point

An AI-enabled decision support platform for Manjeshwar Grama Panchayat,
Kasaragod District, Kerala.

Usage:
    1. First run: python data/generate_dataset.py
    2. Then run: python app.py
    3. Open: http://127.0.0.1:8050/dashboard/
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, redirect
from dashboard.app import create_dash_app
from dashboard.layout import create_layout
from dashboard.callbacks import register_callbacks
from services.analysis_service import AnalysisEngine
from config import DASH_HOST, DASH_PORT, DASH_DEBUG, RAW_DATA_FILE


def ensure_data_exists():
    """Generate dataset if it doesn't exist."""
    if not os.path.exists(RAW_DATA_FILE):
        print("📊 Dataset not found. Generating synthetic data...")
        from data.generate_dataset import main as generate_data
        generate_data()
        print()


def create_app():
    """Create and configure the full application."""
    # Step 1: Ensure data exists
    ensure_data_exists()

    # Step 2: Create Flask server
    server = Flask(__name__)
    server.secret_key = "kerala-smart-panchayat-ai-2025"

    # Step 3: Create Dash app
    dash_app = create_dash_app(server)

    # Step 4: Initialize AI engine
    print("\n🧠 Initializing AI Analysis Engine...")
    engine = AnalysisEngine()
    engine.initialize()

    # Step 5: Set layout and register callbacks
    dash_app.layout = create_layout()
    register_callbacks(dash_app, engine)

    # Step 6: Serve custom CSS
    @server.route("/static/css/<path:filename>")
    def serve_css(filename):
        from flask import send_from_directory
        return send_from_directory(os.path.join("static", "css"), filename)

    # Step 7: Redirect root to dashboard
    @server.route("/")
    def index():
        return redirect("/dashboard/")

    return server, dash_app


if __name__ == "__main__":
    server, dash_app = create_app()

    print("\n" + "=" * 60)
    print("  🏛️  Kerala Smart Panchayat AI Planner")
    print("  📍 Manjeshwar Grama Panchayat, Kasaragod, Kerala")
    print(f"  🌐 Dashboard: http://{DASH_HOST}:{DASH_PORT}/dashboard/")
    print("=" * 60 + "\n")

    dash_app.run(
        host=DASH_HOST,
        port=DASH_PORT,
        debug=DASH_DEBUG,
    )
