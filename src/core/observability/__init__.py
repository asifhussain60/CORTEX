"""
CORTEX Observability Package

Provides OpenTelemetry integration for distributed tracing, metrics collection,
and operational visibility across the CORTEX system.

Modules:
    otel_exporter: OpenTelemetry exporter for trace collection and export
    span_manager: Span lifecycle management and context propagation
"""

from src.core.observability.otel_exporter import OtelExporter, TraceConfig
from src.core.observability.span_manager import SpanManager, SpanContext

__all__ = [
    "OtelExporter",
    "TraceConfig",
    "SpanManager",
    "SpanContext",
]
