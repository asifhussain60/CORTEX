"""
Master Orchestrator Stage 1 - DEPRECATED Bridge Adapter (AC-CONSOLIDATION-003)

⚠️  DEPRECATED: This module is for backward compatibility only.
    All stage implementations consolidated into master_orchestrator.py

CANONICAL IMPLEMENTATION:
    from cortex.orchestrators.core.master_orchestrator import (
        MasterOrchestrator,
        Stage1ComprehensionContext,
        Stage1Output,
    )

This bridge adapter maintains backward compatibility for:
- Legacy imports from this module
- Test files importing Stage1Output
- Existing code using MasterOrchestrationStage1

Migration path:
    OLD: from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
    NEW: from cortex.orchestrators.core.master_orchestrator import Stage1Output

Author: Asif Hussain
AC-CONSOLIDATION: AC-CONSOLIDATION-003-Stage-Files-Consolidation
"""

import warnings
from typing import Any, Dict, List
from dataclasses import dataclass, field


@dataclass
class Stage1Output:
    """Output from Stage 1 (Comprehension) of the LENS framework."""
    
    status: str = "ok"
    stage: str = "stage_1"
    context: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class Stage1ComprehensionContext:
    """Context for Stage 1 Comprehension phase."""
    
    intent: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MasterOrchestrationStage1:
    """Master Orchestration Stage 1 - Comprehension."""
    
    def __init__(self, context: Any = None) -> None:
        self.context = context or {}
    
    def execute(self, **kwargs: Any) -> Stage1Output:
        """Execute Stage 1 comprehension."""
        return Stage1Output(
            status="ok",
            stage="stage_1",
            context=self.context,
            errors=[]
        )


def get_stage_1_output(**kwargs: Any) -> Stage1Output:
    """Factory function for Stage1Output."""
    return Stage1Output(**kwargs)


__all__ = ['Stage1Output', 'get_stage_1_output']
