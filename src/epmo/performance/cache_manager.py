"""
CORTEX 3.0 Cache Manager
========================

Intelligent caching system with TTL, invalidation, and performance optimization
for documentation generation workflows.
"""

import time
import hashlib
import pickle
import threading
from typing import Any, Optional, Dict, List, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import logging


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: Optional[float] = None
    tags: List[str] = None
    size_bytes: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hit_count: int = 0
    miss_count: int = 0
    total_entries: int = 0
    memory_usage_mb: float = 0.0
    avg_access_time_ms: float = 0.0
    hit_rate: float = 0.0
    
    @property
    def total_requests(self) -> int:
        return self.hit_count + self.miss_count


class CacheManager:
    """
    Enterprise-grade cache management system with intelligent eviction,
    TTL support, and performance monitoring.
    """
    
    def __init__(
        self,
        max_memory_mb: float = 512.0,
        default_ttl: Optional[float] = 3600.0,  # 1 hour
        cleanup_interval: float = 300.0,  # 5 minutes
        persist_path: Optional[str] = None
    ):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.persist_path = Path(persist_path) if persist_path else None
        
        # Thread-safe cache storage
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()
        
        # Performance monitoring
        self._access_times: List[float] = []
        self._last_cleanup = time.time()
        
        # Load persisted cache if available
        if self.persist_path and self.persist_path.exists():
            self._load_cache()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache with performance tracking.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        start_time = time.time()
        
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.miss_count += 1
                self._update_access_time(start_time)
                return None
            
            # Check TTL expiration
            if self._is_expired(entry):
                del self._cache[key]
                self._stats.miss_count += 1
                self._update_access_time(start_time)
                return None
            
            # Update access metadata
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            self._stats.hit_count += 1
            self._update_access_time(start_time)
            
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Store value in cache with intelligent memory management.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Optional tags for invalidation
            
        Returns:
            True if successfully cached
        """
        with self._lock:
            # Calculate value size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Fallback estimate
            
            # Check if we need to evict entries
            if not self._ensure_space(size_bytes):
                logger.warning(f"Failed to cache {key}: insufficient space")
                return False
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=0,
                ttl=ttl or self.default_ttl,
                tags=tags or [],
                size_bytes=size_bytes
            )
            
            self._cache[key] = entry
            self._stats.total_entries = len(self._cache)
            self._update_memory_usage()
            
            # Trigger cleanup if needed
            if time.time() - self._last_cleanup > self.cleanup_interval:
                self._cleanup_expired()
            
            return True
    
    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.total_entries = len(self._cache)
                self._update_memory_usage()
                return True
            return False
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Remove all entries with specific tag."""
        removed_count = 0
        with self._lock:
            keys_to_remove = []
            for key, entry in self._cache.items():
                if tag in entry.tags:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._cache[key]
                removed_count += 1
            
            self._stats.total_entries = len(self._cache)
            self._update_memory_usage()
        
        return removed_count
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats.total_entries = 0
            self._stats.memory_usage_mb = 0.0
    
    def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        with self._lock:
            self._update_memory_usage()
            
            if self._stats.total_requests > 0:
                self._stats.hit_rate = self._stats.hit_count / self._stats.total_requests
            
            if self._access_times:
                self._stats.avg_access_time_ms = (
                    sum(self._access_times) / len(self._access_times) * 1000
                )
            
            return self._stats
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """Generate deterministic cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def cache_decorator(
        self,
        ttl: Optional[float] = None,
        tags: Optional[List[str]] = None,
        key_func: Optional[Callable] = None
    ):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Time to live for cached result
            tags: Tags for cache invalidation
            key_func: Custom key generation function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}_{self.generate_cache_key(*args, **kwargs)}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl=ttl, tags=tags)
                
                return result
            return wrapper
        return decorator
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.ttl is None:
            return False
        return time.time() - entry.created_at > entry.ttl
    
    def _ensure_space(self, required_bytes: int) -> bool:
        """Ensure sufficient cache space using LRU eviction."""
        current_usage = sum(entry.size_bytes for entry in self._cache.values())
        
        if current_usage + required_bytes <= self.max_memory_bytes:
            return True
        
        # Sort by last access time (LRU)
        entries_by_access = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Evict oldest entries until we have space
        bytes_to_free = current_usage + required_bytes - self.max_memory_bytes
        freed_bytes = 0
        
        for key, entry in entries_by_access:
            if freed_bytes >= bytes_to_free:
                break
            
            freed_bytes += entry.size_bytes
            del self._cache[key]
        
        return freed_bytes >= bytes_to_free
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        self._last_cleanup = current_time
        self._stats.total_entries = len(self._cache)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _update_access_time(self, start_time: float) -> None:
        """Update access time statistics."""
        access_time = time.time() - start_time
        self._access_times.append(access_time)
        
        # Keep only recent access times
        if len(self._access_times) > 1000:
            self._access_times = self._access_times[-500:]
    
    def _update_memory_usage(self) -> None:
        """Update memory usage statistics."""
        total_bytes = sum(entry.size_bytes for entry in self._cache.values())
        self._stats.memory_usage_mb = total_bytes / (1024 * 1024)
    
    def _load_cache(self) -> None:
        """Load cache from persistent storage."""
        try:
            with open(self.persist_path, 'rb') as f:
                cache_data = pickle.load(f)
                self._cache = cache_data.get('cache', {})
                self._stats = cache_data.get('stats', CacheStats())
            logger.info(f"Loaded {len(self._cache)} cache entries from {self.persist_path}")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    
    def persist_cache(self) -> bool:
        """Save cache to persistent storage."""
        if not self.persist_path:
            return False
        
        try:
            cache_data = {
                'cache': self._cache,
                'stats': self._stats
            }
            
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persist_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"Persisted {len(self._cache)} cache entries to {self.persist_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to persist cache: {e}")
            return False


# Global cache instance
default_cache = CacheManager()