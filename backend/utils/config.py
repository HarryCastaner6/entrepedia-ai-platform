"""
Configuration management using Pydantic settings.
Loads environment variables and provides type-safe configuration.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Entrepedia AI Platform"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = Field(default="dev-secret-key-32-chars-minimum-change-in-production", min_length=32)

    # Database
    database_url: str = "sqlite:///./data/entrepedia.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Entrepedia
    entrepedia_base_url: str = "https://app.entrepedia.co"
    entrepedia_username: str = "placeholder_username"
    entrepedia_password: str = "placeholder_password"

    # AI APIs
    anthropic_api_key: str = "placeholder_anthropic_key"
    openai_api_key: str = "placeholder_openai_key"
    gemini_api_key: str = "AIzaSyB7_gjyyVbSZPLzcrC5vQg0ZGxcLOGpMM8"

    # Vector Database
    vector_db_type: Literal["faiss", "pinecone", "weaviate", "supabase"] = "faiss"
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None
    weaviate_url: str = "http://localhost:8080"

    # Storage
    storage_type: Literal["local", "s3", "supabase"] = "local"
    output_dir: str = "./data/courses"
    
    # S3 / Supabase Storage
    s3_bucket: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = "us-east-1"
    aws_endpoint_url: str | None = None  # For Supabase S3 compatibility

    # Supabase Native
    supabase_url: str | None = None
    supabase_key: str | None = None

    # Integrations
    google_calendar_credentials: str | None = None
    notion_api_key: str | None = None
    trello_api_key: str | None = None
    trello_token: str | None = None

    # Security
    jwt_secret_key: str = "dev-jwt-secret-32-chars-minimum-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str | None = None

    # Scraper
    scraper_schedule_hours: int = 24
    max_concurrent_downloads: int = 5
    request_timeout: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()