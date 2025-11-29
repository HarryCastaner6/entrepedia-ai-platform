"""
Authentication routes for user management and JWT tokens.
"""
from typing import Dict, Any
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from backend.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)
from backend.utils.config import settings
from backend.utils.logger import app_logger


router = APIRouter()


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
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


class TokenData(BaseModel):
    username: str | None = None


# Simple in-memory user store (replace with database in production)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        # Pre-hashed password for "test123"
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqz3qK6a",
        "is_active": True,
    }
}


def get_user(username: str):
    """Get user from database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str):
    """Authenticate user credentials."""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate) -> UserResponse:
    """
    Register a new user.
    """
    try:
        # Check if user already exists
        if user.username in fake_users_db:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Check if email already exists
        for existing_user in fake_users_db.values():
            if existing_user["email"] == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )

        # Hash password and create user
        hashed_password = hash_password(user.password)
        fake_users_db[user.username] = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
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
    """
    Login and receive access token.
    """
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
    """
    Logout user (client should discard token).
    """
    return {
        "success": True,
        "message": "Successfully logged out. Please discard your access token."
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me() -> UserResponse:
    """
    Get current user information.
    Note: This is a demo endpoint. In production, add authentication dependency.
    """
    # Demo: return test user
    return UserResponse(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )


@router.get("/verify-token")
async def verify_token() -> Dict[str, Any]:
    """
    Verify if the current token is valid.
    Note: This is a demo endpoint. In production, add authentication dependency.
    """
    return {
        "success": True,
        "message": "Token is valid",
        "user": "testuser"
    }


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str
) -> Dict[str, Any]:
    """
    Change user password.
    """
    try:
        # In production, get current user from dependency
        username = "testuser"  # current_user["username"]
        user = get_user(username)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify old password
        if not verify_password(old_password, user["hashed_password"]):
            raise HTTPException(
                status_code=400,
                detail="Incorrect current password"
            )

        # Update password
        user["hashed_password"] = hash_password(new_password)
        fake_users_db[username] = user

        app_logger.info(f"Password changed for user: {username}")

        return {
            "success": True,
            "message": "Password updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password change failed"
        )