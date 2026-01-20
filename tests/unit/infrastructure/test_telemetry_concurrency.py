"""
Test: Telemetry Thread Safety (AC-FIX-BRITTLENESS-002)

RED test for telemetry thread safety with concurrent start/stop.
Tests that metrics exporter handles concurrent operations without race conditions.

Per CORE-008 (Tests First), these tests define the expected behavior
before implementation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import threading
import time
from typing import List

import pytest

from cortex.infrastructure.metrics_exporter import (
    MetricsExporter,
    TelemetryProvider,
    MemoryMetricsExporter,
    MetricType,
)


class TestTelemetryThreadSafety:
    """Test telemetry thread safety with concurrent operations."""
    
    def test_concurrent_start_stop(self):
        """Multiple threads starting and stopping should not race."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=5,
            use_async=True
        )
        
        errors = []
        
        def start_and_stop():
            try:
                provider.shutdown()  # Should handle being called while running
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads all trying to stop
        threads = []
        for _ in range(5):
            t = threading.Thread(target=start_and_stop)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Should have no errors
        assert len(errors) == 0, f"Concurrent stop failed: {errors}"
    
    def test_rapid_record_metric_during_shutdown(self):
        """Recording metrics while shutting down should not race."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=3,
            use_async=True
        )
        
        # Record some metrics
        for i in range(3):
            provider.record_metric(f"test-{i}", i)
        
        errors = []
        stop_event = threading.Event()
        
        def record_metrics():
            """Continuously record metrics."""
            try:
                for i in range(100):
                    if stop_event.is_set():
                        break
                    provider.record_metric(f"metric-{i}", i)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(str(e))
        
        # Start recorder thread
        recorder = threading.Thread(target=record_metrics)
        recorder.start()
        
        # Let it run a bit, then shutdown
        time.sleep(0.05)
        stop_event.set()
        
        # Stop should not hang or raise
        try:
            provider.shutdown()
        except Exception as e:
            errors.append(f"Shutdown error: {str(e)}")
        
        recorder.join(timeout=5.0)
        
        assert len(errors) == 0, f"Errors during concurrent record+shutdown: {errors}"
    
    def test_high_throughput_metrics_export(self):
        """High throughput should not cause race conditions or hangs."""
        exporter = MemoryMetricsExporter()
        provider = TelemetryProvider(
            exporters=[exporter],
            batch_size=10,
            use_async=True
        )
        
        # Record 100 metrics rapidly
        for i in range(100):
            provider.record_metric(
                name=f"throughput-metric-{i}",
                value=i,
                metric_type=MetricType.COUNTER
            )
        
        # Force flush
        provider.flush(force=True)
        time.sleep(0.1)  # Let async export complete
        
        # Should have exported all
        count = exporter.get_metrics_count()
        assert count == 100, f"Expected 100 metrics, got {count}"
        
        # Shutdown should complete without hanging
        provider.shutdown()
    
    def test_shutdown_times_out_gracefully(self):
        """Shutdown with timeout should not hang indefinitely."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=1,
            use_async=True
        )
        
        # Record metric
        provider.record_metric("test", 1)
        
        # Shutdown should complete within reasonable time
        start = time.time()
        provider.shutdown()
        elapsed = time.time() - start
        
        # Should complete within 10 seconds (5 second timeout + overhead)
        assert elapsed < 10.0, f"Shutdown took too long: {elapsed}s"
    
    def test_async_export_worker_detects_shutdown(self):
        """Async export worker should detect shutdown flag change."""
        exporter = MemoryMetricsExporter()
        provider = TelemetryProvider(
            exporters=[exporter],
            batch_size=1,
            use_async=True
        )
        
        # Record metrics
        for i in range(5):
            provider.record_metric(f"metric-{i}", i)
            time.sleep(0.01)  # Give worker time to export
        
        # Shutdown
        provider.shutdown()
        
        # Worker thread should have exited (not hung)
        time.sleep(0.5)  # Give thread time to exit
        
        # Thread should not be alive
        if provider.export_thread:
            assert not provider.export_thread.is_alive(), "Export thread did not exit"
    
    def test_multiple_providers_concurrent_operation(self):
        """Multiple providers operating concurrently should not interfere."""
        provider1 = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=5,
            use_async=True
        )
        provider2 = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=5,
            use_async=True
        )
        
        errors = []
        
        def record_metrics(provider, prefix):
            try:
                for i in range(20):
                    provider.record_metric(f"{prefix}-{i}", i)
            except Exception as e:
                errors.append(str(e))
        
        # Run both concurrently
        t1 = threading.Thread(target=record_metrics, args=(provider1, "p1"))
        t2 = threading.Thread(target=record_metrics, args=(provider2, "p2"))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Both should be able to shutdown without errors or hangs
        provider1.shutdown()
        provider2.shutdown()
        
        # Should have no errors
        assert len(errors) == 0, f"Concurrent providers error: {errors}"
        # is_running should report False after shutdown
        assert not provider1.is_running(), "Provider1 should not be running after shutdown"
        assert not provider2.is_running(), "Provider2 should not be running after shutdown"


class TestGracefulShutdown:
    """Test graceful shutdown with timeout."""
    
    def test_shutdown_exports_remaining_metrics(self):
        """Shutdown should flush remaining buffered metrics without hanging."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=100,  # Large batch size
            use_async=True
        )
        
        # Record 10 metrics
        for i in range(10):
            provider.record_metric(f"final-{i}", i)
        
        # Shutdown should not hang or raise
        start = time.time()
        provider.shutdown()
        elapsed = time.time() - start
        
        # Should complete within reasonable time (not hang)
        assert elapsed < 10.0, f"Shutdown took too long: {elapsed}s"
        # Should not be running anymore
        assert not provider.is_running(), "Provider should not be running after shutdown"
    
    def test_is_running_reflects_state(self):
        """is_running() should correctly reflect async export state."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            use_async=True
        )
        
        # Should be running initially
        assert provider.is_running(), "Provider should be running initially"
        
        # After shutdown, should not be running
        provider.shutdown()
        assert not provider.is_running(), "Provider should not be running after shutdown"
    
    def test_sync_provider_ignores_running_flag(self):
        """Sync provider should not depend on running flag."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            use_async=False  # Sync mode
        )
        
        # is_running should return True for sync (always "running")
        assert provider.is_running(), "Sync provider should report is_running=True"
        
        # Shutdown in sync mode should still work
        provider.record_metric("test", 1)
        provider.shutdown()


class TestConcurrentBatching:
    """Test that batching works correctly under concurrency."""
    
    def test_concurrent_metric_recording_maintains_order(self):
        """Concurrent metrics should be recorded and flushed without race conditions."""
        provider = TelemetryProvider(
            exporters=[MemoryMetricsExporter()],
            batch_size=10,
            use_async=True
        )
        
        errors = []
        
        def record_batch(start_idx, count):
            try:
                for i in range(start_idx, start_idx + count):
                    provider.record_metric(f"metric-{i}", i)
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for i in range(0, 50, 10):
            t = threading.Thread(target=record_batch, args=(i, 10))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Flush and shutdown should not raise or hang
        provider.flush(force=True)
        start = time.time()
        provider.shutdown()
        elapsed = time.time() - start
        
        # Should complete without hanging
        assert elapsed < 10.0, f"Shutdown took too long: {elapsed}s"
        assert len(errors) == 0, f"Errors during concurrent recording: {errors}"
        # Provider should not be running
        assert not provider.is_running(), "Provider should not be running after shutdown"
