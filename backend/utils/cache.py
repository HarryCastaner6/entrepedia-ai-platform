"""
Redis cache manager for caching embeddings and query results.
"""
import json
import pickle
from typing import Any, Optional, List
import redis
from backend.utils.config import settings
from backend.utils.logger import app_logger


class CacheManager:
    """Redis cache manager for the application."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        self.enabled = False
        
        try:
            # Parse Redis URL
            if settings.redis_url and settings.redis_url != "redis://localhost:6379/0":
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=False,  # We'll handle encoding/decoding
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self.redis_client.ping()
                self.enabled = True
                app_logger.info("Redis cache initialized successfully")
            else:
                app_logger.info("Redis not configured, caching disabled")
        except Exception as e:
            app_logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            app_logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        if not self.enabled:
            return
        
        try:
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            app_logger.warning(f"Cache set failed for key {key}: {e}")
    
    def delete(self, key: str):
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        if not self.enabled:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            app_logger.warning(f"Cache delete failed for key {key}: {e}")
    
    def clear_pattern(self, pattern: str):
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "embeddings:*")
        """
        if not self.enabled:
            return
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                app_logger.info(f"Cleared {len(keys)} keys matching pattern: {pattern}")
        except Exception as e:
            app_logger.warning(f"Cache clear pattern failed for {pattern}: {e}")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get cached embedding for text.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Embedding vector or None
        """
        key = f"embedding:{hash(text)}"
        return self.get(key)
    
    def set_embedding(self, text: str, embedding: List[float], ttl: int = 86400):
        """
        Cache embedding for text.
        
        Args:
            text: Text
            embedding: Embedding vector
            ttl: Time to live in seconds (default: 24 hours)
        """
        key = f"embedding:{hash(text)}"
        self.set(key, embedding, ttl)
    
    def get_query_result(self, query: str, agent_type: str = "coach") -> Optional[dict]:
        """
        Get cached query result.
        
        Args:
            query: Query text
            agent_type: Type of agent
            
        Returns:
            Cached result or None
        """
        key = f"query:{agent_type}:{hash(query)}"
        return self.get(key)
    
    def set_query_result(self, query: str, result: dict, agent_type: str = "coach", ttl: int = 3600):
        """
        Cache query result.
        
        Args:
            query: Query text
            result: Query result
            agent_type: Type of agent
            ttl: Time to live in seconds (default: 1 hour)
        """
        key = f"query:{agent_type}:{hash(query)}"
        self.set(key, result, ttl)
    
    def get_document(self, filename: str) -> Optional[dict]:
        """
        Get cached document metadata.
        
        Args:
            filename: Document filename
            
        Returns:
            Document metadata or None
        """
        key = f"document:{filename}"
        return self.get(key)
    
    def set_document(self, filename: str, metadata: dict, ttl: int = 7200):
        """
        Cache document metadata.
        
        Args:
            filename: Document filename
            metadata: Document metadata
            ttl: Time to live in seconds (default: 2 hours)
        """
        key = f"document:{filename}"
        self.set(key, metadata, ttl)
    
    def health_check(self) -> dict:
        """
        Check cache health.
        
        Returns:
            Health status dict
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "enabled": False
            }
        
        try:
            self.redis_client.ping()
            info = self.redis_client.info()
            return {
                "status": "healthy",
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "total_keys": self.redis_client.dbsize()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "enabled": False,
                "error": str(e)
            }


# Global cache instance
cache_manager = CacheManager()
