"""brain_health_orchestrator.py — Backward-compatibility shim (Phase 102-C).

The canonical file is now:
  cortex/orchestrators/core/intelligence_health_orchestrator.py

This shim will be removed after 1 consolidation session.
"""
from cortex.orchestrators.core.intelligence_health_orchestrator import (  # noqa: F401
    BrainHealthOrchestrator,
    IntelligenceHealthOrchestrator,
)

__all__ = ["BrainHealthOrchestrator", "IntelligenceHealthOrchestrator"]
