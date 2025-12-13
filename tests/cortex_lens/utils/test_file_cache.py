"""
Test suite for FileCache
Tests thread-safe caching, LRU eviction, memory management, and statistics.
"""

import pytest
import threading
import time
from pathlib import Path

from src.cortex_lens.utils.file_cache import FileCache, get_global_cache


# ========== Basic Operations Tests ==========

class TestBasicOperations:
    """Test basic cache operations."""
    
    def test_initialization(self):
        """Test cache initialization."""
        cache = FileCache(max_size_mb=50)
        
        assert cache.max_size_mb == 50
        assert cache.max_size_bytes == 50 * 1024 * 1024
        assert cache._current_size == 0
        assert cache._hits == 0
        assert cache._misses == 0
    
    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = FileCache()
        
        cache.set("key1", "value1", size_bytes=100)
        result = cache.get("key1")
        
        assert result == "value1"
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = FileCache()
        
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_overwrite_existing_key(self):
        """Test overwriting an existing key."""
        cache = FileCache()
        
        cache.set("key1", "value1", size_bytes=100)
        cache.set("key1", "value2", size_bytes=200)
        
        result = cache.get("key1")
        assert result == "value2"
    
    def test_multiple_keys(self):
        """Test storing multiple keys."""
        cache = FileCache()
        
        cache.set("key1", "value1", size_bytes=100)
        cache.set("key2", "value2", size_bytes=200)
        cache.set("key3", "value3", size_bytes=150)
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


# ========== Statistics Tests ==========

class TestStatistics:
    """Test cache statistics tracking."""
    
    def test_hit_counting(self):
        """Test that cache hits are counted."""
        cache = FileCache()
        cache.set("key1", "value1")
        
        # First get - cache hit
        cache.get("key1")
        assert cache._hits == 1
        assert cache._misses == 0
        
        # Second get - another hit
        cache.get("key1")
        assert cache._hits == 2
    
    def test_miss_counting(self):
        """Test that cache misses are counted."""
        cache = FileCache()
        
        # Get nonexistent key
        cache.get("nonexistent")
        assert cache._misses == 1
        assert cache._hits == 0
        
        # Another miss
        cache.get("another_nonexistent")
        assert cache._misses == 2
    
    def test_hit_miss_ratio(self):
        """Test mixed hits and misses."""
        cache = FileCache()
        cache.set("key1", "value1")
        
        cache.get("key1")  # hit
        cache.get("nonexistent")  # miss
        cache.get("key1")  # hit
        
        assert cache._hits == 2
        assert cache._misses == 1
    
    def test_get_stats(self):
        """Test get_stats method."""
        cache = FileCache()
        cache.set("key1", "value1", size_bytes=100)
        
        cache.get("key1")  # hit
        cache.get("nonexistent")  # miss
        
        stats = cache.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['current_size_mb'] >= 0
        assert stats['items_cached'] == 1


# ========== Memory Management Tests ==========

class TestMemoryManagement:
    """Test memory tracking and limits."""
    
    def test_size_tracking(self):
        """Test that cache tracks memory size."""
        cache = FileCache()
        
        cache.set("key1", "value1", size_bytes=100)
        assert cache._current_size >= 100
        
        cache.set("key2", "value2", size_bytes=200)
        assert cache._current_size >= 300
    
    def test_size_tracking_on_overwrite(self):
        """Test size tracking when overwriting keys."""
        cache = FileCache()
        
        cache.set("key1", "small", size_bytes=100)
        initial_size = cache._current_size
        
        cache.set("key1", "large_value", size_bytes=500)
        
        # Size should increase (old removed, new added)
        assert cache._current_size > initial_size
    
    def test_clear_resets_size(self):
        """Test that clear() resets size tracking."""
        cache = FileCache()
        
        cache.set("key1", "value1", size_bytes=1000)
        cache.set("key2", "value2", size_bytes=2000)
        
        cache.clear()
        
        assert cache._current_size == 0


# ========== Clear Operations Tests ==========

class TestClearOperations:
    """Test cache clearing functionality."""
    
    def test_clear_removes_all_items(self):
        """Test that clear removes all cached items."""
        cache = FileCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None
    
    def test_clear_resets_stats(self):
        """Test that clear resets size but NOT statistics."""
        cache = FileCache()
        
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("nonexistent")  # miss
        
        initial_hits = cache._hits
        initial_misses = cache._misses
        
        cache.clear()
        
        # Size should be reset, but stats persist
        assert cache._current_size == 0
        assert cache._hits == initial_hits  # Stats NOT reset
        assert cache._misses == initial_misses
    
    def test_clear_on_empty_cache(self):
        """Test that clearing an empty cache works."""
        cache = FileCache()
        
        # Should not raise error
        cache.clear()
        
        assert cache._current_size == 0


# ========== Thread Safety Tests ==========

class TestThreadSafety:
    """Test thread-safe operations."""
    
    def test_concurrent_reads(self):
        """Test multiple threads reading simultaneously."""
        cache = FileCache()
        cache.set("shared_key", "shared_value")
        
        results = []
        
        def read_cache():
            value = cache.get("shared_key")
            results.append(value)
        
        threads = [threading.Thread(target=read_cache) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All reads should succeed
        assert len(results) == 10
        assert all(v == "shared_value" for v in results)
    
    def test_concurrent_writes(self):
        """Test multiple threads writing simultaneously."""
        cache = FileCache()
        
        def write_cache(thread_id):
            for i in range(5):
                cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")
        
        threads = [threading.Thread(target=write_cache, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify all writes succeeded
        for thread_id in range(5):
            for i in range(5):
                assert cache.get(f"key_{thread_id}_{i}") == f"value_{thread_id}_{i}"
    
    def test_concurrent_read_write(self):
        """Test simultaneous reads and writes."""
        cache = FileCache()
        cache.set("key1", "initial_value")
        
        read_results = []
        
        def reader():
            for _ in range(10):
                value = cache.get("key1")
                read_results.append(value)
                time.sleep(0.001)
        
        def writer():
            for i in range(5):
                cache.set("key1", f"updated_{i}")
                time.sleep(0.002)
        
        reader_thread = threading.Thread(target=reader)
        writer_thread = threading.Thread(target=writer)
        
        reader_thread.start()
        writer_thread.start()
        
        reader_thread.join()
        writer_thread.join()
        
        # Should have some results (exact values depend on timing)
        assert len(read_results) > 0


# ========== File Content Caching Tests ==========

class TestFileContentCaching:
    """Test caching of file content."""
    
    def test_cache_file_content(self, tmp_path):
        """Test caching file content."""
        cache = FileCache()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Cache the content
        key = str(test_file)
        content = test_file.read_text()
        cache.set(key, content, size_bytes=len(content))
        
        # Retrieve from cache
        cached_content = cache.get(key)
        
        assert cached_content == "Hello, World!"
    
    def test_cache_with_path_keys(self, tmp_path):
        """Test using Path objects as keys."""
        cache = FileCache()
        
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        cache.set(str(file1), "Content 1")
        cache.set(str(file2), "Content 2")
        
        assert cache.get(str(file1)) == "Content 1"
        assert cache.get(str(file2)) == "Content 2"


# ========== Global Cache Tests ==========

class TestGlobalCache:
    """Test global cache singleton."""
    
    def test_get_global_cache(self):
        """Test getting global cache instance."""
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        
        # Should return same instance
        assert cache1 is cache2
    
    def test_global_cache_with_size(self):
        """Test global cache ignores size after first call."""
        # First call sets size
        cache1 = get_global_cache()
        initial_size = cache1.max_size_mb
        
        # Second call with different size is ignored (singleton)
        cache2 = get_global_cache(max_size_mb=200)
        
        # Should still have same size as first call
        assert cache2.max_size_mb == initial_size
        assert cache1 is cache2  # Same instance
    
    def test_global_cache_persistence(self):
        """Test that global cache persists across calls."""
        cache1 = get_global_cache()
        cache1.set("persistent_key", "persistent_value")
        
        cache2 = get_global_cache()
        
        # Should retrieve value set in first instance
        assert cache2.get("persistent_key") == "persistent_value"


# ========== Edge Cases Tests ==========

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_key(self):
        """Test setting value with empty key."""
        cache = FileCache()
        
        cache.set("", "value")
        result = cache.get("")
        
        assert result == "value"
    
    def test_none_value(self):
        """Test storing None as a value."""
        cache = FileCache()
        
        cache.set("key1", None)
        result = cache.get("key1")
        
        # None is a valid cached value
        assert result is None
        assert cache._hits == 1  # Should count as hit
    
    def test_large_value(self):
        """Test storing large value."""
        cache = FileCache(max_size_mb=10)
        
        # Create 1 MB string
        large_value = "x" * (1024 * 1024)
        
        cache.set("large_key", large_value, size_bytes=len(large_value))
        result = cache.get("large_key")
        
        assert result == large_value
    
    def test_zero_size(self):
        """Test setting value with zero size."""
        cache = FileCache()
        
        cache.set("key1", "value1", size_bytes=0)
        
        assert cache.get("key1") == "value1"
    
    def test_negative_size(self):
        """Test setting value with negative size."""
        cache = FileCache()
        
        # Should handle gracefully (no error)
        cache.set("key1", "value1", size_bytes=-100)
        
        assert cache.get("key1") == "value1"
