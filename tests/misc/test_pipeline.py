"""
Test suite for DataCollectionPipeline
Tests orchestration, parallel execution, error handling, and caching.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.cortex_lens.core.pipeline import DataCollectionPipeline


# ========== Fixtures ==========

@pytest.fixture
def pipeline():
    """Create a pipeline instance for testing."""
    return DataCollectionPipeline(max_workers=2, use_cache=False)


@pytest.fixture
def mock_collector():
    """Create a mock collector."""
    collector = Mock()
    collector.name = 'test_collector'
    collector.collect.return_value = {'status': 'success', 'data': [1, 2, 3]}
    return collector


@pytest.fixture
def sample_classification():
    """Sample classification result."""
    return {
        'primary_type': 'api_service',
        'confidence_scores': {'api_service': 0.85},
        'detected_patterns': {'has_controllers': True},
        'metadata': {'total_files': 42}
    }


@pytest.fixture
def sample_repo(tmp_path):
    """Create a minimal repository structure."""
    # API service structure
    (tmp_path / "Controllers").mkdir()
    (tmp_path / "Controllers" / "UsersController.cs").write_text("""
    [ApiController]
    [Route("api/[controller]")]
    public class UsersController : ControllerBase
    {
        [HttpGet]
        public IActionResult Get() => Ok();
    }
    """)
    
    (tmp_path / "Program.cs").write_text("""
    var app = WebApplication.CreateBuilder().Build();
    app.Run();
    """)
    
    return tmp_path


# ========== Initialization Tests ==========

class TestPipelineInitialization:
    """Test pipeline initialization and configuration."""
    
    def test_default_initialization(self):
        """Test pipeline with default settings."""
        pipeline = DataCollectionPipeline()
        
        assert pipeline is not None
        assert pipeline._max_workers == 4  # default
        assert pipeline._use_cache is True  # default
        assert pipeline._collector_registry is None  # lazy init
        assert pipeline._file_cache is None  # lazy init
    
    def test_custom_initialization(self):
        """Test pipeline with custom settings."""
        pipeline = DataCollectionPipeline(max_workers=8, use_cache=False)
        
        assert pipeline._max_workers == 8
        assert pipeline._use_cache is False
    
    def test_collector_classification(self):
        """Test that collectors are properly classified."""
        # Verify independent collectors list
        assert 'health' in DataCollectionPipeline.INDEPENDENT_COLLECTORS
        assert 'security' in DataCollectionPipeline.INDEPENDENT_COLLECTORS
        assert 'dependency' in DataCollectionPipeline.INDEPENDENT_COLLECTORS
        
        # Verify dependent collectors list
        assert 'architecture' in DataCollectionPipeline.DEPENDENT_COLLECTORS
        assert 'api_endpoint' in DataCollectionPipeline.DEPENDENT_COLLECTORS


# ========== Collector Registry Tests ==========

class TestCollectorRegistration:
    """Test collector registration and retrieval."""
    
    def test_registry_lazy_initialization(self, pipeline):
        """Test that registry is lazily initialized."""
        assert pipeline._collector_registry is None
        
        # Should initialize on first execute
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = []
                MockRegistry.return_value = mock_registry
                
                classification = {'primary_type': 'api_service'}
                pipeline.execute(Path('/fake/path'), classification)
                
                assert pipeline._collector_registry is not None


# ========== Execution Tests ==========

class TestPipelineExecution:
    """Test pipeline execution flow."""
    
    def test_execute_with_no_collectors(self, pipeline, sample_repo, sample_classification):
        """Test execution when no collectors are applicable."""
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = []
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                assert 'metadata' in result
                assert result['metadata']['repo_type'] == ['api_service']
                assert 'scan_timestamp' in result['metadata']
    
    def test_execute_with_independent_collectors(self, pipeline, sample_repo, sample_classification):
        """Test execution with only independent collectors."""
        # Create mock collectors
        health_collector = Mock()
        health_collector.name = 'health'
        health_collector.collect_safe.return_value = {'status': 'healthy'}
        
        security_collector = Mock()
        security_collector.name = 'security'
        security_collector.collect_safe.return_value = {'vulnerabilities': 0}
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = [
                    health_collector, security_collector
                ]
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                assert 'health' in result
                assert result['health'] == {'status': 'healthy'}
                assert 'security' in result
                assert result['security'] == {'vulnerabilities': 0}
    
    def test_execute_with_dependent_collectors(self, pipeline, sample_repo, sample_classification):
        """Test execution with dependent collectors."""
        arch_collector = Mock()
        arch_collector.name = 'architecture'
        arch_collector.collect.return_value = {'layers': 3}
        
        api_collector = Mock()
        api_collector.name = 'api_endpoint'
        api_collector.collect.return_value = {'endpoints': 5}
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = [
                    arch_collector, api_collector
                ]
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                assert 'architecture' in result
                assert 'api_endpoint' in result
    
    def test_execute_with_mixed_collectors(self, pipeline, sample_repo, sample_classification):
        """Test execution with both independent and dependent collectors."""
        # Independent
        health = Mock()
        health.name = 'health'
        health.collect.return_value = {'status': 'ok'}
        
        # Dependent
        arch = Mock()
        arch.name = 'architecture'
        arch.collect.return_value = {'layers': 2}
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = [health, arch]
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                # Should have both
                assert 'health' in result
                assert 'architecture' in result
                assert len(result) >= 3  # metadata + health + architecture


# ========== Progress Callback Tests ==========

class TestProgressCallbacks:
    """Test progress callback functionality."""
    
    def test_progress_callback_invoked(self, pipeline, sample_repo, sample_classification):
        """Test that progress callback is invoked."""
        callback = Mock()
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = []
                MockRegistry.return_value = mock_registry
                
                pipeline.execute(sample_repo, sample_classification, progress_callback=callback)
                
                # Should be called at least once
                assert callback.call_count >= 1
                
                # Check call structure
                args = callback.call_args_list[0][0]
                assert len(args) == 3  # phase, name, message
    
    def test_progress_callback_phases(self, pipeline, sample_repo, sample_classification):
        """Test that different phases are reported."""
        phases = []
        
        def track_callback(phase, name, message):
            phases.append((phase, name))
        
        health = Mock()
        health.name = 'health'
        health.collect.return_value = {'status': 'ok'}
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = [health]
                MockRegistry.return_value = mock_registry
                
                pipeline.execute(sample_repo, sample_classification, progress_callback=track_callback)
                
                # Should have phase callbacks
                assert len(phases) > 0
                assert any('data_collection' in name for phase, name in phases)


# ========== Error Handling Tests ==========

class TestErrorHandling:
    """Test error handling and resilience."""
    
    def test_collector_failure_isolation(self, pipeline, sample_repo, sample_classification):
        """Test that one collector failure doesn't crash pipeline."""
        good_collector = Mock()
        good_collector.name = 'health'
        good_collector.collect.return_value = {'status': 'ok'}
        
        bad_collector = Mock()
        bad_collector.name = 'security'
        bad_collector.collect.side_effect = Exception("Collector crashed")
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = [good_collector, bad_collector]
                MockRegistry.return_value = mock_registry
                
                # Should not raise, should return partial results
                result = pipeline.execute(sample_repo, sample_classification)
                
                assert 'metadata' in result
                assert 'health' in result  # Good collector succeeded
    
    def test_nonexistent_repo_path(self, pipeline, sample_classification):
        """Test handling of nonexistent repository path."""
        fake_path = Path("/nonexistent/path/to/repo")
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = []
                MockRegistry.return_value = mock_registry
                
                # Should handle gracefully
                result = pipeline.execute(fake_path, sample_classification)
                
                assert 'metadata' in result
                assert result['metadata']['repo_name'] == 'repo'


# ========== Cache Integration Tests ==========

class TestCacheIntegration:
    """Test file cache integration."""
    
    def test_cache_disabled(self):
        """Test pipeline with cache disabled."""
        pipeline = DataCollectionPipeline(use_cache=False)
        
        cache = pipeline._get_file_cache()
        assert cache is None
    
    def test_cache_enabled(self):
        """Test pipeline with cache enabled."""
        pipeline = DataCollectionPipeline(use_cache=True)
        
        with patch('src.cortex_lens.utils.file_cache.get_global_cache') as mock_get_cache:
            mock_cache = Mock()
            mock_get_cache.return_value = mock_cache
            
            cache = pipeline._get_file_cache()
            
            assert cache is mock_cache
            mock_get_cache.assert_called_once_with(max_size_mb=100)


# ========== Result Structure Tests ==========

class TestResultStructure:
    """Test result data structure and validation."""
    
    def test_metadata_structure(self, pipeline, sample_repo, sample_classification):
        """Test that metadata has required fields."""
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = []
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                metadata = result['metadata']
                assert 'repo_name' in metadata
                assert 'repo_type' in metadata
                assert 'scan_timestamp' in metadata
                assert 'cortex_version' in metadata
                assert 'classification' in metadata
    
    def test_timestamp_format(self, pipeline, sample_repo, sample_classification):
        """Test that timestamp is valid ISO format."""
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = []
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                timestamp = result['metadata']['scan_timestamp']
                # Should parse without error
                datetime.fromisoformat(timestamp)
    
    def test_collector_results_merged(self, pipeline, sample_repo, sample_classification):
        """Test that collector results are properly merged."""
        c1 = Mock()
        c1.name = 'health'
        c1.collect.return_value = {'status': 'ok'}
        
        c2 = Mock()
        c2.name = 'security'
        c2.collect.return_value = {'vulns': 0}
        
        with patch.object(pipeline, '_register_builtin_collectors'):
            with patch('src.cortex_lens.collectors.registry.CollectorRegistry') as MockRegistry:
                mock_registry = Mock()
                mock_registry.get_collectors_for_type.return_value = [c1, c2]
                MockRegistry.return_value = mock_registry
                
                result = pipeline.execute(sample_repo, sample_classification)
                
                # Should have metadata + both collectors
                assert len(result) == 3
                assert all(key in result for key in ['metadata', 'health', 'security'])
