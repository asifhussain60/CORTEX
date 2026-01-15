"""Performance Optimization & Caching Layer.

This module implements the CachingLayer for result caching with TTL and
performance optimization through intelligent invalidation.

AC-EX-002-02: Results cached with TTL, cache invalidation on relevant changes,
and performance improvement measurable.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import fnmatch
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CacheEntry:
    """A cache entry with TTL tracking.
    
    Attributes:
        key: Cache key
        value: Cached value
        timestamp: When the entry was created
        ttl_seconds: Time to live in seconds
    """
    
    key: str
    value: Any
    timestamp: float
    ttl_seconds: float
    
    def is_expired(self) -> bool:
        """Check if entry has expired.
        
        Returns:
            True if the entry has exceeded its TTL
        """
        current_time = time.time()
        return (current_time - self.timestamp) > self.ttl_seconds


class CachingLayer:
    """Caching layer for result caching with TTL and invalidation.
    
    Features:
    - TTL-based cache expiration
    - Manual cache invalidation
    - Dependency tracking for smart invalidation
    - Pattern-based invalidation
    - Cache statistics tracking
    
    Example:
        >>> cache = CachingLayer()
        >>> cache.set("user_123", user_data, ttl_seconds=300)
        >>> cached_user = cache.get("user_123")
        >>> cache.invalidate_pattern("user_*")  # Invalidate all users
    """
    
    def __init__(self) -> None:
        """Initialize the caching layer."""
        self._cache: Dict[str, CacheEntry] = {}
        self._dependencies: Dict[str, set] = {}  # key -> dependent keys
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.
        
        Checks if the key exists and has not expired. Returns the cached
        value or the default if not found or expired.
        
        Args:
            key: Cache key
            default: Default value if not found or expired
            
        Returns:
            Cached value or default
        """
        if key not in self._cache:
            self._stats["misses"] += 1
            return default
        
        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return default
        
        self._stats["hits"] += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: float = 60.0) -> None:
        """Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default: 60)
        """
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds,
        )
    
    def invalidate(self, key: str, cascade: bool = True) -> None:
        """Invalidate cache entry.
        
        Args:
            key: Cache key to invalidate
            cascade: Whether to cascade invalidation to dependent keys
        """
        if key in self._cache:
            del self._cache[key]
            self._stats["invalidations"] += 1
        
        if cascade and key in self._dependencies:
            for dependent_key in self._dependencies[key]:
                self.invalidate(dependent_key, cascade=True)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern.
        
        Uses fnmatch for pattern matching (e.g., "user_*", "cache_*_data").
        
        Args:
            pattern: Pattern to match
            
        Returns:
            Number of keys invalidated
        """
        keys_to_invalidate = [
            k for k in self._cache.keys()
            if fnmatch.fnmatch(k, pattern)
        ]
        
        count = len(keys_to_invalidate)
        for key in keys_to_invalidate:
            self.invalidate(key, cascade=False)
        
        return count
    
    def set_dependency(self, key: str, depends_on: str) -> None:
        """Register that key depends on another key.
        
        When the dependency is invalidated, this key will also be
        invalidated if cascade is enabled.
        
        Args:
            key: Dependent key
            depends_on: Key this depends on
        """
        if depends_on not in self._dependencies:
            self._dependencies[depends_on] = set()
        self._dependencies[depends_on].add(key)
    
    def clear(self) -> None:
        """Clear all cache entries and dependencies."""
        self._cache.clear()
        self._dependencies.clear()
        self._stats["invalidations"] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Statistics dictionary with hits, misses, hit rate, etc.
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total,
            "hit_rate_percent": hit_rate,
            "cached_entries": len(self._cache),
        }
