"""
CORTEX Core Orchestrators

Framework-level orchestrators:
- master_orchestrator.py: Routes to appropriate domain orchestrator
- composite_orchestrator.py: Chains multiple orchestrators
- tdd_orchestrator.py: TDD discipline enforcer with knowledge guidance (AC-REM-011-02)
"""

from typing import Dict, List, Optional

# AC-REM-011-02: Export TDD Orchestrator for knowledge integration
try:
    from cortex.orchestrators.core.tdd_orchestrator import (
        TDDDisciplineRule,
        TDDImplementationGuidance,
        TDDKnowledgeLoader,
        TDDOrchestrator,
        TDDPhase,
        get_tdd_orchestrator,
    )
    __all__ = [
        "TDDOrchestrator",
        "TDDKnowledgeLoader",
        "TDDPhase",
        "TDDDisciplineRule",
        "TDDImplementationGuidance",
        "get_tdd_orchestrator",
    ]
except ImportError:
    pass
