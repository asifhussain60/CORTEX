"""central_brain_orchestrator.py — Backward-compatibility shim (Phase 102-C).

The canonical file is now:
  cortex/orchestrators/core/collaboration_orchestrator.py

This shim will be removed after 1 consolidation session.
"""
from cortex.orchestrators.core.collaboration_orchestrator import (  # noqa: F401
    CentralBrainOrchestrator,
    CollaborationOrchestrator,
)

__all__ = ["CentralBrainOrchestrator", "CollaborationOrchestrator"]
