"""
WSGI entry point for production deployment (Render, Railway, etc.)
Exposes the Flask `server` object for gunicorn.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

server, dash_app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    server.run(host="0.0.0.0", port=port)
