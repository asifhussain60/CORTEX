"""LENS Result Caching Layer

Main cache manager with support for multiple backends (Redis, In-Memory).
Implements TTL-based LRU eviction with multi-layer caching.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json


@dataclass
class CacheEntry:
    """Single cache entry with TTL."""
    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int
    hit_count: int = 0

    def is_expired(self) -> bool:
        """Check if entry has exceeded TTL."""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds


@dataclass
class CacheKey:
    """Cache key generation from request context."""
    user_request: str
    repo_state_hash: str
    lens_version: str

    def build(self) -> str:
        """Generate unique cache key."""
        combined = f"{self.user_request}:{self.repo_state_hash}:{self.lens_version}"
        return hashlib.sha256(combined.encode()).hexdigest()


class LENSCache:
    """Main cache manager interface."""

    def __init__(self, backend_type: str = "memory", **kwargs):
        """Initialize cache with specified backend.
        
        Args:
            backend_type: "memory" (development) or "redis" (production)
            **kwargs: Backend-specific configuration
        """
        self.backend_type = backend_type
        self._statistics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "set_operations": 0,
            "get_operations": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache.
        
        Args:
            key: Cache key (typically from CacheKey.build())
            
        Returns:
            Cached value if found and not expired, else None
        """
        self._statistics["get_operations"] += 1
        raise NotImplementedError("Implement in subclass")

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (typically LENSResult)
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self._statistics["set_operations"] += 1
        raise NotImplementedError("Implement in subclass")

    def invalidate(self, pattern: str = "*") -> None:
        """Invalidate cache entries matching pattern.
        
        Args:
            pattern: Glob pattern (default: "*" = all)
        """
        raise NotImplementedError("Implement in subclass")

    def get_statistics(self) -> Dict[str, int]:
        """Get cache hit/miss statistics."""
        hit_rate = 0.0
        total = self._statistics["hits"] + self._statistics["misses"]
        if total > 0:
            hit_rate = (self._statistics["hits"] / total) * 100
        
        return {
            **self._statistics,
            "hit_rate_percent": round(hit_rate, 2),
            "total_operations": total
        }


# Phase 65 S6: Canonical LENSCache singleton accessor
_lens_cache_instance: Optional['LENSCache'] = None


def get_lens_cache(backend_type: str = "memory", **kwargs) -> 'LENSCache':
    """
    Get singleton LENSCache instance.
    
    Ensures single canonical cache across all LENS consumers (CORE-035).
    
    Args:
        backend_type: "memory" (development) or "redis" (production)
        **kwargs: Backend-specific configuration
        
    Returns:
        Singleton LENSCache instance
    """
    global _lens_cache_instance
    
    if _lens_cache_instance is None:
        # Import concrete implementation
        from cortex.lens.cache.memory_backend import MemoryBackend
        
        if backend_type == "memory":
            _lens_cache_instance = MemoryBackend(**kwargs)
        else:
            # Redis backend (future)
            raise NotImplementedError(f"Backend '{backend_type}' not yet implemented")
    
    return _lens_cache_instance


__all__ = ["LENSCache", "CacheEntry", "CacheKey", "get_lens_cache"]
