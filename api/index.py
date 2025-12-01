"""
Vercel serverless function entry point for FastAPI backend.
"""
import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

try:
    # Try to import the full backend
    from backend.api.main import app
    print("Successfully imported full backend")
    handler = app
except Exception as e:
    print(f"Full backend import failed: {e}")
    try:
        # Try to import the minimal version
        from main_minimal import app
        print("Using minimal backend")
        handler = app
    except Exception as e2:
        print(f"Minimal backend import failed: {e2}")
        # Last resort: create a simple FastAPI app
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse

        app = FastAPI()

        @app.get("/")
        async def root():
            return {"error": "All imports failed", "backend_error": str(e), "minimal_error": str(e2)}

        @app.get("/health")
        async def health():
            return {"status": "error", "message": "Fallback mode"}

        handler = app
