"""
CORTEX Observability Package

Visibility controls and usage metrics for orchestrator activity.

Components:
- VisibilityController: Toggle orchestrator visibility (training wheels)
- UsageMetricsCollector: Track engagement for lifecycle transitions (TODO Phase 20.2.2)

Authority: AC-UX-VISIBILITY-001 (Phase 20.2)
"""

from .visibility_controller import (
    IntelligenceFlags,
    OrchestratorContext,
    VisibilityController,
    VisibilityMode,
    get_visibility_controller,
)

__all__ = [
    "VisibilityController",
    "VisibilityMode",
    "OrchestratorContext",
    "IntelligenceFlags",
    "get_visibility_controller",
]
