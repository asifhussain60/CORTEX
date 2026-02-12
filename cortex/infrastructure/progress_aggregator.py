"""
Progress Aggregator - Aggregating progress from multiple sources.

This module is imported from dashboard_service.py for convenience.
"""

from cortex.infrastructure.dashboard_service import (
    DashboardStatus,
    ProgressAggregator,
    ProgressMetrics,
    ProgressSnapshot,
)

__all__ = [
    "ProgressAggregator",
    "ProgressSnapshot",
    "ProgressMetrics",
    "DashboardStatus",
]
