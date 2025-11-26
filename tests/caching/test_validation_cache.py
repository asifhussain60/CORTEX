"""
Test suite for ValidationCache class.

Tests cache operations, file hash tracking, TTL expiration, cross-operation
result sharing, and statistics tracking.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
import json

from src.caching.validation_cache import ValidationCache, CacheEntry


@pytest.fixture
def temp_cache_db():
    """Create temporary cache database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def cache(temp_cache_db):
    """Create ValidationCache instance with temporary database."""
    return ValidationCache(str(temp_cache_db))


@pytest.fixture
def temp_files():
    """Create temporary files for file hash testing."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Create test files
    file1 = temp_path / "test1.py"
    file2 = temp_path / "test2.py"
    file1.write_text("def test1(): pass")
    file2.write_text("def test2(): pass")
    
    yield [str(file1), str(file2)]
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


class TestCacheBasicOperations:
    """Test basic cache operations (get, set, invalidate)."""
    
    def test_set_and_get(self, cache):
        """Test setting and retrieving cache entry."""
        result = {"status": "success", "data": [1, 2, 3]}
        
        cache.set("test_op", "key1", result)
        cached = cache.get("test_op", "key1")
        
        assert cached is not None
        assert cached == result
    
    def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key returns None."""
        result = cache.get("test_op", "nonexistent")
        assert result is None
    
    def test_invalidate_specific_key(self, cache):
        """Test invalidating specific cache key."""
        cache.set("test_op", "key1", {"data": "value1"})
        cache.set("test_op", "key2", {"data": "value2"})
        
        cache.invalidate("test_op", "key1")
        
        assert cache.get("test_op", "key1") is None
        assert cache.get("test_op", "key2") is not None
    
    def test_invalidate_all_operation_keys(self, cache):
        """Test invalidating all keys for operation."""
        cache.set("test_op", "key1", {"data": "value1"})
        cache.set("test_op", "key2", {"data": "value2"})
        cache.set("other_op", "key3", {"data": "value3"})
        
        cache.invalidate("test_op")
        
        assert cache.get("test_op", "key1") is None
        assert cache.get("test_op", "key2") is None
        assert cache.get("other_op", "key3") is not None


class TestFileHashTracking:
    """Test file hash tracking for automatic invalidation."""
    
    def test_cache_with_file_tracking(self, cache, temp_files):
        """Test caching with file hash tracking."""
        result = {"status": "valid"}
        
        cache.set("test_op", "key1", result, files=temp_files)
        cached = cache.get("test_op", "key1", files=temp_files)
        
        assert cached == result
    
    def test_invalidation_on_file_change(self, cache, temp_files):
        """Test automatic invalidation when tracked file changes."""
        result = {"status": "valid"}
        
        # Cache with file tracking
        cache.set("test_op", "key1", result, files=temp_files)
        
        # Modify tracked file
        Path(temp_files[0]).write_text("def test1(): return 42")
        
        # Should return None due to file change
        cached = cache.get("test_op", "key1", files=temp_files)
        assert cached is None
    
    def test_cache_valid_when_files_unchanged(self, cache, temp_files):
        """Test cache remains valid when files unchanged."""
        result = {"status": "valid"}
        
        cache.set("test_op", "key1", result, files=temp_files)
        
        # Multiple gets without file changes
        for _ in range(5):
            cached = cache.get("test_op", "key1", files=temp_files)
            assert cached == result
    
    def test_missing_file_invalidates_cache(self, cache, temp_files):
        """Test cache invalidated if tracked file is deleted."""
        result = {"status": "valid"}
        
        cache.set("test_op", "key1", result, files=temp_files)
        
        # Delete tracked file
        Path(temp_files[0]).unlink()
        
        cached = cache.get("test_op", "key1", files=temp_files)
        assert cached is None


class TestTTLExpiration:
    """Test time-to-live expiration."""
    
    def test_ttl_zero_never_expires(self, cache):
        """Test TTL=0 means infinite (never expires)."""
        cache.set("test_op", "key1", {"data": "immortal"}, ttl_seconds=0)
        
        # Should still be valid after time passes
        time.sleep(0.1)
        cached = cache.get("test_op", "key1")
        assert cached is not None
    
    def test_ttl_expiration(self, cache):
        """Test entry expires after TTL."""
        cache.set("test_op", "key1", {"data": "temporary"}, ttl_seconds=1)
        
        # Should be valid immediately
        cached = cache.get("test_op", "key1")
        assert cached is not None
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired
        cached = cache.get("test_op", "key1")
        assert cached is None
    
    def test_different_ttls_per_operation(self, cache):
        """Test different TTLs for different operations."""
        cache.set("fast_op", "key1", {"data": "expires fast"}, ttl_seconds=1)
        cache.set("slow_op", "key2", {"data": "expires slow"}, ttl_seconds=10)
        
        time.sleep(1.5)
        
        assert cache.get("fast_op", "key1") is None
        assert cache.get("slow_op", "key2") is not None


class TestCrossOperationSharing:
    """Test cross-operation result sharing."""
    
    def test_share_result_creates_entries(self, cache):
        """Test share_result creates cache entries for target operation."""
        result = {"orchestrators": ["OrchestratorA", "OrchestratorB"]}
        files = ["src/operations/test.py"]
        
        cache.set("align", "orchestrators", result, files=files)
        cache.share_result("align", "deploy", "orchestrators")  # (source_op, target_op, key)
        
        # Should be available in deploy namespace
        cached = cache.get("deploy", "orchestrators", files=files)
        assert cached == result
    
    def test_share_result_preserves_file_tracking(self, cache, temp_files):
        """Test shared result maintains file hash tracking."""
        result = {"data": "shared"}
        
        cache.set("align", "key1", result, files=temp_files)
        cache.share_result("align", "deploy", "key1")  # (source_op, target_op, key)
        
        # Modify file
        Path(temp_files[0]).write_text("changed content")
        
        # Both operations should be invalidated
        assert cache.get("align", "key1", files=temp_files) is None
        assert cache.get("deploy", "key1", files=temp_files) is None
    
    def test_share_multiple_results(self, cache):
        """Test sharing multiple results from one operation to another."""
        results = {
            "orchestrators": ["OrchestratorA"],
            "agents": ["AgentA", "AgentB"],
            "scores": {"FeatureA": 85, "FeatureB": 92}
        }
        
        # Cache all results in align
        for key, result in results.items():
            cache.set("align", key, result)
            cache.share_result("align", "deploy", key)  # (source_op, target_op, key)
        
        # All should be available in deploy
        for key, expected in results.items():
            assert cache.get("deploy", key) == expected


class TestStatisticsTracking:
    """Test cache statistics and metrics."""
    
    def test_stats_track_hits(self, cache):
        """Test statistics track cache hits."""
        cache.set("test_op", "key1", {"data": "value"})
        
        # Generate hits
        for _ in range(5):
            cache.get("test_op", "key1")
        
        stats = cache.get_stats("test_op")
        assert stats["hits"] == 5
    
    def test_stats_track_misses(self, cache):
        """Test statistics track cache misses."""
        # Generate misses
        for i in range(3):
            cache.get("test_op", f"nonexistent_{i}")
        
        stats = cache.get_stats("test_op")
        assert stats["misses"] == 3
    
    def test_stats_track_invalidations(self, cache):
        """Test statistics track invalidations."""
        cache.set("test_op", "key1", {"data": "value"})
        cache.set("test_op", "key2", {"data": "value"})
        
        cache.invalidate("test_op", "key1")
        cache.invalidate("test_op")
        
        stats = cache.get_stats("test_op")
        assert stats["invalidations"] == 2
    
    def test_stats_calculate_hit_rate(self, cache):
        """Test statistics calculate hit rate correctly."""
        cache.set("test_op", "key1", {"data": "value"})
        
        # 7 hits, 3 misses = 70% hit rate
        for _ in range(7):
            cache.get("test_op", "key1")
        for i in range(3):
            cache.get("test_op", f"miss_{i}")
        
        stats = cache.get_stats("test_op")
        assert stats["hit_rate"] == 0.7


class TestCacheKeyListing:
    """Test cache key listing functionality."""
    
    def test_get_all_keys_empty(self, cache):
        """Test get_all_keys returns empty list when cache empty."""
        keys = cache.get_all_keys("test_op")
        assert keys == []
    
    def test_get_all_keys_single_operation(self, cache):
        """Test get_all_keys lists keys for operation."""
        cache.set("test_op", "key1", {"data": "value1"})
        cache.set("test_op", "key2", {"data": "value2"})
        cache.set("other_op", "key3", {"data": "value3"})
        
        keys = cache.get_all_keys("test_op")
        assert sorted(keys) == ["key1", "key2"]
    
    def test_get_all_keys_excludes_expired(self, cache):
        """Test get_all_keys excludes expired entries."""
        cache.set("test_op", "key1", {"data": "value1"}, ttl_seconds=1)
        cache.set("test_op", "key2", {"data": "value2"}, ttl_seconds=0)
        
        time.sleep(1.5)
        
        keys = cache.get_all_keys("test_op")
        assert keys == ["key2"]


class TestConcurrency:
    """Test cache behavior under concurrent access."""
    
    def test_multiple_operations_isolated(self, cache):
        """Test operations don't interfere with each other."""
        operations = ["align", "deploy", "optimize", "cleanup"]
        
        # Set different data for same key across operations
        for op in operations:
            cache.set(op, "config", {"operation": op})
        
        # Each should retrieve its own data
        for op in operations:
            cached = cache.get(op, "config")
            assert cached == {"operation": op}
    
    def test_sequential_updates(self, cache):
        """Test sequential updates to same key."""
        values = [{"version": i} for i in range(10)]
        
        for value in values:
            cache.set("test_op", "key1", value)
        
        # Should have latest value
        cached = cache.get("test_op", "key1")
        assert cached == {"version": 9}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
