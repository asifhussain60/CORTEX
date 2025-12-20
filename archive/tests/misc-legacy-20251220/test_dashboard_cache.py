"""
Tests for Dashboard Cache Infrastructure

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0

Tests:
- Cache storage and retrieval
- TTL expiration
- LRU eviction
- Cache statistics
- Decorator functionality
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.dashboard.infrastructure.dashboard_cache import (
    DashboardCache,
    DashboardCacheEntry,
    cached,
    get_cache,
    invalidate_dashboard_cache
)


class TestDashboardCacheEntry:
    """Tests for DashboardCacheEntry dataclass."""
    
    def test_is_expired_returns_false_for_fresh_entry(self):
        """Test that fresh entries are not expired."""
        now = datetime.now()
        expires = now + timedelta(hours=1)
        entry = DashboardCacheEntry(
            key="test",
            value="data",
            created_at=now,
            expires_at=expires
        )
        
        assert not entry.is_expired()
    
    def test_is_expired_returns_true_for_expired_entry(self):
        """Test that expired entries are detected."""
        now = datetime.now()
        expires = now - timedelta(hours=1)  # Expired 1 hour ago
        entry = DashboardCacheEntry(
            key="test",
            value="data",
            created_at=now - timedelta(hours=2),
            expires_at=expires
        )
        
        assert entry.is_expired()
    
    def test_update_access_increments_hit_count(self):
        """Test that update_access increments hit count."""
        entry = DashboardCacheEntry(
            key="test",
            value="data",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        assert entry.hit_count == 0
        entry.update_access()
        assert entry.hit_count == 1
        entry.update_access()
        assert entry.hit_count == 2


class TestDashboardCache:
    """Tests for DashboardCache class."""
    
    @pytest.fixture
    def cache(self):
        """Create a fresh cache instance for each test."""
        return DashboardCache(
            default_ttl_hours=1,
            max_memory_mb=1.0,  # 1MB for tests
            enable_persistence=False
        )
    
    def test_cache_initialization(self, cache):
        """Test cache initializes with correct defaults."""
        assert cache.default_ttl_hours == 1
        assert cache.max_memory_bytes == 1024 * 1024
        assert len(cache._cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0
    
    def test_set_and_get_value(self, cache):
        """Test storing and retrieving value from cache."""
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        
        assert result == "test_value"
        assert cache._hits == 1
        assert cache._misses == 0
    
    def test_get_nonexistent_key_returns_none(self, cache):
        """Test that getting non-existent key returns None."""
        result = cache.get("nonexistent")
        
        assert result is None
        assert cache._misses == 1
    
    def test_get_expired_entry_returns_none(self, cache):
        """Test that expired entries return None."""
        # Set with very short TTL
        cache.set("test_key", "test_value", ttl_hours=0.001)  # ~3.6 seconds
        
        # Wait for expiration
        time.sleep(4)
        
        result = cache.get("test_key")
        assert result is None
        assert cache._misses == 1
    
    def test_invalidate_removes_entry(self, cache):
        """Test that invalidate removes cache entry."""
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        removed = cache.invalidate("test_key")
        assert removed is True
        assert cache.get("test_key") is None
    
    def test_invalidate_nonexistent_key_returns_false(self, cache):
        """Test that invalidating non-existent key returns False."""
        removed = cache.invalidate("nonexistent")
        assert removed is False
    
    def test_invalidate_pattern_removes_matching_entries(self, cache):
        """Test that invalidate_pattern removes all matching entries."""
        cache.set("project_1_overview", "data1")
        cache.set("project_1_quality", "data2")
        cache.set("project_2_overview", "data3")
        
        count = cache.invalidate_pattern("project_1")
        
        assert count == 2
        assert cache.get("project_1_overview") is None
        assert cache.get("project_1_quality") is None
        assert cache.get("project_2_overview") == "data3"
    
    def test_clear_removes_all_entries(self, cache):
        """Test that clear removes all cache entries."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        cache.clear()
        
        assert len(cache._cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_get_stats_returns_correct_metrics(self, cache):
        """Test that get_stats returns accurate statistics."""
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5
        assert stats['total_entries'] == 1
        assert stats['memory_usage_mb'] > 0
    
    def test_lru_eviction_on_memory_limit(self, cache):
        """Test that LRU eviction occurs when memory limit reached."""
        # Fill cache with large values
        large_value = "x" * 500000  # 500KB
        
        cache.set("key1", large_value)
        cache.set("key2", large_value)
        cache.set("key3", large_value)  # This should trigger eviction of key1
        
        # key1 should be evicted (least recently used)
        assert cache.get("key1") is None
        # key2 and key3 should still be there
        assert cache.get("key2") == large_value
        assert cache.get("key3") == large_value
        assert cache._evictions > 0
    
    def test_cleanup_expired_removes_only_expired(self, cache):
        """Test that cleanup_expired removes only expired entries."""
        cache.set("fresh", "value1", ttl_hours=1)
        cache.set("expired", "value2", ttl_hours=0.001)  # ~3.6 seconds
        
        time.sleep(4)
        
        removed = cache.cleanup_expired()
        
        assert removed == 1
        assert cache.get("fresh") == "value1"
        assert cache.get("expired") is None
    
    def test_generate_key_creates_deterministic_keys(self, cache):
        """Test that generate_key creates consistent keys for same args."""
        key1 = cache.generate_key("func", "arg1", kwarg1="value1")
        key2 = cache.generate_key("func", "arg1", kwarg1="value1")
        key3 = cache.generate_key("func", "arg2", kwarg1="value1")
        
        assert key1 == key2  # Same args = same key
        assert key1 != key3  # Different args = different key
        assert key1.startswith("func:")


class TestCachedDecorator:
    """Tests for @cached decorator."""
    
    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear cache before each test."""
        get_cache().clear()
        yield
        get_cache().clear()
    
    def test_cached_decorator_caches_result(self):
        """Test that @cached decorator caches function results."""
        call_count = 0
        
        @cached(ttl_hours=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Function only called once
    
    def test_cached_decorator_respects_different_args(self):
        """Test that @cached decorator caches separately for different args."""
        call_count = 0
        
        @cached(ttl_hours=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(10)
        
        assert result1 == 10
        assert result2 == 20
        assert call_count == 2  # Function called twice (different args)
    
    def test_cached_decorator_custom_key_prefix(self):
        """Test that @cached decorator uses custom key prefix."""
        @cached(ttl_hours=1, key_prefix="custom")
        def my_function():
            return "result"
        
        result = my_function()
        stats = get_cache().get_stats()
        
        assert result == "result"
        assert stats['total_entries'] == 1
        
        # Check that key starts with custom prefix
        keys = list(get_cache()._cache.keys())
        assert any(k.startswith("custom:") for k in keys)
    
    def test_cached_decorator_respects_ttl(self):
        """Test that @cached decorator respects TTL."""
        @cached(ttl_hours=0.001)  # Very short TTL
        def my_function():
            return "result"
        
        result1 = my_function()
        time.sleep(4)  # Wait for expiration
        result2 = my_function()
        
        assert result1 == "result"
        assert result2 == "result"
        
        # Cache should have one miss after expiration
        stats = get_cache().get_stats()
        assert stats['misses'] >= 1


class TestCacheHelpers:
    """Tests for cache helper functions."""
    
    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear cache before each test."""
        get_cache().clear()
        yield
        get_cache().clear()
    
    def test_get_cache_returns_global_instance(self):
        """Test that get_cache returns global cache instance."""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
    
    def test_invalidate_dashboard_cache_with_project_id(self):
        """Test invalidating cache for specific project."""
        cache = get_cache()
        cache.set("project_123_overview", "data1")
        cache.set("project_123_quality", "data2")
        cache.set("project_456_overview", "data3")
        
        invalidate_dashboard_cache(project_id="project_123")
        
        assert cache.get("project_123_overview") is None
        assert cache.get("project_123_quality") is None
        assert cache.get("project_456_overview") == "data3"
    
    def test_invalidate_dashboard_cache_all_projects(self):
        """Test invalidating cache for all projects."""
        cache = get_cache()
        cache.set("project_123_overview", "data1")
        cache.set("project_456_overview", "data2")
        
        invalidate_dashboard_cache()
        
        assert len(cache._cache) == 0


class TestCachePerformance:
    """Performance tests for cache operations."""
    
    @pytest.fixture
    def cache(self):
        """Create cache with larger memory limit for performance tests."""
        return DashboardCache(
            default_ttl_hours=24,
            max_memory_mb=10.0,
            enable_persistence=False
        )
    
    def test_cache_lookup_performance(self, cache):
        """Test that cache lookup is fast (<5ms)."""
        # Populate cache
        for i in range(100):
            cache.set(f"key_{i}", {"data": f"value_{i}"})
        
        # Time lookups
        start = time.perf_counter()
        for i in range(100):
            cache.get(f"key_{i}")
        end = time.perf_counter()
        
        avg_lookup_ms = ((end - start) / 100) * 1000
        
        assert avg_lookup_ms < 5.0, f"Average lookup time {avg_lookup_ms:.2f}ms exceeds 5ms target"
    
    def test_cache_set_performance(self, cache):
        """Test that cache set operations are fast (<10ms)."""
        start = time.perf_counter()
        for i in range(100):
            cache.set(f"key_{i}", {"data": f"value_{i}"})
        end = time.perf_counter()
        
        avg_set_ms = ((end - start) / 100) * 1000
        
        assert avg_set_ms < 10.0, f"Average set time {avg_set_ms:.2f}ms exceeds 10ms target"
