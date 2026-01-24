"""
BRT-022: Observability Integration Test Suite

Comprehensive tests for metrics aggregation, distributed tracing, and
observability integration across all Phase 4 patterns.

Tests organized into 10 categories covering initialization, metrics,
tracing, correlation, integration, and concurrent operations.

All tests use TDD-first approach with comprehensive coverage.
"""

import pytest
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from threading import RLock
from collections import defaultdict


class MetricType(str, Enum):
    """Type of metric."""
    COUNTER = "counter"          # Monotonically increasing
    GAUGE = "gauge"              # Point-in-time value
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Duration measurements


class TracingLevel(str, Enum):
    """Level of tracing detail."""
    DISABLED = "disabled"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"
    TRACE = "trace"


class SpanStatus(str, Enum):
    """Status of a span."""
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    metric_type: MetricType
    value: float
    timestamp_ms: float
    tags: Dict[str, str] = field(default_factory=lambda: {})
    
    def get_value(self) -> float:
        """Get metric value."""
        return self.value
    
    def get_tags(self) -> Dict[str, str]:
        """Get metric tags."""
        return self.tags.copy()


@dataclass
class TraceSpan:
    """Trace span for distributed tracing."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time_ms: float
    end_time_ms: float = 0.0
    status: SpanStatus = SpanStatus.RUNNING
    tags: Dict[str, str] = field(default_factory=lambda: {})
    logs: List[Dict[str, Any]] = field(default_factory=lambda: [])
    duration_ms: float = 0.0
    
    def add_tag(self, key: str, value: Any) -> None:
        """Add tag to span."""
        self.tags[key] = str(value)
    
    def add_log(self, message: str, level: str = "info") -> None:
        """Add log to span."""
        self.logs.append({
            "message": message,
            "level": level,
            "timestamp_ms": time.time() * 1000,
        })
    
    def finish(self, status: SpanStatus = SpanStatus.SUCCESS) -> None:
        """Finish span."""
        self.end_time_ms = time.time() * 1000
        self.status = status
        self.duration_ms = self.end_time_ms - self.start_time_ms
    
    def get_duration_ms(self) -> float:
        """Get span duration."""
        return self.duration_ms


@dataclass
class TraceContext:
    """Context for distributed tracing."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=lambda: {})
    sampling_enabled: bool = True
    
    def get_trace_id(self) -> str:
        """Get trace ID."""
        return self.trace_id
    
    def get_span_id(self) -> str:
        """Get span ID."""
        return self.span_id
    
    def add_baggage(self, key: str, value: str) -> None:
        """Add item to baggage."""
        self.baggage[key] = value
    
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage item."""
        return self.baggage.get(key)


@dataclass
class ObservabilityConfig:
    """Configuration for observability."""
    enable_metrics: bool = True
    enable_tracing: bool = True
    tracing_level: TracingLevel = TracingLevel.INFO
    metrics_interval_sec: float = 60.0
    trace_batch_size: int = 100
    trace_flush_interval_sec: float = 5.0
    correlation_enabled: bool = True
    max_metrics: int = 10000
    max_traces: int = 5000
    sample_rate: float = 1.0  # 0.0 to 1.0


class MetricsCollector:
    """Collector for metrics aggregation."""
    
    def __init__(self, config: Optional[ObservabilityConfig] = None) -> None:
        """Initialize metrics collector."""
        self.config = config or ObservabilityConfig()
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}
        self.metric_count: int = 0
        self._lock = RLock()
    
    def record_metric(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric."""
        if self.metric_count >= self.config.max_metrics:
            raise RuntimeError(f"Maximum metrics ({self.config.max_metrics}) reached")
        
        with self._lock:
            metric = Metric(
                name=name,
                metric_type=metric_type,
                value=value,
                timestamp_ms=time.time() * 1000,
                tags=tags or {},
            )
            self.metrics[name].append(metric)
            self.metric_count += 1
    
    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a counter metric."""
        self.record_metric(name, MetricType.COUNTER, value, tags)
    
    def record_gauge(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a gauge metric."""
        self.record_metric(name, MetricType.GAUGE, value, tags)
    
    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram metric."""
        self.record_metric(name, MetricType.HISTOGRAM, value, tags)
    
    def record_timer(
        self,
        name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a timer metric."""
        self.record_metric(name, MetricType.TIMER, duration_ms, tags)
    
    def get_metrics(self, name: str) -> List[Metric]:
        """Get metrics by name."""
        with self._lock:
            return self.metrics[name].copy()
    
    def aggregate_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate all metrics."""
        with self._lock:
            self.aggregated_metrics = {}
            for name, metrics_list in self.metrics.items():
                if not metrics_list:
                    continue
                
                values = [m.value for m in metrics_list]
                self.aggregated_metrics[name] = {
                    "count": len(metrics_list),
                    "sum": sum(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "latest": values[-1] if values else 0.0,
                }
            
            return self.aggregated_metrics.copy()
    
    def get_aggregated_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get aggregated metrics."""
        with self._lock:
            return self.aggregated_metrics.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self._lock:
            return {
                "total_metrics": self.metric_count,
                "metric_names": len(self.metrics),
                "max_metrics": self.config.max_metrics,
            }
    
    def reset(self) -> None:
        """Reset metrics."""
        with self._lock:
            self.metrics.clear()
            self.aggregated_metrics.clear()
            self.metric_count = 0


class TracingCollector:
    """Collector for distributed tracing."""
    
    def __init__(self, config: Optional[ObservabilityConfig] = None) -> None:
        """Initialize tracing collector."""
        self.config = config or ObservabilityConfig()
        self.spans: Dict[str, TraceSpan] = {}
        self.traces: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.span_count: int = 0
        self.trace_count: int = 0
        self._lock = RLock()
    
    def create_span(
        self,
        trace_id: str,
        span_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
    ) -> TraceSpan:
        """Create a trace span."""
        if self.span_count >= self.config.max_traces:
            raise RuntimeError(f"Maximum spans ({self.config.max_traces}) reached")
        
        with self._lock:
            span = TraceSpan(
                span_id=span_id,
                trace_id=trace_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                start_time_ms=time.time() * 1000,
            )
            self.spans[span_id] = span
            self.traces[trace_id].append(span)
            self.span_count += 1
            
            return span
    
    def get_span(self, span_id: str) -> Optional[TraceSpan]:
        """Get span by ID."""
        with self._lock:
            return self.spans.get(span_id)
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get trace by ID (all spans)."""
        with self._lock:
            return self.traces[trace_id].copy()
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get trace summary."""
        with self._lock:
            spans = self.traces.get(trace_id, [])
            if not spans:
                return {"trace_id": trace_id, "span_count": 0}
            
            durations = [s.duration_ms for s in spans if s.duration_ms > 0]
            
            return {
                "trace_id": trace_id,
                "span_count": len(spans),
                "total_duration_ms": sum(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
            }
    
    def get_tracing_summary(self) -> Dict[str, Any]:
        """Get tracing summary."""
        with self._lock:
            return {
                "total_spans": self.span_count,
                "total_traces": len(self.traces),
                "max_spans": self.config.max_traces,
            }
    
    def reset(self) -> None:
        """Reset traces."""
        with self._lock:
            self.spans.clear()
            self.traces.clear()
            self.span_count = 0
            self.trace_count = 0


class CorrelationContext:
    """Context for request correlation."""
    
    def __init__(self) -> None:
        """Initialize correlation context."""
        self.request_id: str = ""
        self.trace_id: str = ""
        self.span_id: str = ""
        self.user_id: str = ""
        self.session_id: str = ""
        self.correlation_tags: Dict[str, str] = {}
        self._lock = RLock()
    
    def set_request_id(self, request_id: str) -> None:
        """Set request ID."""
        with self._lock:
            self.request_id = request_id
    
    def set_trace_id(self, trace_id: str) -> None:
        """Set trace ID."""
        with self._lock:
            self.trace_id = trace_id
    
    def set_span_id(self, span_id: str) -> None:
        """Set span ID."""
        with self._lock:
            self.span_id = span_id
    
    def add_correlation_tag(self, key: str, value: str) -> None:
        """Add correlation tag."""
        with self._lock:
            self.correlation_tags[key] = value
    
    def get_correlation_context(self) -> Dict[str, str]:
        """Get full correlation context."""
        with self._lock:
            return {
                "request_id": self.request_id,
                "trace_id": self.trace_id,
                "span_id": self.span_id,
                "user_id": self.user_id,
                "session_id": self.session_id,
                **self.correlation_tags,
            }


# ============================================================================
# TESTS: 10 Categories
# ============================================================================

class TestMetricInitialization:
    """Category 1: Metric initialization and configuration."""

    def test_creates_metric_with_defaults(self) -> None:
        """Test creating metric with defaults."""
        metric = Metric(
            name="test_metric",
            metric_type=MetricType.GAUGE,
            value=100.0,
            timestamp_ms=time.time() * 1000,
        )
        assert metric.name == "test_metric"
        assert metric.metric_type == MetricType.GAUGE
        assert metric.value == 100.0
        assert metric.tags == {}

    def test_creates_metric_with_tags(self) -> None:
        """Test creating metric with tags."""
        metric = Metric(
            name="request_latency",
            metric_type=MetricType.HISTOGRAM,
            value=150.5,
            timestamp_ms=time.time() * 1000,
            tags={"service": "payment", "endpoint": "/api/pay"},
        )
        assert metric.name == "request_latency"
        assert len(metric.tags) == 2
        assert metric.tags["service"] == "payment"

    def test_metric_get_methods(self) -> None:
        """Test metric get methods."""
        metric = Metric(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=75.5,
            timestamp_ms=time.time() * 1000,
            tags={"host": "server1"},
        )
        assert metric.get_value() == 75.5
        assert metric.get_tags() == {"host": "server1"}


class TestMetricsCollectorInitialization:
    """Category 2: Metrics collector initialization."""

    def test_creates_collector_with_defaults(self) -> None:
        """Test collector creation with defaults."""
        collector = MetricsCollector()
        assert collector.config.enable_metrics is True
        assert collector.config.max_metrics == 10000
        assert collector.metric_count == 0

    def test_creates_collector_with_custom_config(self) -> None:
        """Test collector creation with custom config."""
        config = ObservabilityConfig(max_metrics=1000)
        collector = MetricsCollector(config=config)
        assert collector.config.max_metrics == 1000

    def test_rejects_metric_at_max_limit(self) -> None:
        """Test that collector rejects metric when max reached."""
        config = ObservabilityConfig(max_metrics=2)
        collector = MetricsCollector(config=config)
        
        collector.record_counter("metric1", 1.0)
        collector.record_counter("metric2", 1.0)
        
        with pytest.raises(RuntimeError):
            collector.record_counter("metric3", 1.0)


class TestMetricsRecording:
    """Category 3: Metrics recording and retrieval."""

    def test_records_counter_metric(self) -> None:
        """Test recording counter metric."""
        collector = MetricsCollector()
        collector.record_counter("requests_total", 1.0)
        
        metrics = collector.get_metrics("requests_total")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.COUNTER

    def test_records_gauge_metric(self) -> None:
        """Test recording gauge metric."""
        collector = MetricsCollector()
        collector.record_gauge("memory_usage", 1024.5)
        
        metrics = collector.get_metrics("memory_usage")
        assert len(metrics) == 1
        assert metrics[0].value == 1024.5

    def test_records_histogram_metric(self) -> None:
        """Test recording histogram metric."""
        collector = MetricsCollector()
        collector.record_histogram("request_size", 5000.0)
        
        metrics = collector.get_metrics("request_size")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.HISTOGRAM

    def test_records_timer_metric(self) -> None:
        """Test recording timer metric."""
        collector = MetricsCollector()
        collector.record_timer("api_latency", 150.0)
        
        metrics = collector.get_metrics("api_latency")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.TIMER

    def test_records_multiple_metrics(self) -> None:
        """Test recording multiple metrics."""
        collector = MetricsCollector()
        collector.record_counter("requests", 1.0)
        collector.record_counter("requests", 1.0)
        collector.record_gauge("cpu", 50.0)
        
        requests = collector.get_metrics("requests")
        assert len(requests) == 2
        
        cpu = collector.get_metrics("cpu")
        assert len(cpu) == 1


class TestMetricsAggregation:
    """Category 4: Metrics aggregation."""

    def test_aggregates_metrics_correctly(self) -> None:
        """Test metrics aggregation."""
        collector = MetricsCollector()
        collector.record_timer("latency", 100.0)
        collector.record_timer("latency", 200.0)
        collector.record_timer("latency", 300.0)
        
        agg = collector.aggregate_metrics()
        
        assert agg["latency"]["count"] == 3
        assert agg["latency"]["sum"] == 600.0
        assert agg["latency"]["min"] == 100.0
        assert agg["latency"]["max"] == 300.0
        assert agg["latency"]["avg"] == 200.0

    def test_calculates_average_correctly(self) -> None:
        """Test average calculation in aggregation."""
        collector = MetricsCollector()
        collector.record_gauge("temp", 20.0)
        collector.record_gauge("temp", 25.0)
        collector.record_gauge("temp", 30.0)
        
        agg = collector.aggregate_metrics()
        assert agg["temp"]["avg"] == 25.0

    def test_tracks_latest_metric_value(self) -> None:
        """Test that latest value is tracked."""
        collector = MetricsCollector()
        collector.record_counter("events", 5.0)
        collector.record_counter("events", 10.0)
        
        agg = collector.aggregate_metrics()
        assert agg["events"]["latest"] == 10.0


class TestTraceSpanManagement:
    """Category 5: Trace span creation and management."""

    def test_creates_trace_span(self) -> None:
        """Test creating trace span."""
        span = TraceSpan(
            span_id="span1",
            trace_id="trace1",
            parent_span_id=None,
            operation_name="api_call",
            start_time_ms=time.time() * 1000,
        )
        assert span.span_id == "span1"
        assert span.trace_id == "trace1"
        assert span.status == SpanStatus.RUNNING

    def test_adds_tag_to_span(self) -> None:
        """Test adding tag to span."""
        span = TraceSpan(
            span_id="span1",
            trace_id="trace1",
            parent_span_id=None,
            operation_name="db_query",
            start_time_ms=time.time() * 1000,
        )
        span.add_tag("database", "postgres")
        span.add_tag("query_type", "SELECT")
        
        assert span.tags["database"] == "postgres"
        assert len(span.tags) == 2

    def test_adds_log_to_span(self) -> None:
        """Test adding log to span."""
        span = TraceSpan(
            span_id="span1",
            trace_id="trace1",
            parent_span_id=None,
            operation_name="process",
            start_time_ms=time.time() * 1000,
        )
        span.add_log("Processing started", "info")
        span.add_log("Error occurred", "error")
        
        assert len(span.logs) == 2
        assert span.logs[0]["level"] == "info"

    def test_finishes_span_with_duration(self) -> None:
        """Test finishing span."""
        span = TraceSpan(
            span_id="span1",
            trace_id="trace1",
            parent_span_id=None,
            operation_name="api",
            start_time_ms=time.time() * 1000,
        )
        time.sleep(0.01)  # 10ms
        span.finish(SpanStatus.SUCCESS)
        
        assert span.status == SpanStatus.SUCCESS
        assert span.duration_ms > 0


class TestTracingCollector:
    """Category 6: Tracing collector operations."""

    def test_creates_and_retrieves_span(self) -> None:
        """Test creating and retrieving span."""
        collector = TracingCollector()
        span = collector.create_span(
            trace_id="trace1",
            span_id="span1",
            operation_name="query",
        )
        
        retrieved = collector.get_span("span1")
        assert retrieved is not None
        assert retrieved.operation_name == "query"

    def test_creates_trace_with_multiple_spans(self) -> None:
        """Test creating trace with multiple spans."""
        collector = TracingCollector()
        collector.create_span("trace1", "span1", "op1")
        collector.create_span("trace1", "span2", "op2", parent_span_id="span1")
        collector.create_span("trace1", "span3", "op3", parent_span_id="span2")
        
        trace = collector.get_trace("trace1")
        assert len(trace) == 3

    def test_rejects_span_at_max_limit(self) -> None:
        """Test that collector rejects span when max reached."""
        config = ObservabilityConfig(max_traces=2)
        collector = TracingCollector(config=config)
        
        collector.create_span("trace1", "span1", "op1")
        collector.create_span("trace1", "span2", "op2")
        
        with pytest.raises(RuntimeError):
            collector.create_span("trace1", "span3", "op3")

    def test_gets_trace_summary(self) -> None:
        """Test getting trace summary."""
        collector = TracingCollector()
        span_obj = collector.create_span("trace1", "span1", "op1")
        time.sleep(0.01)
        span_obj.finish()
        
        summary = collector.get_trace_summary("trace1")
        assert summary["trace_id"] == "trace1"
        assert summary["span_count"] == 1
        assert summary["total_duration_ms"] > 0


class TestTraceContext:
    """Category 7: Trace context and baggage."""

    def test_creates_trace_context(self) -> None:
        """Test creating trace context."""
        ctx = TraceContext(
            trace_id="trace1",
            span_id="span1",
        )
        assert ctx.get_trace_id() == "trace1"
        assert ctx.get_span_id() == "span1"

    def test_adds_baggage_to_context(self) -> None:
        """Test adding baggage."""
        ctx = TraceContext(trace_id="trace1", span_id="span1")
        ctx.add_baggage("user_id", "user123")
        ctx.add_baggage("tenant_id", "tenant456")
        
        assert ctx.get_baggage("user_id") == "user123"
        assert ctx.get_baggage("tenant_id") == "tenant456"

    def test_baggage_inheritance(self) -> None:
        """Test that baggage can be inherited."""
        ctx1 = TraceContext(trace_id="trace1", span_id="span1")
        ctx1.add_baggage("request_id", "req1")
        
        # New context inherits baggage
        ctx2 = TraceContext(
            trace_id="trace1",
            span_id="span2",
            baggage=ctx1.baggage.copy(),
        )
        assert ctx2.get_baggage("request_id") == "req1"


class TestCorrelationContext:
    """Category 8: Request correlation."""

    def test_sets_correlation_ids(self) -> None:
        """Test setting correlation IDs."""
        ctx = CorrelationContext()
        ctx.set_request_id("req1")
        ctx.set_trace_id("trace1")
        ctx.set_span_id("span1")
        
        corr = ctx.get_correlation_context()
        assert corr["request_id"] == "req1"
        assert corr["trace_id"] == "trace1"
        assert corr["span_id"] == "span1"

    def test_adds_correlation_tags(self) -> None:
        """Test adding correlation tags."""
        ctx = CorrelationContext()
        ctx.set_request_id("req1")
        ctx.add_correlation_tag("service", "payment")
        ctx.add_correlation_tag("region", "us-east")
        
        corr = ctx.get_correlation_context()
        assert corr["service"] == "payment"
        assert corr["region"] == "us-east"

    def test_correlation_context_complete(self) -> None:
        """Test complete correlation context."""
        ctx = CorrelationContext()
        ctx.set_request_id("req123")
        ctx.set_trace_id("trace456")
        ctx.set_span_id("span789")
        ctx.user_id = "user1"
        ctx.session_id = "session1"
        
        corr = ctx.get_correlation_context()
        assert len(corr) >= 5


class TestObservabilityIntegration:
    """Category 9: Integration with Phase 4 patterns."""

    def test_collects_priority_queue_metrics(self) -> None:
        """Test metrics collection from BRT-017 (Priority Queue)."""
        collector = MetricsCollector()
        
        # Simulate priority queue metrics
        collector.record_gauge("queue_depth_high", 5.0, {"priority": "HIGH"})
        collector.record_gauge("queue_depth_normal", 15.0, {"priority": "NORMAL"})
        collector.record_gauge("queue_depth_low", 50.0, {"priority": "LOW"})
        
        summary = collector.get_metrics_summary()
        assert summary["metric_names"] == 3

    def test_collects_quota_management_metrics(self) -> None:
        """Test metrics collection from BRT-019 (Quota)."""
        collector = MetricsCollector()
        
        # Simulate quota metrics
        collector.record_gauge("quota_used_high", 80.0, {"priority": "HIGH"})
        collector.record_gauge("quota_used_normal", 60.0, {"priority": "NORMAL"})
        
        agg = collector.aggregate_metrics()
        assert "quota_used_high" in agg
        assert "quota_used_normal" in agg

    def test_collects_adaptive_timeout_metrics(self) -> None:
        """Test metrics collection from BRT-020 (Adaptive Timeout)."""
        collector = MetricsCollector()
        
        # Simulate adaptive timeout metrics
        collector.record_timer("timeout_adjustment", 1.5, {"strategy": "conservative"})
        collector.record_timer("timeout_adjustment", 1.2, {"strategy": "balanced"})
        collector.record_timer("timeout_adjustment", 0.7, {"strategy": "aggressive"})
        
        metrics = collector.get_metrics("timeout_adjustment")
        assert len(metrics) == 3

    def test_traces_request_flow_across_patterns(self) -> None:
        """Test tracing request flow through multiple patterns."""
        tracer = TracingCollector()
        
        # Policy routing span
        policy_span = tracer.create_span("trace1", "span1", "policy_evaluation")
        policy_span.add_tag("matched_rules", "2")
        policy_span.finish()
        
        # Priority queue span
        pq_span = tracer.create_span(
            "trace1", "span2", "priority_queue_assign",
            parent_span_id="span1"
        )
        pq_span.add_tag("queue", "high")
        pq_span.finish()
        
        # Quota allocation span
        quota_span = tracer.create_span(
            "trace1", "span3", "quota_allocation",
            parent_span_id="span2"
        )
        quota_span.add_tag("quota_allocated", "100")
        quota_span.finish()
        
        trace = tracer.get_trace("trace1")
        assert len(trace) == 3


class TestConcurrentOperations:
    """Category 10: Concurrent operations and thread safety."""

    def test_handles_concurrent_metric_recording(self) -> None:
        """Test thread-safe metric recording."""
        collector = MetricsCollector()
        
        def record_metrics(thread_id: int) -> None:
            for _ in range(10):
                collector.record_counter(
                    "concurrent_metric",
                    1.0,
                    {"thread": str(thread_id)},
                )
        
        threads = [threading.Thread(target=record_metrics, args=(i,)) for i in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = collector.get_metrics("concurrent_metric")
        assert len(metrics) == 50

    def test_handles_concurrent_span_creation(self) -> None:
        """Test thread-safe span creation."""
        tracer = TracingCollector()
        
        def create_spans(thread_id: int) -> None:
            for i in range(5):
                tracer.create_span(
                    f"trace{thread_id}",
                    f"span{thread_id}_{i}",
                    f"op{i}",
                )
        
        threads = [threading.Thread(target=create_spans, args=(i,)) for i in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        summary = tracer.get_tracing_summary()
        assert summary["total_spans"] == 15

    def test_concurrent_aggregation_while_recording(self) -> None:
        """Test concurrent aggregation and recording."""
        collector = MetricsCollector()
        
        def record(count: int) -> None:
            for i in range(count):
                collector.record_gauge("value", float(i))
        
        def aggregate() -> None:
            time.sleep(0.01)
            collector.aggregate_metrics()
        
        t1 = threading.Thread(target=record, args=(20,))
        t2 = threading.Thread(target=aggregate)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        agg = collector.get_aggregated_metrics()
        assert "value" in agg


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def collector() -> MetricsCollector:
    """Fixture: Basic metrics collector."""
    return MetricsCollector()


@pytest.fixture
def tracer() -> TracingCollector:
    """Fixture: Basic tracing collector."""
    return TracingCollector()


@pytest.fixture
def observability_suite() -> Tuple[MetricsCollector, TracingCollector, CorrelationContext]:
    """Fixture: Complete observability suite."""
    return (MetricsCollector(), TracingCollector(), CorrelationContext())
