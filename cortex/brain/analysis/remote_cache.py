"""
Remote Git Analysis Caching Layer.

Provides disk-based caching for remote git API responses with TTL
and size management.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
Phase: 10 - LENS Remote Intelligence
Task: LENS-013
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

from diskcache import Cache


@dataclass
class CacheEntry:
    """Cache entry with metadata.

    Attributes:
        key: Cache key (hash of request parameters)
        value: Cached response data
        timestamp: Unix timestamp when cached
        ttl: Time-to-live in seconds
        provider: Git provider (github, gitlab, etc.)
        repo: Repository identifier
    """

    key: str
    value: Any
    timestamp: float
    ttl: int
    provider: str
    repo: str


@dataclass
class CacheStats:
    """Cache statistics.

    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        size: Current cache size in bytes
        entries: Number of cached entries
        evictions: Number of evicted entries
    """

    hits: int = 0
    misses: int = 0
    size: int = 0
    entries: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate.

        Returns:
            Hit rate as percentage (0.0-100.0)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100


class RemoteCache:
    """Disk-based cache for remote git analysis results.

    Uses diskcache for persistent, disk-based caching with automatic
    eviction and size management.

    Example:
        >>> cache = RemoteCache(cache_dir=Path("~/.cortex/cache"))
        >>> cache.set("key", {"data": "value"}, ttl=3600)
        >>> result = cache.get("key")
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_size: int = 1024 * 1024 * 100,  # 100 MB default
        default_ttl: int = 3600,  # 1 hour default
    ):
        """Initialize remote cache.

        Args:
            cache_dir: Directory for cache storage. Defaults to ~/.cortex/cache
            max_size: Maximum cache size in bytes
            default_ttl: Default time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cortex" / "cache"

        self.cache_dir = cache_dir.expanduser().resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_size = max_size
        self.default_ttl = default_ttl

        # Initialize diskcache
        self._cache = Cache(
            directory=str(self.cache_dir),
            size_limit=max_size,
        )

        # Statistics tracking
        self._stats = CacheStats()

    def _make_key(
        self,
        provider: str,
        repo: str,
        operation: str,
        **params: Any
    ) -> str:
        """Generate cache key from parameters.

        Args:
            provider: Git provider (github, gitlab, etc.)
            repo: Repository identifier
            operation: Operation name (fetch_file, fetch_commits, etc.)
            **params: Additional parameters (ref, path, etc.)

        Returns:
            SHA256 hash of normalized parameters
        """
        # Normalize parameters
        key_parts = [
            provider.lower(),
            repo.lower(),
            operation.lower(),
        ]

        # Add sorted parameters
        for key in sorted(params.keys()):
            value = params[key]
            key_parts.append(f"{key}={value}")

        # Generate hash
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(
        self,
        provider: str,
        repo: str,
        operation: str,
        **params: Any
    ) -> Optional[Any]:
        """Get cached value.

        Args:
            provider: Git provider
            repo: Repository identifier
            operation: Operation name
            **params: Operation parameters

        Returns:
            Cached value if found and not expired, None otherwise
        """
        key = self._make_key(provider, repo, operation, **params)

        try:
            # Check if key exists
            if key not in self._cache:
                self._stats.misses += 1
                return None

            # Get entry
            entry_data = self._cache.get(key)
            if entry_data is None:
                self._stats.misses += 1
                return None

            # Check expiration
            entry = CacheEntry(**entry_data)
            age = time.time() - entry.timestamp

            if age > entry.ttl:
                # Expired - remove and return None
                self._cache.delete(key)
                self._stats.evictions += 1
                self._stats.misses += 1
                return None

            # Valid entry
            self._stats.hits += 1
            return entry.value

        except Exception:
            # Cache read error - treat as miss
            self._stats.misses += 1
            return None

    def set(
        self,
        provider: str,
        repo: str,
        operation: str,
        value: Any,
        ttl: Optional[int] = None,
        **params: Any
    ) -> bool:
        """Set cached value.

        Args:
            provider: Git provider
            repo: Repository identifier
            operation: Operation name
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            **params: Operation parameters

        Returns:
            True if successfully cached, False otherwise
        """
        if ttl is None:
            ttl = self.default_ttl

        key = self._make_key(provider, repo, operation, **params)

        try:
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                provider=provider,
                repo=repo,
            )

            # Store entry
            self._cache.set(key, asdict(entry))
            return True

        except Exception:
            # Cache write error
            return False

    def invalidate(
        self,
        provider: Optional[str] = None,
        repo: Optional[str] = None,
        operation: Optional[str] = None,
        **params: Any
    ) -> int:
        """Invalidate cached entries.

        Args:
            provider: Filter by provider (None = all)
            repo: Filter by repository (None = all)
            operation: Filter by operation (None = all)
            **params: Additional filter parameters

        Returns:
            Number of entries invalidated
        """
        if not any([provider, repo, operation, params]):
            # Clear all
            count = len(self._cache)
            self._cache.clear()
            self._stats.evictions += count
            return count

        # Selective invalidation
        count = 0
        keys_to_delete = []

        for key in self._cache.iterkeys():
            try:
                entry_data = self._cache.get(key)
                if entry_data is None:
                    continue

                entry = CacheEntry(**entry_data)

                # Check filters
                if provider and entry.provider != provider:
                    continue
                if repo and entry.repo != repo:
                    continue

                keys_to_delete.append(key)

            except Exception:
                continue

        # Delete matched keys
        for key in keys_to_delete:
            self._cache.delete(key)
            count += 1

        self._stats.evictions += count
        return count

    def stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Current cache statistics
        """
        # Update size and entries
        self._stats.size = self._cache.volume()
        self._stats.entries = len(self._cache)

        return self._stats

    def clear(self) -> None:
        """Clear all cached entries."""
        count = len(self._cache)
        self._cache.clear()
        self._stats.evictions += count
        self._stats.entries = 0
        self._stats.size = 0

    def close(self) -> None:
        """Close cache and release resources."""
        self._cache.close()


# Global cache instance
_global_cache: Optional[RemoteCache] = None


def get_remote_cache(
    cache_dir: Optional[Path] = None,
    max_size: int = 1024 * 1024 * 100,
    default_ttl: int = 3600,
) -> RemoteCache:
    """Get or create global cache instance.

    Args:
        cache_dir: Cache directory (only used on first call)
        max_size: Maximum cache size in bytes
        default_ttl: Default TTL in seconds

    Returns:
        Global RemoteCache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = RemoteCache(
            cache_dir=cache_dir,
            max_size=max_size,
            default_ttl=default_ttl,
        )

    return _global_cache
