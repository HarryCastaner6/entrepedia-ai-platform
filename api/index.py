"""
Vercel serverless function entry point for FastAPI backend.
"""
from backend.api.main import app

# Vercel expects a variable named 'app' or 'handler'
# FastAPI is ASGI, Vercel supports it natively
handler = app
