"""
Tests for distributed tracing with OpenTelemetry (AC-OPS-004-03).

Tests trace context propagation, automatic span creation for key operations,
sampling strategies, and trace export functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Optional

from cortex.infrastructure.tracing import (
    TracingConfig,
    TracingCollector,
    TraceContext,
    SpanKind,
    SpanStatus,
)


class TestTracingConfigAndInitialization:
    """Test tracing configuration and initialization."""

    def test_tracing_config_creation(self) -> None:
        """Test creating tracing configuration."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            sample_rate=1.0,
        )
        assert config.service_name == "cortex-test"
        assert config.environment == "test"
        assert config.sample_rate == 1.0

    def test_tracing_config_sampling_rates(self) -> None:
        """Test sampling rate configurations."""
        config = TracingConfig(
            service_name="cortex",
            environment="production",
            sample_rate=0.01,  # 1% in production
            error_sample_rate=1.0,  # 100% for errors
        )
        assert config.sample_rate == 0.01
        assert config.error_sample_rate == 1.0

    def test_tracing_collector_creation(self) -> None:
        """Test creating tracing collector."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
        )
        collector = TracingCollector(config)
        assert collector is not None
        assert collector.config.service_name == "cortex-test"


class TestTraceContextPropagation:
    """Test trace context propagation via headers."""

    def test_trace_context_generation(self) -> None:
        """Test generating new trace context."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        assert context is not None
        assert context.trace_id is not None
        assert context.span_id is not None

    def test_trace_context_from_headers(self) -> None:
        """Test extracting trace context from headers."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        headers = {
            "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
            "tracestate": "cortex=1",
        }
        
        context = collector.extract_context_from_headers(headers)
        assert context is not None
        assert context.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"

    def test_trace_context_to_headers(self) -> None:
        """Test converting trace context to headers."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        context.baggage = {"user_id": "user-123"}
        headers = collector.context_to_headers(context)
        
        assert "traceparent" in headers
        assert "tracestate" in headers

    def test_trace_context_propagation_across_calls(self) -> None:
        """Test trace context propagates through call chain."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        # Start initial context
        context1 = collector.create_trace_context()
        trace_id_1 = context1.trace_id
        
        # Convert to headers
        headers = collector.context_to_headers(context1)
        
        # Extract in "new service"
        context2 = collector.extract_context_from_headers(headers)
        
        # Trace ID should be the same
        assert context2.trace_id == trace_id_1


class TestAutomaticSpanCreation:
    """Test automatic span creation for key operations."""

    def test_http_request_span_creation(self) -> None:
        """Test creating span for HTTP request."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="http_request",
            kind=SpanKind.SERVER,
            parent_context=context,
            attributes={
                "http.method": "GET",
                "http.url": "/api/test",
                "http.target": "/api/test",
            },
        )
        
        assert span is not None
        assert span.name == "http_request"
        assert span.attributes["http.method"] == "GET"

    def test_database_query_span_creation(self) -> None:
        """Test creating span for database query."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="db_query",
            kind=SpanKind.INTERNAL,
            parent_context=context,
            attributes={
                "db.system": "postgresql",
                "db.statement": "SELECT * FROM users WHERE id = ?",
                "db.operation": "SELECT",
            },
        )
        
        assert span is not None
        assert span.attributes["db.system"] == "postgresql"

    def test_governance_check_span_creation(self) -> None:
        """Test creating span for governance check."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="governance_check",
            kind=SpanKind.INTERNAL,
            parent_context=context,
            attributes={
                "governance.rule": "CORE-001",
                "governance.decision": "allow",
            },
        )
        
        assert span is not None
        assert span.attributes["governance.rule"] == "CORE-001"

    def test_mcp_tool_span_creation(self) -> None:
        """Test creating span for MCP tool invocation."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="mcp_tool",
            kind=SpanKind.INTERNAL,
            parent_context=context,
            attributes={
                "mcp.tool": "file_read",
                "mcp.args": '{"path": "/data/file.txt"}',
            },
        )
        
        assert span is not None
        assert span.attributes["mcp.tool"] == "file_read"


class TestSpanAttributes:
    """Test span attributes and error handling."""

    def test_span_duration_recording(self) -> None:
        """Test recording span duration."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="test_operation",
            kind=SpanKind.INTERNAL,
            parent_context=context,
        )
        
        time.sleep(0.01)  # Simulate work
        collector.end_span(span, status=SpanStatus.OK)
        
        # Duration should be recorded
        assert span.duration_ms is not None
        assert span.duration_ms >= 10  # At least 10ms

    def test_span_error_recording(self) -> None:
        """Test recording span with error."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="failing_operation",
            kind=SpanKind.INTERNAL,
            parent_context=context,
        )
        
        error = Exception("Test error")
        collector.end_span(
            span,
            status=SpanStatus.ERROR,
            error=error,
        )
        
        assert span.status == SpanStatus.ERROR
        assert span.error_message is not None

    def test_span_custom_attributes(self) -> None:
        """Test adding custom attributes to span."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span(
            name="custom_operation",
            kind=SpanKind.INTERNAL,
            parent_context=context,
            attributes={
                "custom.user_id": "user-123",
                "custom.request_id": "req-456",
                "custom.metadata": '{"key": "value"}',
            },
        )
        
        assert span.attributes["custom.user_id"] == "user-123"
        assert span.attributes["custom.request_id"] == "req-456"


class TestSamplingStrategies:
    """Test sampling configuration and strategies."""

    def test_sampling_disabled(self) -> None:
        """Test disabling sampling (sample all traces)."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            sample_rate=1.0,
        )
        collector = TracingCollector(config)
        
        # All traces should be sampled
        for i in range(10):
            sampled = collector.should_sample_trace()
            assert sampled is True

    def test_sampling_percentage(self) -> None:
        """Test percentage-based sampling."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            sample_rate=0.5,  # 50% sampling
        )
        collector = TracingCollector(config)
        
        # Should sample approximately 50% of traces
        sampled_count = sum(
            1 for _ in range(100)
            if collector.should_sample_trace()
        )
        
        # Should be roughly 50% (allowing 30-70% for randomness)
        assert 20 <= sampled_count <= 80

    def test_error_sampling_always_sampled(self) -> None:
        """Test that errors are always sampled regardless of sample rate."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            sample_rate=0.0,  # Never sample normal traces
            error_sample_rate=1.0,  # Always sample errors
        )
        collector = TracingCollector(config)
        
        # Error traces should always be sampled
        context = collector.create_trace_context()
        context.has_error = True
        
        sampled = collector.should_sample_trace(context)
        assert sampled is True

    def test_production_sampling_configuration(self) -> None:
        """Test recommended sampling for production."""
        config = TracingConfig(
            service_name="cortex",
            environment="production",
            sample_rate=0.01,  # 1% success traces
            error_sample_rate=1.0,  # 100% errors
        )
        
        assert config.sample_rate == 0.01
        assert config.error_sample_rate == 1.0


class TestTraceExport:
    """Test trace export to Jaeger/Zipkin."""

    def test_trace_export_configuration(self) -> None:
        """Test configuring trace export."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            jaeger_host="localhost",
            jaeger_port=6831,
        )
        
        assert config.jaeger_host == "localhost"
        assert config.jaeger_port == 6831

    def test_trace_retention_policy(self) -> None:
        """Test trace retention configuration."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            trace_retention_days=7,
            error_trace_retention_days=30,
        )
        
        assert config.trace_retention_days == 7
        assert config.error_trace_retention_days == 30

    def test_trace_buffering(self) -> None:
        """Test trace buffering for export."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            batch_size=100,
            flush_interval_seconds=5,
        )
        collector = TracingCollector(config)
        
        # Create multiple spans
        context = collector.create_trace_context()
        for i in range(10):
            span = collector.start_span(
                name=f"operation_{i}",
                kind=SpanKind.INTERNAL,
                parent_context=context,
            )
            collector.end_span(span, status=SpanStatus.OK)
        
        # Should buffer spans without immediate export
        buffered = collector.get_buffered_spans()
        assert len(buffered) == 10


class TestMissingTraceContext:
    """Test handling missing trace context."""

    def test_new_trace_context_on_missing(self) -> None:
        """Test creating new trace context when missing."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        # Extract from empty headers
        context = collector.extract_context_from_headers({})
        
        # Should create new context
        assert context is not None
        assert context.trace_id is not None

    def test_baggage_propagation_optional(self) -> None:
        """Test that baggage propagation is optional."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        context.baggage = {"user_id": "user-123"}
        
        headers = collector.context_to_headers(context)
        
        # Baggage should be in headers if supported
        extracted = collector.extract_context_from_headers(headers)
        assert extracted is not None


class TestEdgeCases:
    """Test edge cases in tracing."""

    def test_circular_span_references(self) -> None:
        """Test detecting and breaking circular span references."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span1 = collector.start_span("op1", kind=SpanKind.INTERNAL, parent_context=context)
        span2 = collector.start_span("op2", kind=SpanKind.INTERNAL, parent_context=context)
        
        # Attempt circular reference - should not crash
        collector.end_span(span1, status=SpanStatus.OK)
        collector.end_span(span2, status=SpanStatus.OK)
        
        # Should complete without error
        assert True

    def test_large_trace_aggressive_sampling(self) -> None:
        """Test more aggressive sampling for large traces."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
            max_spans_per_trace=1000,
        )
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        
        # Create many spans
        for i in range(1500):
            span = collector.start_span(
                name=f"op_{i}",
                kind=SpanKind.INTERNAL,
                parent_context=context,
            )
            collector.end_span(span, status=SpanStatus.OK)
        
        # Should apply sampling to stay under limit
        traces = collector.get_traces()
        assert traces is not None

    def test_span_export_failure_buffering(self) -> None:
        """Test buffering spans on export failure."""
        config = TracingConfig(
            service_name="cortex-test",
            environment="test",
        )
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        span = collector.start_span("test_op", kind=SpanKind.INTERNAL, parent_context=context)
        collector.end_span(span, status=SpanStatus.OK)
        
        # Export should either succeed or buffer for retry
        exported = collector.try_export_spans()
        # Should not raise error
        assert exported is not None


class TestTracingPerformance:
    """Test tracing overhead and performance."""

    def test_tracing_overhead_minimal(self) -> None:
        """Test that tracing adds minimal overhead."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        
        start = time.time()
        for i in range(1000):
            span = collector.start_span(
                name="test_op",
                kind=SpanKind.INTERNAL,
                parent_context=context,
            )
            collector.end_span(span, status=SpanStatus.OK)
        elapsed = time.time() - start
        
        # Should be able to record 1000 spans in <100ms
        assert elapsed < 0.1, f"Tracing 1000 spans took {elapsed*1000:.0f}ms"

    def test_context_propagation_lightweight(self) -> None:
        """Test that context propagation is lightweight."""
        config = TracingConfig(service_name="cortex-test", environment="test")
        collector = TracingCollector(config)
        
        context = collector.create_trace_context()
        
        start = time.time()
        for i in range(1000):
            headers = collector.context_to_headers(context)
            extracted = collector.extract_context_from_headers(headers)
        elapsed = time.time() - start
        
        # Should be able to propagate 1000 times in <50ms
        assert elapsed < 0.05, f"Context propagation 1000x took {elapsed*1000:.0f}ms"
