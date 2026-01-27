"""
CORTEX Observability Package

Provides OpenTelemetry integration for distributed tracing, metrics collection,
alerting, health monitoring, performance profiling, audit trail, and operational
visibility across the CORTEX system.

Modules:
    otel_exporter: OpenTelemetry exporter for trace collection and export
    span_manager: Span lifecycle management and context propagation
    metrics_aggregator: Metrics collection and statistical aggregation
    metrics_dashboard: Web-based dashboard for metrics visualization
    alerting: Alert rules, notifications, and routing
    health_monitor: Health checks and status reporting
    performance_profiler: Performance analysis and optimization recommendations
    audit_trail: Searchable audit history with retention and export
"""

from cortex.brain.core.observability.otel_exporter import OtelExporter, TraceConfig
from cortex.brain.core.observability.span_manager import SpanManager, SpanContext
from cortex.brain.core.observability.metrics_aggregator import MetricsAggregator, MetricPoint
from cortex.brain.core.observability.metrics_dashboard import MetricsDashboard, DashboardConfig
from cortex.brain.core.observability.alerting import (
    AlertManager,
    AlertRule,
    AlertSeverity,
    AlertNotification,
)
from cortex.brain.core.observability.health_monitor import (
    HealthMonitor,
    HealthStatus,
    HealthStatusLevel,
)
from cortex.brain.core.observability.performance_profiler import (
    PerformanceProfiler,
    BottleneckDetector,
    Bottleneck,
    OptimizationRecommendation,
)
from cortex.brain.core.observability.audit_trail import (
    AuditTrail,
    AuditEntry,
    RetentionPolicy,
    AuditExporter,
)

__all__ = [
    "OtelExporter",
    "TraceConfig",
    "SpanManager",
    "SpanContext",
    "MetricsAggregator",
    "MetricPoint",
    "MetricsDashboard",
    "DashboardConfig",
    "AlertManager",
    "AlertRule",
    "AlertSeverity",
    "AlertNotification",
    "HealthMonitor",
    "HealthStatus",
    "HealthStatusLevel",
    "PerformanceProfiler",
    "BottleneckDetector",
    "Bottleneck",
    "OptimizationRecommendation",
    "AuditTrail",
    "AuditEntry",
    "RetentionPolicy",
    "AuditExporter",
]
