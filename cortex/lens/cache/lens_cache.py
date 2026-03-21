"""LENS Result Caching Layer

Main cache manager with support for multiple backends (Redis, In-Memory).
Implements TTL-based LRU eviction with multi-layer caching.
"""

import hashlib
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


@dataclass
class CacheEntry:  # CORE-035-scoped — independent cache implementation — not shared type
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
    """Abstract base cache manager interface.

    Subclasses must implement get(), set(), and invalidate().
    Concrete backends: MemoryBackend, RedisBackend.
    """

    def __init__(self, backend_type: str = "memory", **kwargs) -> None:
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
        self._store: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache.

        Args:
            key: Cache key (typically from CacheKey.build())

        Returns:
            Cached value if found and not expired, else None
        """
        self._statistics["get_operations"] += 1
        entry = self._store.get(key)
        if entry is None:
            self._statistics["misses"] += 1
            return None
        if entry.is_expired():
            self._statistics["misses"] += 1
            self._store.pop(key, None)
            return None
        entry.hit_count += 1
        self._statistics["hits"] += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (typically LENSResult)
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self._statistics["set_operations"] += 1
        self._store[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            ttl_seconds=ttl,
        )

    def invalidate(self, pattern: str = "*") -> None:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Glob pattern (default: "*" = all)
        """
        if pattern == "*":
            self._store.clear()
            return
        keys_to_remove = [k for k in self._store.keys() if pattern in k]
        for key in keys_to_remove:
            self._store.pop(key, None)

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

    def generate_key(
        self,
        file_path: Union[str, Path],
        repo_path: Union[str, Path],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate cache key for file analysis.

        Cache key incorporates:
        - File path relative to repo
        - Optional additional context

        Args:
            file_path: Path to file being analyzed
            repo_path: Path to repository root
            additional_context: Optional extra context for cache key

        Returns:
            Cache key string
        """
        if not isinstance(file_path, (str, Path)):
            raise TypeError("file_path must be str or Path")
        if not isinstance(repo_path, (str, Path)):
            raise TypeError("repo_path must be str or Path")

        file_path = Path(file_path)
        repo_path = Path(repo_path)

        # Get relative path
        try:
            rel_path = file_path.relative_to(repo_path)
        except ValueError:
            rel_path = file_path

        # Build key components
        key_parts = [str(rel_path)]

        # Add additional context if provided
        if additional_context:
            context_str = str(sorted(additional_context.items()))
            key_parts.append(context_str)

        # Generate hash
        key_string = "|".join(key_parts)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        return f"lens:{key_hash}:{rel_path.name}"


# Phase 65 S6: Canonical LENSCache singleton accessor
_lens_cache_instance: Optional['LENSCache'] = None
_lens_cache_lock = threading.Lock()


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
        with _lens_cache_lock:
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
