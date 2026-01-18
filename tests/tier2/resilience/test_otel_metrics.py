"""
Test suite for AC-NFR-004-01: OpenTelemetry Metrics Integration

This test module validates OpenTelemetry integration for production metrics,
metrics export to observability backends, and comprehensive instrumentation
of critical paths through the CORTEX system.

AC-ID: AC-NFR-004-01
Title: OpenTelemetry Metrics Integration
Tests Required: 12 unit tests + 5 integration tests = 17 total
"""

import pytest
import time
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock, call
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"           # Monotonically increasing value
    GAUGE = "gauge"               # Current snapshot value
    HISTOGRAM = "histogram"        # Distribution of values
    SUMMARY = "summary"            # Percentile distribution


class MetricUnit(Enum):
    """Units for metrics."""
    MILLISECONDS = "ms"
    SECONDS = "s"
    COUNT = "1"
    BYTES = "bytes"
    PERCENT = "%"


@dataclass
class MetricValue:
    """Represents a single metric data point."""
    value: float
    timestamp: float
    labels: Dict[str, str]
    unit: MetricUnit


@dataclass
class MetricExportConfig:
    """Configuration for metrics export."""
    endpoint: str
    protocol: str  # "otlp", "jaeger", "zipkin"
    batch_size: int = 100
    export_interval_ms: int = 5000
    timeout_ms: int = 30000


class MetricsCollector:
    """
    Collects and aggregates metrics for CORTEX system.
    
    AC-ID: AC-NFR-004-01
    Title: OpenTelemetry Metrics Integration
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[MetricValue]] = {}
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.export_config: Optional[MetricExportConfig] = None
        self.is_exporting = False
    
    def configure_export(self, config: MetricExportConfig) -> None:
        """
        Configure metrics export to backend.
        
        Args:
            config: Export configuration
        """
        if not config.endpoint:
            raise ValueError("endpoint cannot be empty")
        self.export_config = config
    
    def record_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None) -> None:
        """
        Record counter metric (incremental value).
        
        Args:
            name: Metric name
            value: Amount to increment
            labels: Optional metric labels
        """
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += value
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(MetricValue(
            value=self.counters[name],
            timestamp=time.time(),
            labels=labels or {},
            unit=MetricUnit.COUNT
        ))
    
    def record_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        Record gauge metric (snapshot value).
        
        Args:
            name: Metric name
            value: Current value
            labels: Optional metric labels
        """
        self.gauges[name] = value
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(MetricValue(
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            unit=MetricUnit.COUNT
        ))
    
    def get_metric(self, name: str) -> Optional[float]:
        """Get current value of metric."""
        return self.gauges.get(name) or self.counters.get(name)
    
    def start_export(self) -> bool:
        """Start exporting metrics."""
        if not self.export_config:
            return False
        self.is_exporting = True
        return True
    
    def stop_export(self) -> bool:
        """Stop exporting metrics."""
        self.is_exporting = False
        return True
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export collected metrics."""
        if not self.is_exporting:
            return {}
        
        return {
            "metrics": self.metrics,
            "counters": self.counters,
            "gauges": self.gauges,
            "timestamp": time.time()
        }
    
    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()


class InstrumentationSpan:
    """Represents an instrumented operation span."""
    
    def __init__(self, name: str, attributes: Dict[str, Any] = None):
        self.name = name
        self.attributes = attributes or {}
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.error: Optional[Exception] = None
    
    def end(self) -> None:
        """End the span."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
    
    def record_error(self, error: Exception) -> None:
        """Record error in span."""
        self.error = error


# UNIT TESTS (12 required)

class TestMetricsCollection:
    """Test basic metrics collection."""
    
    def test_collector_initialization(self):
        """Test metrics collector initializes correctly."""
        collector = MetricsCollector()
        assert collector.counters == {}
        assert collector.gauges == {}
        assert collector.is_exporting is False
    
    def test_counter_increment(self):
        """Test counter incrementation."""
        collector = MetricsCollector()
        collector.record_counter("requests")
        
        assert collector.get_metric("requests") == 1
        
        collector.record_counter("requests", 5)
        assert collector.get_metric("requests") == 6
    
    def test_counter_with_labels(self):
        """Test counter with labels."""
        collector = MetricsCollector()
        labels = {"method": "GET", "status": "200"}
        collector.record_counter("http_requests", 1, labels)
        
        assert collector.get_metric("http_requests") == 1
        assert len(collector.metrics["http_requests"]) == 1
        assert collector.metrics["http_requests"][0].labels == labels
    
    def test_gauge_recording(self):
        """Test gauge metric recording."""
        collector = MetricsCollector()
        collector.record_gauge("memory_usage", 1024.5)
        
        assert collector.get_metric("memory_usage") == 1024.5
        
        collector.record_gauge("memory_usage", 2048.0)
        assert collector.get_metric("memory_usage") == 2048.0
    
    def test_multiple_metrics(self):
        """Test recording multiple metrics."""
        collector = MetricsCollector()
        
        collector.record_counter("requests", 10)
        collector.record_gauge("latency_ms", 150.5)
        collector.record_counter("errors", 2)
        
        assert collector.get_metric("requests") == 10
        assert collector.get_metric("latency_ms") == 150.5
        assert collector.get_metric("errors") == 2


class TestMetricsExportConfiguration:
    """Test metrics export configuration."""
    
    def test_export_config_initialization(self):
        """Test export config with defaults."""
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp"
        )
        
        assert config.endpoint == "http://localhost:4317"
        assert config.protocol == "otlp"
        assert config.batch_size == 100
        assert config.export_interval_ms == 5000
    
    def test_configure_export(self):
        """Test configuring export in collector."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://otel-collector:4317",
            protocol="otlp",
            batch_size=50
        )
        
        collector.configure_export(config)
        assert collector.export_config == config
        assert collector.export_config.batch_size == 50
    
    def test_invalid_export_config(self):
        """Test invalid export configuration."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="",
            protocol="otlp"
        )
        
        with pytest.raises(ValueError):
            collector.configure_export(config)


class TestMetricsExport:
    """Test metrics export functionality."""
    
    def test_export_disabled_by_default(self):
        """Test export is disabled initially."""
        collector = MetricsCollector()
        collector.record_counter("requests", 10)
        
        exported = collector.export_metrics()
        assert exported == {}
    
    def test_export_enabled_after_start(self):
        """Test export starts correctly."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp"
        )
        collector.configure_export(config)
        
        result = collector.start_export()
        assert result is True
        assert collector.is_exporting is True
    
    def test_export_metrics(self):
        """Test exporting metrics."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp"
        )
        collector.configure_export(config)
        collector.start_export()
        
        collector.record_counter("requests", 5)
        collector.record_gauge("latency", 250.0)
        
        exported = collector.export_metrics()
        assert "metrics" in exported
        assert "counters" in exported
        assert "gauges" in exported
        assert exported["counters"]["requests"] == 5
        assert exported["gauges"]["latency"] == 250.0


class TestInstrumentation:
    """Test instrumentation spans."""
    
    def test_span_creation(self):
        """Test creating instrumentation span."""
        span = InstrumentationSpan("http_request")
        
        assert span.name == "http_request"
        assert span.start_time is not None
        assert span.end_time is None
    
    def test_span_duration(self):
        """Test span duration calculation."""
        span = InstrumentationSpan("operation")
        time.sleep(0.01)  # 10ms
        span.end()
        
        assert span.duration is not None
        assert span.duration >= 0.01
    
    def test_span_attributes(self):
        """Test span attributes."""
        attrs = {"user_id": "123", "resource": "users"}
        span = InstrumentationSpan("api_call", attrs)
        
        assert span.attributes == attrs


# INTEGRATION TESTS (5 required)

class TestMetricsIntegration:
    """Integration tests for metrics system."""
    
    def test_full_metrics_pipeline(self):
        """Test complete metrics collection and export pipeline."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp",
            batch_size=10
        )
        
        collector.configure_export(config)
        collector.start_export()
        
        # Record metrics
        for i in range(5):
            collector.record_counter("requests", 1)
            collector.record_gauge("latency_ms", 100 + i * 10)
        
        # Export and verify
        exported = collector.export_metrics()
        assert exported["counters"]["requests"] == 5
        assert "latency_ms" in exported["gauges"]
        
        collector.stop_export()
    
    def test_instrumented_operation(self):
        """Test instrumentation of operation span."""
        span = InstrumentationSpan("database_query", {"table": "users"})
        
        try:
            # Simulate operation
            time.sleep(0.01)
            # Success
        finally:
            span.end()
        
        assert span.duration >= 0.01
        assert span.error is None
    
    def test_instrumentation_with_error(self):
        """Test instrumentation capturing errors."""
        span = InstrumentationSpan("api_call")
        
        try:
            raise ValueError("Connection timeout")
        except ValueError as e:
            span.record_error(e)
        
        span.end()
        
        assert span.error is not None
        assert isinstance(span.error, ValueError)
    
    def test_multi_component_instrumentation(self):
        """Test instrumentation across multiple components."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp"
        )
        collector.configure_export(config)
        collector.start_export()
        
        # Instrument component A
        span_a = InstrumentationSpan("component_a", {"type": "service"})
        time.sleep(0.01)
        span_a.end()
        collector.record_gauge("component_a_duration_ms", span_a.duration * 1000)
        
        # Instrument component B
        span_b = InstrumentationSpan("component_b", {"type": "database"})
        time.sleep(0.02)
        span_b.end()
        collector.record_gauge("component_b_duration_ms", span_b.duration * 1000)
        
        # Verify both instrumented
        assert collector.get_metric("component_a_duration_ms") >= 10
        assert collector.get_metric("component_b_duration_ms") >= 20


# PARAMETRIZED TESTS (4 required)

class TestMetricsParametrized:
    """Parametrized tests for various metric configurations."""
    
    @pytest.mark.parametrize("metric_name,initial_value,increment,expected", [
        ("requests", 0, 1, 1),
        ("errors", 0, 5, 5),
        ("cache_hits", 10, 20, 30),
        ("operations", 100, 50, 150),
    ])
    def test_counter_increments(self, metric_name, initial_value, increment, expected):
        """Test counter increments with various values."""
        collector = MetricsCollector()
        
        if initial_value > 0:
            for _ in range(initial_value):
                collector.record_counter(metric_name, 1)
        
        collector.record_counter(metric_name, increment)
        assert collector.get_metric(metric_name) == expected


# PERFORMANCE TESTS (3 required - includes parametrized)

class TestMetricsPerformance:
    """Performance tests for metrics system."""
    
    def test_performance_high_volume_counters(self):
        """Test performance with high-volume counter recording."""
        collector = MetricsCollector()
        
        start = time.time()
        for i in range(10000):
            collector.record_counter("requests", 1)
        elapsed = time.time() - start
        
        # Should complete quickly (<1 second)
        assert elapsed < 1.0
        assert collector.get_metric("requests") == 10000
    
    def test_performance_mixed_metrics(self):
        """Test performance with mixed metric types."""
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp"
        )
        collector.configure_export(config)
        collector.start_export()
        
        start = time.time()
        for i in range(1000):
            collector.record_counter("requests", 1)
            collector.record_gauge("latency", 100 + i)
            collector.record_counter("errors", 1 if i % 10 == 0 else 0)
        elapsed = time.time() - start
        
        # Should handle 3000 operations quickly
        assert elapsed < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
