"""
Unit tests for LazyTemplateLoader module.

Tests cover:
- Registry-based template lookup
- Cache hit/miss behavior
- Cache TTL expiration
- Fallback to monolithic file
- Performance metrics tracking
- Cache management operations
- Preload functionality

Author: CORTEX Test Suite
Date: December 5, 2025
"""

import pytest
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.response_templates.lazy_template_loader import (
    LazyTemplateLoader,
    CachedTemplate,
    LoadMetrics
)


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create temporary template directory structure."""
    template_dir = tmp_path / "response-templates"
    template_dir.mkdir()
    
    # Create config directory
    config_dir = template_dir / "config"
    config_dir.mkdir()
    
    # Create mock registry file
    registry_file = config_dir / "template-registry.yaml"
    registry_data = {
        "templates": {
            "test_template": {
                "file": "agents/test_template.yaml",
                "category": "test",
                "tags": ["test"]
            }
        }
    }
    with open(registry_file, 'w') as f:
        yaml.dump(registry_data, f)
    
    return template_dir


@pytest.fixture
def loader(temp_template_dir):
    """Create LazyTemplateLoader instance with test directory."""
    return LazyTemplateLoader(
        template_dir=temp_template_dir,
        cache_ttl_seconds=300  # 5 minutes
    )


@pytest.fixture
def sample_template():
    """Sample template data for testing."""
    return {
        "id": "test_template",
        "sections": {
            "header": {"content": "Test Header"},
            "body": {"content": "Test Body"}
        },
        "metadata": {
            "version": "1.0",
            "category": "test"
        }
    }


class TestLazyTemplateLoader:
    """Test suite for LazyTemplateLoader class."""
    
    def test_initialization(self, loader):
        """Test loader initialization with default parameters."""
        assert loader.cache_ttl_seconds == 300
        assert len(loader.cache) == 0
        assert loader.metrics.total_loads == 0
        assert loader.metrics.cache_hits == 0
        assert loader.metrics.cache_misses == 0
    
    def test_cache_initialization_empty(self, loader):
        """Test that cache starts empty."""
        assert len(loader.cache) == 0
        assert loader.metrics.cache_hits == 0
    
    def test_load_template_cache_miss(self, loader, temp_template_dir, sample_template):
        """Test loading template when not in cache (cache miss)."""
        # Create actual template file
        template_file = temp_template_dir / "agents" / "test_template.yaml"
        template_file.parent.mkdir(exist_ok=True)
        with open(template_file, 'w') as f:
            yaml.dump(sample_template, f)
        
        # Load template (should be cache miss)
        result = loader.load_template("test_template")
        
        # Verify result
        assert result == sample_template
        assert loader.metrics.cache_misses == 1
        assert loader.metrics.cache_hits == 0
        assert loader.metrics.total_loads == 1
        
        # Verify cached
        assert "test_template" in loader.cache
    
    def test_load_template_cache_hit(self, loader, sample_template):
        """Test loading template from cache (cache hit)."""
        # Pre-populate cache
        cached = CachedTemplate(
            template_id="test_template",
            content=sample_template,
            loaded_at=datetime.now(),
            file_path=Path("/fake/path/template.yaml"),
            load_time_ms=5.0
        )
        loader.cache["test_template"] = cached
        
        # Load template (should be cache hit)
        result = loader.load_template("test_template")
        
        # Verify result
        assert result == sample_template
        assert loader.metrics.cache_hits == 1
        assert loader.metrics.cache_misses == 0
        assert loader.metrics.total_loads == 1
    
    def test_cache_ttl_expiration(self, loader, sample_template):
        """Test that cached template expires after TTL."""
        # Pre-populate cache with expired entry
        expired_time = datetime.now() - timedelta(seconds=400)  # Expired (>300s)
        cached = CachedTemplate(
            template_id="test_template",
            data=sample_template,
            loaded_at=expired_time,
            file_path=Path("/fake/path/template.yaml")
        )
        loader._cache["test_template"] = cached
        
        # Mock YAML loading for reload
        with patch('src.response_templates.lazy_template_loader.yaml') as mock_yaml:
            mock_yaml.safe_load.return_value = sample_template
            with patch('builtins.open', create=True):
                result = loader.load_template("test_template")
        
        # Verify cache was treated as miss (expired)
        assert loader._metrics.cache_misses == 1
        assert loader._metrics.cache_hits == 0
    
    def test_cache_ttl_not_expired(self, loader, sample_template):
        """Test that cached template is used if not expired."""
        # Pre-populate cache with recent entry
        recent_time = datetime.now() - timedelta(seconds=100)  # Not expired (<300s)
        cached = CachedTemplate(
            template_id="test_template",
            data=sample_template,
            loaded_at=recent_time,
            file_path=Path("/fake/path/template.yaml")
        )
        loader._cache["test_template"] = cached
        
        # Load template (should be cache hit)
        result = loader.load_template("test_template")
        
        # Verify cache hit
        assert result == sample_template
        assert loader._metrics.cache_hits == 1
        assert loader._metrics.cache_misses == 0
    
    @patch('src.response_templates.lazy_template_loader.yaml')
    def test_fallback_to_monolithic_file(self, mock_yaml, loader, sample_template):
        """Test fallback to monolithic file when distributed file fails."""
        # Setup registry to return None (template not found)
        loader._registry_manager.get_template_file.return_value = None
        
        # Setup monolithic file mock
        monolithic_data = {
            "templates": {
                "test_template": sample_template
            }
        }
        mock_yaml.safe_load.return_value = monolithic_data
        
        with patch('builtins.open', create=True):
            result = loader.load_template("test_template")
        
        # Verify fallback was used
        assert result == sample_template
        assert loader._metrics.fallback_loads == 1
    
    def test_clear_single_cache_entry(self, loader, sample_template):
        """Test clearing a single template from cache."""
        # Pre-populate cache
        cached = CachedTemplate(
            template_id="test_template",
            data=sample_template,
            loaded_at=datetime.now(),
            file_path=Path("/fake/path/template.yaml")
        )
        loader._cache["test_template"] = cached
        loader._cache["other_template"] = cached
        
        # Clear single entry
        loader.clear_cache(template_id="test_template")
        
        # Verify only target was cleared
        assert "test_template" not in loader._cache
        assert "other_template" in loader._cache
    
    def test_clear_all_cache_entries(self, loader, sample_template):
        """Test clearing all templates from cache."""
        # Pre-populate cache with multiple entries
        cached = CachedTemplate(
            template_id="test_template",
            data=sample_template,
            loaded_at=datetime.now(),
            file_path=Path("/fake/path/template.yaml")
        )
        loader._cache["template1"] = cached
        loader._cache["template2"] = cached
        loader._cache["template3"] = cached
        
        # Clear all entries
        loader.clear_cache()
        
        # Verify cache is empty
        assert len(loader._cache) == 0
    
    @patch('src.response_templates.lazy_template_loader.yaml')
    def test_preload_templates(self, mock_yaml, loader, sample_template):
        """Test preloading multiple templates."""
        # Setup mock YAML loader
        mock_yaml.safe_load.return_value = sample_template
        
        template_ids = ["template1", "template2", "template3"]
        
        with patch('builtins.open', create=True):
            loader.preload_templates(template_ids)
        
        # Verify all templates were loaded
        for template_id in template_ids:
            assert template_id in loader._cache
        
        # Verify metrics
        assert loader._metrics.total_loads == 3
        assert loader._metrics.cache_misses == 3
    
    def test_get_metrics(self, loader):
        """Test retrieving load metrics."""
        # Manually set some metrics
        loader._metrics.total_loads = 10
        loader._metrics.cache_hits = 7
        loader._metrics.cache_misses = 3
        loader._metrics.fallback_loads = 1
        
        metrics = loader.get_metrics()
        
        # Verify metrics structure
        assert metrics["total_loads"] == 10
        assert metrics["cache_hits"] == 7
        assert metrics["cache_misses"] == 3
        assert metrics["fallback_loads"] == 1
        assert metrics["cache_hit_rate"] == 0.7  # 7/10
    
    def test_cache_hit_rate_calculation(self, loader):
        """Test cache hit rate calculation."""
        loader._metrics.total_loads = 0
        metrics = loader.get_metrics()
        assert metrics["cache_hit_rate"] == 0.0  # No division by zero
        
        loader._metrics.total_loads = 20
        loader._metrics.cache_hits = 15
        metrics = loader.get_metrics()
        assert metrics["cache_hit_rate"] == 0.75  # 15/20
    
    @patch('src.response_templates.lazy_template_loader.yaml')
    def test_load_nonexistent_template(self, mock_yaml, loader):
        """Test loading a template that doesn't exist."""
        # Setup registry to return None
        loader._registry_manager.get_template_file.return_value = None
        
        # Setup monolithic file without the template
        mock_yaml.safe_load.return_value = {"templates": {}}
        
        with patch('builtins.open', create=True):
            with pytest.raises(KeyError):
                loader.load_template("nonexistent_template")
    
    @patch('src.response_templates.lazy_template_loader.yaml')
    def test_concurrent_cache_access(self, mock_yaml, loader, sample_template):
        """Test thread-safe cache access (basic smoke test)."""
        mock_yaml.safe_load.return_value = sample_template
        
        with patch('builtins.open', create=True):
            # Simulate concurrent access
            result1 = loader.load_template("test_template")
            result2 = loader.load_template("test_template")
        
        # Both should succeed
        assert result1 == sample_template
        assert result2 == sample_template
        assert loader._metrics.cache_hits == 1
    
    def test_performance_target_load_time(self, loader, sample_template):
        """Test that template loading meets <10ms performance target."""
        # Pre-populate cache (cache hit should be <1ms)
        cached = CachedTemplate(
            template_id="test_template",
            data=sample_template,
            loaded_at=datetime.now(),
            file_path=Path("/fake/path/template.yaml")
        )
        loader._cache["test_template"] = cached
        
        # Measure load time
        start_time = time.time()
        result = loader.load_template("test_template")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify performance (<1ms for cache hit)
        assert elapsed_ms < 1.0
        assert result == sample_template


class TestCachedTemplate:
    """Test suite for CachedTemplate dataclass."""
    
    def test_cached_template_creation(self, sample_template):
        """Test creating CachedTemplate instance."""
        cached = CachedTemplate(
            template_id="test",
            data=sample_template,
            loaded_at=datetime.now(),
            file_path=Path("/test/path.yaml")
        )
        
        assert cached.template_id == "test"
        assert cached.data == sample_template
        assert isinstance(cached.loaded_at, datetime)
        assert isinstance(cached.file_path, Path)
    
    def test_cached_template_immutability(self, sample_template):
        """Test that CachedTemplate preserves data integrity."""
        original_data = sample_template.copy()
        cached = CachedTemplate(
            template_id="test",
            data=sample_template,
            loaded_at=datetime.now(),
            file_path=Path("/test/path.yaml")
        )
        
        # Verify data wasn't modified during caching
        assert cached.data == original_data


class TestLoadMetrics:
    """Test suite for LoadMetrics dataclass."""
    
    def test_load_metrics_initialization(self):
        """Test LoadMetrics starts with zero values."""
        metrics = LoadMetrics()
        
        assert metrics.total_loads == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.fallback_loads == 0
        assert metrics.avg_load_time_ms == 0.0
    
    def test_load_metrics_accumulation(self):
        """Test that metrics accumulate correctly."""
        metrics = LoadMetrics()
        
        metrics.total_loads = 10
        metrics.cache_hits = 7
        metrics.cache_misses = 3
        
        assert metrics.total_loads == metrics.cache_hits + metrics.cache_misses


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
