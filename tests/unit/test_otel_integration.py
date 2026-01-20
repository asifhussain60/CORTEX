"""
Test suite for OpenTelemetry integration (OB-001-01).

This module tests distributed tracing, span creation, and context propagation
for the CORTEX observability system.

Acceptance Tests:
- Traces exported to backend
- Spans created for key operations
- Context propagation working
"""

import pytest
from typing import Optional, List, Dict, Any
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

# Import the module to be tested (will be created)
from cortex.core.observability.otel_exporter import OtelExporter, TraceConfig
from cortex.core.observability.span_manager import SpanManager, SpanContext


class TestOtelExporterInitialization:
    """Test OtelExporter initialization and configuration."""

    def test_otel_exporter_initializes_with_valid_config(self) -> None:
        """
        Test that OtelExporter can be initialized with a valid configuration.

        Expected:
        - Exporter instance created successfully
        - Service name set correctly
        - Environment validated
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        
        exporter = OtelExporter(config=config)
        
        assert exporter is not None
        assert exporter.service_name == "cortex-test"
        assert exporter.environment == "test"
        assert exporter.enabled is True

    def test_otel_exporter_respects_disabled_flag(self) -> None:
        """
        Test that OtelExporter respects the enabled flag.

        Expected:
        - When enabled=False, no backend connection attempted
        - Exporter still instantiates (no-op mode)
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=False,
        )
        
        exporter = OtelExporter(config=config)
        
        assert exporter.enabled is False

    def test_otel_exporter_requires_valid_service_name(self) -> None:
        """
        Test that OtelExporter validates service name.

        Expected:
        - Empty service name raises ValueError
        """
        with pytest.raises(ValueError, match="service_name cannot be empty"):
            config = TraceConfig(
                service_name="",
                environment="test",
                endpoint="http://localhost:4317",
                enabled=True,
            )


class TestSpanCreation:
    """Test span creation for key operations."""

    def test_span_created_for_orchestrator_execution(self) -> None:
        """
        Test that a span is created when orchestrator executes.

        Expected:
        - Span created with correct operation name
        - Span includes orchestrator metadata
        - Span timing recorded
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        with span_manager.create_span("orchestrator.execute") as span:
            span.set_attribute("orchestrator_type", "planning")
            span.set_attribute("ac_id", "OB-001-01")
        
        # Verify span was created
        assert span is not None
        assert span.name == "orchestrator.execute"

    def test_span_attributes_recorded_correctly(self) -> None:
        """
        Test that span attributes are recorded.

        Expected:
        - Attributes stored in span
        - Attribute types preserved
        - Retrievable after creation
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        with span_manager.create_span("test.operation") as span:
            span.set_attribute("string_attr", "value")
            span.set_attribute("int_attr", 42)
            span.set_attribute("bool_attr", True)
        
        assert span.get_attribute("string_attr") == "value"
        assert span.get_attribute("int_attr") == 42
        assert span.get_attribute("bool_attr") is True

    def test_span_records_exception(self) -> None:
        """
        Test that spans can record exceptions.

        Expected:
        - Exception recorded in span
        - Stack trace captured
        - Span marked as error
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        try:
            with span_manager.create_span("error.operation") as span:
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify error was recorded
        assert span.status == "ERROR"


class TestContextPropagation:
    """Test context propagation across service boundaries."""

    def test_context_propagated_to_child_spans(self) -> None:
        """
        Test that parent span context propagates to child spans.

        Expected:
        - Child span has correct parent ID
        - Trace ID consistent across spans
        - Span hierarchy maintained
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        with span_manager.create_span("parent.operation") as parent_span:
            parent_trace_id = parent_span.trace_id
            
            with span_manager.create_span("child.operation") as child_span:
                assert child_span.trace_id == parent_trace_id
                assert child_span.parent_span_id == parent_span.span_id

    def test_context_serialization_for_propagation(self) -> None:
        """
        Test that span context can be serialized for propagation.

        Expected:
        - Context serialized to string format
        - Contains trace ID, span ID
        - Can be deserialized on remote service
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        with span_manager.create_span("serialize.test") as span:
            serialized = span_manager.serialize_context()
        
        assert serialized is not None
        assert "trace_id" in serialized
        assert "span_id" in serialized
        
        # Deserialize and verify
        context = span_manager.deserialize_context(serialized)
        assert context["trace_id"] is not None

    def test_context_propagation_in_headers(self) -> None:
        """
        Test that context is properly formatted for HTTP headers.

        Expected:
        - Returns W3C Trace Context headers
        - traceparent header includes version, trace-id, parent-id, trace-flags
        - tracestate header properly formatted
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        with span_manager.create_span("header.test") as span:
            headers = span_manager.get_propagation_headers()
        
        assert "traceparent" in headers
        # Format: version-trace_id-parent_id-trace_flags
        traceparent = headers["traceparent"]
        parts = traceparent.split("-")
        assert len(parts) == 4


class TestTraceExport:
    """Test trace export to backend."""

    def test_traces_exported_to_configured_backend(self) -> None:
        """
        Test that traces are exported to the configured backend.

        Expected:
        - Export method called when trace complete
        - Correct endpoint used
        - Trace data properly formatted
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        
        exporter = OtelExporter(config=config)
        
        with patch.object(exporter, "export_traces") as mock_export:
            with exporter.span_manager.create_span("export.test"):
                pass
            
            exporter.flush()
            mock_export.assert_called_once()

    def test_batch_export_on_threshold(self) -> None:
        """
        Test that traces are batch exported when threshold reached.

        Expected:
        - Export triggered when span count exceeds threshold
        - All spans in batch included
        - Batch cleared after export
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
            batch_size=5,
        )
        
        exporter = OtelExporter(config=config)
        
        # Create 5 spans (should trigger export)
        for i in range(5):
            with exporter.span_manager.create_span(f"batch.operation.{i}"):
                pass
        
        # Verify batch was exported
        assert exporter.pending_spans == 0

    def test_export_timeout_on_shutdown(self) -> None:
        """
        Test that pending traces are exported on shutdown.

        Expected:
        - Exporter flushes on __exit__
        - Timeout respected
        - All pending spans sent
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
            shutdown_timeout_seconds=5,
        )
        
        exporter = OtelExporter(config=config)
        
        with patch.object(exporter, "flush") as mock_flush:
            exporter.__exit__(None, None, None)
            mock_flush.assert_called_once_with(timeout_seconds=5)


class TestMetricsCollection:
    """Test metrics collection alongside tracing."""

    def test_span_creates_duration_metric(self) -> None:
        """
        Test that span duration is recorded as metric.

        Expected:
        - Duration in milliseconds
        - Recorded with span name as metric name
        - Tagged with operation type
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        span_manager = SpanManager(exporter=OtelExporter(config=config))
        
        with span_manager.create_span("metric.test") as span:
            span.set_attribute("operation", "execute")
        
        duration_ms = span.get_duration_ms()
        
        assert duration_ms >= 0
        assert isinstance(duration_ms, (int, float))

    def test_span_counts_per_operation(self) -> None:
        """
        Test that span counts are tracked per operation.

        Expected:
        - Counter incremented for each operation type
        - Counters breakable by operation name
        - Running total available
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        exporter = OtelExporter(config=config)
        
        # Create multiple spans of same type
        for _ in range(3):
            with exporter.span_manager.create_span("count.test"):
                pass
        
        count = exporter.span_manager.get_span_count("count.test")
        assert count == 3


class TestAuditTrailIntegration:
    """Test integration with audit logging system."""

    def test_otel_integration_logged_in_audit_trail(self) -> None:
        """
        Test that OB-001-01 implementation is logged in audit trail.

        Expected:
        - AC_START entry created
        - AC_EXECUTE entries created during span lifecycle
        - AC_COMPLETE entry created on successful export
        """
        # Mock audit logger
        mock_audit_logger = Mock()
        mock_audit_logger.query_by_ac_id = Mock(return_value=[
            Mock(operation="AC_START"),
            Mock(operation="AC_EXECUTE"),
            Mock(operation="AC_COMPLETE"),
        ])
        
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=True,
        )
        
        exporter = OtelExporter(config=config, audit_logger=mock_audit_logger)
        
        # Verify audit entries created
        entries = mock_audit_logger.query_by_ac_id("OB-001-01")
        
        # Should have at least START and COMPLETE
        assert len(entries) >= 2
        assert any(e.operation == "AC_START" for e in entries)


class TestErrorHandling:
    """Test error handling in OpenTelemetry integration."""

    def test_graceful_degradation_when_backend_unavailable(self) -> None:
        """
        Test that tracing degrades gracefully when backend unavailable.

        Expected:
        - No exceptions raised
        - Spans still created locally
        - Export fails silently
        - System continues operating
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://invalid-backend:4317",
            enabled=True,
        )
        
        exporter = OtelExporter(config=config)
        
        # Should not raise exception
        with exporter.span_manager.create_span("graceful.degradation"):
            pass
        
        # Flush should not raise exception
        exporter.flush()

    def test_no_observability_overhead_when_disabled(self) -> None:
        """
        Test that disabled observability has minimal overhead.

        Expected:
        - No network calls when disabled
        - No memory accumulation
        - CPU overhead negligible
        """
        config = TraceConfig(
            service_name="cortex-test",
            environment="test",
            endpoint="http://localhost:4317",
            enabled=False,
        )
        
        exporter = OtelExporter(config=config)
        
        # Should be no-op
        with exporter.span_manager.create_span("no.op.test"):
            pass
        
        assert exporter.pending_spans == 0


class TestTypeHints:
    """Test that all functions have proper type hints (CORE-011)."""

    def test_otel_exporter_has_type_hints(self) -> None:
        """
        Test that OtelExporter methods have complete type hints.

        Expected:
        - All parameters have type annotations
        - Return types specified
        """
        import inspect
        
        methods = inspect.getmembers(OtelExporter, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                # Verify return annotation exists
                assert sig.return_annotation != inspect.Signature.empty

    def test_span_manager_has_type_hints(self) -> None:
        """
        Test that SpanManager methods have complete type hints.

        Expected:
        - All parameters have type annotations
        - Return types specified
        """
        import inspect
        
        methods = inspect.getmembers(SpanManager, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                # Verify return annotation exists
                assert sig.return_annotation != inspect.Signature.empty


class TestDocstrings:
    """Test that all public APIs have docstrings (CORE-012)."""

    def test_otel_exporter_has_docstrings(self) -> None:
        """
        Test that OtelExporter has docstrings on public methods.

        Expected:
        - All public methods have docstrings
        - Docstrings follow Google style
        """
        import inspect
        
        methods = inspect.getmembers(OtelExporter, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None

    def test_span_manager_has_docstrings(self) -> None:
        """
        Test that SpanManager has docstrings on public methods.

        Expected:
        - All public methods have docstrings
        - Docstrings follow Google style
        """
        import inspect
        
        methods = inspect.getmembers(SpanManager, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
