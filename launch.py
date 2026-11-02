"""
Kerala Smart Panchayat AI — One-Click Launcher
Double-click this file (or run: python launch.py) to start the app.
The dashboard will open automatically in your browser.
"""

import os
import sys
import time
import threading
import webbrowser

# Set UTF-8 encoding for Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

URL = "http://127.0.0.1:8050/dashboard/"


def open_browser():
    """Wait for server to start, then open browser."""
    time.sleep(3)  # Give the server 3 seconds to start
    print(f"\n Opening browser at {URL}")
    webbrowser.open(URL)


def main():
    print("=" * 72)
    print("  Smart Panchayat AI Platform (5 States)")
    print("  Kerala • Karnataka • Tamil Nadu • Andhra Pradesh • Maharashtra")
    print("  Research ML Decision Support & Linear Programming Optimization Engine")
    print("=" * 72)
    print("\n[1/3] Verifying multi-state dataset & auth database...")

    from app import ensure_data_exists
    ensure_data_exists()
    print("      Statewide dataset and user auth verified!")

    print("\n[2/3] Starting AI engine & dashboard...")

    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    print("[3/3] Server starting...")
    print(f"\n  Dashboard URL: {URL}")
    print("  Press CTRL+C to stop the server.\n")

    # Import and run the app
    from app import create_app
    server, dash_app = create_app()

    dash_app.run(
        host="127.0.0.1",
        port=8050,
        debug=False,
    )


if __name__ == "__main__":
    main()
