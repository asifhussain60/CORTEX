"""Unit tests for LENS cache manager."""

import pytest
from cortex.lens.cache.lens_cache import LENSCache, CacheEntry, CacheKey
from datetime import datetime, timedelta


class TestCacheKey:
    """Test CacheKey generation."""

    def test_build_generates_valid_key(self):
        """CacheKey.build() should generate valid cache key."""
        key = CacheKey(
            user_request="analyze module.py",
            repo_state_hash="abc123",
            lens_version="2.0"
        )
        result = key.build()
        
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hex string length
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_context_generates_same_key(self):
        """Identical contexts should generate identical keys."""
        context = CacheKey(
            user_request="analyze module.py",
            repo_state_hash="abc123",
            lens_version="2.0"
        )
        key1 = context.build()
        key2 = context.build()
        
        assert key1 == key2

    def test_different_context_generates_different_key(self):
        """Different contexts should generate different keys."""
        context1 = CacheKey(
            user_request="analyze module.py",
            repo_state_hash="abc123",
            lens_version="2.0"
        )
        context2 = CacheKey(
            user_request="analyze other.py",
            repo_state_hash="abc123",
            lens_version="2.0"
        )
        
        key1 = context1.build()
        key2 = context2.build()
        
        assert key1 != key2


class TestCacheEntry:
    """Test CacheEntry expiration logic."""

    def test_entry_not_expired_within_ttl(self):
        """Entry should not be expired within TTL."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            ttl_seconds=300
        )
        
        assert not entry.is_expired()

    def test_entry_expired_after_ttl(self):
        """Entry should be expired after TTL."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now() - timedelta(seconds=400),
            ttl_seconds=300
        )
        
        assert entry.is_expired()


class TestLENSCacheStatistics:
    """Test cache statistics collection."""

    def test_statistics_initialized_to_zero(self):
        """Cache statistics should initialize to zero."""
        cache = LENSCache(backend_type="memory")
        stats = cache.get_statistics()
        
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
        assert stats["set_operations"] == 0
        assert stats["get_operations"] == 0
        assert stats["hit_rate_percent"] == 0.0
        assert stats["total_operations"] == 0

    def test_hit_rate_calculation_zero_operations(self):
        """Hit rate should be 0.0 with no operations."""
        cache = LENSCache(backend_type="memory")
        stats = cache.get_statistics()
        
        assert stats["hit_rate_percent"] == 0.0

    def test_hit_rate_calculation_all_hits(self):
        """Hit rate should be 100% when all operations are hits."""
        cache = LENSCache(backend_type="memory")
        # Manually set statistics for testing
        cache._statistics["hits"] = 10
        cache._statistics["misses"] = 0
        
        stats = cache.get_statistics()
        assert stats["hit_rate_percent"] == 100.0
        assert stats["total_operations"] == 10

    def test_hit_rate_calculation_all_misses(self):
        """Hit rate should be 0% when all operations are misses."""
        cache = LENSCache(backend_type="memory")
        cache._statistics["hits"] = 0
        cache._statistics["misses"] = 10
        
        stats = cache.get_statistics()
        assert stats["hit_rate_percent"] == 0.0
        assert stats["total_operations"] == 10

    def test_hit_rate_calculation_mixed(self):
        """Hit rate should calculate correctly for mixed hits/misses."""
        cache = LENSCache(backend_type="memory")
        cache._statistics["hits"] = 7
        cache._statistics["misses"] = 3
        
        stats = cache.get_statistics()
        assert stats["hit_rate_percent"] == 70.0
        assert stats["total_operations"] == 10


class TestLENSCacheInterface:
    """Test LENSCache abstract interface."""

    def test_get_raises_not_implemented(self):
        """LENSCache.get() should raise NotImplementedError."""
        cache = LENSCache(backend_type="memory")
        
        with pytest.raises(NotImplementedError):
            cache.get("test_key")

    def test_set_raises_not_implemented(self):
        """LENSCache.set() should raise NotImplementedError."""
        cache = LENSCache(backend_type="memory")
        
        with pytest.raises(NotImplementedError):
            cache.set("test_key", {"result": "data"})

    def test_invalidate_raises_not_implemented(self):
        """LENSCache.invalidate() should raise NotImplementedError."""
        cache = LENSCache(backend_type="memory")
        
        with pytest.raises(NotImplementedError):
            cache.invalidate("*")

    def test_backend_type_stored(self):
        """Backend type should be stored during initialization."""
        cache_memory = LENSCache(backend_type="memory")
        cache_redis = LENSCache(backend_type="redis")
        
        assert cache_memory.backend_type == "memory"
        assert cache_redis.backend_type == "redis"


class TestCacheEntryStatistics:
    """Test CacheEntry hit counting."""

    def test_hit_count_initial(self):
        """CacheEntry should initialize with hit_count=0."""
        entry = CacheEntry(
            key="test",
            value="data",
            created_at=datetime.now(),
            ttl_seconds=300
        )
        
        assert entry.hit_count == 0

    def test_hit_count_custom(self):
        """CacheEntry should accept custom hit_count."""
        entry = CacheEntry(
            key="test",
            value="data",
            created_at=datetime.now(),
            ttl_seconds=300,
            hit_count=5
        )
        
        assert entry.hit_count == 5

    def test_entry_expiration_boundary(self):
        """Entry should expire at exact TTL boundary."""
        now = datetime.now()
        entry = CacheEntry(
            key="test",
            value="data",
            created_at=now - timedelta(seconds=300),
            ttl_seconds=300
        )
        
        # Just at boundary - implementation may vary (> vs >=)
        # This tests implementation detail
        assert entry.is_expired()

    def test_entry_fresh(self):
        """Fresh entry should not be expired."""
        entry = CacheEntry(
            key="test",
            value="data",
            created_at=datetime.now() - timedelta(seconds=1),
            ttl_seconds=300
        )
        
        assert not entry.is_expired()


class TestCacheKeyEdgeCases:
    """Test CacheKey edge cases."""

    def test_empty_user_request(self):
        """CacheKey should handle empty user request."""
        key = CacheKey(
            user_request="",
            repo_state_hash="abc123",
            lens_version="2.0"
        )
        
        result = key.build()
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_special_characters_in_request(self):
        """CacheKey should handle special characters."""
        key = CacheKey(
            user_request="analyze 'module.py' @repo",
            repo_state_hash="xyz789",
            lens_version="2.0"
        )
        
        result = key.build()
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_different_versions_different_keys(self):
        """Different versions should produce different keys."""
        context_v1 = CacheKey(
            user_request="analyze",
            repo_state_hash="abc123",
            lens_version="1.0"
        )
        context_v2 = CacheKey(
            user_request="analyze",
            repo_state_hash="abc123",
            lens_version="2.0"
        )
        
        key1 = context_v1.build()
        key2 = context_v2.build()
        
        assert key1 != key2
