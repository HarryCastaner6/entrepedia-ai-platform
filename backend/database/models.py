"""
Database models for the Entrepedia AI Platform.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    """Document model for tracking uploaded and processed documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    source = Column(String(50), default="upload")  # upload, scraper
    
    # Processing status
    processed = Column(Boolean, default=False)
    embeddings_created = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    # Metadata
    text_content = Column(Text)
    metadata_json = Column(Text)  # JSON string of additional metadata
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="documents")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Query(Base):
    """Query model for tracking user queries and responses."""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    agent_type = Column(String(50))  # coach, strategist
    
    # Response
    response_text = Column(Text)
    response_metadata = Column(Text)  # JSON string
    
    # Performance metrics
    processing_time = Column(Float)
    knowledge_base_results = Column(Integer, default=0)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="queries")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Integration(Base):
    """Integration model for external service connections."""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    integration_type = Column(String(50))  # entrepedia, notion, etc.
    
    # Configuration
    config_json = Column(Text)  # JSON string of configuration
    credentials_encrypted = Column(Text)  # Encrypted credentials
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String(50))
    sync_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
