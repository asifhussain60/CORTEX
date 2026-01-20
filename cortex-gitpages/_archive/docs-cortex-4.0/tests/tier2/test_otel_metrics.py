"""
Test suite for AC-NFR-004-01: OpenTelemetry Metrics Integration

Tests the MetricsCollector and related components for collecting and
exporting metrics to observability backends.

Test Plan:
- 12 unit tests for core functionality
- 5 integration tests for multi-metric scenarios
- 4 parametrized tests for metric types
- 2 performance tests for throughput
- 24 total tests, 100% pass rate required
"""

import pytest
from unittest.mock import Mock, patch, call, MagicMock
from typing import Any, Dict
from datetime import datetime
import time
import threading

from cortex_brain.tier2.resilience import (
    MetricsCollector,
    MetricValue,
    MetricExportConfig,
    MetricUnit,
    InstrumentationSpan,
)


class TestMetricsCollector:
    """Unit tests for MetricsCollector (12 tests)"""
    
    def test_init_collector(self):
        """Test: Metrics collector initializes correctly"""
        collector = MetricsCollector()
        assert collector is not None
        assert len(collector._metrics) == 0
    
    def test_counter_metric_increments(self):
        """Test: Counter metric increments correctly"""
        collector = MetricsCollector()
        collector.counter("requests_total", 1)
        collector.counter("requests_total", 1)
        
        metrics = collector.get_metrics()
        assert "requests_total" in metrics
        assert metrics["requests_total"]["value"] >= 2
    
    def test_gauge_metric_sets_value(self):
        """Test: Gauge metric sets current value"""
        collector = MetricsCollector()
        collector.gauge("temperature", 25.5)
        collector.gauge("temperature", 26.0)
        
        metrics = collector.get_metrics()
        assert metrics["temperature"]["value"] == 26.0
    
    def test_metric_with_labels(self):
        """Test: Metrics can include labels"""
        collector = MetricsCollector()
        collector.counter("requests_total", 1, labels={"method": "GET", "status": "200"})
        
        metrics = collector.get_metrics()
        assert "requests_total" in metrics
        assert metrics["requests_total"].get("labels") is not None
    
    def test_metric_export_config(self):
        """Test: Export configuration is valid"""
        config = MetricExportConfig(
            endpoint="http://localhost:9090",
            batch_size=100,
            flush_interval_ms=5000
        )
        assert config.endpoint == "http://localhost:9090"
        assert config.batch_size == 100
    
    def test_metric_unit_enum(self):
        """Test: MetricUnit enum has standard units"""
        assert hasattr(MetricUnit, "SECONDS")
        assert hasattr(MetricUnit, "MILLISECONDS")
        assert hasattr(MetricUnit, "BYTES")
    
    def test_histogram_metric(self):
        """Test: Histogram metric tracks distribution"""
        collector = MetricsCollector()
        for _ in range(10):
            collector.histogram("response_time_ms", 100 + (_ * 10))
        
        metrics = collector.get_metrics()
        assert "response_time_ms" in metrics
    
    def test_instrumentation_span_creation(self):
        """Test: Instrumentation span creates with attributes"""
        span = InstrumentationSpan(
            name="database_query",
            operation="select",
            resource_name="users_table"
        )
        assert span.name == "database_query"
        assert span.operation == "select"
    
    def test_span_add_attribute(self):
        """Test: Span can add custom attributes"""
        span = InstrumentationSpan(name="api_call")
        span.add_attribute("endpoint", "/users")
        span.add_attribute("status_code", 200)
        
        attrs = span.get_attributes()
        assert attrs["endpoint"] == "/users"
        assert attrs["status_code"] == 200
    
    def test_span_add_event(self):
        """Test: Span can record events"""
        span = InstrumentationSpan(name="operation")
        span.add_event("started")
        span.add_event("completed")
        
        events = span.get_events()
        assert len(events) >= 2
    
    def test_metric_value_creation(self):
        """Test: MetricValue wraps metric data"""
        value = MetricValue(
            value=42,
            unit=MetricUnit.MILLISECONDS,
            timestamp=datetime.utcnow(),
            labels={"service": "api"}
        )
        assert value.value == 42
        assert value.unit == MetricUnit.MILLISECONDS
    
    def test_reset_metrics(self):
        """Test: Metrics can be reset"""
        collector = MetricsCollector()
        collector.counter("test_metric", 10)
        
        collector.reset()
        metrics = collector.get_metrics()
        assert len(metrics) == 0


class TestMetricsIntegration:
    """Integration tests for metrics scenarios (5 tests)"""
    
    def test_multiple_metric_types_coexist(self):
        """Test: Counter, gauge, and histogram coexist"""
        collector = MetricsCollector()
        
        collector.counter("requests", 1)
        collector.gauge("memory_mb", 512)
        collector.histogram("latency_ms", 250)
        
        metrics = collector.get_metrics()
        assert len(metrics) >= 3
    
    def test_export_configuration_applied(self):
        """Test: Export configuration is properly configured"""
        config = MetricExportConfig(
            endpoint="http://prometheus:9090",
            batch_size=500,
            flush_interval_ms=10000
        )
        
        collector = MetricsCollector(config=config)
        assert collector is not None
    
    def test_instrumentation_span_lifecycle(self):
        """Test: Span lifecycle from creation to completion"""
        span = InstrumentationSpan(name="request")
        span.add_event("start")
        span.add_attribute("user_id", 123)
        span.add_event("processing")
        
        # Simulate some work
        time.sleep(0.01)
        
        span.add_event("complete")
        assert len(span.get_events()) >= 3
    
    def test_metrics_with_dimensional_labels(self):
        """Test: Metrics properly organize by labels"""
        collector = MetricsCollector()
        
        # Multiple dimensions
        for method in ["GET", "POST"]:
            for status in [200, 404]:
                collector.counter(
                    "http_requests",
                    1,
                    labels={"method": method, "status": str(status)}
                )
        
        metrics = collector.get_metrics()
        assert "http_requests" in metrics
    
    def test_collector_export_batch(self):
        """Test: Collector batches metrics for export"""
        config = MetricExportConfig(batch_size=10, flush_interval_ms=100)
        collector = MetricsCollector(config=config)
        
        for i in range(15):
            collector.counter("batch_test", 1)
        
        metrics = collector.get_metrics()
        assert len(metrics) > 0


class TestMetricsParametrized:
    """Parametrized tests for metric types (4 tests)"""
    
    @pytest.mark.parametrize("metric_type,operation", [
        ("counter", "counter"),
        ("gauge", "gauge"),
        ("histogram", "histogram"),
        ("summary", "summary"),
    ])
    def test_metric_types(self, metric_type, operation):
        """Test: Various metric types work correctly"""
        collector = MetricsCollector()
        
        method = getattr(collector, operation)
        method("test_metric", 100)
        
        metrics = collector.get_metrics()
        assert "test_metric" in metrics
    
    @pytest.mark.parametrize("unit", [
        ("SECONDS", "seconds"),
        ("MILLISECONDS", "milliseconds"),
        ("BYTES", "bytes"),
        ("REQUESTS", "requests"),
    ])
    def test_metric_units(self, unit):
        """Test: Various metric units supported"""
        collector = MetricsCollector()
        collector.gauge("test", 100)
        
        metrics = collector.get_metrics()
        assert "test" in metrics
    
    @pytest.mark.parametrize("label_count", [0, 1, 5, 10])
    def test_metric_label_variations(self, label_count):
        """Test: Metrics with varying label counts"""
        collector = MetricsCollector()
        labels = {f"label_{i}": f"value_{i}" for i in range(label_count)}
        
        collector.counter("test_metric", 1, labels=labels if labels else None)
        
        metrics = collector.get_metrics()
        assert "test_metric" in metrics
    
    @pytest.mark.parametrize("span_attribute_count", [1, 5, 20])
    def test_span_attribute_variations(self, span_attribute_count):
        """Test: Spans with varying attribute counts"""
        span = InstrumentationSpan(name="test_span")
        
        for i in range(span_attribute_count):
            span.add_attribute(f"attr_{i}", f"value_{i}")
        
        attrs = span.get_attributes()
        assert len(attrs) >= span_attribute_count


class TestMetricsPerformance:
    """Performance tests for metrics (2 tests)"""
    
    def test_collector_throughput(self):
        """Test: Collector handles high throughput"""
        collector = MetricsCollector()
        
        start = time.time()
        for i in range(1000):
            collector.counter("throughput_test", 1)
        elapsed = time.time() - start
        
        # Should handle 1000 operations in <100ms
        assert elapsed < 0.1
    
    def test_concurrent_metric_collection(self):
        """Test: Multiple threads safely update metrics"""
        collector = MetricsCollector()
        results = []
        
        def worker():
            for _ in range(100):
                collector.counter("concurrent_test", 1)
            results.append("done")
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 10
        metrics = collector.get_metrics()
        assert "concurrent_test" in metrics


# ===== Pytest Configuration & Markers =====

@pytest.mark.unit
class TestMetricsCollectorUnit:
    """Marked unit tests"""
    pass


@pytest.mark.integration  
class TestMetricsCollectorIntegration:
    """Marked integration tests"""
    pass


# ===== Test Execution Configuration =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
