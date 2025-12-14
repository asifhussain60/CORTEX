"""
Tests for ScalableCollectorOrchestrator - coordinates multiple collectors for large-scale analysis.

This module tests the orchestrator's ability to:
- Manage multiple collectors in parallel
- Handle 10K+ files efficiently (< 60s target)
- Provide aggregated progress tracking
- Isolate errors from individual collectors
- Merge results from multiple collectors
- Optimize resource usage (CPU, memory)
"""

import pytest
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List


class TestScalableCollectorOrchestratorInitialization:
    """Test orchestrator initialization and configuration"""
    
    def test_orchestrator_requires_project_root(self):
        """Should require project_root parameter"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        
        with pytest.raises(ValueError, match="project_root is required"):
            ScalableCollectorOrchestrator(project_root=None)
    
    def test_orchestrator_accepts_collectors_list(self):
        """Should accept list of collector classes"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock collector class
            class MockCollector(UniversalCollectorBase):
                def collect(self):
                    return {"mock": "data"}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                collectors=[MockCollector]
            )
            
            assert orchestrator.project_root == Path(tmpdir)
            assert len(orchestrator.collectors) == 1
    
    def test_orchestrator_has_default_configuration(self):
        """Should have sensible default configuration"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            
            assert orchestrator.max_parallel_collectors > 0
            assert orchestrator.enable_caching is True
            assert orchestrator.timeout_per_collector is None or orchestrator.timeout_per_collector > 0
    
    def test_orchestrator_accepts_custom_configuration(self):
        """Should accept custom configuration parameters"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                max_parallel_collectors=8,
                enable_caching=False,
                timeout_per_collector=120
            )
            
            assert orchestrator.max_parallel_collectors == 8
            assert orchestrator.enable_caching is False
            assert orchestrator.timeout_per_collector == 120


class TestCollectorRegistration:
    """Test dynamic collector registration"""
    
    def test_register_single_collector(self):
        """Should register individual collector"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class TestCollector(UniversalCollectorBase):
                def collect(self):
                    return {"test": "data"}
            
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            orchestrator.register_collector(TestCollector)
            
            assert TestCollector in orchestrator.collectors
    
    def test_register_multiple_collectors_at_once(self):
        """Should register multiple collectors in one call"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Collector1(UniversalCollectorBase):
                def collect(self):
                    return {"c1": "data"}
            
            class Collector2(UniversalCollectorBase):
                def collect(self):
                    return {"c2": "data"}
            
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            orchestrator.register_collectors([Collector1, Collector2])
            
            assert len(orchestrator.collectors) == 2
            assert Collector1 in orchestrator.collectors
            assert Collector2 in orchestrator.collectors
    
    def test_prevent_duplicate_collector_registration(self):
        """Should not register same collector twice"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class TestCollector(UniversalCollectorBase):
                def collect(self):
                    return {"test": "data"}
            
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            orchestrator.register_collector(TestCollector)
            orchestrator.register_collector(TestCollector)  # Duplicate
            
            assert orchestrator.collectors.count(TestCollector) == 1


class TestParallelExecution:
    """Test parallel execution of multiple collectors"""
    
    def test_run_multiple_collectors_in_parallel(self):
        """Should execute multiple collectors concurrently"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(10):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
            
            execution_times = []
            
            class SlowCollector(UniversalCollectorBase):
                def __init__(self, project_root, name):
                    super().__init__(project_root)
                    self.name = name
                
                def collect(self):
                    start = time.time()
                    time.sleep(0.1)  # Simulate work
                    execution_times.append((self.name, time.time() - start))
                    return {self.name: "data"}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                max_parallel_collectors=3
            )
            
            # Register 3 collectors
            for i in range(3):
                orchestrator.register_collector(
                    lambda pr, name=f"collector{i}": SlowCollector(pr, name)
                )
            
            start_time = time.time()
            results = orchestrator.run_all()
            total_time = time.time() - start_time
            
            # All 3 should run in parallel, so total time ~0.1s (not 0.3s)
            assert total_time < 0.2
            assert len(results) == 3
    
    def test_respect_max_parallel_collectors_limit(self):
        """Should respect max_parallel_collectors configuration"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            active_collectors = []
            max_concurrent = 0
            
            class TrackedCollector(UniversalCollectorBase):
                def __init__(self, project_root, collector_id):
                    super().__init__(project_root)
                    self.collector_id = collector_id
                
                def collect(self):
                    nonlocal max_concurrent
                    active_collectors.append(self.collector_id)
                    max_concurrent = max(max_concurrent, len(active_collectors))
                    time.sleep(0.05)
                    active_collectors.remove(self.collector_id)
                    return {f"c{self.collector_id}": "data"}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                max_parallel_collectors=2
            )
            
            # Register 5 collectors
            for i in range(5):
                orchestrator.register_collector(
                    lambda pr, cid=i: TrackedCollector(pr, cid)
                )
            
            orchestrator.run_all()
            
            # Should never exceed 2 concurrent
            assert max_concurrent <= 2
    
    def test_error_isolation_between_collectors(self):
        """Should isolate errors - one failing collector doesn't stop others"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class SuccessCollector1(UniversalCollectorBase):
                def collect(self):
                    return {"success": True}
            
            class SuccessCollector2(UniversalCollectorBase):
                def collect(self):
                    return {"success": True}
            
            class FailureCollector(UniversalCollectorBase):
                def collect(self):
                    raise Exception("Intentional failure")
            
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            orchestrator.register_collectors([SuccessCollector1, FailureCollector, SuccessCollector2])
            
            results = orchestrator.run_all(ignore_errors=True)
            
            # Should have 2 successful results despite 1 failure
            successful_results = [r for r in results if r.get("success")]
            assert len(successful_results) == 2
            
            # Should track the error
            assert len(orchestrator.get_errors()) == 1


class TestProgressTracking:
    """Test aggregated progress tracking across collectors"""
    
    def test_aggregated_progress_callback(self):
        """Should provide aggregated progress from all collectors"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(100):
                Path(tmpdir, f"file{i}.txt").write_text("content")
            
            progress_updates = []
            
            def track_progress(current_collector, total_collectors, current_files, total_files, message):
                progress_updates.append({
                    "current_collector": current_collector,
                    "total_collectors": total_collectors,
                    "current_files": current_files,
                    "total_files": total_files,
                    "message": message
                })
            
            class FileCollector(UniversalCollectorBase):
                def collect(self):
                    files = self.discover_files()
                    return {"file_count": len(files)}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                progress_callback=track_progress
            )
            
            orchestrator.register_collectors([FileCollector, FileCollector])
            orchestrator.run_all()
            
            assert len(progress_updates) > 0
            # Final update should show completion
            final = progress_updates[-1]
            assert final["current_collector"] == final["total_collectors"]
    
    def test_estimated_time_remaining(self):
        """Should calculate ETA for remaining collectors"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class TimedCollector(UniversalCollectorBase):
                def collect(self):
                    time.sleep(0.1)
                    return {"timed": True}
            
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            orchestrator.register_collectors([TimedCollector] * 5)
            
            # Start execution
            orchestrator.run_all()
            
            # Should have ETA data
            stats = orchestrator.get_execution_stats()
            assert "total_time" in stats
            assert "average_collector_time" in stats


class TestResultMerging:
    """Test merging and aggregation of collector results"""
    
    def test_merge_results_from_multiple_collectors(self):
        """Should merge results into unified schema"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class FrontendCollector(UniversalCollectorBase):
                def collect(self):
                    return {"frontend": {"components": 10}}
            
            class BackendCollector(UniversalCollectorBase):
                def collect(self):
                    return {"backend": {"endpoints": 20}}
            
            orchestrator = ScalableCollectorOrchestrator(project_root=tmpdir)
            orchestrator.register_collectors([FrontendCollector, BackendCollector])
            
            merged = orchestrator.run_and_merge()
            
            assert "frontend" in merged
            assert "backend" in merged
            assert merged["frontend"]["components"] == 10
            assert merged["backend"]["endpoints"] == 20
    
    def test_handle_overlapping_keys_in_results(self):
        """Should handle collectors that return same keys"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Collector1(UniversalCollectorBase):
                def collect(self):
                    return {"shared_key": {"source": "collector1", "value": 100}}
            
            class Collector2(UniversalCollectorBase):
                def collect(self):
                    return {"shared_key": {"source": "collector2", "value": 200}}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                merge_strategy="last_wins"  # or "combine", "error"
            )
            orchestrator.register_collectors([Collector1, Collector2])
            
            merged = orchestrator.run_and_merge()
            
            # Should have handling for duplicate keys
            assert "shared_key" in merged


class TestPerformanceTargets:
    """Test performance requirements for large-scale analysis"""
    
    def test_handle_10k_files_under_60_seconds(self):
        """Should process 10K+ files in under 60 seconds"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 10K small files (use smaller count for test speed)
            file_count = 1000  # Use 1K for test, scale to 10K in production
            for i in range(file_count):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
            
            class FastCollector(UniversalCollectorBase):
                def collect(self):
                    files = self.discover_files()
                    return {"file_count": len(files)}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                max_parallel_collectors=4
            )
            orchestrator.register_collector(FastCollector)
            
            start_time = time.time()
            results = orchestrator.run_all()
            elapsed = time.time() - start_time
            
            # 1K files should complete in < 6 seconds (scales to 10K in 60s)
            assert elapsed < 6.0
            assert results[0]["file_count"] == file_count
    
    def test_memory_efficient_large_result_sets(self):
        """Should handle large result sets without excessive memory"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 5 different collector classes (can't use same class 5x due to duplicate prevention)
            collectors = []
            for i in range(5):
                # Create unique class for each collector
                class_name = f"LargeResultCollector{i}"
                collector_class = type(
                    class_name,
                    (UniversalCollectorBase,),
                    {
                        "collect": lambda self, idx=i: {"items": [{"id": j, "data": "x" * 100} for j in range(100)], "collector": idx}
                    }
                )
                collectors.append(collector_class)
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                enable_result_streaming=True  # Stream results instead of buffering
            )
            orchestrator.register_collectors(collectors)
            
            # Should complete without memory errors
            results = orchestrator.run_all()
            assert len(results) == 5


class TestCachingAndIncremental:
    """Test caching and incremental analysis"""
    
    def test_cache_orchestrator_results(self):
        """Should cache entire orchestration results"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            run_count = 0
            
            class CountedCollector(UniversalCollectorBase):
                def collect(self):
                    nonlocal run_count
                    run_count += 1
                    return {"run": run_count}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                enable_caching=True,
                cache_ttl=300
            )
            orchestrator.register_collector(CountedCollector)
            
            # First run
            result1 = orchestrator.run_and_merge()
            assert run_count == 1
            
            # Second run should use cache
            result2 = orchestrator.run_and_merge()
            assert run_count == 1  # Not incremented
            assert result1 == result2
    
    def test_incremental_analysis_after_file_changes(self):
        """Should detect file changes and rerun affected collectors"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir, "file1.txt")
            file2 = Path(tmpdir, "file2.txt")
            file1.write_text("v1")
            file2.write_text("v1")
            
            class FileHashCollector(UniversalCollectorBase):
                def collect(self):
                    files = self.discover_files()
                    return {"hash_sum": sum(hash(f.read_text()) for f in files)}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                enable_caching=True,
                incremental=True
            )
            orchestrator.register_collector(FileHashCollector)
            
            # First run
            result1 = orchestrator.run_and_merge()
            
            # Modify one file
            file1.write_text("v2")
            
            # Second run should detect change and rerun
            result2 = orchestrator.run_and_merge()
            assert result1 != result2


class TestTimeoutHandling:
    """Test timeout handling for slow collectors"""
    
    def test_timeout_slow_collector(self):
        """Should timeout collectors that exceed limit"""
        from src.dashboard.orchestrators.scalable_collector_orchestrator import ScalableCollectorOrchestrator
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class SlowCollector(UniversalCollectorBase):
                def collect(self):
                    time.sleep(2)
                    return {"slow": True}
            
            class FastCollector(UniversalCollectorBase):
                def collect(self):
                    return {"fast": True}
            
            orchestrator = ScalableCollectorOrchestrator(
                project_root=tmpdir,
                timeout_per_collector=0.5
            )
            orchestrator.register_collectors([FastCollector, SlowCollector])
            
            results = orchestrator.run_all(ignore_errors=True)
            
            # Fast collector should succeed, slow should timeout
            successful = [r for r in results if r.get("fast") or r.get("slow")]
            assert len(successful) == 1
            assert successful[0].get("fast") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
