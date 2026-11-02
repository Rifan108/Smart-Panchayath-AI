# Vercel Deployment Configuration for Kerala Smart Panchayat AI
# Render.com is the primary deployment target for Dash/Flask apps.
# This Procfile is used by Render.

web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 wsgi:server
