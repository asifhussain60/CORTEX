"""Unit tests for in-memory LRU cache backend."""

import pytest
from cortex.lens.cache.memory_backend import MemoryBackend
from datetime import datetime, timedelta
import time


class TestMemoryBackendInit:
    """Test MemoryBackend initialization."""

    def test_init_default_values(self):
        """Backend should initialize with default parameters."""
        backend = MemoryBackend()
        
        assert backend.max_entries == 1000
        assert backend.max_size_mb == 100
        assert backend.backend_type == "memory"
        assert len(backend._cache) == 0

    def test_init_custom_values(self):
        """Backend should accept custom parameters."""
        backend = MemoryBackend(max_entries=500, max_size_mb=50)
        
        assert backend.max_entries == 500
        assert backend.max_size_mb == 50

    def test_init_invalid_max_entries(self):
        """Backend should reject invalid max_entries."""
        with pytest.raises(ValueError, match="max_entries must be positive"):
            MemoryBackend(max_entries=0)
        
        with pytest.raises(ValueError, match="max_entries must be positive"):
            MemoryBackend(max_entries=-1)

    def test_init_invalid_max_size_mb(self):
        """Backend should reject invalid max_size_mb."""
        with pytest.raises(ValueError, match="max_size_mb must be positive"):
            MemoryBackend(max_size_mb=0)
        
        with pytest.raises(ValueError, match="max_size_mb must be positive"):
            MemoryBackend(max_size_mb=-1)


class TestMemoryBackendBasicOps:
    """Test basic get/set operations."""

    def test_set_and_get(self):
        """Should store and retrieve values."""
        backend = MemoryBackend()
        test_value = {"result": "test"}
        
        backend.set("key1", test_value)
        result = backend.get("key1")
        
        assert result == test_value

    def test_get_missing_key(self):
        """Should return None for missing keys."""
        backend = MemoryBackend()
        
        result = backend.get("nonexistent")
        
        assert result is None

    def test_set_updates_existing_key(self):
        """Updating existing key should replace value."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.set("key1", "value2")
        
        assert backend.get("key1") == "value2"

    def test_set_invalid_ttl_zero(self):
        """Backend should reject TTL of 0."""
        backend = MemoryBackend()
        
        with pytest.raises(ValueError, match="ttl must be positive"):
            backend.set("key1", "value", ttl=0)

    def test_set_invalid_ttl_negative(self):
        """Backend should reject negative TTL."""
        backend = MemoryBackend()
        
        with pytest.raises(ValueError, match="ttl must be positive"):
            backend.set("key1", "value", ttl=-1)


class TestMemoryBackendTTL:
    """Test TTL expiration behavior."""

    def test_entry_not_expired_within_ttl(self):
        """Entry should not be expired within TTL."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1", ttl=300)
        result = backend.get("key1")
        
        assert result == "value1"

    def test_entry_expired_after_ttl(self):
        """Entry should be expired after TTL."""
        backend = MemoryBackend()
        
        # Use very short TTL for testing
        backend.set("key1", "value1", ttl=1)
        time.sleep(1.1)
        
        result = backend.get("key1")
        
        assert result is None

    def test_expired_entry_cleaned_on_access(self):
        """Expired entries should be removed from cache on access."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1", ttl=1)
        time.sleep(1.1)
        
        # Access expired entry
        backend.get("key1")
        
        # Verify entry removed
        assert "key1" not in backend._cache

    def test_custom_ttl_values(self):
        """Should respect custom TTL values."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1", ttl=10)
        backend.set("key2", "value2", ttl=100)
        
        assert backend.get("key1") == "value1"
        assert backend.get("key2") == "value2"


class TestMemoryBackendStatistics:
    """Test hit/miss statistics."""

    def test_statistics_tracking_hits(self):
        """Backend should track cache hits."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.get("key1")  # Hit
        backend.get("key1")  # Hit
        
        stats = backend.get_statistics()
        assert stats["hits"] == 2

    def test_statistics_tracking_misses(self):
        """Backend should track cache misses."""
        backend = MemoryBackend()
        
        backend.get("missing1")  # Miss
        backend.get("missing2")  # Miss
        
        stats = backend.get_statistics()
        assert stats["misses"] == 2

    def test_statistics_hit_rate(self):
        """Backend should calculate hit rate correctly."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.get("key1")  # Hit
        backend.get("missing")  # Miss
        
        stats = backend.get_statistics()
        assert stats["hit_rate_percent"] == 50.0
        assert stats["total_operations"] == 2

    def test_statistics_set_operations(self):
        """Backend should track set operations."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        
        stats = backend.get_statistics()
        assert stats["set_operations"] == 2

    def test_statistics_get_operations(self):
        """Backend should track get operations."""
        backend = MemoryBackend()
        
        backend.get("key1")
        backend.get("key2")
        backend.get("key3")
        
        stats = backend.get_statistics()
        assert stats["get_operations"] == 3


class TestMemoryBackendLRUEviction:
    """Test LRU eviction behavior."""

    def test_lru_eviction_on_max_entries(self):
        """Backend should evict LRU entries when max_entries exceeded."""
        backend = MemoryBackend(max_entries=3)
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")
        backend.set("key4", "value4")  # Should evict key1 (LRU)
        
        assert backend.get("key1") is None  # Evicted
        assert backend.get("key4") == "value4"  # Still there

    def test_lru_eviction_updates_statistics(self):
        """Backend should track evictions in statistics."""
        backend = MemoryBackend(max_entries=2)
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")  # Eviction occurs
        
        stats = backend.get_statistics()
        assert stats["evictions"] == 1

    def test_lru_respects_recency(self):
        """LRU should consider get() as updating recency."""
        backend = MemoryBackend(max_entries=2)
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.get("key1")  # Refresh key1 recency
        backend.set("key3", "value3")  # Should evict key2, not key1
        
        assert backend.get("key1") == "value1"
        assert backend.get("key2") is None

    def test_no_eviction_below_limit(self):
        """Backend should not evict when below max_entries."""
        backend = MemoryBackend(max_entries=5)
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        
        stats = backend.get_statistics()
        assert stats["evictions"] == 0
        assert len(backend._cache) == 2


class TestMemoryBackendMemoryEviction:
    """Test size-based eviction."""

    def test_memory_size_tracking(self):
        """Backend should track memory usage."""
        backend = MemoryBackend(max_size_mb=1)
        
        backend.set("key1", "x" * 100)
        usage = backend.get_memory_usage()
        
        assert usage["num_entries"] == 1
        assert usage["current_bytes"] > 0

    def test_memory_usage_calculation(self):
        """Backend should calculate memory usage percentage."""
        backend = MemoryBackend(max_size_mb=1)
        
        backend.set("key1", "value1")
        usage = backend.get_memory_usage()
        
        assert 0 <= usage["usage_percent"] <= 100
        assert usage["max_bytes"] == 1024 * 1024

    def test_lru_eviction_on_memory_limit(self):
        """Backend should evict when exceeding memory limit."""
        backend = MemoryBackend(max_size_mb=1, max_entries=1000)
        
        # Fill cache to trigger size-based eviction
        large_value = "x" * (500 * 1024)  # 500KB each
        
        backend.set("key1", large_value)
        backend.set("key2", large_value)
        backend.set("key3", large_value)  # Should trigger eviction
        
        # Verify eviction occurred
        stats = backend.get_statistics()
        assert stats["evictions"] > 0


class TestMemoryBackendInvalidation:
    """Test pattern-based invalidation."""

    def test_invalidate_all(self):
        """Invalidate '*' should clear all entries."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")
        
        backend.invalidate("*")
        
        assert len(backend._cache) == 0
        assert backend.get("key1") is None

    def test_invalidate_pattern_glob(self):
        """Should invalidate matching glob patterns."""
        backend = MemoryBackend()
        
        backend.set("analyze_module.py", "result1")
        backend.set("analyze_utils.py", "result2")
        backend.set("audit_module.py", "result3")
        
        backend.invalidate("analyze_*")
        
        assert backend.get("analyze_module.py") is None
        assert backend.get("analyze_utils.py") is None
        assert backend.get("audit_module.py") == "result3"

    def test_invalidate_no_matches(self):
        """Invalidate non-matching pattern should do nothing."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.invalidate("nonexistent_*")
        
        assert backend.get("key1") == "value1"

    def test_invalidate_single_key(self):
        """Should invalidate specific key pattern."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        
        backend.invalidate("key1")
        
        assert backend.get("key1") is None
        assert backend.get("key2") == "value2"


class TestMemoryBackendCleanup:
    """Test expired entry cleanup."""

    def test_cleanup_expired_removes_stale_entries(self):
        """cleanup_expired() should remove expired entries."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1", ttl=1)
        backend.set("key2", "value2", ttl=300)
        
        time.sleep(1.1)
        
        removed = backend.cleanup_expired()
        
        assert removed == 1
        assert backend.get("key1") is None
        assert backend.get("key2") == "value2"

    def test_cleanup_expired_returns_count(self):
        """cleanup_expired() should return count of removed entries."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1", ttl=1)
        backend.set("key2", "value1", ttl=1)
        backend.set("key3", "value1", ttl=300)
        
        time.sleep(1.1)
        
        removed = backend.cleanup_expired()
        
        assert removed == 2


class TestMemoryBackendConcurrency:
    """Test entry statistics tracking."""

    def test_hit_count_increments(self):
        """Each get() should increment hit_count."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.get("key1")
        backend.get("key1")
        backend.get("key1")
        
        entry = backend._cache["key1"]
        assert entry.hit_count == 3

    def test_hit_count_reset_on_set(self):
        """Updating entry should reset hit_count."""
        backend = MemoryBackend()
        
        backend.set("key1", "value1")
        backend.get("key1")
        backend.get("key1")
        
        backend.set("key1", "value2")
        
        entry = backend._cache["key1"]
        assert entry.hit_count == 0


class TestMemoryBackendIntegration:
    """Integration tests for memory backend."""

    def test_full_workflow_basic(self):
        """Test typical usage workflow."""
        backend = MemoryBackend(max_entries=100)
        
        # Set some values
        backend.set("analyze_module", {"results": "data1"})
        backend.set("analyze_utils", {"results": "data2"})
        
        # Get and verify
        assert backend.get("analyze_module") == {"results": "data1"}
        
        # Check statistics
        stats = backend.get_statistics()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
        assert stats["set_operations"] == 2

    def test_full_workflow_with_expiration(self):
        """Test workflow with TTL expiration."""
        backend = MemoryBackend()
        
        backend.set("cache_key_1", "value1", ttl=1)
        backend.set("cache_key_2", "value2", ttl=300)
        
        # Access before expiration
        assert backend.get("cache_key_1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Access after expiration
        assert backend.get("cache_key_1") is None
        assert backend.get("cache_key_2") == "value2"

    def test_full_workflow_with_invalidation(self):
        """Test workflow with pattern invalidation."""
        backend = MemoryBackend()
        
        backend.set("v1_result_1", "data1")
        backend.set("v1_result_2", "data2")
        backend.set("v2_result_1", "data3")
        
        # Invalidate v1 results
        backend.invalidate("v1_*")
        
        assert backend.get("v1_result_1") is None
        assert backend.get("v2_result_1") == "data3"


__all__ = ["TestMemoryBackendInit", "TestMemoryBackendBasicOps", 
           "TestMemoryBackendTTL", "TestMemoryBackendStatistics"]
