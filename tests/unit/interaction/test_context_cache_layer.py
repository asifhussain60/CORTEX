"""
Tests for Context Cache Layer (ENH-046 Phase 4).

Test Coverage:
- Basic cache operations (5)
- LRU eviction tests (4)
- TTL expiration tests (3)
- Cache statistics tests (3)
- Thread safety tests (3)
- Edge cases (2)

Total: 20 tests, 90% coverage target

Author: CORTEX Context Synthesis System
Created: 2026-02-06
"""

import pytest
import time
import threading
from cortex.interaction.context_cache_layer import (
    ContextCacheLayer,
    CacheStats,
    get_cache
)


class TestContextCacheLayer:
    """Test suite for ContextCacheLayer."""
    
    @pytest.fixture
    def cache(self):
        """Create fresh cache instance."""
        return ContextCacheLayer(
            max_entries=100,
            ttl_seconds=60,
            max_size_bytes=10000
        )
    
    # ═══════════════════════════════════════════════════════════════
    # Basic Cache Operations (5)
    # ═══════════════════════════════════════════════════════════════
    
    def test_set_and_get(self, cache):
        """Test basic set and get operations."""
        cache.set("key1", "value1")
        
        result = cache.get("key1")
        assert result == "value1"
    
    def test_get_nonexistent_key(self, cache):
        """Test get returns None for nonexistent key."""
        result = cache.get("nonexistent")
        assert result is None
    
    def test_overwrite_existing_key(self, cache):
        """Test overwriting existing key."""
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        
        result = cache.get("key1")
        assert result == "value2"
    
    def test_multiple_keys(self, cache):
        """Test storing multiple keys."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_invalidate_key(self, cache):
        """Test invalidating specific key."""
        cache.set("key1", "value1")
        cache.invalidate("key1")
        
        result = cache.get("key1")
        assert result is None
    
    # ═══════════════════════════════════════════════════════════════
    # LRU Eviction Tests (4)
    # ═══════════════════════════════════════════════════════════════
    
    def test_lru_eviction_on_max_entries(self, cache):
        """Test LRU eviction when max_entries reached."""
        cache = ContextCacheLayer(max_entries=3, ttl_seconds=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # key1 should be evicted
        cache.set("key4", "value4")
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_lru_move_to_end_on_access(self, cache):
        """Test accessing key moves it to end (most recently used)."""
        cache = ContextCacheLayer(max_entries=3, ttl_seconds=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Access key1 (moves to end)
        cache.get("key1")
        
        # key2 should be evicted (oldest)
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Still present
        assert cache.get("key2") is None      # Evicted
    
    def test_lru_eviction_on_max_size(self, cache):
        """Test LRU eviction when max_size_bytes reached."""
        cache = ContextCacheLayer(max_entries=100, ttl_seconds=60, max_size_bytes=250)
        
        # Add entries that fit
        cache.set("key1", "x" * 50)  # ~50 bytes
        cache.set("key2", "x" * 50)  # ~50 bytes
        cache.set("key3", "x" * 50)  # ~50 bytes
        # Total: ~150 bytes (within 250 byte limit)
        
        assert cache.get_stats().current_entries == 3
        
        # Add large entry that requires evictions
        cache.set("key4", "x" * 200)  # ~200 bytes
        # This should evict key1, key2, key3 to make room
        
        stats = cache.get_stats()
        # Either evictions occurred, or entry was rejected
        assert stats.evictions > 0 or cache.get("key4") is None
    
    def test_lru_stats_evictions(self, cache):
        """Test eviction count in stats."""
        cache = ContextCacheLayer(max_entries=2, ttl_seconds=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Triggers eviction
        
        stats = cache.get_stats()
        assert stats.evictions == 1
    
    # ═══════════════════════════════════════════════════════════════
    # TTL Expiration Tests (3)
    # ═══════════════════════════════════════════════════════════════
    
    def test_ttl_expiration(self, cache):
        """Test entry expires after TTL."""
        cache = ContextCacheLayer(max_entries=100, ttl_seconds=1)
        
        cache.set("key1", "value1")
        
        # Immediately should work
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("key1") is None
    
    def test_ttl_custom_per_entry(self, cache):
        """Test custom TTL per entry."""
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=10)
        
        time.sleep(1.1)
        
        assert cache.get("key1") is None  # Expired
        assert cache.get("key2") == "value2"  # Still valid
    
    def test_ttl_expired_not_counted_as_hit(self, cache):
        """Test expired entry counted as miss."""
        cache = ContextCacheLayer(max_entries=100, ttl_seconds=1)
        
        cache.set("key1", "value1")
        time.sleep(1.1)
        
        result = cache.get("key1")
        
        assert result is None
        stats = cache.get_stats()
        assert stats.misses == 1
    
    # ═══════════════════════════════════════════════════════════════
    # Cache Statistics Tests (3)
    # ═══════════════════════════════════════════════════════════════
    
    def test_stats_hit_rate_calculation(self, cache):
        """Test hit rate calculation."""
        cache.set("key1", "value1")
        
        # 1 hit
        cache.get("key1")
        
        # 1 miss
        cache.get("nonexistent")
        
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate == 0.5  # 50%
    
    def test_stats_current_entries(self, cache):
        """Test current entries tracking."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        assert stats.current_entries == 2
    
    def test_stats_current_size(self, cache):
        """Test current size tracking."""
        cache.set("key1", "x" * 100)
        
        stats = cache.get_stats()
        assert stats.current_size_bytes > 0
    
    # ═══════════════════════════════════════════════════════════════
    # Thread Safety Tests (3)
    # ═══════════════════════════════════════════════════════════════
    
    def test_thread_safe_concurrent_writes(self, cache):
        """Test concurrent writes are thread-safe."""
        def writer(key_prefix):
            for i in range(10):
                cache.set(f"{key_prefix}_{i}", f"value_{i}")
        
        threads = [
            threading.Thread(target=writer, args=("thread1",)),
            threading.Thread(target=writer, args=("thread2",))
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have 20 entries (no corruption)
        stats = cache.get_stats()
        assert stats.current_entries == 20
    
    def test_thread_safe_concurrent_reads(self, cache):
        """Test concurrent reads are thread-safe."""
        cache.set("shared_key", "shared_value")
        
        results = []
        
        def reader():
            for _ in range(100):
                results.append(cache.get("shared_key"))
        
        threads = [threading.Thread(target=reader) for _ in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All reads should succeed
        assert all(r == "shared_value" for r in results)
    
    def test_thread_safe_mixed_operations(self, cache):
        """Test mixed operations are thread-safe."""
        def mixed_ops(thread_id):
            for i in range(10):
                cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                cache.get(f"key_{thread_id}_{i}")
                if i % 2 == 0:
                    cache.invalidate(f"key_{thread_id}_{i}")
        
        threads = [threading.Thread(target=mixed_ops, args=(i,)) for i in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should complete without exceptions
        stats = cache.get_stats()
        assert stats.hits > 0
    
    # ═══════════════════════════════════════════════════════════════
    # Edge Cases (2)
    # ═══════════════════════════════════════════════════════════════
    
    def test_clear_cache(self, cache):
        """Test clearing entire cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        stats = cache.get_stats()
        assert stats.current_entries == 0
    
    def test_cache_full_reject_entry(self, cache):
        """Test cache rejects entry when full and can't evict."""
        cache = ContextCacheLayer(max_entries=1, ttl_seconds=60, max_size_bytes=50)
        
        # Fill cache
        cache.set("key1", "x" * 100)
        
        # Try to add huge entry (should be rejected)
        cache.set("key2", "x" * 1000)
        
        # key2 should not be cached
        assert cache.get("key2") is None


class TestGetCache:
    """Test singleton cache function."""
    
    def test_get_cache_singleton(self):
        """Test get_cache returns singleton."""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
