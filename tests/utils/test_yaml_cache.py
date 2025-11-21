"""
Tests for Universal YAML Cache

Tests timestamp-based caching functionality, cache invalidation,
performance improvements, and multi-file support.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
import time
from pathlib import Path
from src.utils.yaml_cache import (
    YAMLCache, 
    get_global_cache, 
    load_yaml_cached,
    get_cache_stats,
    clear_cache,
    benchmark_cache_performance
)


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Create a temporary YAML file for testing."""
    yaml_file = tmp_path / "test.yaml"
    data = {
        "version": "1.0",
        "test_data": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)
    return yaml_file


@pytest.fixture
def cache():
    """Create a fresh YAMLCache instance."""
    return YAMLCache()


class TestYAMLCacheBasics:
    """Test basic caching functionality."""
    
    def test_cache_initialization(self, cache):
        """Test cache initializes correctly."""
        assert cache._cache == {}
        assert cache._stats == {}
    
    def test_load_file_first_time(self, cache, temp_yaml_file):
        """Test loading file for first time (cold cache)."""
        data = cache.load(temp_yaml_file)
        
        assert data is not None
        assert data['version'] == '1.0'
        assert data['test_data']['key1'] == 'value1'
        
        # Check cache stats
        stats = cache.get_stats(temp_yaml_file)
        assert stats['cached'] is True
        assert stats['misses'] == 1
        assert stats['hits'] == 0
    
    def test_load_file_second_time(self, cache, temp_yaml_file):
        """Test loading file second time (warm cache)."""
        # First load
        data1 = cache.load(temp_yaml_file)
        
        # Second load (should be cached)
        data2 = cache.load(temp_yaml_file)
        
        assert data1 == data2
        
        # Check cache stats
        stats = cache.get_stats(temp_yaml_file)
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0
    
    def test_cache_invalidation_on_file_change(self, cache, temp_yaml_file):
        """Test cache invalidates when file is modified."""
        # First load
        data1 = cache.load(temp_yaml_file)
        
        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        with open(temp_yaml_file, 'w') as f:
            yaml.dump({"version": "2.0", "test_data": {"key1": "changed"}}, f)
        
        # Second load (should reload due to mtime change)
        data2 = cache.load(temp_yaml_file)
        
        assert data1 != data2
        assert data2['version'] == '2.0'
        assert data2['test_data']['key1'] == 'changed'
        
        # Check stats show cache miss
        stats = cache.get_stats(temp_yaml_file)
        assert stats['misses'] == 2  # Initial load + reload after change
    
    def test_force_reload(self, cache, temp_yaml_file):
        """Test force_reload parameter."""
        # First load
        data1 = cache.load(temp_yaml_file)
        
        # Force reload without file change
        data2 = cache.load(temp_yaml_file, force_reload=True)
        
        assert data1 == data2
        
        # Check stats show cache miss for forced reload
        stats = cache.get_stats(temp_yaml_file)
        assert stats['misses'] == 2


class TestYAMLCacheMultiFile:
    """Test caching with multiple files."""
    
    def test_multiple_files_independent_cache(self, cache, tmp_path):
        """Test that multiple files have independent caches."""
        # Create two files
        file1 = tmp_path / "file1.yaml"
        file2 = tmp_path / "file2.yaml"
        
        with open(file1, 'w') as f:
            yaml.dump({"name": "file1"}, f)
        with open(file2, 'w') as f:
            yaml.dump({"name": "file2"}, f)
        
        # Load both
        data1 = cache.load(file1)
        data2 = cache.load(file2)
        
        assert data1['name'] == 'file1'
        assert data2['name'] == 'file2'
        
        # Check both are cached
        assert cache.is_cached(file1)
        assert cache.is_cached(file2)
        
        # Check aggregated stats
        all_stats = cache.get_stats()
        assert all_stats['total_files'] == 2
        assert all_stats['total_misses'] == 2
    
    def test_clear_specific_file(self, cache, tmp_path):
        """Test clearing cache for specific file."""
        file1 = tmp_path / "file1.yaml"
        file2 = tmp_path / "file2.yaml"
        
        with open(file1, 'w') as f:
            yaml.dump({"name": "file1"}, f)
        with open(file2, 'w') as f:
            yaml.dump({"name": "file2"}, f)
        
        # Load both
        cache.load(file1)
        cache.load(file2)
        
        # Clear only file1
        cache.clear(file1)
        
        assert not cache.is_cached(file1)
        assert cache.is_cached(file2)


class TestYAMLCacheStats:
    """Test cache statistics functionality."""
    
    def test_stats_tracking(self, cache, temp_yaml_file):
        """Test that stats are tracked correctly."""
        # Multiple loads
        cache.load(temp_yaml_file)  # miss
        cache.load(temp_yaml_file)  # hit
        cache.load(temp_yaml_file)  # hit
        
        stats = cache.get_stats(temp_yaml_file)
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['total_calls'] == 3
        assert stats['hit_rate'] == pytest.approx(66.7, abs=0.1)
    
    def test_reset_stats(self, cache, temp_yaml_file):
        """Test resetting statistics."""
        # Load file multiple times
        cache.load(temp_yaml_file)
        cache.load(temp_yaml_file)
        
        # Reset stats
        cache.reset_stats(temp_yaml_file)
        
        # Stats should be reset but cache still present
        stats = cache.get_stats(temp_yaml_file)
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert cache.is_cached(temp_yaml_file)
    
    def test_aggregated_stats(self, cache, tmp_path):
        """Test aggregated statistics across files."""
        file1 = tmp_path / "file1.yaml"
        file2 = tmp_path / "file2.yaml"
        
        with open(file1, 'w') as f:
            yaml.dump({"name": "file1"}, f)
        with open(file2, 'w') as f:
            yaml.dump({"name": "file2"}, f)
        
        # Load files multiple times
        cache.load(file1)  # miss
        cache.load(file1)  # hit
        cache.load(file2)  # miss
        cache.load(file2)  # hit
        cache.load(file2)  # hit
        
        all_stats = cache.get_stats()
        assert all_stats['total_files'] == 2
        assert all_stats['total_hits'] == 3
        assert all_stats['total_misses'] == 2
        assert all_stats['total_calls'] == 5
        assert all_stats['overall_hit_rate'] == 60.0


class TestYAMLCachePerformance:
    """Test cache performance improvements."""
    
    def test_cache_is_faster(self, cache, temp_yaml_file):
        """Test that cached loads are significantly faster."""
        # Cold load
        start = time.perf_counter()
        cache.load(temp_yaml_file)
        cold_time = time.perf_counter() - start
        
        # Warm load
        start = time.perf_counter()
        cache.load(temp_yaml_file)
        warm_time = time.perf_counter() - start
        
        # Warm should be at least 10x faster
        assert warm_time < cold_time / 10
    
    def test_benchmark_performance(self, temp_yaml_file):
        """Test benchmark utility function."""
        results = benchmark_cache_performance(temp_yaml_file, iterations=5)
        
        assert 'cold_load_ms' in results
        assert 'warm_load_ms' in results
        assert 'speedup' in results
        assert 'improvement_percent' in results
        
        # Warm should be significantly faster
        assert results['speedup'] > 10
        assert results['improvement_percent'] > 90


class TestYAMLCacheGlobalInstance:
    """Test global cache instance functionality."""
    
    def test_global_cache_singleton(self):
        """Test that get_global_cache returns same instance."""
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        
        assert cache1 is cache2
    
    def test_load_yaml_cached_convenience(self, temp_yaml_file):
        """Test load_yaml_cached convenience function."""
        data1 = load_yaml_cached(temp_yaml_file)
        data2 = load_yaml_cached(temp_yaml_file)
        
        assert data1 == data2
        
        # Check global cache was used
        stats = get_cache_stats(temp_yaml_file)
        assert stats['hits'] == 1
    
    def test_clear_cache_convenience(self, temp_yaml_file):
        """Test clear_cache convenience function."""
        load_yaml_cached(temp_yaml_file)
        clear_cache(temp_yaml_file)
        
        cache = get_global_cache()
        assert not cache.is_cached(temp_yaml_file)


class TestYAMLCacheErrorHandling:
    """Test error handling."""
    
    def test_file_not_found(self, cache):
        """Test FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            cache.load("nonexistent_file.yaml")
    
    def test_invalid_yaml(self, cache, tmp_path):
        """Test yaml.YAMLError for invalid YAML."""
        bad_yaml = tmp_path / "bad.yaml"
        with open(bad_yaml, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        with pytest.raises(yaml.YAMLError):
            cache.load(bad_yaml)


class TestYAMLCacheRealFiles:
    """Test with real CORTEX YAML files (integration tests)."""
    
    @pytest.mark.skipif(
        not Path("cortex-brain/response-templates.yaml").exists(),
        reason="Real CORTEX files not available"
    )
    def test_load_response_templates(self, cache):
        """Test loading actual response-templates.yaml."""
        data = cache.load("cortex-brain/response-templates.yaml")
        
        assert data is not None
        assert 'templates' in data
        
        # Second load should be cached
        data2 = cache.load("cortex-brain/response-templates.yaml")
        assert data == data2
        
        stats = cache.get_stats("cortex-brain/response-templates.yaml")
        assert stats['hits'] == 1
    
    @pytest.mark.skipif(
        not Path("cortex-brain/brain-protection-rules.yaml").exists(),
        reason="Real CORTEX files not available"
    )
    def test_load_brain_protection_rules(self, cache):
        """Test loading actual brain-protection-rules.yaml."""
        data = cache.load("cortex-brain/brain-protection-rules.yaml")
        
        assert data is not None
        assert 'skull_rules' in data
        
        stats = cache.get_stats("cortex-brain/brain-protection-rules.yaml")
        assert stats['misses'] == 1
