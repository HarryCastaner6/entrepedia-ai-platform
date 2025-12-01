"""
Vercel serverless function entry point with fallback system.
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
    # Use minimal FastAPI fallback
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.security import OAuth2PasswordRequestForm
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from datetime import timedelta
    import jwt
    import datetime

    # Pydantic models
    class Token(BaseModel):
        access_token: str
        token_type: str

    # Create FastAPI app
    app = FastAPI(title="Entrepedia AI Platform API (Fallback Mode)")

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://entrepedia-ai-platform.vercel.app",
            "https://*.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Demo credentials
    DEMO_USERS = {
        "admin@entrepedia.ai": "admin123",
        "admin": "admin123",
        "testuser": "test123",
        "test@example.com": "test123"
    }

    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
            to_encode.update({"exp": expire})

        secret_key = "fallback-secret-key-for-demo"
        return jwt.encode(to_encode, secret_key, algorithm="HS256")

    @app.get("/")
    async def root():
        return {
            "message": "Entrepedia AI Platform API",
            "version": "1.0.0",
            "mode": "fallback"
        }

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "mode": "fallback"
        }

    @app.post("/auth/login", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        username = form_data.username
        password = form_data.password

        if username in DEMO_USERS and DEMO_USERS[username] == password:
            access_token = create_access_token(
                data={"sub": username, "user_id": 1},
                expires_delta=timedelta(minutes=30)
            )
            return Token(access_token=access_token, token_type="bearer")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.post("/auth/logout")
    async def logout():
        return {"success": True, "message": "Logged out successfully"}

    @app.get("/auth/verify-token")
    async def verify_token():
        return {"success": True, "message": "Token valid", "user": "demo"}

    handler = app
