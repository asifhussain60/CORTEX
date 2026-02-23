"""COMPAT shim — cortex.core.health_metrics → cortex.core.core.health_metrics.

Phase 58: Canonical implementation lives in cortex/core/core/health_metrics.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.health_metrics import MetricType, MetricEntry, MetricSummary, HealthMetrics

__all__ = ["MetricType", "MetricEntry", "MetricSummary", "HealthMetrics"]
