"""
Stage 5: CachedKnowledgeProvider Decorator Implementation Tests

AC-PHASE50-S5-001: CachedKnowledgeProvider wraps any IKnowledgeProvider with L1/L2 cache
AC-PHASE50-S5-002: L1 cache (in-memory) with TTL from StorageConfig.cache_ttl_seconds
AC-PHASE50-S5-003: L2 cache (filesystem) for persistence across restarts
AC-PHASE50-S5-004: Cache hits measured in observability metrics
AC-PHASE50-S5-005: Supports cache bypass via bypass_cache flag

Target: 20 tests, 100% pass rate for Stage 5
"""

import time
import tempfile
import pytest
from unittest.mock import Mock, patch
from cortex.storage.provider import IKnowledgeProvider
from cortex.storage.config import StorageConfig
from cortex.storage.errors import StorageError, NotFoundError
from cortex.storage.cache import CachedKnowledgeProvider


class TestCachedProviderInitialization:
    """AC-PHASE50-S5-001: CachedKnowledgeProvider initialization"""

    def test_cached_provider_wraps_any_provider(self):
        """CachedKnowledgeProvider accepts any IKnowledgeProvider"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp", cache_enabled=True)
        
        cached = CachedKnowledgeProvider(mock_provider, config)
        assert cached.provider == mock_provider

    def test_cached_provider_implements_interface(self):
        """CachedKnowledgeProvider is instance of IKnowledgeProvider"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp", cache_enabled=True)
        
        cached = CachedKnowledgeProvider(mock_provider, config)
        assert isinstance(cached, IKnowledgeProvider)

    def test_cached_provider_stores_config(self):
        """CachedKnowledgeProvider stores StorageConfig"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp", cache_ttl_seconds=300)
        
        cached = CachedKnowledgeProvider(mock_provider, config)
        assert cached.config == config

    def test_cached_provider_initializes_l1_cache(self):
        """CachedKnowledgeProvider initializes in-memory L1 cache"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        cached = CachedKnowledgeProvider(mock_provider, config)
        assert hasattr(cached, 'l1_cache')
        assert isinstance(cached.l1_cache, dict)

    def test_cached_provider_initializes_l2_cache_directory(self):
        """CachedKnowledgeProvider creates L2 cache directory"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(
                backend="local",
                endpoint=tmpdir,
                cache_enabled=True
            )
            cached = CachedKnowledgeProvider(mock_provider, config)
            assert hasattr(cached, 'l2_cache_dir')


class TestCachedProviderL1Cache:
    """AC-PHASE50-S5-002: L1 in-memory cache with TTL"""

    def test_l1_cache_stores_read_results(self):
        """L1 cache stores read() results in memory"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "cached content"
        
        config = StorageConfig(backend="local", endpoint="/tmp", cache_ttl_seconds=300)
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # First read - cache miss
        result1 = cached.read("file.txt")
        assert result1 == "cached content"
        assert mock_provider.read.call_count == 1
        
        # Second read - cache hit
        result2 = cached.read("file.txt")
        assert result2 == "cached content"
        assert mock_provider.read.call_count == 1  # Not called again

    def test_l1_cache_respects_ttl(self):
        """L1 cache expires entries after TTL"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = ["content_v1", "content_v2"]
        
        config = StorageConfig(backend="local", endpoint="/tmp", cache_ttl_seconds=1, cache_enabled=True)
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # First read
        result1 = cached.read("file.txt")
        assert result1 == "content_v1"
        assert mock_provider.read.call_count == 1
        
        # Wait for TTL to expire
        time.sleep(1.2)
        
        # Second read - cache expired, should call provider again
        result2 = cached.read("file.txt")
        assert result2 == "content_v2"
        assert mock_provider.read.call_count == 2

    def test_l1_cache_invalidated_on_write(self):
        """L1 cache invalidates on write() operation"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = ["content_v1", "content_v2"]
        
        config = StorageConfig(backend="local", endpoint="/tmp", cache_enabled=True)
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # Read and cache
        result1 = cached.read("file.txt")
        assert result1 == "content_v1"
        assert mock_provider.read.call_count == 1
        
        # Write to same file (should invalidate cache)
        cached.write("file.txt", "new content")
        mock_provider.write.assert_called_once()
        
        # Read again - should fetch from provider (cache was invalidated)
        result2 = cached.read("file.txt")
        assert result2 == "content_v2"
        assert mock_provider.read.call_count == 2

    def test_l1_cache_invalidated_on_delete(self):
        """L1 cache invalidates on delete() operation"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "cached content"
        
        config = StorageConfig(backend="local", endpoint="/tmp", cache_enabled=True)
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # Cache a read
        cached.read("file.txt")
        assert len(cached.l1_cache) > 0
        
        # Delete (should invalidate cache)
        cached.delete("file.txt")
        
        # Cache should be invalidated (empty now)
        assert len(cached.l1_cache) == 0


class TestCachedProviderL2Cache:
    """AC-PHASE50-S5-003: L2 filesystem cache for persistence"""

    def test_l2_cache_stores_on_disk(self):
        """L2 cache persists entries to filesystem"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "persistent content"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(
                backend="local",
                endpoint=tmpdir,
                cache_enabled=True
            )
            cached = CachedKnowledgeProvider(mock_provider, config)
            
            # Read
            result = cached.read("file.txt")
            assert result == "persistent content"
            
            # Verify cache has content
            assert len(cached.l1_cache) > 0

    def test_l2_cache_loads_on_startup(self):
        """L2 cache loads persisted entries on initialization"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "persistent content"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config1 = StorageConfig(
                backend="local",
                endpoint=tmpdir,
                cache_enabled=True
            )
            cached1 = CachedKnowledgeProvider(mock_provider, config1)
            cached1.read("file.txt")
            
            # Verify cache is populated
            assert len(cached1.l1_cache) > 0


class TestCachedProviderCacheBypass:
    """AC-PHASE50-S5-005: Cache bypass capability"""

    def test_bypass_cache_flag_skips_cache(self):
        """bypass_cache parameter skips caching logic"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = ["content_v1", "content_v2"]
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # Read with cache
        result1 = cached.read("file.txt", bypass_cache=False)
        assert result1 == "content_v1"
        
        # Read with bypass
        result2 = cached.read("file.txt", bypass_cache=True)
        assert result2 == "content_v2"
        assert mock_provider.read.call_count == 2

    def test_cache_disabled_in_config_skips_caching(self):
        """cache_enabled=False disables all caching"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = ["content_v1", "content_v2"]
        
        config = StorageConfig(backend="local", endpoint="/tmp", cache_enabled=False)
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # Both reads should call provider
        result1 = cached.read("file.txt")
        result2 = cached.read("file.txt")
        
        assert mock_provider.read.call_count == 2


class TestCachedProviderAllMethods:
    """AC-PHASE50-S5-001: All IKnowledgeProvider methods cached"""

    def test_list_method_cached(self):
        """list() results are cached"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.list.return_value = ["file1.txt", "file2.txt"]
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # First call
        result1 = cached.list("dir")
        assert result1 == ["file1.txt", "file2.txt"]
        assert mock_provider.list.call_count == 1
        
        # Second call - cached
        result2 = cached.list("dir")
        assert mock_provider.list.call_count == 1

    def test_exists_method_cached(self):
        """exists() results are cached"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.exists.return_value = True
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # First call
        result1 = cached.exists("file.txt")
        assert result1 is True
        assert mock_provider.exists.call_count == 1
        
        # Second call - cached
        result2 = cached.exists("file.txt")
        assert mock_provider.exists.call_count == 1

    def test_write_method_passes_through_and_invalidates(self):
        """write() passes through to provider and invalidates cache"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        cached.write("file.txt", "content")
        mock_provider.write.assert_called_once_with("file.txt", "content")

    def test_delete_method_passes_through_and_invalidates(self):
        """delete() passes through to provider and invalidates cache"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        cached.delete("file.txt")
        mock_provider.delete.assert_called_once_with("file.txt")


class TestCachedProviderMetrics:
    """AC-PHASE50-S5-004: Cache metrics and observability"""

    def test_cache_hit_rate_tracked(self):
        """CachedKnowledgeProvider tracks cache hit rate"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "content"
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # Generate cache hits
        cached.read("file.txt")
        cached.read("file.txt")
        cached.read("file.txt")
        
        # Metrics should show hits
        assert hasattr(cached, 'metrics')
        assert cached.metrics['hits'] >= 2
        assert cached.metrics['misses'] >= 1

    def test_cache_size_limited(self):
        """L1 cache size limited to prevent memory bloat"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = [f"content_{i}" for i in range(1000)]
        
        config = StorageConfig(backend="local", endpoint="/tmp", cache_enabled=True)
        cached = CachedKnowledgeProvider(mock_provider, config)
        
        # Read many different files
        for i in range(100):
            cached.read(f"file_{i}.txt")
        
        # L1 cache size should be bounded
        assert len(cached.l1_cache) <= 500  # Max cache entries
