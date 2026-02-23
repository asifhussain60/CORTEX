"""COMPAT shim — cortex.lens.ml_patterns.dashboard_generator → cortex.core.registry.dashboard_generator.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/core/registry/dashboard_generator.py.
"""
# noqa: F401
from cortex.core.registry.dashboard_generator import PhaseSummary, DashboardData, DashboardSyncResult, DashboardGenerator

__all__ = ["PhaseSummary", "DashboardData", "DashboardSyncResult", "DashboardGenerator"]
