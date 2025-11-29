"""
Simplified authentication routes for demo purposes.
"""
from typing import Dict, Any
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from backend.utils.security import create_access_token
from backend.utils.config import settings
from backend.utils.logger import app_logger


router = APIRouter()


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ""


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Simple user store (for demo only)
simple_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "test123",  # Plain text for demo
        "is_active": True,
    }
}


def get_user(username: str):
    """Get user from database."""
    return simple_users_db.get(username)


def authenticate_user(username: str, password: str):
    """Authenticate user credentials."""
    user = get_user(username)
    if not user or user["password"] != password:
        return False
    return user


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate) -> UserResponse:
    """Register a new user."""
    try:
        # Check if user already exists
        if user.username in simple_users_db:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Create user
        simple_users_db[user.username] = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "password": user.password,  # Plain text for demo
            "is_active": True,
        }

        app_logger.info(f"New user registered: {user.username}")

        return UserResponse(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=True
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Login and receive access token."""
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )

        app_logger.info(f"User logged in: {user['username']}")

        return Token(access_token=access_token, token_type="bearer")

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )


@router.post("/logout")
async def logout() -> Dict[str, Any]:
    """Logout user."""
    return {
        "success": True,
        "message": "Successfully logged out. Please discard your access token."
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me() -> UserResponse:
    """Get current user information."""
    return UserResponse(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )


@router.get("/verify-token")
async def verify_token() -> Dict[str, Any]:
    """Verify if the current token is valid."""
    return {
        "success": True,
        "message": "Token is valid",
        "user": "testuser"
    }