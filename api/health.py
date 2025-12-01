"""
Health check endpoint for Vercel deployment.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Health Check")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "Entrepedia AI Platform",
        "version": "1.0.0",
        "deployment": "vercel"
    }

# For Vercel
handler = app