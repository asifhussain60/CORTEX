"""COMPAT shim — cortex.core.common.health_check → cortex.core.wiring.health_check.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/core/wiring/health_check.py.
"""
# noqa: F401
from cortex.core.wiring.health_check import HealthStatus, HealthCheckResult, SystemHealthReport, HealthCheckExecutor, SystemHealthMonitor

__all__ = ["HealthStatus", "HealthCheckResult", "SystemHealthReport", "HealthCheckExecutor", "SystemHealthMonitor"]
