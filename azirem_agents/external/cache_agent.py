"""
Cache Agent - Provides instant responses for cached queries
Reduces AWS costs by 70-90% for repeated questions
"""
import json
import hashlib
import time
from typing import Optional, Dict, Any
import redis
from config import config
import structlog

logger = structlog.get_logger()

class CacheAgent:
    """Agent responsible for caching and retrieving responses"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            password=config.redis_password,
            decode_responses=True
        )
        self.cache_ttl = config.cache_ttl_seconds
        logger.info("CacheAgent initialized", redis_host=config.redis_host)
    
    def _generate_key(self, query: str, user_id: Optional[str] = None) -> str:
        """Generate cache key from query"""
        # Normalize query (lowercase, strip whitespace)
        normalized = query.lower().strip()
        # Add user_id if provided for personalized cache
        if user_id:
            normalized = f"{user_id}:{normalized}"
        # Generate hash for consistent key
        key_hash = hashlib.md5(normalized.encode()).hexdigest()
        return f"chat:response:{key_hash}"
    
    def get(self, query: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response if exists
        Returns None if not found or expired
        """
        if not config.enable_cache:
            return None
        
        try:
            key = self._generate_key(query, user_id)
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info("Cache hit", query=query[:50], key=key)
                return data
            else:
                logger.debug("Cache miss", query=query[:50], key=key)
                return None
        except Exception as e:
            logger.error("Cache get error", error=str(e), query=query[:50])
            return None
    
    def set(self, query: str, response: Dict[str, Any], user_id: Optional[str] = None, ttl: Optional[int] = None) -> bool:
        """
        Cache response with TTL
        Returns True if successful
        """
        if not config.enable_cache:
            return False
        
        try:
            key = self._generate_key(query, user_id)
            ttl = ttl or self.cache_ttl
            
            # Add metadata
            cached_data = {
                "response": response,
                "cached_at": time.time(),
                "query": query
            }
            
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(cached_data)
            )
            
            logger.info("Cache set", query=query[:50], key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Cache set error", error=str(e), query=query[:50])
            return False
    
    def invalidate(self, query: str, user_id: Optional[str] = None) -> bool:
        """Invalidate cache for a specific query"""
        try:
            key = self._generate_key(query, user_id)
            deleted = self.redis_client.delete(key)
            logger.info("Cache invalidated", query=query[:50], key=key, deleted=bool(deleted))
            return bool(deleted)
        except Exception as e:
            logger.error("Cache invalidation error", error=str(e))
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info("stats")
            keys = self.redis_client.keys("chat:response:*")
            hits = int(info.get("keyspace_hits", 0))
            misses = int(info.get("keyspace_misses", 0))
            total = hits + misses
            hit_rate = hits / max(total, 1)
            
            return {
                "total_keys": len(keys),
                "hits": hits,
                "misses": misses,
                "hit_rate": round(hit_rate, 3)
            }
        except Exception as e:
            logger.error("Cache stats error", error=str(e))
            return {"error": str(e), "total_keys": 0, "hits": 0, "misses": 0, "hit_rate": 0.0}
