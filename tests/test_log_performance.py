"""
Performance Tests for Audit Logger

Tests:
- Write latency (<5ms requirement)
- Throughput (writes per second)
- Memory usage
- Buffer performance
- Compression effectiveness
- Load testing (concurrent operations)

Author: Asif Hussain
Created: 2026-01-05
"""

import pytest
import time
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from src.logging.performance_monitor import PerformanceMonitor, PerformanceOptimizer


class TestPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    def test_record_operation(self):
        """Test recording a single operation"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        start = time.time()
        time.sleep(0.001)  # Simulate 1ms operation
        monitor.record_operation('write', start, bytes_processed=100)
        
        metrics = monitor.get_metrics()
        assert metrics.total_log_entries == 1
        assert metrics.total_bytes_written == 100
        assert metrics.avg_write_latency_ms >= 1.0
    
    def test_multiple_operations(self):
        """Test recording multiple operations"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        for i in range(10):
            start = time.time()
            time.sleep(0.001)  # Simulate 1ms operation
            monitor.record_operation('write', start, bytes_processed=100)
        
        metrics = monitor.get_metrics()
        assert metrics.total_log_entries == 10
        assert metrics.total_bytes_written == 1000
        assert metrics.writes_per_second > 0
    
    def test_latency_percentiles(self):
        """Test latency percentile calculations"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        # Record operations with known latencies
        latencies_ms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        for latency_ms in latencies_ms:
            start = time.time() - (latency_ms / 1000)  # Backdate start time
            monitor.record_operation('write', start)
        
        metrics = monitor.get_metrics()
        
        # P50 should be around 5-6ms
        assert 4 <= metrics.p50_write_latency_ms <= 7
        
        # P95 should be around 9-10ms
        assert metrics.p95_write_latency_ms >= 9
        
        # Max should be around 10ms
        assert metrics.max_write_latency_ms >= 10
    
    def test_performance_alert_on_high_latency(self):
        """Test that alerts are triggered for high latency"""
        monitor = PerformanceMonitor(alert_threshold_ms=5.0)
        monitor.reset_metrics()
        monitor.clear_alerts()
        
        # Record an operation with 10ms latency (above threshold)
        start = time.time() - 0.010  # 10ms ago
        monitor.record_operation('write', start)
        
        alerts = monitor.get_recent_alerts()
        assert len(alerts) > 0
        assert 'High latency detected' in alerts[0]
    
    def test_buffer_overflow_tracking(self):
        """Test buffer overflow event tracking"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        monitor.record_buffer_overflow()
        monitor.record_buffer_overflow()
        
        metrics = monitor.get_metrics()
        assert metrics.buffer_overflows == 2
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        # Record some operations
        for i in range(5):
            start = time.time()
            monitor.record_operation('write', start, bytes_processed=100)
        
        summary = monitor.get_performance_summary()
        
        assert 'latency' in summary
        assert 'throughput' in summary
        assert 'resources' in summary
        assert 'issues' in summary
        
        assert 'average_ms' in summary['latency']
        assert 'writes_per_second' in summary['throughput']
        assert 'memory_mb' in summary['resources']


class TestPerformanceOptimizer:
    """Test performance optimization recommendations"""
    
    def test_suggest_buffer_increase_on_overflow(self):
        """Test buffer size increase suggestion when overflows occur"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        optimizer = PerformanceOptimizer(monitor)
        
        # Simulate buffer overflows
        monitor.record_buffer_overflow()
        
        current_size = 1000
        suggested_size = optimizer.suggest_buffer_size(current_size)
        
        # Should suggest increase
        assert suggested_size > current_size
        assert suggested_size <= optimizer.max_buffer_size
    
    def test_suggest_buffer_decrease_on_low_utilization(self):
        """Test buffer size decrease suggestion with low utilization"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        optimizer = PerformanceOptimizer(monitor)
        
        # Record operations with low latency
        for i in range(10):
            start = time.time()
            monitor.record_operation('write', start)
        
        current_size = 5000
        suggested_size = optimizer.suggest_buffer_size(current_size)
        
        # May suggest decrease or stay same (depends on metrics)
        assert suggested_size >= optimizer.min_buffer_size
        assert suggested_size <= optimizer.max_buffer_size
    
    def test_suggest_flush_interval_decrease_on_high_latency(self):
        """Test flush interval decrease suggestion with high latency"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        optimizer = PerformanceOptimizer(monitor)
        
        # Record operations with high latency (>10ms)
        for i in range(10):
            start = time.time() - 0.015  # 15ms latency
            monitor.record_operation('write', start)
        
        current_interval = 10.0
        suggested_interval = optimizer.suggest_flush_interval(current_interval)
        
        # Should suggest decrease (flush more often)
        assert suggested_interval <= current_interval
        assert suggested_interval >= optimizer.min_flush_interval


class TestWriteLatency:
    """Test write latency requirements"""
    
    def test_single_write_latency_under_5ms(self):
        """Test that a single write operation completes in <5ms"""
        # Simulate a simple write operation
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            start = time.time()
            f.write("Test log entry\n")
            f.flush()
            latency_ms = (time.time() - start) * 1000
            temp_path = Path(f.name)
        
        temp_path.unlink()
        
        # Should be well under 5ms for a single line
        assert latency_ms < 5.0, f"Write latency {latency_ms:.2f}ms exceeds 5ms threshold"
    
    def test_batch_write_latency_under_5ms_per_entry(self):
        """Test that batch writes maintain <5ms per entry"""
        num_entries = 100
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            start = time.time()
            
            for i in range(num_entries):
                f.write(f"Log entry {i}\n")
            
            f.flush()
            total_time_ms = (time.time() - start) * 1000
            temp_path = Path(f.name)
        
        temp_path.unlink()
        
        avg_latency_per_entry = total_time_ms / num_entries
        
        # Average should be well under 5ms per entry
        assert avg_latency_per_entry < 5.0, \
            f"Average write latency {avg_latency_per_entry:.2f}ms exceeds 5ms threshold"


class TestThroughput:
    """Test throughput requirements"""
    
    def test_sequential_write_throughput(self):
        """Test sequential write throughput"""
        num_entries = 1000
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            start = time.time()
            
            for i in range(num_entries):
                f.write(f"{{\"id\": {i}, \"message\": \"Test log entry\"}}\n")
            
            f.flush()
            duration = time.time() - start
            temp_path = Path(f.name)
        
        temp_path.unlink()
        
        writes_per_second = num_entries / duration
        
        # Should achieve at least 1000 writes/second
        assert writes_per_second >= 1000, \
            f"Throughput {writes_per_second:.2f} writes/sec below 1000 writes/sec target"
    
    def test_concurrent_write_throughput(self):
        """Test concurrent write throughput"""
        num_threads = 10
        writes_per_thread = 100
        
        def write_logs(thread_id):
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for i in range(writes_per_thread):
                    f.write(f"{{\"thread\": {thread_id}, \"id\": {i}}}\n")
                f.flush()
                return Path(f.name)
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(write_logs, i) for i in range(num_threads)]
            temp_paths = [f.result() for f in futures]
        
        duration = time.time() - start
        
        # Cleanup
        for path in temp_paths:
            path.unlink()
        
        total_writes = num_threads * writes_per_thread
        writes_per_second = total_writes / duration
        
        # Should maintain throughput under concurrent load
        assert writes_per_second >= 500, \
            f"Concurrent throughput {writes_per_second:.2f} writes/sec below 500 writes/sec target"


class TestMemoryUsage:
    """Test memory usage characteristics"""
    
    def test_monitor_memory_tracking(self):
        """Test that memory usage is tracked correctly"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        # Record some operations
        for i in range(100):
            start = time.time()
            monitor.record_operation('write', start, bytes_processed=1000)
        
        metrics = monitor.get_metrics()
        
        # Memory usage should be reasonable (< 100MB for monitor)
        assert metrics.memory_usage_mb < 100, \
            f"Memory usage {metrics.memory_usage_mb:.2f}MB is excessive"
    
    def test_sliding_window_prevents_unbounded_growth(self):
        """Test that sliding window prevents unbounded memory growth"""
        window_size = 100
        monitor = PerformanceMonitor(window_size=window_size)
        monitor.reset_metrics()
        
        # Record many more operations than window size
        for i in range(window_size * 10):
            start = time.time()
            monitor.record_operation('write', start)
        
        metrics = monitor.get_metrics()
        
        # Should only have window_size samples in memory
        # (internal state should be bounded)
        assert metrics.memory_usage_mb < 50, \
            f"Memory growth not controlled: {metrics.memory_usage_mb:.2f}MB"


class TestLoadTesting:
    """Load and stress testing"""
    
    def test_sustained_load_1000_writes(self):
        """Test sustained load of 1000 writes"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        num_writes = 1000
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for i in range(num_writes):
                start = time.time()
                f.write(f"{{\"id\": {i}, \"timestamp\": {time.time()}}}\n")
                monitor.record_operation('write', start, bytes_processed=50)
        
        Path(f.name).unlink()
        
        metrics = monitor.get_metrics()
        
        # All writes should complete
        assert metrics.total_log_entries == num_writes
        
        # P95 latency should still be under 5ms
        assert metrics.p95_write_latency_ms < 5.0, \
            f"P95 latency {metrics.p95_write_latency_ms:.2f}ms exceeds 5ms under load"
    
    def test_burst_load_handling(self):
        """Test handling of burst load"""
        monitor = PerformanceMonitor()
        monitor.reset_metrics()
        
        # Simulate burst of 100 writes in quick succession
        num_writes = 100
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            burst_start = time.time()
            
            for i in range(num_writes):
                start = time.time()
                f.write(f"{{\"id\": {i}}}\n")
                monitor.record_operation('write', start, bytes_processed=20)
            
            f.flush()
            burst_duration = time.time() - burst_start
        
        Path(f.name).unlink()
        
        metrics = monitor.get_metrics()
        
        # Should complete burst quickly
        assert burst_duration < 1.0, \
            f"Burst of {num_writes} writes took {burst_duration:.2f}s (should be <1s)"
        
        # Average latency should still be reasonable
        assert metrics.avg_write_latency_ms < 5.0, \
            f"Average latency {metrics.avg_write_latency_ms:.2f}ms exceeds 5ms during burst"


class TestPerformanceRegression:
    """Tests to prevent performance regressions"""
    
    def test_baseline_write_performance(self):
        """Establish baseline write performance"""
        num_iterations = 100
        latencies = []
        
        for _ in range(num_iterations):
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                start = time.time()
                f.write("Test log entry\n")
                f.flush()
                latency_ms = (time.time() - start) * 1000
                temp_path = Path(f.name)
            
            temp_path.unlink()
            latencies.append(latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # Baseline: average should be <2ms, P95 should be <5ms
        assert avg_latency < 2.0, \
            f"Baseline average latency {avg_latency:.2f}ms exceeds 2ms"
        assert p95_latency < 5.0, \
            f"Baseline P95 latency {p95_latency:.2f}ms exceeds 5ms"
    
    def test_performance_with_large_entries(self):
        """Test performance with large log entries (1KB)"""
        large_entry = "x" * 1024  # 1KB entry
        num_writes = 100
        latencies = []
        
        for _ in range(num_writes):
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                start = time.time()
                f.write(large_entry + "\n")
                f.flush()
                latency_ms = (time.time() - start) * 1000
                temp_path = Path(f.name)
            
            temp_path.unlink()
            latencies.append(latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        
        # Should still be reasonable even with large entries
        assert avg_latency < 10.0, \
            f"Average latency for 1KB entries {avg_latency:.2f}ms exceeds 10ms"


@pytest.mark.performance
class TestBenchmarks:
    """Benchmark tests (run with pytest -m performance)"""
    
    def test_benchmark_write_latency(self, benchmark):
        """Benchmark write latency"""
        def write_log():
            with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
                f.write("Test log entry\n")
                f.flush()
        
        result = benchmark(write_log)
        
        # Report results
        print(f"\nBenchmark: Write latency = {result.stats.mean * 1000:.2f}ms")
    
    def test_benchmark_batch_write(self, benchmark):
        """Benchmark batch write performance"""
        def batch_write():
            with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
                for i in range(100):
                    f.write(f"Log entry {i}\n")
                f.flush()
        
        result = benchmark(batch_write)
        
        print(f"\nBenchmark: Batch write (100 entries) = {result.stats.mean * 1000:.2f}ms")
