"""brain_state_manager.py — Backward-compatibility shim (Phase 102-C).

The canonical file is now:
  cortex/core/orchestrator_state_manager.py

This shim will be removed after 1 consolidation session.

Phase 115-a (GAP-115-03): Added missing re-exports StateSnapshot, FlushResult,
ReloadResult, StateValidationError so test_brain_state_manager.py collects correctly.
"""
from cortex.core.orchestrator_state_manager import (  # noqa: F401
    BrainStateManager,
    IntelligenceStateManager,
    StateSnapshot,
    FlushResult,
    ReloadResult,
    StateValidationError,
)

__all__ = [
    "BrainStateManager",
    "IntelligenceStateManager",
    "StateSnapshot",
    "FlushResult",
    "ReloadResult",
    "StateValidationError",
]

