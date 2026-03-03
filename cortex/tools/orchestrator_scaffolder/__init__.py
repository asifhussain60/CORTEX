"""
orchestrator_scaffolder — generates orchestrator implementations from templates.

AC_START: AC-ORCH-SCAFFOLD-001
Phase 103-i: decomposed from orchestrator_scaffolder.py (1,455L) god-object.
Backwards-compatible re-export of all public symbols.
AC_COMPLETE: AC-ORCH-SCAFFOLD-001 ✅
"""
from cortex.tools.orchestrator_scaffolder.models import (
    ScaffoldConfig,
    ScaffoldedFile,
    ScaffoldResult,
    ScaffoldType,
)
from cortex.tools.orchestrator_scaffolder.scaffolder import OrchestratorScaffolder

__all__ = [
    "ScaffoldConfig",
    "ScaffoldedFile",
    "ScaffoldResult",
    "ScaffoldType",
    "OrchestratorScaffolder",
]
