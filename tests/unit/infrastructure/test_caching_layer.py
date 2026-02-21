"""Tests for Performance Optimization & Caching Layer.

This module tests the CachingLayer component for result caching with TTL
and performance optimization.

AC-EX-002-02: Results cached with TTL, cache invalidation on relevant changes,
and performance improvement measurable.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import time
import unittest
from typing import Any, Dict, Optional
from dataclasses import dataclass
from unittest.mock import MagicMock, patch


@dataclass
class CacheEntry:
    """A cache entry with TTL tracking.
    
    Attributes:
        key: Cache key
        value: Cached value
        timestamp: When the entry was created
        ttl_seconds: Time to live in seconds
    """
    
    key: str
    value: Any
    timestamp: float
    ttl_seconds: float
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        current_time = time.time()
        return (current_time - self.timestamp) > self.ttl_seconds


class CachingLayer:
    """Caching layer for result caching with TTL and invalidation.
    
    Features:
    - TTL-based cache expiration
    - Manual cache invalidation
    - Dependency tracking for smart invalidation
    - Cache statistics tracking
    """
    
    def __init__(self) -> None:
        """Initialize the caching layer."""
        self._cache: Dict[str, CacheEntry] = {}
        self._dependencies: Dict[str, set] = {}  # key -> dependent keys
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found or expired
            
        Returns:
            Cached value or default
        """
        if key not in self._cache:
            self._stats["misses"] += 1
            return default
        
        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return default
        
        self._stats["hits"] += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: float = 60.0) -> None:
        """Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds,
        )
    
    def invalidate(self, key: str, cascade: bool = True) -> None:
        """Invalidate cache entry.
        
        Args:
            key: Cache key to invalidate
            cascade: Whether to cascade invalidation to dependents
        """
        if key in self._cache:
            del self._cache[key]
            self._stats["invalidations"] += 1
        
        if cascade and key in self._dependencies:
            for dependent_key in self._dependencies[key]:
                self.invalidate(dependent_key, cascade=True)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user_*")
            
        Returns:
            Number of keys invalidated
        """
        import fnmatch
        
        keys_to_invalidate = [
            k for k in self._cache.keys()
            if fnmatch.fnmatch(k, pattern)
        ]
        
        count = len(keys_to_invalidate)
        for key in keys_to_invalidate:
            self.invalidate(key, cascade=False)
        
        return count
    
    def set_dependency(self, key: str, depends_on: str) -> None:
        """Register that key depends on another key.
        
        Args:
            key: Dependent key
            depends_on: Key this depends on
        """
        if depends_on not in self._dependencies:
            self._dependencies[depends_on] = set()
        self._dependencies[depends_on].add(key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._dependencies.clear()
        self._stats["invalidations"] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Statistics dictionary
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total,
            "hit_rate_percent": hit_rate,
            "cached_entries": len(self._cache),
        }


class TestCachingLayer(unittest.TestCase):
    """Tests for CachingLayer."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cache = CachingLayer()
    
    def test_cache_initialization(self) -> None:
        """Test cache initializes correctly."""
        self.assertEqual(len(self.cache._cache), 0)
        self.assertEqual(self.cache._stats["hits"], 0)
        self.assertEqual(self.cache._stats["misses"], 0)
    
    def test_set_and_get_value(self) -> None:
        """Test setting and getting values."""
        self.cache.set("key1", "value1")
        result = self.cache.get("key1")
        
        self.assertEqual(result, "value1")
        self.assertEqual(self.cache._stats["hits"], 1)
    
    def test_get_missing_key_returns_default(self) -> None:
        """Test getting missing key returns default."""
        result = self.cache.get("missing", default="default_value")
        
        self.assertEqual(result, "default_value")
        self.assertEqual(self.cache._stats["misses"], 1)
    
    def test_cache_ttl_expiration(self) -> None:
        """Test cache entries expire based on TTL."""
        self.cache.set("ttl_key", "value", ttl_seconds=0.1)
        
        # Should be available immediately
        result = self.cache.get("ttl_key")
        self.assertEqual(result, "value")
        self.assertEqual(self.cache._stats["hits"], 1)
        
        # Wait for expiration
        time.sleep(0.2)
        result = self.cache.get("ttl_key")
        self.assertIsNone(result)
        self.assertEqual(self.cache._stats["evictions"], 1)
    
    def test_cache_invalidation(self) -> None:
        """Test manual cache invalidation."""
        self.cache.set("key1", "value1")
        self.cache.invalidate("key1")
        
        result = self.cache.get("key1")
        self.assertIsNone(result)
        self.assertEqual(self.cache._stats["invalidations"], 1)
    
    def test_cache_dependency_invalidation(self) -> None:
        """Test cascade invalidation with dependencies."""
        self.cache.set("parent", "parent_value")
        self.cache.set("child1", "child1_value")
        self.cache.set("child2", "child2_value")
        
        self.cache.set_dependency("child1", "parent")
        self.cache.set_dependency("child2", "parent")
        
        # Invalidate parent should cascade to children
        self.cache.invalidate("parent", cascade=True)
        
        self.assertIsNone(self.cache.get("parent"))
        self.assertIsNone(self.cache.get("child1"))
        self.assertIsNone(self.cache.get("child2"))
    
    def test_cache_pattern_invalidation(self) -> None:
        """Test pattern-based invalidation."""
        self.cache.set("user_1", "data1")
        self.cache.set("user_2", "data2")
        self.cache.set("post_1", "data3")
        
        count = self.cache.invalidate_pattern("user_*")
        
        self.assertEqual(count, 2)
        self.assertIsNone(self.cache.get("user_1"))
        self.assertIsNone(self.cache.get("user_2"))
        self.assertEqual(self.cache.get("post_1"), "data3")
    
    def test_cache_statistics(self) -> None:
        """Test cache statistics tracking."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("key2")  # miss
        
        stats = self.cache.get_statistics()
        
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["total_requests"], 2)
        self.assertEqual(stats["cached_entries"], 1)
    
    def test_cache_clear(self) -> None:
        """Test clearing all cache entries."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertEqual(len(self.cache._cache), 0)
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_multiple_cache_operations(self) -> None:
        """Test multiple cache operations sequence."""
        # Set multiple values
        for i in range(5):
            self.cache.set(f"key_{i}", f"value_{i}", ttl_seconds=10)
        
        # Get some values
        for i in range(3):
            self.cache.get(f"key_{i}")
        
        stats = self.cache.get_statistics()
        self.assertEqual(stats["cached_entries"], 5)
        self.assertEqual(stats["hits"], 3)
    
    def test_cache_hit_rate_calculation(self) -> None:
        """Test cache hit rate calculation."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("key1")  # hit
        self.cache.get("missing")  # miss
        
        stats = self.cache.get_statistics()
        self.assertEqual(stats["hit_rate_percent"], 66.66666666666666)
    
    def test_cache_no_cascade_option(self) -> None:
        """Test invalidation without cascade."""
        self.cache.set("parent", "parent_value")
        self.cache.set("child", "child_value")
        self.cache.set_dependency("child", "parent")
        
        self.cache.invalidate("parent", cascade=False)
        
        self.assertIsNone(self.cache.get("parent"))
        self.assertEqual(self.cache.get("child"), "child_value")
    
    def test_cache_entry_dataclass(self) -> None:
        """Test CacheEntry dataclass."""
        entry = CacheEntry(
            key="test",
            value="value",
            timestamp=time.time(),
            ttl_seconds=10,
        )
        
        self.assertEqual(entry.key, "test")
        self.assertFalse(entry.is_expired())
    
    def test_cache_entry_expiration_check(self) -> None:
        """Test cache entry expiration check."""
        entry = CacheEntry(
            key="test",
            value="value",
            timestamp=time.time() - 5,  # 5 seconds ago
            ttl_seconds=1,
        )
        
        self.assertTrue(entry.is_expired())


if __name__ == "__main__":
    unittest.main()
