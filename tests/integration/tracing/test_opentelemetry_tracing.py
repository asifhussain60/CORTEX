# AC_START: AC-PHASE82.S3-OTEL-TESTS
# Description: OpenTelemetry tracing test suite
# Phase: 82, Stage: 3, Part: 3 (OpenTelemetry Tracing)
# TDD Cycle: RED phase (full coverage)

"""
Test Suite: OpenTelemetry Distributed Tracing

Test Coverage:
- Span creation and lifecycle
- Trace context propagation (W3C format)
- Parent-child span relationships
- Domain-specific router spans
- Span attributes and events
- Trace export format

Author: CORTEX/TDD-Orchestrator
Governance: CORE-008 (tests first), coverage-driven
"""

import pytest
import time
import json
from cortex.opentelemetry_tracing import (
    SpanKind,
    SpanStatus,
    SpanContext,
    Span,
    TracerProvider,
    Tracer,
    IntentRouterTracer,
)


class TestSpanKind:
    """Test SpanKind enum."""

    def test_span_kind_values(self):
        """Test SpanKind enum values."""
        assert SpanKind.INTERNAL.value == "INTERNAL"
        assert SpanKind.SERVER.value == "SERVER"
        assert SpanKind.CLIENT.value == "CLIENT"
        assert SpanKind.PRODUCER.value == "PRODUCER"
        assert SpanKind.CONSUMER.value == "CONSUMER"


class TestSpanStatus:
    """Test SpanStatus enum."""

    def test_span_status_values(self):
        """Test SpanStatus enum values."""
        assert SpanStatus.UNSET.value == "UNSET"
        assert SpanStatus.OK.value == "OK"
        assert SpanStatus.ERROR.value == "ERROR"


class TestSpanContext:
    """Test distributed trace context."""

    def test_span_context_creation(self):
        """Test SpanContext creation with default values."""
        context = SpanContext()
        assert context.trace_id
        assert context.span_id
        assert context.parent_span_id is None
        assert context.flags == 0x01

    def test_span_context_custom_values(self):
        """Test SpanContext with custom values."""
        context = SpanContext(
            trace_id="abc123",
            span_id="def456",
            parent_span_id="ghi789",
        )
        assert context.trace_id == "abc123"
        assert context.span_id == "def456"
        assert context.parent_span_id == "ghi789"

    def test_span_context_to_headers(self):
        """Test converting context to W3C headers."""
        context = SpanContext(
            trace_id="abc123",
            span_id="def456",
            flags=0x01,
        )
        headers = context.to_headers()
        assert "traceparent" in headers
        assert "abc123" in headers["traceparent"]
        assert "def456" in headers["traceparent"]

    def test_span_context_from_headers(self):
        """Test extracting context from W3C headers."""
        headers = {
            "traceparent": "00-abc123-def456-01",
        }
        context = SpanContext.from_headers(headers)
        assert context.trace_id == "abc123"
        assert context.span_id == "def456"
        assert context.flags == 0x01

    def test_span_context_from_invalid_headers(self):
        """Test extracting context from invalid headers."""
        context = SpanContext.from_headers({})
        assert context.trace_id
        assert context.span_id

    def test_span_context_roundtrip(self):
        """Test context round-trip through headers."""
        original = SpanContext(trace_id="test123", span_id="span456")
        headers = original.to_headers()
        restored = SpanContext.from_headers(headers)
        assert restored.trace_id == original.trace_id
        assert restored.span_id == original.span_id


class TestSpan:
    """Test Span class."""

    def test_span_creation(self):
        """Test Span instance creation."""
        span = Span(
            span_id="span123",
            trace_id="trace123",
            parent_span_id=None,
            name="test_span",
            kind=SpanKind.INTERNAL,
        )
        assert span.span_id == "span123"
        assert span.trace_id == "trace123"
        assert span.name == "test_span"
        assert span.status == SpanStatus.UNSET

    def test_span_set_attribute(self):
        """Test setting span attributes."""
        span = Span(
            span_id="s1",
            trace_id="t1",
            parent_span_id=None,
            name="test",
            kind=SpanKind.INTERNAL,
        )
        span.set_attribute("mode", "IMPLEMENT")
        span.set_attribute("request_id", "req123")

        assert span.attributes["mode"] == "IMPLEMENT"
        assert span.attributes["request_id"] == "req123"

    def test_span_add_event(self):
        """Test adding events to span."""
        span = Span(
            span_id="s1",
            trace_id="t1",
            parent_span_id=None,
            name="test",
            kind=SpanKind.INTERNAL,
        )
        span.add_event("started")
        span.add_event("processing", {"step": 1})

        assert len(span.events) == 2
        assert span.events[0]["name"] == "started"
        assert span.events[1]["name"] == "processing"
        assert span.events[1]["attributes"]["step"] == 1

    def test_span_end(self):
        """Test ending span."""
        span = Span(
            span_id="s1",
            trace_id="t1",
            parent_span_id=None,
            name="test",
            kind=SpanKind.INTERNAL,
        )
        assert span.end_time is None
        span.end()
        assert span.end_time is not None

    def test_span_duration_ms(self):
        """Test span duration calculation."""
        span = Span(
            span_id="s1",
            trace_id="t1",
            parent_span_id=None,
            name="test",
            kind=SpanKind.INTERNAL,
        )
        time.sleep(0.01)  # 10ms
        span.end()
        duration = span.duration_ms()
        assert duration >= 10
        assert duration < 100

    def test_span_to_dict(self):
        """Test span serialization to dictionary."""
        span = Span(
            span_id="s1",
            trace_id="t1",
            parent_span_id="p1",
            name="test",
            kind=SpanKind.INTERNAL,
        )
        span.set_attribute("attr1", "value1")
        span.add_event("event1")
        span.end()

        span_dict = span.to_dict()
        assert span_dict["span_id"] == "s1"
        assert span_dict["trace_id"] == "t1"
        assert span_dict["parent_span_id"] == "p1"
        assert span_dict["name"] == "test"
        assert span_dict["kind"] == "INTERNAL"
        assert "duration_ms" in span_dict
        assert span_dict["attributes"]["attr1"] == "value1"
        assert len(span_dict["events"]) == 1


class TestTracerProvider:
    """Test TracerProvider class."""

    def test_tracer_provider_creation(self):
        """Test TracerProvider instance creation."""
        provider = TracerProvider("test-service")
        assert provider.service_name == "test-service"

    def test_tracer_provider_default_service(self):
        """Test TracerProvider default service name."""
        provider = TracerProvider()
        assert provider.service_name == "cortex-intentrouter"

    def test_get_tracer(self):
        """Test getting tracer from provider."""
        provider = TracerProvider()
        tracer = provider.get_tracer("test-tracer")
        assert tracer is not None
        assert isinstance(tracer, Tracer)
        assert tracer.name == "test-tracer"

    def test_start_span(self):
        """Test starting span from provider."""
        provider = TracerProvider()
        context = SpanContext()
        span = provider.start_span("test_span", SpanKind.INTERNAL, context)

        assert span.name == "test_span"
        assert span.trace_id == context.trace_id
        assert span.status == SpanStatus.UNSET

    def test_parent_child_span_relationship(self):
        """Test parent-child span relationships."""
        provider = TracerProvider()
        context = SpanContext()

        # Start parent span
        parent = provider.start_span("parent", SpanKind.SERVER, context)
        parent_id = parent.span_id

        # Start child span
        child = provider.start_span("child", SpanKind.INTERNAL, context)
        assert child.parent_span_id == parent_id

    def test_end_span_pops_stack(self):
        """Test ending span pops from stack."""
        provider = TracerProvider()
        context = SpanContext()

        parent = provider.start_span("parent", SpanKind.SERVER, context)
        provider.start_span("child", SpanKind.INTERNAL, context)

        # Current should be child
        assert provider._current_span is not None
        assert provider._current_span.name == "child"

        # End child, current should revert to parent
        current_span = provider._current_span
        provider.end_span(current_span)
        assert provider._current_span is not None
        assert provider._current_span.name == "parent"

    def test_get_trace(self):
        """Test retrieving all spans in trace."""
        provider = TracerProvider()
        context = SpanContext()

        provider.start_span("span1", SpanKind.INTERNAL, context)
        provider.start_span("span2", SpanKind.INTERNAL, context)

        trace_spans = provider.get_trace(context.trace_id)
        assert len(trace_spans) == 2

    def test_export_trace(self):
        """Test trace export format."""
        provider = TracerProvider("test-service")
        context = SpanContext()

        provider.start_span("span1", SpanKind.INTERNAL, context)
        provider.start_span("span2", SpanKind.INTERNAL, context)

        exported = provider.export_trace(context.trace_id)
        assert exported["trace_id"] == context.trace_id
        assert exported["service"] == "test-service"
        assert exported["span_count"] == 2
        assert "timestamp" in exported
        assert len(exported["spans"]) == 2


class TestTracer:
    """Test Tracer class."""

    @pytest.fixture
    def provider(self):
        """Create provider fixture."""
        return TracerProvider("test-service")

    @pytest.fixture
    def tracer(self, provider):
        """Create tracer fixture."""
        return provider.get_tracer("test-tracer")

    def test_tracer_creation(self, provider):
        """Test Tracer instance creation."""
        tracer = provider.get_tracer("custom-tracer")
        assert tracer.name == "custom-tracer"
        assert tracer.provider is provider

    def test_tracer_start_span(self, tracer):
        """Test tracer start span."""
        context = SpanContext()
        span = tracer.start_span("test", SpanKind.INTERNAL, context)
        assert span.name == "test"

    def test_tracer_span_context_manager(self, tracer):
        """Test tracer span context manager."""
        context = SpanContext()
        with tracer.span_context("test_span", SpanKind.INTERNAL, context) as span:
            assert span.name == "test_span"
            assert span.status == SpanStatus.UNSET

        # After context, span should be ended
        assert span.end_time is not None

    def test_tracer_span_decorator(self, tracer):
        """Test tracer span decorator."""

        @tracer.span_decorator("decorated_function", SpanKind.INTERNAL)
        def sample_function():
            return "result"

        result = sample_function()
        assert result == "result"

    def test_span_context_manager_with_exception(self, tracer):
        """Test span context manager handles exceptions."""
        try:
            with tracer.span_context("error_span") as span:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Span should record error
        assert span.status == SpanStatus.ERROR
        assert "Test error" in span.error


class TestIntentRouterTracer:
    """Test IntentRouterTracer domain-specific spans."""

    @pytest.fixture
    def provider(self):
        """Create provider fixture."""
        return TracerProvider("cortex-intentrouter")

    @pytest.fixture
    def router_tracer(self, provider):
        """Create router tracer fixture."""
        return IntentRouterTracer(provider)

    def test_trace_routing_request(self, router_tracer):
        """Test tracing routing request."""
        with router_tracer.trace_routing_request() as span:
            span.set_attribute("intent_mode", "IMPLEMENT")
            assert span.name == "routing_request"
            assert span.kind == SpanKind.SERVER

    def test_trace_capability_matching(self, router_tracer):
        """Test tracing capability matching."""
        with router_tracer.trace_capability_matching() as span:
            span.set_attribute("modes_checked", 5)
            assert span.name == "capability_matching"
            assert span.kind == SpanKind.INTERNAL

    def test_trace_agent_collaboration(self, router_tracer):
        """Test tracing agent collaboration."""
        with router_tracer.trace_agent_collaboration("sequential") as span:
            span.set_attribute("agent_count", 3)
            assert "agent_collaboration" in span.name
            assert "sequential" in span.name
            assert span.kind == SpanKind.INTERNAL

    def test_trace_mcp_tool_execution(self, router_tracer):
        """Test tracing MCP tool execution."""
        with router_tracer.trace_mcp_tool_execution("cortex_process_request") as span:
            span.set_attribute("status", "success")
            assert "mcp_tool" in span.name
            assert "cortex_process_request" in span.name
            assert span.kind == SpanKind.CLIENT

    def test_trace_cache_operation(self, router_tracer):
        """Test tracing cache operations."""
        with router_tracer.trace_cache_operation("get") as span:
            span.set_attribute("cache_hit", True)
            assert "cache_get" in span.name
            assert span.kind == SpanKind.INTERNAL


class TestTraceHierarchy:
    """Test trace hierarchy with multiple span levels."""

    @pytest.fixture
    def provider(self):
        """Create provider fixture."""
        return TracerProvider("test-service")

    @pytest.fixture
    def router_tracer(self, provider):
        """Create router tracer fixture."""
        return IntentRouterTracer(provider)

    def test_nested_spans(self, router_tracer):
        """Test nested spans in hierarchy."""
        context = SpanContext()

        with router_tracer.trace_routing_request(context) as request_span:
            request_span.set_attribute("request_id", "req123")

            with router_tracer.trace_capability_matching(context) as matching_span:
                matching_span.set_attribute("modes", 5)

                with router_tracer.trace_mcp_tool_execution(
                    "cortex_process_request", context
                ) as tool_span:
                    tool_span.set_attribute("result", "success")

        # Verify hierarchy
        provider_obj = router_tracer.provider
        trace_spans = provider_obj.get_trace(context.trace_id)
        assert len(trace_spans) == 3

    def test_parallel_spans(self, router_tracer):
        """Test parallel spans at same level (create separate spans)."""
        context = SpanContext()

        # Create independent spans (not nested)
        router_tracer.trace_agent_collaboration("sequential").__enter__()
        span1 = router_tracer.provider._current_span
        router_tracer.provider.end_span(span1)

        router_tracer.trace_cache_operation("get").__enter__()
        span2 = router_tracer.provider._current_span
        router_tracer.provider.end_span(span2)

        # Both should be recorded
        assert span1 is not None
        assert span2 is not None
        assert span1.name != span2.name


class TestTraceExport:
    """Test trace export functionality."""

    def test_export_format_compliance(self):
        """Test exported trace meets standard format."""
        provider = TracerProvider("test-service")
        context = SpanContext()

        provider.start_span("span1", SpanKind.INTERNAL, context)
        provider.start_span("span2", SpanKind.INTERNAL, context)

        exported = provider.export_trace(context.trace_id)

        # Verify structure
        assert "trace_id" in exported
        assert "service" in exported
        assert "timestamp" in exported
        assert "span_count" in exported
        assert "spans" in exported
        assert isinstance(exported["spans"], list)

    def test_export_json_serializable(self):
        """Test exported trace is JSON serializable."""
        provider = TracerProvider("test-service")
        context = SpanContext()

        provider.start_span("span1", SpanKind.INTERNAL, context)

        exported = provider.export_trace(context.trace_id)
        json_str = json.dumps(exported)
        assert json_str
        assert "trace_id" in json_str


class TestPerformanceOverhead:
    """Test tracing performance overhead."""

    def test_tracing_overhead_acceptable(self):
        """Test tracing overhead is <10ms per request."""
        provider = TracerProvider()
        context = SpanContext()

        start = time.perf_counter()
        for _ in range(100):
            with provider.get_tracer().span_context("test", SpanKind.INTERNAL, context):
                pass
        duration = (time.perf_counter() - start) * 1000  # Convert to ms

        # 100 traces in <1000ms = <10ms per trace on average
        assert duration < 1000, f"Tracing took {duration}ms for 100 traces"

    def test_span_creation_fast(self):
        """Test individual span creation is fast."""
        provider = TracerProvider()
        context = SpanContext()

        start = time.perf_counter()
        for _ in range(1000):
            provider.start_span("test", SpanKind.INTERNAL, context)
        duration = (time.perf_counter() - start) * 1_000_000  # Convert to microseconds

        # Each span creation should be <1ms on average
        avg_time = duration / 1000
        assert avg_time < 1000, f"Span creation took {avg_time}µs on average"


# AC_COMPLETE: AC-PHASE82.S3-OTEL-TESTS ✅
# OpenTelemetry tracing test suite complete with 28+ comprehensive tests
# All span types, hierarchy, export, and performance covered
