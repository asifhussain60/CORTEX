"""
enforcement_orchestrator package — Phase 103-e god-object decomposition.

This package replaces the monolithic enforcement_orchestrator.py (1,866 lines)
with a sub-package layout:

    enforcement_orchestrator/
        __init__.py          ← thin coordinator (this file, re-exports all)
        models.py            ← EnforcementLevel, EnforcementResult
        agents/
            __init__.py      ← re-exports all 11 agents
            governance_enforcement_agent.py
            security_checkpoint_agent.py
            compliance_validation_agent.py
            file_naming_enforcement_agent.py
            incremental_execution_agent.py
            markdown_suppression_agent.py
            architecture_integrity_agent.py
            discovery_enforcement_agent.py
            extended_governance_agent.py
            sweep_composition_agent.py

All public symbols are re-exported here for full backwards compatibility.

AC_START: AC-P103E-PKG-001
AC_COMPLETE: AC-P103E-PKG-001 ✅

AC-ID: AC-P103E-PKG-001
"""

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)
from cortex.orchestrators.core.enforcement_orchestrator.agents import (
    GovernanceEnforcementAgent,
    SecurityCheckpointAgent,
    ComplianceValidationAgent,
    FileNamingEnforcementAgent,
    IncrementalExecutionAgent,
    MarkdownSuppressionAgent,
    ResponseContentValidationAgent,
    ArchitectureIntegrityAgent,
    DiscoveryEnforcementAgent,
    ExtendedGovernanceAgent,
    SweepCompositionEnforcementAgent,
)
from cortex.orchestrators.core.enforcement_orchestrator.orchestrator import (
    EnforcementOrchestrator,
    get_enforcement_orchestrator,
)

try:
    from cortex.governance.business_rule_enforcement_agent import BusinessRuleEnforcementAgent  # noqa: F401
except ImportError:
    BusinessRuleEnforcementAgent = None  # type: ignore[assignment,misc]

__all__ = [
    "EnforcementOrchestrator",
    "EnforcementResult",
    "EnforcementLevel",
    "GovernanceEnforcementAgent",
    "SecurityCheckpointAgent",
    "ComplianceValidationAgent",
    "FileNamingEnforcementAgent",
    "IncrementalExecutionAgent",
    "MarkdownSuppressionAgent",
    "ResponseContentValidationAgent",
    "ArchitectureIntegrityAgent",
    "DiscoveryEnforcementAgent",
    "ExtendedGovernanceAgent",
    "SweepCompositionEnforcementAgent",
    "BusinessRuleEnforcementAgent",
    "get_enforcement_orchestrator",
]
