"""
Automation hooks for CORTEX orchestrator lifecycle events.

This module provides automated registry updates, recommendation gates,
and validation hooks triggered by orchestrator completions.
"""

from .status_update_hook import StatusUpdateHook
from .recommendation_gate import RecommendationGate

__all__ = ["StatusUpdateHook", "RecommendationGate"]
