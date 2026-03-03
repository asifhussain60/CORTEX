"""brain_state_manager.py — Backward-compatibility shim (Phase 102-C).

The canonical file is now:
  cortex/core/orchestrator_state_manager.py

This shim will be removed after 1 consolidation session.
"""
from cortex.core.orchestrator_state_manager import (  # noqa: F401
    BrainStateManager,
    IntelligenceStateManager,
)

__all__ = ["BrainStateManager", "IntelligenceStateManager"]
