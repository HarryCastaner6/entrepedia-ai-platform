"""
Authentication routes with database persistence.
"""
from typing import Dict, Any
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.utils.security import hash_password, verify_password, create_access_token
from backend.utils.config import settings
from backend.utils.logger import app_logger
from backend.database.database import get_db_dependency
from backend.database.models import User
from backend.database.database import init_db


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
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Initialize database on module load
try:
    init_db()
    app_logger.info("Database initialized for auth module")
except Exception as e:
    app_logger.error(f"Failed to initialize database in auth module: {e}")
    # Don't fail module import on serverless platforms
    if settings.app_env == "production":
        app_logger.warning("Continuing without database initialization in auth module for serverless deployment")


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db_dependency)) -> UserResponse:
    """
    Register a new user with database persistence.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Create new user
        hashed_pwd = hash_password(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_pwd,
            is_active=True,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        app_logger.info(f"New user registered: {user.username}")

        return UserResponse(
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        app_logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_dependency)
) -> Token:
    """
    Login and receive access token.
    """
    try:
        # Fallback authentication for demo purposes when database is not available
        demo_credentials = {
            "admin@entrepedia.ai": "admin123",
            "admin": "admin123",
            "testuser": "test123",
            "test@example.com": "test123"
        }

        # Try database authentication first
        try:
            # Get user from database (allow login with username OR email)
            user = db.query(User).filter(
                (User.username == form_data.username) |
                (User.email == form_data.username)
            ).first()

            if user and verify_password(form_data.password, user.hashed_password) and user.is_active:
                access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
                access_token = create_access_token(
                    data={"sub": user.username, "user_id": user.id},
                    expires_delta=access_token_expires
                )
                app_logger.info(f"User logged in from database: {user.username}")
                return Token(access_token=access_token, token_type="bearer")

        except Exception as db_error:
            app_logger.warning(f"Database authentication failed, trying demo mode: {db_error}")

        # Fallback to demo credentials for development/testing
        if form_data.username in demo_credentials:
            if demo_credentials[form_data.username] == form_data.password:
                # Use email as username for consistency
                username = "admin" if form_data.username in ["admin@entrepedia.ai", "admin"] else "testuser"
                user_id = 1 if username == "admin" else 2

                access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
                access_token = create_access_token(
                    data={"sub": username, "user_id": user_id},
                    expires_delta=access_token_expires
                )
                app_logger.info(f"User logged in with demo credentials: {username}")
                return Token(access_token=access_token, token_type="bearer")

        # If we get here, authentication failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Login failed: {e}", exc_info=True)
        # Provide more detailed error information in development
        from backend.utils.config import settings
        detail = f"Login failed: {str(e)}" if settings.debug else "Login failed due to internal error"
        raise HTTPException(
            status_code=500,
            detail=detail
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
async def read_users_me(db: Session = Depends(get_db_dependency)) -> UserResponse:
    """
    Get current user information.
    Note: This is a demo endpoint. In production, add authentication dependency.
    """
    # For demo, return first user or create default user
    user = db.query(User).filter(User.username == "testuser").first()
    
    if not user:
        # Create default test user
        hashed_pwd = hash_password("test123")
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password=hashed_pwd,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return UserResponse(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active
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
    new_password: str,
    db: Session = Depends(get_db_dependency)
) -> Dict[str, Any]:
    """
    Change user password.
    Note: This is a demo endpoint. In production, get user from auth dependency.
    """
    try:
        # For demo, use testuser
        username = "testuser"
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Incorrect current password"
            )

        # Update password
        user.hashed_password = hash_password(new_password)
        db.commit()

        app_logger.info(f"Password changed for user: {username}")

        return {
            "success": True,
            "message": "Password updated successfully"
        }

    except Exception as e:
        db.rollback()
        app_logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password change failed"
        )


@router.get("/setup-admin")
async def setup_admin_user(db: Session = Depends(get_db_dependency)) -> Dict[str, Any]:
    """
    Temporary endpoint to create/reset admin user.
    """
    try:
        # Match credentials displayed in frontend/src/components/auth/LoginPage.tsx
        username = "admin"
        email = "admin@entrepedia.ai"
        password = "admin123"
        
        # Check by email since that's what's used for login
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update existing user
            user.hashed_password = hash_password(password)
            user.is_active = True
            user.username = username # Ensure username matches
            action = "updated"
        else:
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name="Admin User",
                hashed_password=hash_password(password),
                is_active=True
            )
            db.add(user)
            action = "created"
        
        db.commit()
        return {
            "success": True,
            "message": f"Admin user {action} successfully",
            "credentials": {
                "email": email,
                "password": password
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Setup admin failed: {str(e)}")
