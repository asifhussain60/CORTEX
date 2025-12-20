"""
Performance Benchmark Suite for CORTEX Lens

Establishes performance baselines and tracks improvements/regressions.
Run periodically to ensure performance targets are met.

Author: Asif Hussain
"""

import pytest
import time
import psutil
from pathlib import Path
from datetime import datetime

from cortex_lens.core.performance import PerformanceConfig
from cortex_lens.utils.file_cache import FileCache
from cortex_lens.utils.progress import ProgressReporter


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.fixture
    def benchmark_repo(self, tmp_path):
        """Create benchmark repository with known characteristics."""
        repo = tmp_path / "benchmark_repo"
        repo.mkdir()
        
        # Create 100 Python files (simulating ~10K LOC)
        for i in range(100):
            file_path = repo / f"module_{i}.py"
            content = f'''"""Module {i} documentation."""

def function_{i}_1():
    """Function {i}_1 documentation."""
    return {i} * 2

def function_{i}_2():
    """Function {i}_2 documentation."""
    return {i} + 10

class Class_{i}:
    """Class {i} documentation."""
    
    def method_1(self):
        return {i}
    
    def method_2(self):
        return function_{i}_1() + function_{i}_2()
'''
            file_path.write_text(content)
        
        return repo
    
    def test_performance_config_overhead(self, benchmark):
        """Benchmark: PerformanceConfig.detect() overhead."""
        def detect():
            return PerformanceConfig.detect()
        
        result = benchmark(detect)
        assert result.optimal_workers >= 1
        
        # Target: <50ms
        stats = benchmark.stats.stats
        mean_time = stats['mean']
        assert mean_time < 0.05, f"Config detection: {mean_time*1000:.1f}ms (target: <50ms)"
    
    def test_file_cache_read_performance(self, tmp_path, benchmark):
        """Benchmark: FileCache read performance."""
        cache = FileCache(max_size_mb=50)
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content " * 10000)  # ~120KB
        
        # Warmup
        cache.read_file(test_file)
        
        def read_cached():
            return cache.read_file(test_file)
        
        result = benchmark(read_cached)
        assert result is not None
        
        # Target: <1ms for cached read
        stats = benchmark.stats.stats
        mean_time = stats['mean']
        assert mean_time < 0.001, f"Cached read: {mean_time*1000:.3f}ms (target: <1ms)"
    
    def test_file_cache_miss_performance(self, tmp_path, benchmark):
        """Benchmark: FileCache read performance (cache miss)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content " * 10000)  # ~120KB
        
        def read_uncached():
            cache = FileCache(max_size_mb=50)
            return cache.read_file(test_file)
        
        result = benchmark(read_uncached)
        assert result is not None
        
        # Target: <10ms for disk read
        stats = benchmark.stats.stats
        mean_time = stats['mean']
        assert mean_time < 0.01, f"Uncached read: {mean_time*1000:.1f}ms (target: <10ms)"
    
    def test_progress_reporter_overhead(self, benchmark):
        """Benchmark: ProgressReporter overhead."""
        reporter = ProgressReporter("Test Operation", total_phases=1)
        reporter.start_phase("test", "Testing", 100)
        
        def update_progress():
            reporter.update_phase(1, "Processing item")
        
        benchmark(update_progress)
        
        # Target: <1ms per update
        stats = benchmark.stats.stats
        mean_time = stats['mean']
        assert mean_time < 0.001, f"Progress update: {mean_time*1000:.3f}ms (target: <1ms)"
    
    @pytest.mark.slow
    def test_memory_scaling(self, tmp_path):
        """Benchmark: Memory usage scaling with cache size."""
        process = psutil.Process()
        
        measurements = []
        
        for cache_size_mb in [10, 50, 100, 200]:
            # Create cache
            cache = FileCache(max_size_mb=cache_size_mb)
            
            # Fill cache
            for i in range(100):
                test_file = tmp_path / f"file_{i}.txt"
                test_file.write_text(f"Content {i} " * 1000)
                cache.read_file(test_file)
            
            # Measure memory
            memory_mb = process.memory_info().rss / 1024 / 1024
            measurements.append((cache_size_mb, memory_mb))
            
            # Clear cache
            cache.clear()
        
        # Log measurements
        print("\nMemory Scaling:")
        for cache_size, memory in measurements:
            print(f"  Cache {cache_size} MB → Memory {memory:.1f} MB")
        
        # Validate linear scaling (approximately)
        assert measurements[-1][1] < measurements[-1][0] * 3, "Memory usage exceeds 3x cache size"


@pytest.mark.performance
class TestPerformanceTargets:
    """Validate performance targets from plan."""
    
    def test_small_repo_target(self, tmp_path):
        """Target: 10K LOC analyzed in <2 minutes."""
        # Simulated small repo
        repo = tmp_path / "small_repo"
        repo.mkdir()
        
        # Create 50 files (~10K LOC)
        for i in range(50):
            file_path = repo / f"module_{i}.py"
            content = "def func():\n    pass\n" * 100  # ~200 LOC per file
            file_path.write_text(content)
        
        from cortex_lens import CortexLens
        lens = CortexLens()
        
        start = time.time()
        result = lens.scan(str(repo))
        elapsed = time.time() - start
        
        assert elapsed < 120, f"Small repo analysis: {elapsed:.1f}s (target: <120s)"
        print(f"✅ Small repo (10K LOC): {elapsed:.2f}s")
    
    def test_memory_target_small_repo(self, tmp_path):
        """Target: <100MB memory for 10K LOC."""
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024
        
        # Simulated small repo
        repo = tmp_path / "small_repo"
        repo.mkdir()
        for i in range(50):
            (repo / f"module_{i}.py").write_text("def func(): pass\n" * 100)
        
        from cortex_lens import CortexLens
        lens = CortexLens()
        result = lens.scan(str(repo))
        
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before
        
        assert memory_used < 100, f"Memory used: {memory_used:.1f} MB (target: <100 MB)"
        print(f"✅ Memory usage (10K LOC): {memory_used:.1f} MB")


def pytest_benchmark_compare_failed(config, benchmarks, last_benchmarks):
    """Custom handler for benchmark comparison failures."""
    print("\n⚠️  Performance Regression Detected!")
    print("Review benchmark results and investigate slowdowns.")


if __name__ == '__main__':
    # Run benchmarks standalone
    pytest.main([__file__, '-v', '--benchmark-only', '--benchmark-autosave'])
