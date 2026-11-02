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

import gzip
import io
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from flask import Flask, redirect, request
from dashboard.app import create_dash_app
from dashboard.layout import create_layout
from dashboard.callbacks import register_callbacks
from services.analysis_service import AnalysisEngine
from config import DASH_HOST, DASH_PORT, DASH_DEBUG, RAW_DATA_FILE


def ensure_data_exists():
    """Generate multi-state dataset and train champion models if needed."""
    multi_state_path = os.path.join(
        os.path.dirname(RAW_DATA_FILE), "panchayats_multi_state_data.csv"
    )
    if not os.path.exists(multi_state_path):
        print("📊 Multi-state dataset not found. Generating data for 5 states & 128 panchayats...")
        from data.generate_multi_state_dataset import main as generate_multi
        generate_multi()
        print()

    champion_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "trained_models", "champion_priority_model.joblib"
    )
    if not os.path.exists(champion_path):
        print("🧠 Champion ML models not found. Running training & benchmarking pipeline...")
        from models.train_pipeline import main as run_train
        run_train()
        print()

    # Ensure user database is initialized
    from services.auth_service import init_db
    init_db()


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

    # Step 6: Register REST API Blueprint for location-scoped endpoints
    from services.api_service import api_bp
    server.register_blueprint(api_bp)

    # Step 7: Native Gzip Response Compression Middleware
    @server.after_request
    def compress_response(response):
        """Compress responses (JSON, HTML, CSS, JS, SVG) >= 500 bytes with gzip."""
        if (
            response.status_code < 200
            or response.status_code >= 300
            or "Content-Encoding" in response.headers
            or response.direct_passthrough
        ):
            return response

        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        content_type = response.content_type or ""
        compressible = any(
            t in content_type.lower()
            for t in ["text/", "application/json", "application/javascript", "image/svg+xml"]
        )
        if not compressible:
            return response

        data = response.get_data()
        if len(data) < 500:
            return response

        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(mode="wb", fileobj=gzip_buffer, compresslevel=6) as gzip_file:
            gzip_file.write(data)

        response.set_data(gzip_buffer.getvalue())
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = len(response.get_data())
        return response

    # Step 7: Serve assets from both /assets/ and /static/
    @server.route("/assets/<path:filename>")
    def serve_assets_direct(filename):
        from flask import send_from_directory
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        return send_from_directory(assets_dir, filename, max_age=86400)

    @server.route("/static/css/<path:filename>")
    def serve_css(filename):
        from flask import send_from_directory
        return send_from_directory(os.path.join("static", "css"), filename)

    # Step 8: Redirect root to dashboard
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
