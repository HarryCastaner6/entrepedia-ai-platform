"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from backend.utils.config import settings
from backend.utils.logger import app_logger
from backend.database.models import Base


# Create engine
if settings.database_url.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other databases
    # For serverless environments like Vercel, use smaller pool sizes
    pool_size = 1 if settings.app_env == "production" else 10
    max_overflow = 2 if settings.app_env == "production" else 20

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=30,
        pool_recycle=3600,  # Recycle connections every hour
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database tables created successfully")
    except Exception as e:
        app_logger.error(f"Failed to create database tables: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Usage:
        with get_db() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session.
    
    Usage:
        with get_db_context() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Dependency for FastAPI
def get_db_dependency():
    """FastAPI dependency for database session."""
    try:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        # Return a mock session that will raise exceptions on use
        # This allows the endpoint to handle the database failure gracefully
        from backend.utils.logger import app_logger
        app_logger.error(f"Database session creation failed: {e}")

        class MockSession:
            def query(self, *args, **kwargs):
                raise Exception(f"Database connection failed: {e}")
            def add(self, *args, **kwargs):
                raise Exception(f"Database connection failed: {e}")
            def commit(self, *args, **kwargs):
                raise Exception(f"Database connection failed: {e}")
            def rollback(self, *args, **kwargs):
                pass

        yield MockSession()
