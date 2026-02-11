"""In-memory LRU cache backend for development."""

import fnmatch
import sys
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from cortex.lens.cache.lens_cache import CacheEntry, LENSCache


class MemoryBackend(LENSCache):
    """In-memory LRU cache backend.

    Suitable for development and single-process deployments.
    Features: TTL expiration, LRU eviction, hit/miss statistics.

    Eviction policies:
    - Entry count: Triggers LRU when exceeding max_entries
    - Memory size: Triggers eviction when exceeding max_size_mb
    - TTL expiration: Entries automatically considered expired
    """

    def __init__(self, max_entries: int = 1000, max_size_mb: int = 100):
        """Initialize memory backend.

        Args:
            max_entries: Maximum cache entries (default: 1000)
            max_size_mb: Maximum memory usage in MB (default: 100MB)

        Raises:
            ValueError: If max_entries or max_size_mb invalid
        """
        super().__init__(backend_type="memory")

        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        if max_size_mb <= 0:
            raise ValueError("max_size_mb must be positive")

        self.max_entries = max_entries
        self.max_size_mb = max_size_mb
        # OrderedDict maintains insertion order for LRU
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._current_size_bytes = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from memory cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, else None

        Note:
            Hit updates recency (moves to end for LRU).
            Miss counts toward statistics.
        """
        self._statistics["get_operations"] += 1

        if key not in self._cache:
            self._statistics["misses"] += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if entry.is_expired():
            self._statistics["misses"] += 1
            # Clean up expired entry
            self._remove_entry(key)
            return None

        # Update entry statistics
        entry.hit_count += 1
        self._statistics["hits"] += 1

        # Move to end (most recently used)
        self._cache.move_to_end(key)

        return entry.value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in memory cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 300)

        Raises:
            ValueError: If ttl is invalid
        """
        if ttl <= 0:
            raise ValueError("ttl must be positive")

        self._statistics["set_operations"] += 1

        # Remove existing entry if present
        if key in self._cache:
            self._remove_entry(key)

        # Create new entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            ttl_seconds=ttl,
            hit_count=0
        )

        # Add to cache
        self._cache[key] = entry
        self._update_size(entry)

        # Trigger evictions if needed
        self._evict_if_needed()

    def invalidate(self, pattern: str = "*") -> None:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Glob pattern (e.g., "analyze_*", "*" for all)

        Note:
            Uses fnmatch for glob-style pattern matching.
        """
        if pattern == "*":
            self._cache.clear()
            self._current_size_bytes = 0
            return

        # Find matching keys
        keys_to_remove = [
            key for key in self._cache.keys()
            if fnmatch.fnmatch(key, pattern)
        ]

        # Remove matching entries
        for key in keys_to_remove:
            self._remove_entry(key)

    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache and update size tracking.

        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            entry = self._cache[key]
            size_bytes = sys.getsizeof(entry.value)
            self._current_size_bytes -= size_bytes
            del self._cache[key]

    def _update_size(self, entry: CacheEntry) -> None:
        """Update size tracking for new entry.

        Args:
            entry: CacheEntry to track
        """
        size_bytes = sys.getsizeof(entry.value)
        self._current_size_bytes += size_bytes

    def _evict_if_needed(self) -> None:
        """Evict entries if limits exceeded.

        Eviction order:
        1. Entry count limit (evicts LRU entries first)
        2. Memory size limit (evicts LRU entries first)

        Note:
            LRU eviction uses OrderedDict.popitem(last=False)
            to remove least recently used (oldest) entry.
        """
        # Entry count eviction
        while len(self._cache) > self.max_entries:
            key, entry = self._cache.popitem(last=False)
            self._current_size_bytes -= sys.getsizeof(entry.value)
            self._statistics["evictions"] += 1

        # Memory size eviction
        max_size_bytes = self.max_size_mb * 1024 * 1024
        while self._current_size_bytes > max_size_bytes:
            key, entry = self._cache.popitem(last=False)
            self._current_size_bytes -= sys.getsizeof(entry.value)
            self._statistics["evictions"] += 1

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics.

        Returns:
            Dictionary with:
            - current_bytes: Current memory usage
            - max_bytes: Maximum configured memory
            - usage_percent: Usage as percentage
            - num_entries: Current number of entries
            - max_entries: Maximum configured entries
        """
        max_size_bytes = self.max_size_mb * 1024 * 1024
        usage_percent = (self._current_size_bytes / max_size_bytes * 100) if max_size_bytes > 0 else 0

        return {
            "current_bytes": self._current_size_bytes,
            "max_bytes": max_size_bytes,
            "usage_percent": round(usage_percent, 2),
            "num_entries": len(self._cache),
            "max_entries": self.max_entries
        }

    def cleanup_expired(self) -> int:
        """Remove all expired entries from cache.

        Returns:
            Number of entries removed

        Note:
            Useful for periodic maintenance.
            Expired entries are normally cleaned on access.
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]

        count_removed = 0
        for key in expired_keys:
            self._remove_entry(key)
            count_removed += 1

        return count_removed


__all__ = ["MemoryBackend"]
