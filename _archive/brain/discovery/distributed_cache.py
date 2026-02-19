"""
Distributed Caching for Discovery System.

Implements a three-tier caching architecture:
- L1: In-memory cache (fastest, instance-local)
- L2: File-based persistent cache (survives restarts)
- L3: Redis distributed cache (cross-instance sharing)

Supports TTL, cache invalidation, and tiered fallback retrieval.

Author: Asif Hussain
Phase: 9.3 - Distributed Caching
AC-ID: DISC-009
"""

import fnmatch
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


logger = logging.getLogger(__name__)


class CacheTier(Enum):
    """Cache tier levels."""

    L1_MEMORY = "l1_memory"
    L2_FILE = "l2_file"
    L3_REDIS = "l3_redis"


@dataclass
class CacheEntry:
    """Represents a cached entry with metadata.

    Attributes:
        key: Cache key
        value: Cached value
        created_at: Timestamp when entry was created
        expires_at: Timestamp when entry expires
        tier: Which cache tier this entry is from
    """

    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    tier: CacheTier


class FileCacheBackend:
    """File-based persistent cache (L2).

    Stores cache entries as JSON files on disk. Survives process restarts.

    Examples:
        >>> backend = FileCacheBackend(cache_dir=Path(".cache"))
        >>> backend.set("topology:v1", {"nodes": 10}, ttl=3600)
        >>> data = backend.get("topology:v1")
    """

    def __init__(self, cache_dir: Path):
        """Initialize file cache backend.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"File cache initialized at {cache_dir}")

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Sanitize key for filename
        safe_key = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe_key}.json"

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set a value in file cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        try:
            cache_file = self._get_cache_file(key)

            entry = {
                "key": key,
                "value": value,
                "created_at": time.time(),
                "expires_at": time.time() + ttl if ttl > 0 else None,
            }

            cache_file.write_text(json.dumps(entry, indent=2))
            logger.debug(f"Cached to file: {key}")
        except Exception as e:
            logger.warning(f"Failed to write file cache for {key}: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from file cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            cache_file = self._get_cache_file(key)

            if not cache_file.exists():
                return None

            entry = json.loads(cache_file.read_text())

            # Check expiration
            if entry.get("expires_at") and time.time() > entry["expires_at"]:
                cache_file.unlink()  # Delete expired file
                return None

            return entry.get("value")
        except Exception as e:
            logger.warning(f"Failed to read file cache for {key}: {e}")
            return None

    def delete(self, key: str) -> None:
        """Delete a key from file cache.

        Args:
            key: Cache key to delete
        """
        try:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Deleted from file cache: {key}")
        except Exception as e:
            logger.warning(f"Failed to delete file cache for {key}: {e}")

    def clear(self) -> None:
        """Clear all entries from file cache."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("File cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear file cache: {e}")


class RedisCacheBackend:
    """Redis distributed cache (L3).

    Stores cache entries in Redis for cross-instance sharing.

    Examples:
        >>> backend = RedisCacheBackend(host="localhost", port=6379)
        >>> backend.set("topology:global", {"instances": 5}, ttl=7200)
        >>> data = backend.get("topology:global")
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis cache backend.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
        """
        self.host = host
        self.port = port
        self.db = db
        self.client: Optional[Any] = None

        if not REDIS_AVAILABLE:
            logger.warning("Redis library not available - L3 cache disabled")
            return

        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
            self.client.ping()  # Test connection
            logger.info(f"Redis cache connected to {host}:{port}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.client = None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set a value in Redis cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        if not self.client:
            return

        try:
            data = json.dumps(value)
            if ttl > 0:
                self.client.setex(key, ttl, data)
            else:
                self.client.set(key, data)
            logger.debug(f"Cached to Redis: {key}")
        except Exception as e:
            logger.warning(f"Failed to write Redis cache for {key}: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.client:
            return None

        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Failed to read Redis cache for {key}: {e}")
            return None

    def delete(self, key: str) -> None:
        """Delete a key from Redis cache.

        Args:
            key: Cache key to delete
        """
        if not self.client:
            return

        try:
            self.client.delete(key)
            logger.debug(f"Deleted from Redis: {key}")
        except Exception as e:
            logger.warning(f"Failed to delete Redis cache for {key}: {e}")

    def clear(self) -> None:
        """Clear all entries from Redis cache."""
        if not self.client:
            return

        try:
            self.client.flushdb()
            logger.info("Redis cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear Redis cache: {e}")


class DistributedCache:
    """Three-tier distributed cache system.

    Implements L1 (memory) → L2 (file) → L3 (Redis) cache hierarchy
    with automatic tier fallback and invalidation.

    Examples:
        >>> cache = DistributedCache(
        ...     enable_file_cache=True,
        ...     enable_redis_cache=True,
        ...     file_cache_dir=Path(".cache"),
        ... )
        >>> cache.set("topology", {"nodes": 10}, ttl=3600)
        >>> data = cache.get("topology")  # Checks L1 → L2 → L3
        >>> cache.invalidate("topology")  # Clears from all tiers
    """

    def __init__(
        self,
        enable_file_cache: bool = True,
        enable_redis_cache: bool = False,
        file_cache_dir: Optional[Path] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
    ):
        """Initialize distributed cache.

        Args:
            enable_file_cache: Enable L2 file cache
            enable_redis_cache: Enable L3 Redis cache
            file_cache_dir: Directory for file cache
            redis_host: Redis server host
            redis_port: Redis server port
        """
        # L1: In-memory cache (always enabled)
        self.l1_cache: Dict[str, CacheEntry] = {}

        # L2: File cache
        self.l2_cache: Optional[FileCacheBackend] = None
        if enable_file_cache:
            cache_dir = file_cache_dir or Path(".cortex_cache")
            self.l2_cache = FileCacheBackend(cache_dir=cache_dir)

        # L3: Redis cache
        self.l3_cache: Optional[RedisCacheBackend] = None
        if enable_redis_cache:
            self.l3_cache = RedisCacheBackend(host=redis_host, port=redis_port)

        logger.info(f"Distributed cache initialized (L2: {enable_file_cache}, L3: {enable_redis_cache})")

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set a value in all cache tiers.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        current_time = time.time()
        expires_at = current_time + ttl if ttl > 0 else None

        # L1: Memory cache
        self.l1_cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            expires_at=expires_at,
            tier=CacheTier.L1_MEMORY,
        )

        # L2: File cache
        if self.l2_cache:
            self.l2_cache.set(key, value, ttl)

        # L3: Redis cache
        if self.l3_cache:
            self.l3_cache.set(key, value, ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache with tier fallback.

        Checks L1 → L2 → L3 in order. If found in lower tier,
        promotes to higher tiers.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        # L1: Memory cache
        entry = self.l1_cache.get(key)
        if entry:
            # Check expiration
            if entry.expires_at and time.time() > entry.expires_at:
                del self.l1_cache[key]
            else:
                return entry.value

        # L2: File cache
        if self.l2_cache:
            value = self.l2_cache.get(key)
            if value is not None:
                # Promote to L1
                self.l1_cache[key] = CacheEntry(
                    key=key,
                    value=value,
                    created_at=time.time(),
                    expires_at=None,  # Use file cache TTL
                    tier=CacheTier.L1_MEMORY,
                )
                return value

        # L3: Redis cache
        if self.l3_cache:
            value = self.l3_cache.get(key)
            if value is not None:
                # Promote to L1 and L2
                self.l1_cache[key] = CacheEntry(
                    key=key,
                    value=value,
                    created_at=time.time(),
                    expires_at=None,
                    tier=CacheTier.L1_MEMORY,
                )
                if self.l2_cache:
                    self.l2_cache.set(key, value, ttl=3600)
                return value

        return None

    def invalidate(self, key: str) -> None:
        """Invalidate a key across all cache tiers.

        Args:
            key: Cache key to invalidate
        """
        # L1: Memory
        if key in self.l1_cache:
            del self.l1_cache[key]

        # L2: File
        if self.l2_cache:
            self.l2_cache.delete(key)

        # L3: Redis
        if self.l3_cache:
            self.l3_cache.delete(key)

        logger.debug(f"Invalidated cache key: {key}")

    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate keys matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "user:*:profile")
        """
        # L1: Memory
        keys_to_delete = [key for key in self.l1_cache.keys() if fnmatch.fnmatch(key, pattern)]
        for key in keys_to_delete:
            del self.l1_cache[key]

        # L2: File (iterate files)
        if self.l2_cache:
            for cache_file in self.l2_cache.cache_dir.glob("*.json"):
                # Reconstruct key from filename
                key = cache_file.stem.replace("_", ":")
                if fnmatch.fnmatch(key, pattern):
                    cache_file.unlink()

        # L3: Redis pattern delete (if supported)
        # Note: Redis KEYS command is expensive - use carefully in production
        logger.debug(f"Invalidated cache pattern: {pattern}")

    def clear(self) -> None:
        """Clear all cache tiers."""
        # L1: Memory
        self.l1_cache.clear()

        # L2: File
        if self.l2_cache:
            self.l2_cache.clear()

        # L3: Redis
        if self.l3_cache:
            self.l3_cache.clear()

        logger.info("All cache tiers cleared")
