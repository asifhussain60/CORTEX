"""
Tests for Performance Configuration

Tests system detection, resource calculation, performance configuration,
and dynamic scaling decisions.
"""

import pytest
from unittest.mock import Mock, patch
from src.cortex_lens.core.performance import PerformanceConfig


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_system_4core_8gb():
    """Mock system with 4 cores, 8GB RAM"""
    with patch('src.cortex_lens.core.performance.os.cpu_count', return_value=8), \
         patch('src.cortex_lens.core.performance.psutil.cpu_count') as mock_cpu, \
         patch('src.cortex_lens.core.performance.psutil.virtual_memory') as mock_mem:
        
        mock_cpu.return_value = 4  # 4 physical cores
        
        mock_memory = Mock()
        mock_memory.total = 8 * (1024 ** 3)  # 8GB
        mock_memory.available = 6 * (1024 ** 3)  # 6GB available
        mock_memory.percent = 25.0
        mock_mem.return_value = mock_memory
        
        yield


@pytest.fixture
def mock_system_8core_16gb():
    """Mock system with 8 cores, 16GB RAM"""
    with patch('src.cortex_lens.core.performance.os.cpu_count', return_value=16), \
         patch('src.cortex_lens.core.performance.psutil.cpu_count') as mock_cpu, \
         patch('src.cortex_lens.core.performance.psutil.virtual_memory') as mock_mem:
        
        mock_cpu.return_value = 8  # 8 physical cores
        
        mock_memory = Mock()
        mock_memory.total = 16 * (1024 ** 3)  # 16GB
        mock_memory.available = 12 * (1024 ** 3)  # 12GB available
        mock_memory.percent = 25.0
        mock_mem.return_value = mock_memory
        
        yield


@pytest.fixture
def mock_system_low_memory():
    """Mock system with low available memory"""
    with patch('src.cortex_lens.core.performance.os.cpu_count', return_value=8), \
         patch('src.cortex_lens.core.performance.psutil.cpu_count') as mock_cpu, \
         patch('src.cortex_lens.core.performance.psutil.virtual_memory') as mock_mem:
        
        mock_cpu.return_value = 4  # 4 physical cores
        
        mock_memory = Mock()
        mock_memory.total = 8 * (1024 ** 3)  # 8GB
        mock_memory.available = 1 * (1024 ** 3)  # Only 1GB available
        mock_memory.percent = 87.5  # High memory usage
        mock_mem.return_value = mock_memory
        
        yield


@pytest.fixture
def mock_system_single_core():
    """Mock single-core system"""
    with patch('src.cortex_lens.core.performance.os.cpu_count', return_value=1), \
         patch('src.cortex_lens.core.performance.psutil.cpu_count') as mock_cpu, \
         patch('src.cortex_lens.core.performance.psutil.virtual_memory') as mock_mem:
        
        mock_cpu.return_value = 1  # 1 physical core
        
        mock_memory = Mock()
        mock_memory.total = 4 * (1024 ** 3)  # 4GB
        mock_memory.available = 2 * (1024 ** 3)  # 2GB available
        mock_memory.percent = 50.0
        mock_mem.return_value = mock_memory
        
        yield


# ============================================================================
# Test Configuration Detection
# ============================================================================

class TestConfigurationDetection:
    """Test PerformanceConfig.detect() system detection"""
    
    def test_detect_4core_8gb_system(self, mock_system_4core_8gb):
        """Detect 4-core, 8GB system correctly"""
        config = PerformanceConfig.detect()
        
        assert config.cpu_count == 8
        assert config.physical_cores == 4
        assert config.memory_total_gb == 8.0
        assert config.memory_available_gb == 6.0
        
        # Workers should be physical_cores - 1 = 3
        assert config.optimal_workers == 3
        assert config.max_workers >= config.optimal_workers
    
    def test_detect_8core_16gb_system(self, mock_system_8core_16gb):
        """Detect 8-core, 16GB system correctly"""
        config = PerformanceConfig.detect()
        
        assert config.cpu_count == 16
        assert config.physical_cores == 8
        assert config.memory_total_gb == 16.0
        assert config.memory_available_gb == 12.0
        
        # Workers should be physical_cores - 1 = 7
        assert config.optimal_workers == 7
    
    def test_detect_single_core_system(self, mock_system_single_core):
        """Single-core system should have at least 1 worker"""
        config = PerformanceConfig.detect()
        
        assert config.physical_cores == 1
        # Should be at least 1 worker even on single-core
        assert config.optimal_workers >= 1
    
    def test_detect_low_memory_system(self, mock_system_low_memory):
        """Low memory should limit worker count"""
        config = PerformanceConfig.detect()
        
        # Only 1GB available / 0.5GB per worker = 2 workers max
        # Should be less than physical cores (4)
        assert config.optimal_workers <= 2


# ============================================================================
# Test User Override
# ============================================================================

class TestUserOverride:
    """Test user-specified worker count override"""
    
    def test_user_workers_override(self, mock_system_4core_8gb):
        """User-specified workers should override auto-detection"""
        config = PerformanceConfig.detect(user_workers=10)
        
        assert config.optimal_workers == 10
    
    def test_user_workers_one(self, mock_system_4core_8gb):
        """User can specify single worker"""
        config = PerformanceConfig.detect(user_workers=1)
        
        assert config.optimal_workers == 1
    
    def test_no_user_override(self, mock_system_4core_8gb):
        """None user_workers should use auto-detection"""
        config = PerformanceConfig.detect(user_workers=None)
        
        # Should be auto-detected (physical_cores - 1 = 3)
        assert config.optimal_workers == 3


# ============================================================================
# Test Cache Sizing
# ============================================================================

class TestCacheSizing:
    """Test cache size calculation"""
    
    def test_cache_size_with_6gb_available(self, mock_system_4core_8gb):
        """Cache should be 10% of available memory"""
        config = PerformanceConfig.detect()
        
        # 6GB available * 0.1 * 1024 = 614.4MB, capped at 500MB
        assert config.cache_size_mb == 500  # Capped at 500MB
    
    def test_cache_size_with_low_memory(self, mock_system_low_memory):
        """Low memory should result in smaller cache"""
        config = PerformanceConfig.detect()
        
        # 1GB available * 0.1 * 1024 = 102.4MB (under cap)
        assert config.cache_size_mb < 500
        assert config.cache_size_mb > 0


# ============================================================================
# Test Memory Limits
# ============================================================================

class TestMemoryLimits:
    """Test memory limit calculation per worker"""
    
    def test_memory_limit_per_worker(self, mock_system_4core_8gb):
        """Memory limit should be 90% available / workers"""
        config = PerformanceConfig.detect()
        
        # 6GB * 0.9 / 3 workers = 1.8GB per worker
        assert config.memory_limit_gb > 0
        assert config.memory_limit_gb <= config.memory_available_gb
    
    def test_memory_limit_with_many_workers(self, mock_system_8core_16gb):
        """More workers should reduce per-worker memory limit"""
        config = PerformanceConfig.detect()
        
        # 12GB * 0.9 / 7 workers ≈ 1.54GB per worker
        assert config.memory_limit_gb > 0
        assert config.memory_limit_gb < 2.0  # Should be reasonable


# ============================================================================
# Test to_dict() Method
# ============================================================================

class TestToDictMethod:
    """Test to_dict() serialization"""
    
    def test_to_dict_contains_all_fields(self, mock_system_4core_8gb):
        """to_dict() should contain all config fields"""
        config = PerformanceConfig.detect()
        result = config.to_dict()
        
        assert 'cpu_count' in result
        assert 'physical_cores' in result
        assert 'memory_total_gb' in result
        assert 'memory_available_gb' in result
        assert 'optimal_workers' in result
        assert 'max_workers' in result
        assert 'cache_size_mb' in result
        assert 'memory_limit_gb' in result
    
    def test_to_dict_values_match(self, mock_system_4core_8gb):
        """to_dict() values should match config attributes"""
        config = PerformanceConfig.detect()
        result = config.to_dict()
        
        assert result['cpu_count'] == config.cpu_count
        assert result['physical_cores'] == config.physical_cores
        assert result['optimal_workers'] == config.optimal_workers
        assert result['cache_size_mb'] == config.cache_size_mb
    
    def test_to_dict_is_serializable(self, mock_system_4core_8gb):
        """to_dict() result should be JSON-serializable"""
        import json
        
        config = PerformanceConfig.detect()
        result = config.to_dict()
        
        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None


# ============================================================================
# Test validate_memory_usage() Method
# ============================================================================

class TestValidateMemoryUsage:
    """Test validate_memory_usage() method"""
    
    def test_validate_memory_within_limits(self, mock_system_4core_8gb):
        """Memory usage under 90% of limit should be valid"""
        config = PerformanceConfig.detect()
        
        # Use 50% of memory limit
        current_usage = config.memory_limit_gb * 0.5
        
        assert config.validate_memory_usage(current_usage) is True
    
    def test_validate_memory_approaching_limit(self, mock_system_4core_8gb):
        """Memory usage over 90% of limit should be invalid"""
        config = PerformanceConfig.detect()
        
        # Use 95% of memory limit
        current_usage = config.memory_limit_gb * 0.95
        
        assert config.validate_memory_usage(current_usage) is False
    
    def test_validate_memory_at_exact_limit(self, mock_system_4core_8gb):
        """Memory usage at exact limit should be invalid"""
        config = PerformanceConfig.detect()
        
        current_usage = config.memory_limit_gb
        
        assert config.validate_memory_usage(current_usage) is False
    
    def test_validate_memory_zero_usage(self, mock_system_4core_8gb):
        """Zero memory usage should be valid"""
        config = PerformanceConfig.detect()
        
        assert config.validate_memory_usage(0.0) is True


# ============================================================================
# Test should_scale_down() Method
# ============================================================================

class TestShouldScaleDown:
    """Test should_scale_down() method"""
    
    def test_should_not_scale_down_normal_memory(self, mock_system_4core_8gb):
        """Normal memory usage should not trigger scale down"""
        config = PerformanceConfig.detect()
        
        # Mock has 25% memory usage
        assert config.should_scale_down() is False
    
    def test_should_scale_down_high_memory(self, mock_system_low_memory):
        """High memory usage should trigger scale down"""
        config = PerformanceConfig.detect()
        
        # Mock has 87.5% memory usage
        assert config.should_scale_down() is True
    
    def test_should_scale_down_threshold_85(self, mock_system_4core_8gb):
        """Threshold should be 85%"""
        config = PerformanceConfig.detect()
        
        # Patch memory to be exactly 85%
        with patch('src.cortex_lens.core.performance.psutil.virtual_memory') as mock_mem:
            mock_memory = Mock()
            mock_memory.percent = 85.0
            mock_mem.return_value = mock_memory
            
            # At threshold, should not scale down (> 85, not >= 85)
            assert config.should_scale_down() is False
        
        # Patch memory to be 86%
        with patch('src.cortex_lens.core.performance.psutil.virtual_memory') as mock_mem:
            mock_memory = Mock()
            mock_memory.percent = 86.0
            mock_mem.return_value = mock_memory
            
            # Above threshold, should scale down
            assert config.should_scale_down() is True


# ============================================================================
# Test get_chunk_size() Method
# ============================================================================

class TestGetChunkSize:
    """Test get_chunk_size() calculation"""
    
    def test_chunk_size_for_small_dataset(self, mock_system_4core_8gb):
        """Small dataset should use minimum chunk size"""
        config = PerformanceConfig.detect()
        
        # 50 items / (3 workers * 4) = 4.17, clamped to min 10
        chunk_size = config.get_chunk_size(50)
        
        assert chunk_size == 10  # Minimum
    
    def test_chunk_size_for_medium_dataset(self, mock_system_4core_8gb):
        """Medium dataset should use calculated chunk size"""
        config = PerformanceConfig.detect()
        
        # 500 items / (3 workers * 4) = 41.67
        chunk_size = config.get_chunk_size(500)
        
        assert 10 <= chunk_size <= 100  # Within bounds
        assert chunk_size >= 10
    
    def test_chunk_size_for_large_dataset(self, mock_system_4core_8gb):
        """Large dataset should use maximum chunk size"""
        config = PerformanceConfig.detect()
        
        # 10000 items / (3 workers * 4) = 833, clamped to max 100
        chunk_size = config.get_chunk_size(10000)
        
        assert chunk_size == 100  # Maximum
    
    def test_chunk_size_minimum_bound(self, mock_system_4core_8gb):
        """Chunk size should never be less than 10"""
        config = PerformanceConfig.detect()
        
        # Very small dataset
        chunk_size = config.get_chunk_size(5)
        
        assert chunk_size >= 10
    
    def test_chunk_size_maximum_bound(self, mock_system_4core_8gb):
        """Chunk size should never exceed 100"""
        config = PerformanceConfig.detect()
        
        # Very large dataset
        chunk_size = config.get_chunk_size(100000)
        
        assert chunk_size <= 100


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_max_workers_never_less_than_optimal(self, mock_system_4core_8gb):
        """max_workers should always be >= optimal_workers"""
        config = PerformanceConfig.detect()
        
        assert config.max_workers >= config.optimal_workers
    
    def test_optimal_workers_always_positive(self, mock_system_single_core):
        """optimal_workers should always be at least 1"""
        config = PerformanceConfig.detect()
        
        assert config.optimal_workers >= 1
    
    def test_memory_values_are_rounded(self, mock_system_4core_8gb):
        """Memory values should be rounded to 2 decimal places"""
        config = PerformanceConfig.detect()
        
        # Check that values are rounded (no more than 2 decimal places)
        assert config.memory_total_gb == round(config.memory_total_gb, 2)
        assert config.memory_available_gb == round(config.memory_available_gb, 2)
        assert config.memory_limit_gb == round(config.memory_limit_gb, 2)
    
    def test_config_is_dataclass(self, mock_system_4core_8gb):
        """PerformanceConfig should be a dataclass"""
        config = PerformanceConfig.detect()
        
        # Dataclass instances have __dataclass_fields__
        assert hasattr(config, '__dataclass_fields__')
    
    def test_zero_total_items_chunk_size(self, mock_system_4core_8gb):
        """Zero total items should return minimum chunk size"""
        config = PerformanceConfig.detect()
        
        chunk_size = config.get_chunk_size(0)
        
        assert chunk_size >= 10


# ============================================================================
# Test Logging
# ============================================================================

class TestLogging:
    """Test logging behavior"""
    
    def test_detect_logs_configuration(self, mock_system_4core_8gb, caplog):
        """detect() should log configuration details"""
        import logging
        
        with caplog.at_level(logging.INFO):
            config = PerformanceConfig.detect()
        
        log_text = caplog.text
        
        # Should log performance config info
        assert 'Performance Config' in log_text or 'CPU' in log_text or 'Workers' in log_text
