"""
Context Cache Layer (ENH-046 Phase 1.6)

Purpose: LRU cache with TTL for context reuse
Target: ≥70% hit rate, ≤5% stale entries
Architecture: In-memory LRU with content-hash keys + mtime tracking

Author: CORTEX Architect
Created: 2026-02-06
Version: 1.0.0
"""

import time
import hashlib
from collections import OrderedDict
from typing import Any, Optional, Dict
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 1000
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate (0-1)"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class ContextCacheLayer:
    """
    LRU cache with TTL for context reuse
    
    Features:
    - LRU eviction (least recently used)
    - TTL expiration (default 10 minutes)
    - Content-hash + mtime keys (prevent stale entries)
    - Hit rate tracking (target ≥70%)
    
    Usage:
        cache = ContextCacheLayer(max_entries=1000, default_ttl=600)
        cache.set("key", value, ttl=600)
        cached = cache.get("key")
        hit_rate = cache.get_hit_rate()
    """
    
    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl: float = 600.0  # 10 minutes
    ):
        """
        Initialize cache
        
        Args:
            max_entries: Maximum cache entries (LRU eviction when exceeded)
            default_ttl: Default TTL in seconds
        """
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_entries = max_entries
        self._default_ttl = default_ttl
        self._stats = CacheStats(max_size=max_entries)
        
        logger.debug(f"ContextCacheLayer initialized (max={max_entries}, ttl={default_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if present and not expired, None otherwise
        """
        if key not in self._cache:
            self._stats.misses += 1
            logger.debug(f"Cache miss: {key}")
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if self._is_expired(entry):
            logger.debug(f"Cache expired: {key}")
            self._cache.pop(key)
            self._stats.misses += 1
            return None
        
        # Update access metadata
        entry.access_count += 1
        entry.last_access = time.time()
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        self._stats.hits += 1
        logger.debug(f"Cache hit: {key} (access_count={entry.access_count})")
        
        return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
        """
        ttl = ttl or self._default_ttl
        
        # Check if need to evict (LRU)
        if len(self._cache) >= self._max_entries and key not in self._cache:
            self._evict_lru()
        
        # Create cache entry
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl,
            access_count=0
        )
        
        self._cache[key] = entry
        self._cache.move_to_end(key)
        self._stats.size = len(self._cache)
        
        logger.debug(f"Cache set: {key} (ttl={ttl}s)")
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry
        
        Args:
            key: Cache key to invalidate
        
        Returns:
            True if entry existed and was removed
        """
        if key in self._cache:
            self._cache.pop(key)
            self._stats.size = len(self._cache)
            logger.debug(f"Cache invalidated: {key}")
            return True
        return False
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate (0-1)"""
        return self._stats.hit_rate()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        self._stats.size = len(self._cache)
        return self._stats
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._stats.size = 0
        logger.debug("Cache cleared")
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        age = time.time() - entry.timestamp
        return age > entry.ttl
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self._cache:
            key, _ = self._cache.popitem(last=False)
            self._stats.evictions += 1
            logger.debug(f"LRU eviction: {key}")
    
    @staticmethod
    def generate_key(
        prefix: str,
        identifier: str,
        mtime: Optional[float] = None
    ) -> str:
        """
        Generate cache key with content-hash
        
        Args:
            prefix: Key prefix (e.g., "agent", "yaml")
            identifier: Unique identifier (e.g., filename)
            mtime: File modification time (for invalidation)
        
        Returns:
            Cache key string
        """
        if mtime:
            return f"{prefix}:{identifier}:{int(mtime)}"
        else:
            return f"{prefix}:{identifier}"
    
    @staticmethod
    def hash_content(content: str) -> str:
        """
        Generate content hash for cache key
        
        Args:
            content: Content to hash
        
        Returns:
            SHA256 hash (first 16 chars)
        """
        return hashlib.sha256(content.encode()).hexdigest()[:16]
