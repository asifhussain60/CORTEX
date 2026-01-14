"""
Tests for OpenTelemetry Metrics Exporter

AC-NFR-004-01: OpenTelemetry metrics exported
"""

import pytest
import time
from src.infrastructure.metrics_exporter import (
    MetricsExporter,
    ConsoleMetricsExporter,
    MemoryMetricsExporter,
    TelemetryProvider,
    MetricType,
    MetricData,
    MetricAttribute,
    MetricBatch,
)
from src.infrastructure.telemetry_provider import (
    TelemetryConfiguration,
    create_telemetry_provider,
    get_default_telemetry_provider,
)


@pytest.fixture
def memory_exporter():
    """Create a memory exporter for testing."""
    return MemoryMetricsExporter()


@pytest.fixture
def telemetry_provider(memory_exporter):
    """Create a telemetry provider with memory exporter."""
    provider = TelemetryProvider(
        exporters=[memory_exporter],
        batch_size=5,
        use_async=False
    )
    yield provider
    provider.shutdown()


class TestMetricData:
    """Test metric data structures."""
    
    def test_metric_data_creation(self):
        """Test creating metric data."""
        metric = MetricData(
            name="test.metric",
            type=MetricType.GAUGE,
            value=42,
            unit="requests"
        )
        assert metric.name == "test.metric"
        assert metric.value == 42
        assert metric.unit == "requests"
    
    def test_metric_data_with_attributes(self):
        """Test metric data with attributes."""
        attrs = [
            MetricAttribute("service", "orchestrator"),
            MetricAttribute("region", "us-east-1")
        ]
        metric = MetricData(
            name="test.metric",
            type=MetricType.COUNTER,
            value=100,
            attributes=attrs
        )
        assert len(metric.attributes) == 2
    
    def test_metric_data_to_dict(self):
        """Test converting metric to dict."""
        metric = MetricData(
            name="test.metric",
            type=MetricType.GAUGE,
            value=42
        )
        data = metric.to_dict()
        assert data["name"] == "test.metric"
        assert data["value"] == 42
        assert data["type"] == "gauge"


class TestMetricBatch:
    """Test metric batch functionality."""
    
    def test_batch_creation(self):
        """Test creating metric batch."""
        metrics = [
            MetricData("metric1", MetricType.GAUGE, 10),
            MetricData("metric2", MetricType.COUNTER, 20),
        ]
        batch = MetricBatch(metrics=metrics, batch_id="test-batch")
        assert len(batch.metrics) == 2
        assert batch.batch_id == "test-batch"
    
    def test_batch_to_dict(self):
        """Test converting batch to dict."""
        metrics = [MetricData("metric1", MetricType.GAUGE, 10)]
        batch = MetricBatch(metrics=metrics, batch_id="test-batch")
        data = batch.to_dict()
        assert "batch_id" in data
        assert "timestamp" in data
        assert "metrics" in data
        assert len(data["metrics"]) == 1


class TestConsoleMetricsExporter:
    """Test console metrics exporter."""
    
    def test_export_success(self, capsys):
        """Test exporting metrics to console."""
        exporter = ConsoleMetricsExporter()
        batch = MetricBatch(
            metrics=[MetricData("test.metric", MetricType.GAUGE, 42)],
            batch_id="test-batch"
        )
        result = exporter.export(batch)
        assert result
    
    def test_shutdown_noop(self):
        """Test shutdown is noop."""
        exporter = ConsoleMetricsExporter()
        exporter.shutdown()  # Should not raise


class TestMemoryMetricsExporter:
    """Test memory metrics exporter."""
    
    def test_export_stores_batch(self, memory_exporter):
        """Test exporting stores batch in memory."""
        batch = MetricBatch(
            metrics=[MetricData("test.metric", MetricType.GAUGE, 42)],
            batch_id="test-batch"
        )
        result = memory_exporter.export(batch)
        assert result
        assert len(memory_exporter.get_batches()) == 1
    
    def test_max_batches_limit(self):
        """Test max batches limit."""
        exporter = MemoryMetricsExporter(max_batches=2)
        
        # Add 3 batches
        for i in range(3):
            batch = MetricBatch(
                metrics=[MetricData(f"metric{i}", MetricType.GAUGE, i)],
                batch_id=f"batch-{i}"
            )
            exporter.export(batch)
        
        # Should only keep 2
        assert len(exporter.get_batches()) == 2
    
    def test_metrics_count(self, memory_exporter):
        """Test getting metrics count."""
        batch = MetricBatch(
            metrics=[
                MetricData("metric1", MetricType.GAUGE, 1),
                MetricData("metric2", MetricType.GAUGE, 2),
            ],
            batch_id="test-batch"
        )
        memory_exporter.export(batch)
        assert memory_exporter.get_metrics_count() == 2
    
    def test_shutdown_clears_memory(self, memory_exporter):
        """Test shutdown clears memory."""
        batch = MetricBatch(
            metrics=[MetricData("test.metric", MetricType.GAUGE, 42)],
            batch_id="test-batch"
        )
        memory_exporter.export(batch)
        assert len(memory_exporter.get_batches()) > 0
        
        memory_exporter.shutdown()
        assert len(memory_exporter.get_batches()) == 0


class TestTelemetryProvider:
    """Test telemetry provider."""
    
    def test_record_metric(self, telemetry_provider, memory_exporter):
        """Test recording a metric."""
        metric = telemetry_provider.record_metric(
            name="test.metric",
            value=42,
            metric_type=MetricType.GAUGE
        )
        assert metric.name == "test.metric"
        assert metric.value == 42
    
    def test_automatic_batch_export(self, telemetry_provider, memory_exporter):
        """Test automatic batch export when threshold reached."""
        # Record enough metrics to trigger batch
        batch_size = telemetry_provider.batch_size
        for i in range(batch_size):
            telemetry_provider.record_metric(
                f"metric{i}",
                i,
                metric_type=MetricType.COUNTER
            )
        
        # Should have exported batch
        assert len(memory_exporter.get_batches()) >= 1
    
    def test_manual_flush(self, telemetry_provider, memory_exporter):
        """Test manual flush of metrics."""
        telemetry_provider.record_metric("metric1", 10)
        assert len(memory_exporter.get_batches()) == 0
        
        telemetry_provider.flush()
        assert len(memory_exporter.get_batches()) == 1
    
    def test_add_exporter(self, telemetry_provider):
        """Test adding exporter."""
        new_exporter = MemoryMetricsExporter()
        telemetry_provider.add_exporter(new_exporter)
        assert len(telemetry_provider.get_exporters()) >= 2
    
    def test_get_metrics_count(self, telemetry_provider):
        """Test getting buffered metrics count."""
        telemetry_provider.record_metric("metric1", 10)
        telemetry_provider.record_metric("metric2", 20)
        assert telemetry_provider.get_metrics_count() == 2
    
    def test_shutdown(self, telemetry_provider, memory_exporter):
        """Test provider shutdown."""
        telemetry_provider.record_metric("metric1", 10)
        telemetry_provider.shutdown()
        
        # All metrics should be flushed
        assert telemetry_provider.get_metrics_count() == 0


class TestTelemetryProviderAsync:
    """Test async telemetry provider."""
    
    def test_async_provider_creation(self):
        """Test creating async provider."""
        exporter = MemoryMetricsExporter()
        provider = TelemetryProvider(
            exporters=[exporter],
            batch_size=2,
            use_async=True
        )
        
        # Verify async export thread is running
        assert provider.use_async
        assert provider.is_running()
        
        provider.shutdown()
    
    def test_async_flag(self):
        """Test is_running with async."""
        provider = TelemetryProvider(use_async=True)
        assert provider.is_running()
        provider.shutdown()
    
    def test_sync_flag(self):
        """Test is_running with sync."""
        provider = TelemetryProvider(use_async=False)
        assert provider.is_running()
        provider.shutdown()
    
    def test_sync_export(self):
        """Test synchronous export."""
        exporter = MemoryMetricsExporter()
        provider = TelemetryProvider(
            exporters=[exporter],
            batch_size=2,
            use_async=False
        )
        
        # Record metrics to trigger batch
        provider.record_metric("metric0", 0)
        provider.record_metric("metric1", 1)
        
        # Should be exported immediately in sync mode
        assert len(exporter.get_batches()) >= 1
        
        provider.shutdown()


class TestTelemetryConfiguration:
    """Test telemetry configuration."""
    
    def test_default_configuration(self):
        """Test default configuration."""
        config = TelemetryConfiguration()
        assert config.enable_console
        assert config.enable_memory
        assert config.batch_size == 10
        assert config.use_async
    
    def test_custom_configuration(self):
        """Test custom configuration."""
        config = TelemetryConfiguration(
            enable_console=False,
            enable_memory=True,
            batch_size=20,
            use_async=False
        )
        assert not config.enable_console
        assert config.enable_memory
        assert config.batch_size == 20
        assert not config.use_async


class TestCreateTelemetryProvider:
    """Test telemetry provider factory."""
    
    def test_create_with_defaults(self):
        """Test creating with defaults."""
        provider = create_telemetry_provider()
        assert len(provider.get_exporters()) > 0
        provider.shutdown()
    
    def test_create_with_config(self):
        """Test creating with custom config."""
        config = TelemetryConfiguration(
            enable_console=False,
            enable_memory=True,
            batch_size=5
        )
        provider = create_telemetry_provider(config)
        assert len(provider.get_exporters()) >= 1
        provider.shutdown()
    
    def test_get_default_provider(self):
        """Test getting default provider."""
        provider = get_default_telemetry_provider()
        assert len(provider.get_exporters()) > 0
        provider.shutdown()


class TestMetricTypes:
    """Test different metric types."""
    
    def test_counter_metric(self):
        """Test counter metric."""
        metric = MetricData(
            name="requests.total",
            type=MetricType.COUNTER,
            value=1000
        )
        assert metric.type == MetricType.COUNTER
    
    def test_gauge_metric(self):
        """Test gauge metric."""
        metric = MetricData(
            name="memory.usage",
            type=MetricType.GAUGE,
            value=512.5
        )
        assert metric.type == MetricType.GAUGE
    
    def test_histogram_metric(self):
        """Test histogram metric."""
        metric = MetricData(
            name="latency.ms",
            type=MetricType.HISTOGRAM,
            value=[10, 20, 30, 40, 50]
        )
        assert metric.type == MetricType.HISTOGRAM
    
    def test_summary_metric(self):
        """Test summary metric."""
        metric = MetricData(
            name="response.time",
            type=MetricType.SUMMARY,
            value={"min": 10, "max": 100, "avg": 50}
        )
        assert metric.type == MetricType.SUMMARY
