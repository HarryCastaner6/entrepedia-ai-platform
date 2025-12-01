"""
Minimal FastAPI app for Vercel deployment with fallback authentication.
"""
import os
from datetime import timedelta
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import security functions
try:
    from backend.utils.security import hash_password, verify_password, create_access_token
    from backend.utils.config import settings
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    import hashlib
    import jwt

    # Minimal security implementation
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hash_password(plain_password) == hashed_password

    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            import datetime
            expire = datetime.datetime.utcnow() + expires_delta
            to_encode.update({"exp": expire})

        secret_key = os.environ.get("JWT_SECRET_KEY", "fallback-secret-key")
        return jwt.encode(to_encode, secret_key, algorithm="HS256")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(
    title="Entrepedia AI Platform",
    description="Minimal deployment for Vercel",
    version="1.0.0"
)

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
    "admin@entrepedia.ai": {"password": "admin123", "username": "admin"},
    "admin": {"password": "admin123", "username": "admin"},
    "testuser": {"password": "test123", "username": "testuser"},
    "test@example.com": {"password": "test123", "username": "testuser"}
}

@app.get("/")
async def root():
    return {
        "message": "Entrepedia AI Platform API (Minimal Mode)",
        "version": "1.0.0",
        "mode": "fallback" if not SECURITY_AVAILABLE else "full"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mode": "fallback" if not SECURITY_AVAILABLE else "full",
        "environment": "production"
    }

@app.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Login with demo credentials.
    """
    try:
        username = form_data.username
        password = form_data.password

        # Check demo credentials
        if username in DEMO_USERS:
            user_data = DEMO_USERS[username]
            if user_data["password"] == password:
                access_token_expires = timedelta(minutes=30)
                access_token = create_access_token(
                    data={"sub": user_data["username"], "user_id": 1},
                    expires_delta=access_token_expires
                )

                return Token(access_token=access_token, token_type="bearer")

        # Authentication failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/auth/logout")
async def logout() -> Dict[str, Any]:
    """
    Logout user.
    """
    return {
        "success": True,
        "message": "Successfully logged out"
    }

@app.get("/auth/verify-token")
async def verify_token() -> Dict[str, Any]:
    """
    Verify token (demo endpoint).
    """
    return {
        "success": True,
        "message": "Token is valid",
        "user": "demo"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )