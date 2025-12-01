"""
Clean Vercel authentication API - no backend dependencies.
"""
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
app = FastAPI(title="Entrepedia Authentication API")

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

    secret_key = "demo-secret-key"
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

@app.get("/")
async def root():
    return {
        "message": "Entrepedia Authentication API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/login", response_model=Token)
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

@app.post("/logout")
async def logout():
    return {"success": True, "message": "Logged out successfully"}

# For Vercel
handler = app