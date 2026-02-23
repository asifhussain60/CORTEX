"""COMPAT shim — cortex.observability.observability.health_monitor → cortex.core.registry.health_monitor.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/core/registry/health_monitor.py.
"""
# noqa: F401
from cortex.core.registry.health_monitor import HealthCheckResult, RegistryHealthMonitor

__all__ = ["HealthCheckResult", "RegistryHealthMonitor"]
