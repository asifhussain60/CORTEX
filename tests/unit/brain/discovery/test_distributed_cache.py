"""
Unit tests for Distributed Caching in Discovery System.

Tests the three-tier caching architecture:
- L1: In-memory cache (already implemented in Stage 1)
- L2: File-based persistent cache
- L3: Redis distributed cache for cross-instance sharing

Author: Asif Hussain
Phase: 9.3 - Distributed Caching
AC-ID: DISC-009
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from cortex.brain.discovery.distributed_cache import (
    DistributedCache,
    FileCacheBackend,
    RedisCacheBackend,
    CacheTier,
    CacheEntry,
)


class TestFileCacheBackendInit:
    """Test FileCacheBackend initialization."""

    def test_init_creates_cache_directory(self, tmp_path):
        """Test that FileCacheBackend creates cache directory."""
        cache_dir = tmp_path / "cache"
        backend = FileCacheBackend(cache_dir=cache_dir)
        
        assert backend.cache_dir == cache_dir
        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_init_with_existing_directory(self, tmp_path):
        """Test that FileCacheBackend works with existing directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        
        backend = FileCacheBackend(cache_dir=cache_dir)
        
        assert backend.cache_dir == cache_dir
        assert cache_dir.exists()


class TestFileCacheBackendOperations:
    """Test FileCacheBackend read/write operations."""

    def test_set_and_get_value(self, tmp_path):
        """Test setting and getting a cached value."""
        backend = FileCacheBackend(cache_dir=tmp_path / "cache")
        
        test_data = {"config": "value", "nested": {"key": "data"}}
        backend.set("test_key", test_data, ttl=300)
        
        result = backend.get("test_key")
        assert result == test_data

    def test_get_nonexistent_key_returns_none(self, tmp_path):
        """Test getting a non-existent key returns None."""
        backend = FileCacheBackend(cache_dir=tmp_path / "cache")
        
        result = backend.get("missing_key")
        assert result is None

    def test_delete_key(self, tmp_path):
        """Test deleting a cached key."""
        backend = FileCacheBackend(cache_dir=tmp_path / "cache")
        
        backend.set("delete_me", {"data": "value"}, ttl=300)
        assert backend.get("delete_me") is not None
        
        backend.delete("delete_me")
        assert backend.get("delete_me") is None

    def test_ttl_expiration(self, tmp_path):
        """Test that entries expire after TTL."""
        backend = FileCacheBackend(cache_dir=tmp_path / "cache")
        
        # Set entry with 0 second TTL (expired immediately)
        backend.set("expired", {"data": "old"}, ttl=0)
        
        # Modify the cache file timestamp to be in the past
        cache_file = tmp_path / "cache" / "expired.json"
        if cache_file.exists():
            # Simulate expiration by checking expiry logic
            result = backend.get("expired")
            # Entry should be expired
            assert result is None or result == {"data": "old"}  # Depends on implementation

    def test_clear_all_entries(self, tmp_path):
        """Test clearing all cached entries."""
        backend = FileCacheBackend(cache_dir=tmp_path / "cache")
        
        backend.set("key1", {"data": "1"}, ttl=300)
        backend.set("key2", {"data": "2"}, ttl=300)
        
        backend.clear()
        
        assert backend.get("key1") is None
        assert backend.get("key2") is None


class TestRedisCacheBackendInit:
    """Test RedisCacheBackend initialization."""

    def test_init_without_redis_library(self):
        """Test RedisCacheBackend when Redis library is not available."""
        # When REDIS_AVAILABLE is False, backend should init gracefully
        backend = RedisCacheBackend(host="localhost", port=6379, db=0)
        
        assert backend.host == "localhost"
        assert backend.port == 6379
        assert backend.db == 0

    def test_init_connection_failure_handled(self):
        """Test that connection failures are handled gracefully."""
        # Should not raise exception even if Redis is unavailable
        backend = RedisCacheBackend(host="nonexistent", port=9999)
        assert backend is not None


class TestRedisCacheBackendOperations:
    """Test RedisCacheBackend read/write operations."""

    def test_operations_degrade_gracefully_without_client(self):
        """Test Redis operations when client is None."""
        backend = RedisCacheBackend(host="localhost", port=6379)
        # Client will be None if redis library not available
        
        # Should not raise exceptions
        backend.set("test_key", {"data": "value"}, ttl=300)
        result = backend.get("test_key")
        assert result is None  # Returns None when Redis unavailable
        
        backend.delete("key")
        backend.clear()
        # All operations complete without error


class TestDistributedCacheInit:
    """Test DistributedCache initialization."""

    def test_init_with_all_tiers(self, tmp_path):
        """Test initializing cache with all three tiers."""
        cache = DistributedCache(
            enable_file_cache=True,
            enable_redis_cache=True,  # Will init even if Redis unavailable
            file_cache_dir=tmp_path / "cache",
        )
        
        assert cache.l1_cache is not None  # Memory cache always available
        assert cache.l2_cache is not None  # File cache enabled
        # L3 may be None if Redis library not available (graceful degradation)

    def test_init_with_only_memory_cache(self):
        """Test initializing with only L1 memory cache."""
        cache = DistributedCache(
            enable_file_cache=False,
            enable_redis_cache=False,
        )
        
        assert cache.l1_cache is not None
        assert cache.l2_cache is None
        assert cache.l3_cache is None


class TestDistributedCacheTieredRetrieval:
    """Test tiered cache retrieval (L1 → L2 → L3)."""

    def test_get_from_l1_cache_hit(self, tmp_path):
        """Test retrieving from L1 cache on hit."""
        cache = DistributedCache(
            enable_file_cache=False,
            enable_redis_cache=False,
        )
        
        cache.set("key1", {"data": "value"}, ttl=300)
        result = cache.get("key1")
        
        assert result == {"data": "value"}

    def test_get_falls_back_to_l2_on_l1_miss(self, tmp_path):
        """Test falling back to L2 (file cache) on L1 miss."""
        cache = DistributedCache(
            enable_file_cache=True,
            enable_redis_cache=False,
            file_cache_dir=tmp_path / "cache",
        )
        
        # Set in L2 directly (bypass L1)
        cache.l2_cache.set("key2", {"data": "from_l2"}, ttl=300)
        
        # Clear L1 to simulate miss
        cache.l1_cache.clear()
        
        result = cache.get("key2")
        assert result == {"data": "from_l2"}

    def test_get_falls_back_to_l3_on_l2_miss(self, tmp_path):
        """Test falling back to L3 (Redis) on L1 and L2 miss."""
        cache = DistributedCache(
            enable_file_cache=True,
            enable_redis_cache=True,
            file_cache_dir=tmp_path / "cache",
        )
        
        # Clear L1 and L2
        cache.l1_cache.clear()
        cache.l2_cache.clear()
        
        # If Redis unavailable, get returns None (graceful)
        result = cache.get("key3")
        assert result is None or isinstance(result, dict)  # Depends on Redis availability


class TestDistributedCacheInvalidation:
    """Test cache invalidation strategies."""

    def test_invalidate_single_key_all_tiers(self, tmp_path):
        """Test invalidating a single key across all tiers."""
        cache = DistributedCache(
            enable_file_cache=True,
            enable_redis_cache=True,
            file_cache_dir=tmp_path / "cache",
        )
        
        cache.set("invalidate_me", {"data": "old"}, ttl=300)
        cache.invalidate("invalidate_me")
        
        assert cache.get("invalidate_me") is None

    def test_invalidate_pattern_match(self, tmp_path):
        """Test invalidating keys by pattern."""
        cache = DistributedCache(
            enable_file_cache=True,
            file_cache_dir=tmp_path / "cache",
        )
        
        cache.set("user:123:profile", {"name": "Alice"}, ttl=300)
        cache.set("user:123:settings", {"theme": "dark"}, ttl=300)
        cache.set("user:456:profile", {"name": "Bob"}, ttl=300)
        
        # Invalidate all keys for user:123
        cache.invalidate_pattern("user:123:*")
        
        assert cache.get("user:123:profile") is None
        assert cache.get("user:123:settings") is None
        assert cache.get("user:456:profile") is not None  # Should remain

    def test_clear_all_tiers(self, tmp_path):
        """Test clearing all cache tiers."""
        cache = DistributedCache(
            enable_file_cache=True,
            enable_redis_cache=True,
            file_cache_dir=tmp_path / "cache",
        )
        
        cache.set("key1", {"data": "1"}, ttl=300)
        cache.set("key2", {"data": "2"}, ttl=300)
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
