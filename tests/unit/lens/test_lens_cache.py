"""
Tests for LENS caching layer (ENH-042).

Validates:
- TTL-based expiration
- LRU eviction
- Cache key generation
- Cache statistics
- Integration with LENSOrchestrator

Authority: CORE-008 (TDD), CORE-011, CORE-012
"""

import time
from pathlib import Path
from typing import Dict, Any
import tempfile
import pytest

from cortex.lens.cache import (
    LENSCache,
    InMemoryCacheBackend,
    CacheEntry,
    CacheStats,
    get_lens_cache,
    reset_lens_cache,
)


class TestCacheEntry:
    """Test CacheEntry dataclass."""
    
    def test_cache_entry_creation(self):
        """Test basic cache entry creation."""
        entry = CacheEntry(
            key="test_key",
            value={"data": "test"},
        )
        
        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.access_count == 0
        assert entry.size_bytes > 0  # Should be calculated
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration."""
        entry = CacheEntry(
            key="test_key",
            value={"data": "test"},
        )
        
        # Not expired immediately
        assert not entry.is_expired()
        
        # Force expiration
        entry.expires_at = time.time() - 1
        assert entry.is_expired()
    
    def test_cache_entry_access_tracking(self):
        """Test cache entry access tracking."""
        entry = CacheEntry(
            key="test_key",
            value={"data": "test"},
        )
        
        initial_time = entry.last_accessed
        assert entry.access_count == 0
        
        time.sleep(0.01)  # Small delay
        entry.access()
        
        assert entry.access_count == 1
        assert entry.last_accessed > initial_time


class TestInMemoryCacheBackend:
    """Test in-memory cache backend."""
    
    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        cache = InMemoryCacheBackend(max_entries=10)
        
        # Set value
        cache.set("key1", {"data": "value1"})
        
        # Get value
        result = cache.get("key1")
        assert result == {"data": "value1"}
        
        # Get non-existent key
        result = cache.get("non_existent")
        assert result is None
    
    def test_cache_expiration(self):
        """Test TTL-based expiration."""
        cache = InMemoryCacheBackend()
        
        # Set with short TTL
        cache.set("key1", {"data": "value1"}, ttl_seconds=1)
        
        # Should be available immediately
        assert cache.get("key1") == {"data": "value1"}
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be None after expiration
        assert cache.get("key1") is None
    
    def test_lru_eviction_by_count(self):
        """Test LRU eviction when max_entries is reached."""
        cache = InMemoryCacheBackend(max_entries=3)
        
        # Fill cache
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        cache.set("key3", {"data": "value3"})
        
        # All should be present
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
        
        # Add one more - should evict oldest (key1)
        cache.set("key4", {"data": "value4"})
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None
    
    def test_lru_ordering(self):
        """Test LRU ordering with access updates."""
        cache = InMemoryCacheBackend(max_entries=3)
        
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        cache.set("key3", {"data": "value3"})
        
        # Access key1 to move it to end (most recently used)
        cache.get("key1")
        
        # Add key4 - should evict key2 (now oldest)
        cache.set("key4", {"data": "value4"})
        
        assert cache.get("key1") is not None  # Protected by access
        assert cache.get("key2") is None      # Evicted
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None
    
    def test_cache_delete(self):
        """Test explicit cache deletion."""
        cache = InMemoryCacheBackend()
        
        cache.set("key1", {"data": "value1"})
        assert cache.get("key1") is not None
        
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_cache_clear(self):
        """Test clearing entire cache."""
        cache = InMemoryCacheBackend()
        
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        
        assert len(cache.cache) == 2
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.total_size == 0
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = InMemoryCacheBackend()
        
        # Set entries with different TTLs
        cache.set("key1", {"data": "value1"}, ttl_seconds=10)
        cache.set("key2", {"data": "value2"}, ttl_seconds=1)
        cache.set("key3", {"data": "value3"}, ttl_seconds=1)
        
        assert len(cache.cache) == 3
        
        # Wait for short TTL to expire
        time.sleep(1.1)
        
        # Cleanup
        removed = cache.cleanup_expired()
        
        assert removed == 2  # key2 and key3
        assert cache.get("key1") is not None
        assert cache.get("key2") is None
        assert cache.get("key3") is None


class TestLENSCache:
    """Test LENS cache manager."""
    
    def setup_method(self):
        """Reset cache before each test."""
        reset_lens_cache()
    
    def test_cache_key_generation(self, tmp_path: Path):
        """Test cache key generation."""
        cache = LENSCache()
        
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        # Generate key
        key1 = cache.generate_key(test_file, tmp_path)
        assert key1
        assert ":" in key1  # Should have file:repo format
        
        # Same file should generate same key
        key2 = cache.generate_key(test_file, tmp_path)
        assert key1 == key2
        
        # Different content should generate different key
        test_file.write_text("def test2(): pass")
        key3 = cache.generate_key(test_file, tmp_path)
        assert key1 != key3
    
    def test_cache_key_with_additional_context(self, tmp_path: Path):
        """Test cache key with additional context."""
        cache = LENSCache()
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        # Generate keys with different context
        key1 = cache.generate_key(test_file, tmp_path)
        key2 = cache.generate_key(test_file, tmp_path, {"option": "value1"})
        key3 = cache.generate_key(test_file, tmp_path, {"option": "value2"})
        
        # All should be different
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3
    
    def test_cache_set_and_get(self, tmp_path: Path):
        """Test basic caching operations."""
        cache = LENSCache()
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        key = cache.generate_key(test_file, tmp_path)
        test_data = {"analysis": "result"}
        
        # Cache miss
        result = cache.get(key)
        assert result is None
        assert cache.stats.misses == 1
        
        # Set value
        cache.set(key, test_data)
        
        # Cache hit
        result = cache.get(key)
        assert result == test_data
        assert cache.stats.hits == 1
    
    def test_cache_statistics(self, tmp_path: Path):
        """Test cache statistics tracking."""
        cache = LENSCache()
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        key = cache.generate_key(test_file, tmp_path)
        
        # Generate misses and hits
        cache.get(key)  # miss
        cache.get(key)  # miss
        
        cache.set(key, {"data": "value"})
        
        cache.get(key)  # hit
        cache.get(key)  # hit
        cache.get(key)  # hit
        
        stats = cache.get_stats()
        assert stats.misses == 2
        assert stats.hits == 3
        assert stats.hit_rate == 0.6  # 3/5
    
    def test_cache_clear(self, tmp_path: Path):
        """Test cache clearing."""
        cache = LENSCache()
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        key = cache.generate_key(test_file, tmp_path)
        cache.set(key, {"data": "value"})
        
        assert cache.get(key) is not None
        
        cache.clear()
        
        assert cache.get(key) is None
        assert cache.stats.hits == 0
        assert cache.stats.misses == 1  # From the check above
    
    def test_global_cache_singleton(self):
        """Test global cache singleton."""
        cache1 = get_lens_cache()
        cache2 = get_lens_cache()
        
        assert cache1 is cache2  # Same instance
        
        # Set value in cache1
        cache1.set("test_key", {"data": "value"})
        
        # Should be available in cache2
        assert cache2.get("test_key") == {"data": "value"}
    
    def test_cache_ttl_custom(self, tmp_path: Path):
        """Test custom TTL."""
        cache = LENSCache(ttl_seconds=1)
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        key = cache.generate_key(test_file, tmp_path)
        cache.set(key, {"data": "value"})
        
        # Available immediately
        assert cache.get(key) is not None
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get(key) is None


class TestLENSCacheIntegration:
    """Test integration with LENSOrchestrator."""
    
    @pytest.fixture
    def temp_repo(self, tmp_path: Path) -> Path:
        """Create temporary repo with test file."""
        repo = tmp_path / "repo"
        repo.mkdir()
        
        # Create git repo
        (repo / ".git").mkdir()
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/main")
        
        # Create test file
        test_file = repo / "test.py"
        test_file.write_text("def test(): pass")
        
        return repo
    
    def test_orchestrator_uses_cache(self, temp_repo: Path):
        """Test that LENSOrchestrator uses the cache."""
        from cortex.lens.orchestrator import LENSOrchestrator
        
        orchestrator = LENSOrchestrator(repo_path=temp_repo)
        test_file = temp_repo / "test.py"
        
        # First analysis - cache miss
        initial_stats = orchestrator.get_cache_stats()
        initial_misses = initial_stats["misses"]
        
        result1 = orchestrator.analyze_file(test_file)
        assert result1["_metadata"]["cache_hit"] is False
        
        # Second analysis - cache hit
        result2 = orchestrator.analyze_file(test_file)
        assert result2["_metadata"]["cache_hit"] is True
        
        # Verify cache statistics
        final_stats = orchestrator.get_cache_stats()
        assert final_stats["hits"] > 0
        assert final_stats["misses"] == initial_misses + 1
    
    def test_orchestrator_cache_invalidation(self, temp_repo: Path):
        """Test cache invalidation on file changes."""
        from cortex.lens.orchestrator import LENSOrchestrator
        
        orchestrator = LENSOrchestrator(repo_path=temp_repo)
        test_file = temp_repo / "test.py"
        
        # First analysis
        result1 = orchestrator.analyze_file(test_file)
        
        # Modify file
        test_file.write_text("def test2(): pass")
        
        # Second analysis - should be cache miss (different content)
        result2 = orchestrator.analyze_file(test_file)
        assert result2["_metadata"]["cache_hit"] is False
    
    def test_orchestrator_clear_cache(self, temp_repo: Path):
        """Test cache clearing."""
        from cortex.lens.orchestrator import LENSOrchestrator
        
        orchestrator = LENSOrchestrator(repo_path=temp_repo)
        test_file = temp_repo / "test.py"
        
        # Analyze and cache
        orchestrator.analyze_file(test_file)
        
        # Clear cache
        orchestrator.clear_cache()
        
        # Next analysis should be cache miss
        result = orchestrator.analyze_file(test_file)
        assert result["_metadata"]["cache_hit"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
