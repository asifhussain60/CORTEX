"""
Tests for RemoteCache.

Authority: CORE-008 (TDD)
Phase: 10 - LENS Remote Intelligence
Task: LENS-013
"""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Skip all tests if diskcache is not installed
pytest.importorskip("diskcache", reason="diskcache not installed")

from cortex.brain.analysis.remote_cache import (
    RemoteCache,
    CacheEntry,
    CacheStats,
    get_remote_cache,
)


class TestCacheEntry:
    """Test CacheEntry dataclass."""
    
    def test_cache_entry_creation(self):
        """Test creating a CacheEntry."""
        entry = CacheEntry(
            key="test_key",
            value={"data": "value"},
            timestamp=1234567890.0,
            ttl=3600,
            provider="github",
            repo="owner/repo",
        )
        assert entry.key == "test_key"
        assert entry.value == {"data": "value"}
        assert entry.ttl == 3600
        assert entry.provider == "github"


class TestCacheStats:
    """Test CacheStats dataclass."""
    
    def test_cache_stats_creation(self):
        """Test creating CacheStats."""
        stats = CacheStats(hits=10, misses=5, size=1024, entries=5)
        assert stats.hits == 10
        assert stats.misses == 5
        assert stats.entries == 5
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats(hits=75, misses=25)
        assert stats.hit_rate == 75.0
        
        stats = CacheStats(hits=0, misses=0)
        assert stats.hit_rate == 0.0


class TestRemoteCache:
    """Test RemoteCache functionality."""
    
    @pytest.fixture
    def cache(self, tmp_path: Path):
        """Create cache with temporary directory."""
        cache = RemoteCache(
            cache_dir=tmp_path / "cache",
            max_size=1024 * 1024,  # 1 MB
            default_ttl=60,  # 1 minute
        )
        yield cache
        cache.close()
    
    def test_cache_initialization(self, tmp_path: Path):
        """Test cache initialization."""
        cache_dir = tmp_path / "test_cache"
        cache = RemoteCache(cache_dir=cache_dir)
        
        assert cache.cache_dir == cache_dir
        assert cache_dir.exists()
        assert cache.default_ttl == 3600
        
        cache.close()
    
    def test_cache_key_generation(self, cache: RemoteCache):
        """Test cache key generation."""
        key1 = cache._make_key("github", "owner/repo", "fetch_file", path="test.py", ref="main")
        key2 = cache._make_key("github", "owner/repo", "fetch_file", path="test.py", ref="main")
        key3 = cache._make_key("github", "owner/repo", "fetch_file", path="other.py", ref="main")
        
        # Same parameters = same key
        assert key1 == key2
        
        # Different parameters = different key
        assert key1 != key3
        
        # Keys are SHA256 hashes
        assert len(key1) == 64
    
    def test_set_and_get(self, cache: RemoteCache):
        """Test setting and getting cached values."""
        value = {"file": "test.py", "content": "print('hello')"}
        
        # Set value
        success = cache.set(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            value=value,
            path="test.py",
            ref="main",
        )
        assert success is True
        
        # Get value
        cached = cache.get(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            path="test.py",
            ref="main",
        )
        assert cached == value
    
    def test_cache_miss(self, cache: RemoteCache):
        """Test cache miss."""
        result = cache.get(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            path="nonexistent.py",
            ref="main",
        )
        assert result is None
        assert cache.stats().misses == 1
    
    def test_cache_hit(self, cache: RemoteCache):
        """Test cache hit statistics."""
        cache.set(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            value={"data": "value"},
            path="test.py",
            ref="main",
        )
        
        # First get - hit
        cache.get(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            path="test.py",
            ref="main",
        )
        
        stats = cache.stats()
        assert stats.hits == 1
        assert stats.hit_rate == 100.0
    
    def test_ttl_expiration(self, cache: RemoteCache):
        """Test TTL expiration."""
        # Set with short TTL
        cache.set(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            value={"data": "value"},
            ttl=1,  # 1 second
            path="test.py",
            ref="main",
        )
        
        # Immediate get - should work
        result = cache.get(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            path="test.py",
            ref="main",
        )
        assert result is not None
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Get after expiration - should be None
        result = cache.get(
            provider="github",
            repo="owner/repo",
            operation="fetch_file",
            path="test.py",
            ref="main",
        )
        assert result is None
    
    def test_invalidate_all(self, cache: RemoteCache):
        """Test invalidating all entries."""
        # Add multiple entries
        cache.set("github", "repo1", "op1", value=1)
        cache.set("github", "repo2", "op2", value=2)
        cache.set("gitlab", "repo3", "op3", value=3)
        
        # Invalidate all
        count = cache.invalidate()
        assert count == 3
        
        # Verify empty
        stats = cache.stats()
        assert stats.entries == 0
    
    def test_invalidate_by_provider(self, cache: RemoteCache):
        """Test invalidating by provider."""
        cache.set("github", "repo1", "op1", value=1)
        cache.set("github", "repo2", "op2", value=2)
        cache.set("gitlab", "repo3", "op3", value=3)
        
        # Invalidate github only
        count = cache.invalidate(provider="github")
        assert count == 2
        
        # Verify gitlab entry remains
        stats = cache.stats()
        assert stats.entries == 1
    
    def test_invalidate_by_repo(self, cache: RemoteCache):
        """Test invalidating by repository."""
        cache.set("github", "owner/repo1", "op1", value=1)
        cache.set("github", "owner/repo2", "op2", value=2)
        cache.set("github", "owner/repo1", "op3", value=3)
        
        # Invalidate repo1 only
        count = cache.invalidate(repo="owner/repo1")
        assert count == 2
        
        # Verify repo2 entry remains
        stats = cache.stats()
        assert stats.entries == 1
    
    def test_clear(self, cache: RemoteCache):
        """Test clearing cache."""
        cache.set("github", "repo1", "op1", value=1)
        cache.set("github", "repo2", "op2", value=2)
        
        cache.clear()
        
        stats = cache.stats()
        assert stats.entries == 0
        # Note: Disk cache may maintain some overhead after clear
    
    def test_stats_tracking(self, cache: RemoteCache):
        """Test statistics tracking."""
        # Add entries
        cache.set("github", "repo1", "op1", value=1)
        cache.set("github", "repo2", "op2", value=2)
        
        # Hit
        cache.get("github", "repo1", "op1")
        
        # Miss
        cache.get("github", "repo3", "op3")
        
        stats = cache.stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.entries == 2
        assert stats.hit_rate == 50.0


class TestGlobalCache:
    """Test global cache instance."""
    
    def test_get_remote_cache_singleton(self, tmp_path: Path):
        """Test global cache singleton pattern."""
        # Reset global cache
        import cortex.brain.analysis.remote_cache as cache_module
        cache_module._global_cache = None
        
        cache1 = get_remote_cache(cache_dir=tmp_path / "cache")
        cache2 = get_remote_cache()
        
        # Should be same instance
        assert cache1 is cache2
        
        cache1.close()
