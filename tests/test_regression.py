"""
Regression Test Suite for CORTEX Lens

Baseline tests to detect performance/functionality degradation.
Run before major changes to establish baseline, after to validate.

Author: Asif Hussain
"""

import pytest
import time
import psutil
from pathlib import Path
from datetime import datetime

from cortex_lens import CortexLens
from cortex_lens.core.performance import PerformanceConfig
from cortex_lens.utils.file_cache import FileCache


class TestRegressionBaseline:
    """Baseline tests for regression detection."""
    
    @pytest.fixture
    def sample_repo_path(self, tmp_path):
        """Create minimal sample repository for testing."""
        repo = tmp_path / "sample_repo"
        repo.mkdir()
        
        # Create Python file
        (repo / "main.py").write_text("""
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
""")
        
        # Create requirements.txt
        (repo / "requirements.txt").write_text("pytest>=8.0.0\n")
        
        # Create README
        (repo / "README.md").write_text("# Sample Repository\n\nTest project.")
        
        return repo
    
    @pytest.mark.regression
    def test_performance_config_detection_speed(self):
        """Performance config detection should be <100ms."""
        start = time.time()
        config = PerformanceConfig.detect()
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Config detection took {elapsed:.3f}s (baseline: <0.1s)"
        assert config.optimal_workers >= 1
        assert config.memory_total_gb > 0
    
    @pytest.mark.regression
    def test_file_cache_performance(self, tmp_path):
        """File cache should provide >80% hit rate on repeated reads."""
        cache = FileCache(max_size_mb=10)
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content " * 1000)
        
        # First read (miss)
        content1 = cache.read_file(test_file)
        assert content1 is not None
        
        # Subsequent reads (hits)
        for _ in range(10):
            content = cache.read_file(test_file)
            assert content == content1
        
        stats = cache.get_stats()
        assert stats['hit_rate_percent'] > 80, f"Hit rate {stats['hit_rate_percent']}% < 80%"
    
    @pytest.mark.regression
    @pytest.mark.slow
    def test_basic_analysis_speed(self, sample_repo_path):
        """Basic repository analysis should complete <5s for small repo."""
        lens = CortexLens()
        
        start = time.time()
        result = lens.scan(str(sample_repo_path))
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Analysis took {elapsed:.1f}s (baseline: <5s)"
        assert result['classification']['primary_type'] in ['console_app', 'library_package']
    
    @pytest.mark.regression
    def test_memory_footprint(self, sample_repo_path):
        """Analysis should not leak memory or exceed reasonable limits."""
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        lens = CortexLens()
        result = lens.scan(str(sample_repo_path))
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        assert memory_used < 100, f"Memory used {memory_used:.1f} MB (baseline: <100 MB)"
    
    @pytest.mark.regression
    def test_import_times(self):
        """Module imports should be fast (<500ms total)."""
        import_times = {}
        
        modules = [
            'cortex_lens',
            'cortex_lens.core.classifier',
            'cortex_lens.analyzers.python_analyzer',
            'cortex_lens.collectors.health',
            'cortex_lens.core.performance',
        ]
        
        total_time = 0
        for module_name in modules:
            start = time.time()
            __import__(module_name)
            elapsed = time.time() - start
            import_times[module_name] = elapsed
            total_time += elapsed
        
        assert total_time < 0.5, f"Total import time {total_time:.3f}s (baseline: <0.5s)"
        
        # Log individual times for monitoring
        for module, elapsed in import_times.items():
            print(f"  {module}: {elapsed*1000:.1f}ms")


class TestRegressionValidation:
    """Validation tests to ensure no functionality breaks."""
    
    @pytest.mark.regression
    def test_all_base_classes_importable(self):
        """All base classes should import without errors."""
        from cortex_lens.analyzers.base import BaseAnalyzer
        from cortex_lens.collectors.base import BaseCollector
        from cortex_lens.generators.base import BaseGenerator
        
        assert BaseAnalyzer is not None
        assert BaseCollector is not None
        assert BaseGenerator is not None
    
    @pytest.mark.regression
    def test_registries_functional(self):
        """Plugin registries should be functional."""
        from cortex_lens.analyzers.registry import AnalyzerRegistry
        from cortex_lens.collectors.registry import CollectorRegistry
        
        # Check built-in analyzers registered
        python_analyzer = AnalyzerRegistry.get('python')
        assert python_analyzer is not None
        
        # Check built-in collectors registered
        health_collector = CollectorRegistry.get('health')
        assert health_collector is not None
    
    @pytest.mark.regression
    def test_performance_config_values_reasonable(self):
        """Performance config should detect reasonable values."""
        config = PerformanceConfig.detect()
        
        assert 1 <= config.cpu_count <= 256
        assert 1 <= config.physical_cores <= config.cpu_count
        assert 1 <= config.optimal_workers <= config.cpu_count
        assert 0.5 <= config.memory_total_gb <= 2048  # 512MB to 2TB
        assert 10 <= config.cache_size_mb <= 500
    
    @pytest.mark.regression
    def test_file_cache_thread_safety(self, tmp_path):
        """File cache should be thread-safe."""
        import threading
        
        cache = FileCache(max_size_mb=10)
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        errors = []
        
        def worker():
            try:
                for _ in range(100):
                    content = cache.read_file(test_file)
                    assert content is not None
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        stats = cache.get_stats()
        assert stats['total_requests'] == 500  # 5 threads × 100 reads


@pytest.fixture(scope="session")
def regression_baseline_file(tmp_path_factory):
    """
    Create/load regression baseline file.
    
    Stores baseline metrics for comparison:
    - Performance timings
    - Memory usage
    - Cache hit rates
    """
    baseline_file = tmp_path_factory.getbasetemp() / "regression_baseline.json"
    
    if not baseline_file.exists():
        # Create initial baseline
        import json
        baseline = {
            'created': datetime.now().isoformat(),
            'metrics': {
                'config_detection_ms': 100,
                'cache_hit_rate_percent': 80,
                'small_repo_analysis_seconds': 5,
                'memory_footprint_mb': 100,
                'import_time_ms': 500
            }
        }
        baseline_file.write_text(json.dumps(baseline, indent=2))
    
    return baseline_file


def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "regression: Regression tests (baseline validation)"
    )
