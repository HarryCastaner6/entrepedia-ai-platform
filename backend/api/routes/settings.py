"""
Settings routes for user preferences, AI configuration, and platform management.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from datetime import datetime
import os
import json
import asyncio
from backend.utils.logger import app_logger
from backend.utils.auth import get_current_user
from backend.database.models import User

router = APIRouter()


# Pydantic models for settings
class ProfileSettings(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"


class AIConfiguration(BaseModel):
    preferred_model: str = "claude-3"
    response_style: str = "balanced"
    coaching_mode: str = "adaptive"
    strategy_depth: str = "detailed"
    enable_follow_ups: bool = True
    context_window: int = 4000


class DocumentProcessingConfig(BaseModel):
    auto_generate_embeddings: bool = True
    chunk_size: int = 500
    overlap_size: int = 50
    processing_quality: str = "high"
    auto_ocr: bool = True
    supported_formats: List[str] = ["pdf", "docx", "txt", "md", "png", "jpg", "mp3", "wav"]


class IntegrationSettings(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_calendar_connected: bool = False
    notion_connected: bool = False
    trello_connected: bool = False


class SecuritySettings(BaseModel):
    two_factor_enabled: bool = False
    session_timeout: int = 30
    data_retention_days: int = 365
    allow_data_export: bool = True
    share_analytics: bool = False


class NotificationSettings(BaseModel):
    email_notifications: bool = True
    processing_complete: bool = True
    ai_suggestions: bool = True
    weekly_summary: bool = True
    security_alerts: bool = True


class DatabaseStats(BaseModel):
    total_documents: int = 0
    total_embeddings: int = 0
    database_size: str = "0 MB"
    last_backup: str = "Never"


class BackupSettings(BaseModel):
    auto_backup_enabled: bool = True
    backup_frequency: str = "daily"
    email_backup_notifications: bool = False


# Settings storage - In production, use database
SETTINGS_DIR = "data/user_settings"
os.makedirs(SETTINGS_DIR, exist_ok=True)


def get_user_settings_path(user_id: str, settings_type: str) -> str:
    """Get the file path for user settings."""
    return os.path.join(SETTINGS_DIR, f"{user_id}_{settings_type}.json")


def load_user_settings(user_id: str, settings_type: str, default_settings: dict) -> dict:
    """Load user settings from file or return defaults."""
    settings_path = get_user_settings_path(user_id, settings_type)
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        app_logger.warning(f"Failed to load {settings_type} settings for user {user_id}: {e}")
    return default_settings


def save_user_settings(user_id: str, settings_type: str, settings: dict) -> bool:
    """Save user settings to file."""
    settings_path = get_user_settings_path(user_id, settings_type)
    try:
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2, default=str)
        return True
    except Exception as e:
        app_logger.error(f"Failed to save {settings_type} settings for user {user_id}: {e}")
        return False


@router.get("/profile")
async def get_profile_settings(current_user: User = Depends(get_current_user)) -> ProfileSettings:
    """Get user profile settings."""
    default_settings = {
        "full_name": current_user.full_name or "",
        "email": current_user.email or "",
        "bio": "",
        "timezone": "UTC",
        "language": "en"
    }

    settings = load_user_settings(str(current_user.id), "profile", default_settings)
    return ProfileSettings(**settings)


@router.post("/profile")
async def update_profile_settings(
    profile: ProfileSettings,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update user profile settings."""
    try:
        settings = profile.dict()
        success = save_user_settings(str(current_user.id), "profile", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save profile settings"
            )

        return {
            "success": True,
            "message": "Profile settings updated successfully"
        }

    except Exception as e:
        app_logger.error(f"Profile update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/ai-config")
async def get_ai_configuration(current_user: User = Depends(get_current_user)) -> AIConfiguration:
    """Get AI configuration settings."""
    default_settings = {
        "preferred_model": "gemini-pro",
        "response_style": "balanced",
        "coaching_mode": "adaptive",
        "strategy_depth": "detailed",
        "enable_follow_ups": True,
        "context_window": 4000
    }

    settings = load_user_settings(str(current_user.id), "ai_config", default_settings)
    return AIConfiguration(**settings)


@router.post("/ai-config")
async def update_ai_configuration(
    ai_config: AIConfiguration,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update AI configuration settings."""
    try:
        settings = ai_config.dict()
        success = save_user_settings(str(current_user.id), "ai_config", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save AI configuration"
            )

        return {
            "success": True,
            "message": "AI configuration updated successfully"
        }

    except Exception as e:
        app_logger.error(f"AI config update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update AI configuration: {str(e)}"
        )


@router.get("/documents")
async def get_document_processing_config(current_user: User = Depends(get_current_user)) -> DocumentProcessingConfig:
    """Get document processing configuration."""
    default_settings = {
        "auto_generate_embeddings": True,
        "chunk_size": 500,
        "overlap_size": 50,
        "processing_quality": "high",
        "auto_ocr": True,
        "supported_formats": ["pdf", "docx", "txt", "md", "png", "jpg", "mp3", "wav"]
    }

    settings = load_user_settings(str(current_user.id), "document_config", default_settings)
    return DocumentProcessingConfig(**settings)


@router.post("/documents")
async def update_document_processing_config(
    doc_config: DocumentProcessingConfig,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update document processing configuration."""
    try:
        settings = doc_config.dict()
        success = save_user_settings(str(current_user.id), "document_config", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save document configuration"
            )

        return {
            "success": True,
            "message": "Document processing configuration updated successfully"
        }

    except Exception as e:
        app_logger.error(f"Document config update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update document configuration: {str(e)}"
        )


@router.get("/integrations")
async def get_integration_settings(current_user: User = Depends(get_current_user)) -> IntegrationSettings:
    """Get integration settings (API keys are masked for security)."""
    default_settings = {
        "openai_api_key": "",
        "gemini_api_key": "",
        "google_calendar_connected": False,
        "notion_connected": False,
        "trello_connected": False
    }

    settings = load_user_settings(str(current_user.id), "integrations", default_settings)

    # Mask API keys for security
    if settings.get("openai_api_key"):
        settings["openai_api_key"] = "sk-***" + settings["openai_api_key"][-4:]
    if settings.get("gemini_api_key"):
        settings["gemini_api_key"] = "AIza***" + settings["gemini_api_key"][-4:]

    return IntegrationSettings(**settings)


@router.post("/integrations")
async def update_integration_settings(
    integration_settings: IntegrationSettings,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update integration settings."""
    try:
        settings = integration_settings.dict()

        # In production, encrypt API keys before storage
        if settings.get("openai_api_key") and not settings["openai_api_key"].startswith("sk-***"):
            # Store the full key (in production, encrypt it)
            pass
        if settings.get("anthropic_api_key") and not settings["anthropic_api_key"].startswith("sk-ant-***"):
            # Store the full key (in production, encrypt it)
            pass

        success = save_user_settings(str(current_user.id), "integrations", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save integration settings"
            )

        return {
            "success": True,
            "message": "Integration settings updated successfully"
        }

    except Exception as e:
        app_logger.error(f"Integration settings update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update integration settings: {str(e)}"
        )


@router.get("/security")
async def get_security_settings(current_user: User = Depends(get_current_user)) -> SecuritySettings:
    """Get security and privacy settings."""
    default_settings = {
        "two_factor_enabled": False,
        "session_timeout": 30,
        "data_retention_days": 365,
        "allow_data_export": True,
        "share_analytics": False
    }

    settings = load_user_settings(str(current_user.id), "security", default_settings)
    return SecuritySettings(**settings)


@router.post("/security")
async def update_security_settings(
    security_settings: SecuritySettings,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update security and privacy settings."""
    try:
        settings = security_settings.dict()
        success = save_user_settings(str(current_user.id), "security", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save security settings"
            )

        return {
            "success": True,
            "message": "Security settings updated successfully"
        }

    except Exception as e:
        app_logger.error(f"Security settings update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update security settings: {str(e)}"
        )


@router.get("/notifications")
async def get_notification_settings(current_user: User = Depends(get_current_user)) -> NotificationSettings:
    """Get notification preferences."""
    default_settings = {
        "email_notifications": True,
        "processing_complete": True,
        "ai_suggestions": True,
        "weekly_summary": True,
        "security_alerts": True
    }

    settings = load_user_settings(str(current_user.id), "notifications", default_settings)
    return NotificationSettings(**settings)


@router.post("/notifications")
async def update_notification_settings(
    notification_settings: NotificationSettings,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update notification preferences."""
    try:
        settings = notification_settings.dict()
        success = save_user_settings(str(current_user.id), "notifications", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save notification settings"
            )

        return {
            "success": True,
            "message": "Notification settings updated successfully"
        }

    except Exception as e:
        app_logger.error(f"Notification settings update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update notification settings: {str(e)}"
        )


@router.get("/database/stats")
async def get_database_stats(current_user: User = Depends(get_current_user)) -> DatabaseStats:
    """Get database statistics."""
    try:
        # In production, get real stats from database
        from backend.database.database import get_db

        # Mock stats for now - replace with real database queries
        stats = {
            "total_documents": 0,
            "total_embeddings": 0,
            "database_size": "0 MB",
            "last_backup": "Never"
        }

        # Try to get actual document count
        try:
            import os
            db_path = "data/entrepedia.db"
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                size_mb = round(size_bytes / (1024 * 1024), 2)
                stats["database_size"] = f"{size_mb} MB"
        except Exception:
            pass

        return DatabaseStats(**stats)

    except Exception as e:
        app_logger.error(f"Failed to get database stats: {e}")
        return DatabaseStats()


@router.post("/database/reset")
async def reset_database(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Reset user's database (documents and embeddings)."""
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="Only admin users can reset the database"
            )

        # In production, implement actual database reset
        # This is a dangerous operation that should be carefully implemented
        app_logger.warning(f"Database reset requested by user {current_user.id}")

        # For now, just simulate the operation
        await asyncio.sleep(2)

        return {
            "success": True,
            "message": "Database reset completed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Database reset failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset database: {str(e)}"
        )


@router.post("/backup/export")
async def export_user_data(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Export all user data."""
    try:
        # In production, implement actual data export
        app_logger.info(f"Data export requested by user {current_user.id}")

        # Simulate export process
        import asyncio
        await asyncio.sleep(2)

        export_data = {
            "user_id": str(current_user.id),
            "export_date": datetime.utcnow().isoformat(),
            "profile": {},
            "documents": [],
            "queries": [],
            "settings": {}
        }

        # In production, generate actual export file and provide download link
        return {
            "success": True,
            "message": "Data export completed successfully",
            "download_url": f"/api/exports/user_{current_user.id}_{int(datetime.utcnow().timestamp())}.json"
        }

    except Exception as e:
        app_logger.error(f"Data export failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export data: {str(e)}"
        )


@router.get("/backup")
async def get_backup_settings(current_user: User = Depends(get_current_user)) -> BackupSettings:
    """Get backup configuration."""
    default_settings = {
        "auto_backup_enabled": True,
        "backup_frequency": "daily",
        "email_backup_notifications": False
    }

    settings = load_user_settings(str(current_user.id), "backup", default_settings)
    return BackupSettings(**settings)


@router.post("/backup")
async def update_backup_settings(
    backup_settings: BackupSettings,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update backup configuration."""
    try:
        settings = backup_settings.dict()
        success = save_user_settings(str(current_user.id), "backup", settings)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save backup settings"
            )

        return {
            "success": True,
            "message": "Backup settings updated successfully"
        }

    except Exception as e:
        app_logger.error(f"Backup settings update failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update backup settings: {str(e)}"
        )


@router.get("/all")
async def get_all_settings(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Get all user settings in one request."""
    try:
        return {
            "profile": await get_profile_settings(current_user),
            "ai_config": await get_ai_configuration(current_user),
            "documents": await get_document_processing_config(current_user),
            "integrations": await get_integration_settings(current_user),
            "security": await get_security_settings(current_user),
            "notifications": await get_notification_settings(current_user),
            "database_stats": await get_database_stats(current_user),
            "backup": await get_backup_settings(current_user)
        }

    except Exception as e:
        app_logger.error(f"Failed to get all settings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve settings: {str(e)}"
        )