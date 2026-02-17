"""VacuumOrchestrator wrapper for backward compatibility.

This module provides a convenient import path for VacuumOrchestrator,
which is implemented in cortex_intelligence tier1_learned.

The actual implementation is in:
    cortex_intelligence/memory/tier1_learned/orchestrators/vacuum/orchestrator.py

This wrapper allows imports from the expected location:
    from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator

Authority: Phase 20 - Registry consolidation compatibility layer
Governance: CORE-035 (SSOT), CORE-042 (single source)
"""

from cortex_intelligence.memory.tier1_learned.orchestrators.vacuum.orchestrator import (
    VacuumOrchestrator,
    VacuumStrategy,
    OrchestratorState,
    StateTracker,
    VacuumStats,
)

# Alias for backward compatibility
VacuumState = OrchestratorState

__all__ = [
    "VacuumOrchestrator",
    "VacuumStrategy",
    "VacuumState",
    "OrchestratorState",
    "StateTracker",
    "VacuumStats",
]
