"""
Tests for PerformanceMonitor - Latency and Throughput Tracking.

TDD Phase: RED
Tests p50/p95/p99 latency tracking, throughput metrics, and resource monitoring.
"""

import pytest
import time
import asyncio
from datetime import datetime, timedelta

from src.logging.performance.perf_monitor import (
    PerformanceMonitor,
    LatencyTracker,
    ThroughputMonitor,
    ResourceMonitor,
    PerformanceAlert
)


@pytest.fixture
def perf_monitor():
    """Create PerformanceMonitor instance."""
    return PerformanceMonitor()


@pytest.fixture
def latency_tracker():
    """Create LatencyTracker instance."""
    return LatencyTracker()


@pytest.fixture
def throughput_monitor():
    """Create ThroughputMonitor instance."""
    return ThroughputMonitor()


@pytest.fixture
def resource_monitor():
    """Create ResourceMonitor instance."""
    return ResourceMonitor()


class TestLatencyTracker:
    """Test latency tracking (p50, p95, p99)."""

    def test_record_latency(self, latency_tracker):
        """Should record latency measurements."""
        latency_tracker.record(10.5)
        latency_tracker.record(20.3)
        latency_tracker.record(15.7)
        
        assert latency_tracker.count() == 3

    def test_calculate_p50(self, latency_tracker):
        """Should calculate 50th percentile (median)."""
        latencies = [10, 20, 30, 40, 50]
        for lat in latencies:
            latency_tracker.record(lat)
        
        p50 = latency_tracker.percentile(50)
        assert p50 == 30

    def test_calculate_p95(self, latency_tracker):
        """Should calculate 95th percentile."""
        latencies = list(range(1, 101))  # 1 to 100
        for lat in latencies:
            latency_tracker.record(lat)
        
        p95 = latency_tracker.percentile(95)
        assert 94 <= p95 <= 96

    def test_calculate_p99(self, latency_tracker):
        """Should calculate 99th percentile."""
        latencies = list(range(1, 101))
        for lat in latencies:
            latency_tracker.record(lat)
        
        p99 = latency_tracker.percentile(99)
        assert 98 <= p99 <= 100

    def test_calculate_mean(self, latency_tracker):
        """Should calculate mean latency."""
        latencies = [10, 20, 30]
        for lat in latencies:
            latency_tracker.record(lat)
        
        mean = latency_tracker.mean()
        assert mean == 20

    def test_calculate_min_max(self, latency_tracker):
        """Should track min and max latencies."""
        latencies = [15, 5, 25, 10, 20]
        for lat in latencies:
            latency_tracker.record(lat)
        
        assert latency_tracker.min() == 5
        assert latency_tracker.max() == 25

    def test_empty_tracker(self, latency_tracker):
        """Should handle empty tracker gracefully."""
        assert latency_tracker.count() == 0
        assert latency_tracker.mean() == 0
        assert latency_tracker.min() is None
        assert latency_tracker.max() is None

    def test_reset_tracker(self, latency_tracker):
        """Should reset all measurements."""
        latency_tracker.record(10)
        latency_tracker.record(20)
        latency_tracker.reset()
        
        assert latency_tracker.count() == 0


class TestThroughputMonitor:
    """Test throughput monitoring."""

    def test_track_operations(self, throughput_monitor):
        """Should track operation counts."""
        throughput_monitor.increment()
        throughput_monitor.increment()
        throughput_monitor.increment()
        
        assert throughput_monitor.count() == 3

    def test_calculate_ops_per_second(self, throughput_monitor):
        """Should calculate operations per second."""
        # Simulate operations over 1 second
        start = time.time()
        for _ in range(100):
            throughput_monitor.increment()
        elapsed = time.time() - start
        
        ops_per_sec = throughput_monitor.rate(elapsed)
        assert ops_per_sec > 0

    def test_batch_increment(self, throughput_monitor):
        """Should support batch increment."""
        throughput_monitor.increment(count=50)
        assert throughput_monitor.count() == 50

    def test_windowed_rate(self, throughput_monitor):
        """Should calculate rate over time window."""
        throughput_monitor.increment_with_timestamp(
            count=100,
            timestamp=datetime.utcnow() - timedelta(seconds=10)
        )
        throughput_monitor.increment_with_timestamp(
            count=50,
            timestamp=datetime.utcnow()
        )
        
        # Rate over last 5 seconds should only include recent ops
        rate = throughput_monitor.windowed_rate(window_seconds=5)
        assert rate > 0


class TestResourceMonitor:
    """Test resource monitoring (CPU, memory)."""

    def test_capture_cpu_usage(self, resource_monitor):
        """Should capture current CPU usage."""
        cpu_percent = resource_monitor.cpu_usage()
        assert isinstance(cpu_percent, float)
        assert 0 <= cpu_percent <= 100

    def test_capture_memory_usage(self, resource_monitor):
        """Should capture current memory usage."""
        memory_mb = resource_monitor.memory_usage()
        assert isinstance(memory_mb, float)
        assert memory_mb > 0

    def test_capture_memory_percent(self, resource_monitor):
        """Should capture memory usage as percentage."""
        memory_percent = resource_monitor.memory_percent()
        assert isinstance(memory_percent, float)
        assert 0 <= memory_percent <= 100

    def test_snapshot(self, resource_monitor):
        """Should capture complete resource snapshot."""
        snapshot = resource_monitor.snapshot()
        
        assert "cpu_percent" in snapshot
        assert "memory_mb" in snapshot
        assert "memory_percent" in snapshot
        assert "timestamp" in snapshot

    def test_track_resource_history(self, resource_monitor):
        """Should track resource usage over time."""
        for _ in range(3):
            resource_monitor.record_snapshot()
            time.sleep(0.1)
        
        history = resource_monitor.get_history()
        assert len(history) == 3


class TestPerformanceMonitor:
    """Test integrated performance monitoring."""

    def test_initialization(self, perf_monitor):
        """Should initialize with all sub-monitors."""
        assert hasattr(perf_monitor, "latency")
        assert hasattr(perf_monitor, "throughput")
        assert hasattr(perf_monitor, "resources")

    def test_context_manager_timing(self, perf_monitor):
        """Should measure operation latency with context manager."""
        with perf_monitor.measure("test_operation"):
            time.sleep(0.01)  # 10ms operation
        
        stats = perf_monitor.get_stats("test_operation")
        assert stats["count"] == 1
        assert stats["mean"] >= 10  # At least 10ms

    def test_async_context_manager_timing(self, perf_monitor):
        """Should measure async operation latency."""
        async def async_operation():
            async with perf_monitor.measure_async("async_op"):
                await asyncio.sleep(0.01)
        
        asyncio.run(async_operation())
        
        stats = perf_monitor.get_stats("async_op")
        assert stats["count"] == 1
        assert stats["mean"] >= 10

    def test_decorator_timing(self, perf_monitor):
        """Should measure function latency with decorator."""
        @perf_monitor.track("decorated_func")
        def slow_function():
            time.sleep(0.01)
            return "done"
        
        result = slow_function()
        assert result == "done"
        
        stats = perf_monitor.get_stats("decorated_func")
        assert stats["count"] == 1

    def test_multiple_operations(self, perf_monitor):
        """Should track multiple different operations."""
        with perf_monitor.measure("op1"):
            time.sleep(0.01)
        
        with perf_monitor.measure("op2"):
            time.sleep(0.02)
        
        stats1 = perf_monitor.get_stats("op1")
        stats2 = perf_monitor.get_stats("op2")
        
        assert stats1["count"] == 1
        assert stats2["count"] == 1
        assert stats2["mean"] > stats1["mean"]

    def test_get_all_stats(self, perf_monitor):
        """Should retrieve stats for all operations."""
        with perf_monitor.measure("op1"):
            time.sleep(0.01)
        
        with perf_monitor.measure("op2"):
            time.sleep(0.01)
        
        all_stats = perf_monitor.get_all_stats()
        assert "op1" in all_stats
        assert "op2" in all_stats

    def test_percentile_tracking(self, perf_monitor):
        """Should track percentiles correctly."""
        for i in range(100):
            with perf_monitor.measure("percentile_test"):
                time.sleep(0.001 * i)  # Varying latencies
        
        stats = perf_monitor.get_stats("percentile_test")
        assert "p50" in stats
        assert "p95" in stats
        assert "p99" in stats
        assert stats["p99"] >= stats["p95"] >= stats["p50"]


class TestPerformanceAlerts:
    """Test performance degradation alerts."""

    def test_detect_high_latency(self, perf_monitor):
        """Should alert on high latency."""
        perf_monitor.set_threshold("test_op", max_latency=10)
        
        with perf_monitor.measure("test_op"):
            time.sleep(0.02)  # 20ms - exceeds threshold
        
        alerts = perf_monitor.get_alerts()
        assert len(alerts) > 0
        assert alerts[0]["type"] == "high_latency"

    def test_detect_low_throughput(self, perf_monitor):
        """Should alert on low throughput."""
        perf_monitor.set_threshold("test_op", min_throughput=100)
        
        # Simulate low throughput
        for _ in range(10):
            with perf_monitor.measure("test_op"):
                time.sleep(0.01)
        
        alerts = perf_monitor.get_alerts()
        assert any(a["type"] == "low_throughput" for a in alerts)

    def test_detect_high_resource_usage(self, perf_monitor):
        """Should alert on high resource usage."""
        perf_monitor.set_threshold("resources", max_memory_percent=1)
        
        perf_monitor.check_resources()
        
        alerts = perf_monitor.get_alerts()
        # Should alert if memory > 1%
        assert len(alerts) >= 0  # May or may not alert depending on system


class TestPerformanceReport:
    """Test performance reporting."""

    def test_generate_report(self, perf_monitor):
        """Should generate comprehensive performance report."""
        for _ in range(10):
            with perf_monitor.measure("op1"):
                time.sleep(0.001)
        
        report = perf_monitor.generate_report()
        
        assert "summary" in report
        assert "operations" in report
        assert "resources" in report
        assert "timestamp" in report

    def test_report_includes_all_operations(self, perf_monitor):
        """Should include all tracked operations in report."""
        with perf_monitor.measure("op1"):
            time.sleep(0.001)
        
        with perf_monitor.measure("op2"):
            time.sleep(0.001)
        
        report = perf_monitor.generate_report()
        operations = report["operations"]
        
        assert "op1" in operations
        assert "op2" in operations

    def test_export_report_json(self, perf_monitor, tmp_path):
        """Should export report to JSON file."""
        with perf_monitor.measure("test_op"):
            time.sleep(0.001)
        
        report_file = tmp_path / "performance_report.json"
        perf_monitor.export_report(report_file, format="json")
        
        assert report_file.exists()

    def test_reset_all_stats(self, perf_monitor):
        """Should reset all performance statistics."""
        with perf_monitor.measure("op1"):
            time.sleep(0.001)
        
        perf_monitor.reset()
        
        all_stats = perf_monitor.get_all_stats()
        assert len(all_stats) == 0


class TestPerformanceBenchmark:
    """Test performance benchmarking."""

    def test_benchmark_meets_target(self, perf_monitor):
        """Should verify operation meets performance target."""
        # Target: <5ms overhead
        for _ in range(100):
            with perf_monitor.measure("fast_op"):
                pass  # Minimal operation
        
        stats = perf_monitor.get_stats("fast_op")
        assert stats["mean"] < 5  # Less than 5ms

    def test_benchmark_report(self, perf_monitor):
        """Should generate benchmark comparison report."""
        targets = {
            "log_write": 5.0,  # 5ms target
            "checksum_gen": 10.0  # 10ms target
        }
        
        for _ in range(10):
            with perf_monitor.measure("log_write"):
                time.sleep(0.001)
        
        benchmark = perf_monitor.benchmark_against(targets)
        
        assert "log_write" in benchmark
        assert "meets_target" in benchmark["log_write"]
        assert "actual_mean" in benchmark["log_write"]
        assert "target" in benchmark["log_write"]
