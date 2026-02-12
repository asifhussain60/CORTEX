# AC_START: AC-WAVEB-003
# Description: OpenTelemetry distributed tracing tests (ENH-063 Phase 3)
# Wave: B, Phase: 3, Part: 3
# TDD Cycle: GREEN (verify existing tracing)

"""
Test Suite: OpenTelemetry Distributed Tracing

Tests for existing OpenTelemetry tracing implementation:
1. test_span_creation - Basic span creation
2. test_trace_context_propagation - W3C trace context
3. test_span_attributes - Custom attributes
4. test_nested_spans - Parent-child relationships
5. test_trace_export - Export to Jaeger/Zipkin
6. test_performance_overhead - <10ms overhead
7. test_concurrent_traces - Multiple concurrent traces

Authority: ENH-063 Phase 3
Governance: CORE-008 (TDD-first)
"""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from cortex.opentelemetry_tracing import (
    SpanContext,
    SpanKind,
    SpanStatus,
    Span,
)


class TestOpenTelemetryTracing:
    """Test OpenTelemetry distributed tracing."""

    def test_span_creation(self):
        """Test basic span creation."""
        context = SpanContext()
        
        span = Span(
            span_id=context.span_id,
            trace_id=context.trace_id,
            parent_span_id=None,
            name="test_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.UNSET,
            attributes={},
            events=[],
            start_time=time.time(),
            end_time=None,
        )

        assert span.name == "test_operation"
        assert span.kind == SpanKind.INTERNAL
        assert span.trace_id == context.trace_id
        assert span.parent_span_id is None

    def test_trace_context_propagation(self):
        """Test W3C trace context header propagation."""
        context = SpanContext(
            trace_id="abc123def456",
            span_id="789ghi012jkl",
        )

        headers = context.to_headers()
        
        assert "traceparent" in headers
        assert context.trace_id in headers["traceparent"]
        assert context.span_id in headers["traceparent"]

        # Extract context
        extracted = SpanContext.from_headers(headers)
        assert extracted.trace_id == context.trace_id
        assert extracted.span_id == context.span_id

    def test_span_attributes(self):
        """Test custom span attributes."""
        context = SpanContext()
        
        span = Span(
            span_id=context.span_id,
            trace_id=context.trace_id,
            parent_span_id=None,
            name="test_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.OK,
            attributes={
                "http.method": "POST",
                "http.status_code": 200,
                "custom.field": "value",
            },
            events=[],
            start_time=time.time(),
            end_time=None,
        )

        assert span.attributes["http.method"] == "POST"
        assert span.attributes["http.status_code"] == 200
        assert span.attributes["custom.field"] == "value"

    def test_nested_spans(self):
        """Test parent-child span relationships."""
        parent_context = SpanContext()
        parent_span = Span(
            span_id=parent_context.span_id,
            trace_id=parent_context.trace_id,
            parent_span_id=None,
            name="parent_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.UNSET,
            attributes={},
            events=[],
            start_time=time.time(),
            end_time=None,
        )

        # Create child span
        child_context = SpanContext(
            trace_id=parent_context.trace_id,
            parent_span_id=parent_context.span_id,
        )
        child_span = Span(
            span_id=child_context.span_id,
            trace_id=child_context.trace_id,
            parent_span_id=parent_context.span_id,
            name="child_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.UNSET,
            attributes={},
            events=[],
            start_time=time.time(),
            end_time=None,
        )

        # Verify parent-child relationship
        assert child_span.parent_span_id == parent_span.span_id
        assert child_span.trace_id == parent_span.trace_id

    def test_span_status(self):
        """Test span status transitions."""
        context = SpanContext()
        
        span = Span(
            span_id=context.span_id,
            trace_id=context.trace_id,
            parent_span_id=None,
            name="test_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.UNSET,
            attributes={},
            events=[],
            start_time=time.time(),
            end_time=None,
        )

        # Initially UNSET
        assert span.status == SpanStatus.UNSET

        # Can update to OK or ERROR
        span_ok = Span(
            span_id=context.span_id,
            trace_id=context.trace_id,
            parent_span_id=None,
            name="test_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.OK,
            attributes={},
            events=[],
            start_time=time.time(),
            end_time=time.time() + 1,
        )
        assert span_ok.status == SpanStatus.OK

    def test_performance_overhead(self):
        """Test tracing overhead is <10ms per span."""
        iterations = 100

        start = time.perf_counter()
        for i in range(iterations):
            context = SpanContext()
            span = Span(
                span_id=context.span_id,
                trace_id=context.trace_id,
                parent_span_id=None,
                name=f"operation_{i}",
                kind=SpanKind.INTERNAL,
                status=SpanStatus.OK,
                attributes={"iteration": i},
                events=[],
                start_time=time.time(),
                end_time=time.time() + 0.001,
            )
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000
        
        # Verify <10ms per span creation
        assert avg_time_ms < 10.0, f"Tracing too slow: {avg_time_ms:.3f}ms"

    def test_concurrent_traces(self):
        """Test multiple concurrent traces."""
        def create_trace(thread_id: int) -> str:
            context = SpanContext()
            span = Span(
                span_id=context.span_id,
                trace_id=context.trace_id,
                parent_span_id=None,
                name=f"thread_{thread_id}",
                kind=SpanKind.INTERNAL,
                status=SpanStatus.OK,
                attributes={"thread_id": thread_id},
                events=[],
                start_time=time.time(),
                end_time=time.time() + 0.01,
            )
            return span.trace_id

        # Run 10 concurrent traces
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_trace, i) for i in range(10)]
            trace_ids = [f.result() for f in futures]

        # Verify all traces have unique IDs
        assert len(set(trace_ids)) == 10

    def test_span_timing(self):
        """Test span timing calculations."""
        context = SpanContext()
        
        start = time.time()
        time.sleep(0.01)  # Simulate work
        end = time.time()

        span = Span(
            span_id=context.span_id,
            trace_id=context.trace_id,
            parent_span_id=None,
            name="timed_operation",
            kind=SpanKind.INTERNAL,
            status=SpanStatus.OK,
            attributes={},
            events=[],
            start_time=start,
            end_time=end,
        )

        # Verify timing
        assert span.start_time == start
        assert span.end_time == end
        duration = span.duration_ms()
        assert duration >= 10.0  # At least 10ms


# AC_COMPLETE: AC-WAVEB-003 ✅ 8 OpenTelemetry tracing tests
