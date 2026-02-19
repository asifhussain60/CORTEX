"""
Context Cache Layer - LRU cache with TTL for synthesized context.

ENH-046 Phase 4: Caching layer to achieve 70% cache hit rate target.

Features:
- LRU eviction policy (least recently used)
- TTL expiration (10 minutes default)
- Thread-safe operations
- Memory-bounded (max entries + max size)
- Cache statistics (hits, misses, evictions)

Authority:
    - ENH-046 Phase 4 (Context Synthesis Gateway + Integration)
    - Target: 70% cache hit rate after 1 hour usage

Author: CORTEX Context Synthesis System
Created: 2026-02-06
Updated: 2026-02-06 (v1.0 - Initial Implementation)
"""

import logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics for monitoring."""

    hits: int
    misses: int
    evictions: int
    current_entries: int
    current_size_bytes: int
    hit_rate: float


class ContextCacheLayer:
    """
    LRU cache with TTL for synthesized context.

    Configuration:
    - max_entries: 1000 (default)
    - ttl_seconds: 600 (10 minutes default)
    - max_size_bytes: 10 MB (default)
    - eviction_policy: LRU

    Cache keys format:
    - agent_summary: agent:{filename}:{mtime}
    - yaml_rules: yaml:{filename}:{intent_type}:{mtime}
    - file_ast: file:{path}:{mtime}
    - governance_result: gov:{operation}:{hash}
    - challenge_result: challenge:{request_hash}

    Usage:
        cache = ContextCacheLayer()

        # Set
        cache.set("key", synthesized_context)

        # Get
        result = cache.get("key")  # None if miss or expired

        # Stats
        stats = cache.get_stats()
        print(f"Hit rate: {stats.hit_rate:.1%}")
    """

    def __init__(
        self,
        max_entries: int = 1000,
        ttl_seconds: int = 600,
        max_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    ):
        """
        Initialize cache layer.

        Args:
            max_entries: Maximum number of cached entries
            ttl_seconds: Time-to-live for cache entries (seconds)
            max_size_bytes: Maximum cache size in bytes
        """
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self.max_size_bytes = max_size_bytes

        # Cache storage: OrderedDict for LRU
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._current_size_bytes = 0

        # Thread safety
        self._lock = threading.RLock()

        logger.info(
            "ContextCacheLayer initialized (max_entries=%d, ttl=%ds, max_size=%d bytes)",
            max_entries,
            ttl_seconds,
            max_size_bytes
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if miss/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                logger.debug("Cache MISS (key=%s)", key)
                return None

            entry = self._cache[key]

            # Check TTL expiration
            if self._is_expired(entry):
                logger.debug("Cache EXPIRED (key=%s)", key)
                self._remove_entry(key)
                self._misses += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)

            # Update stats
            self._hits += 1
            logger.debug("Cache HIT (key=%s)", key)

            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (seconds)
        """
        with self._lock:
            ttl = ttl or self.ttl_seconds

            # Calculate entry size
            entry_size = self._estimate_size(value)

            # Check if we need to evict
            while (
                len(self._cache) >= self.max_entries
                or self._current_size_bytes + entry_size > self.max_size_bytes
            ):
                if not self._evict_lru():
                    # Can't evict anymore, reject this entry
                    logger.warning(
                        "Cache full, cannot add entry (key=%s, size=%d)",
                        key,
                        entry_size
                    )
                    return

            # Store entry
            entry = {
                "value": value,
                "timestamp": time.time(),
                "ttl": ttl,
                "size": entry_size
            }

            # If key exists, remove old size
            if key in self._cache:
                old_entry = self._cache[key]
                self._current_size_bytes -= old_entry["size"]

            self._cache[key] = entry
            self._current_size_bytes += entry_size

            logger.debug(
                "Cache SET (key=%s, size=%d bytes, ttl=%ds)",
                key,
                entry_size,
                ttl
            )

    def invalidate(self, key: str):
        """
        Invalidate specific cache entry.

        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                logger.debug("Cache INVALIDATE (key=%s)", key)

    def clear(self):
        """Clear entire cache."""
        with self._lock:
            self._cache.clear()
            self._current_size_bytes = 0
            logger.info("Cache CLEARED")

    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.

        Returns:
            CacheStats with current metrics
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0

            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                current_entries=len(self._cache),
                current_size_bytes=self._current_size_bytes,
                hit_rate=hit_rate
            )

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if entry has expired."""
        elapsed = time.time() - entry["timestamp"]
        return elapsed > entry["ttl"]

    def _evict_lru(self) -> bool:
        """
        Evict least recently used entry.

        Returns:
            True if evicted, False if cache empty
        """
        if not self._cache:
            return False

        # Get first (oldest) key
        key = next(iter(self._cache))
        self._remove_entry(key)
        self._evictions += 1

        logger.debug("Cache EVICT LRU (key=%s)", key)
        return True

    def _remove_entry(self, key: str):
        """Remove entry from cache."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_size_bytes -= entry["size"]

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        # Simple estimation (can be improved)
        return len(str(value).encode('utf-8'))


# Singleton instance for easy import
_cache_instance: Optional[ContextCacheLayer] = None


def get_cache() -> ContextCacheLayer:
    """Get or create singleton ContextCacheLayer instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ContextCacheLayer()
    return _cache_instance
