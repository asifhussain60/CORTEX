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

from cortex.core.observability.alerting import (
    AlertManager,
    AlertNotification,
    AlertRule,
    AlertSeverity,
)
from cortex.core.observability.audit_trail import (
    AuditEntry,
    AuditExporter,
    AuditTrail,
    RetentionPolicy,
)
from cortex.core.observability.health_monitor import (
    HealthMonitor,
    HealthStatus,
    HealthStatusLevel,
)
from cortex.core.observability.metrics_aggregator import (
    MetricPoint,
    MetricsAggregator,
)
from cortex.core.observability.metrics_dashboard import (
    DashboardConfig,
    MetricsDashboard,
)
from cortex.core.observability.otel_exporter import OtelExporter, TraceConfig
from cortex.core.observability.performance_profiler import (
    Bottleneck,
    BottleneckDetector,
    OptimizationRecommendation,
    PerformanceProfiler,
)
from cortex.core.observability.span_manager import SpanContext, SpanManager

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
