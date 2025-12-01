"""
Minimal Vercel serverless function with basic authentication.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import timedelta
import jwt
import hashlib
import datetime

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

# Create FastAPI app
app = FastAPI(title="Entrepedia AI Platform API")

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
        "mode": "minimal"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mode": "minimal"
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

# For Vercel
handler = app
