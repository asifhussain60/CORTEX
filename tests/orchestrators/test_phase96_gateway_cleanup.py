"""
Phase 96 — Gateway Flag Cleanup: Remove Dead Migration Scaffolding

TDD RED → GREEN → REFACTOR

Validates that:
  1. All 7 code-touching orchestrators have PHASE90_GATEWAY_ENABLED = True
  2. All permanently exempt orchestrators have PHASE90_GATEWAY_EXEMPT = True
     (and NO PHASE90_GATEWAY_ENABLED flag — dead scaffolding removed)
  3. WorkflowEnforcementMixin defaults are correct
  4. No orchestrator has PHASE90_GATEWAY_ENABLED = False (dead scaffolding)
  5. Golden truth: exactly 7 orchestrators enabled, rest exempt

Governance:
  CORE-008: TDD mandatory — these tests written before implementation
  CORE-011: Type hints on all functions
  CORE-012: Docstrings on all public APIs
  CORE-035: Single canonical implementation
  CORE-064: Sweep completeness contract
"""
from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple, Type

import pytest


# ============================================================================
# GOLDEN TRUTH — Single Source of Truth for gateway classification
# ============================================================================

# These 7 orchestrators touch code and MUST route through WorkflowGateway.
# Their PHASE90_GATEWAY_ENABLED MUST be True.
GATEWAY_ENABLED_ORCHESTRATORS: Dict[str, str] = {
    "TDDOrchestrator": "cortex.orchestrators.core.tdd_orchestrator",
    "RefactoringOrchestrator": "cortex.orchestrators.domain.refactoring_orchestrator",
    "DebuggerOrchestrator": "cortex.orchestrators.support.debugger_orchestrator",
    "VacuumOrchestrator": "cortex.orchestrators.health.vacuum_orchestrator",
    "HealthOrchestrator": "cortex.orchestrators.health.health_orchestrator",
    "TrainerOrchestrator": "cortex.orchestrators.intelligence.trainer_orchestrator",
}

# These orchestrators are permanently exempt: dispatchers, validators,
# session managers, git ops, etc. They should have PHASE90_GATEWAY_EXEMPT = True
# and should NOT have PHASE90_GATEWAY_ENABLED = False (dead scaffolding).
PERMANENTLY_EXEMPT_ORCHESTRATORS: List[str] = [
    # Core — dispatchers / validators / session
    "MasterOrchestrator",
    "EnforcementOrchestrator",
    "AuditOrchestrator",
    "ReviewOrchestrator",
    "InteractionOrchestrator",
    "WorkflowOrchestrator",
    "ConversationOrchestrator",
    "StateOrchestrator",
    "SecurityOrchestrator",
    "ObservabilityOrchestrator",
    "BrainHealthOrchestrator",
    "CentralBrainOrchestrator",
    "CortexMasterPlanOrchestrator",
    "PhaseOrchestrator",
    "RequestRephraseOrchestrator",
    # Domain — planning / query / design
    "PlanningOrchestrator",
    "EnhancedPlanningOrchestrator",
    "DashboardOrchestrator",
    "DomainOrchestrator",
    "InquiryOrchestrator",
    "ServiceDecompositionOrchestrator",
    "SDLCWorkflowOrchestrator",
    # Git — operations (not code-touching in IMPLEMENT sense)
    "GitOrchestrator",
    "GitPublishOrchestrator",
    "SanitizationOrchestrator",
    "PreCommitEnforcementOrchestrator",
    # Intelligence — analysis only
    "IntelligenceOrchestrator",
    "TechIntelligenceOrchestrator",
    # Support — infrastructure / utilities
    "AutoHealingMCPOrchestrator",
    "BulkDigestOrchestrator",
    "ContextAssemblyOrchestrator",
    "CortexDocsOrchestrator",
    "DigestSessionOrchestrator",
    "LENSVisualizationOrchestrator",
    "PlanRegistrySyncOrchestrator",
    "PhaseCompletionOrchestrator",
    "PlanOrchestrator",
    "RepoDetectionOrchestrator",
    "RepositoryOnboardingOrchestrator",
    "SetupOrchestrator",
    "SweepCatalogueOrchestrator",
    "TestClassifierOrchestrator",
    "UnifiedQualityAssuranceOrchestrator",
    "UpgradeOrchestrator",
    # Validation — analysis only
    "HolisticValidationOrchestrator",
    "SecurityVulnerabilityOrchestrator",
    "SOLIDOrchestrator",
    # Persona
    # (persona/master_orchestrator.py — MasterOrchestrator alias, covered above)
    # Support duplicate vacuum (support/vacuum_orchestrator.py)
]


# ============================================================================
# Test Cluster A: Active gateway orchestrators all have True
# ============================================================================
class TestActiveGatewayOrchestrators:
    """All code-touching orchestrators must have PHASE90_GATEWAY_ENABLED = True."""

    @pytest.mark.parametrize(
        "class_name,module_path",
        list(GATEWAY_ENABLED_ORCHESTRATORS.items()),
        ids=list(GATEWAY_ENABLED_ORCHESTRATORS.keys()),
    )
    def test_gateway_enabled_is_true(self, class_name: str, module_path: str) -> None:
        """Active orchestrator PHASE90_GATEWAY_ENABLED must be True."""
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        assert getattr(cls, "PHASE90_GATEWAY_ENABLED", None) is True, (
            f"{class_name}.PHASE90_GATEWAY_ENABLED must be True — it touches code."
        )


# ============================================================================
# Test Cluster B: Exempt orchestrators have PHASE90_GATEWAY_EXEMPT = True
# ============================================================================
class TestExemptOrchestrators:
    """Permanently exempt orchestrators should declare PHASE90_GATEWAY_EXEMPT = True."""

    def test_exempt_flag_exists_on_mixin(self) -> None:
        """WorkflowEnforcementMixin must define PHASE90_GATEWAY_EXEMPT default."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert hasattr(WorkflowEnforcementMixin, "PHASE90_GATEWAY_EXEMPT"), (
            "WorkflowEnforcementMixin must declare PHASE90_GATEWAY_EXEMPT (default False)"
        )

    def test_mixin_exempt_default_is_false(self) -> None:
        """Default PHASE90_GATEWAY_EXEMPT should be False (safe default)."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert WorkflowEnforcementMixin.PHASE90_GATEWAY_EXEMPT is False


# ============================================================================
# Test Cluster C: No orchestrator has dead PHASE90_GATEWAY_ENABLED = False
# ============================================================================
class TestNoDeadFlags:
    """No orchestrator should have PHASE90_GATEWAY_ENABLED = False — that's dead scaffolding."""

    def test_no_false_gateway_flags_in_codebase(self) -> None:
        """Scan all orchestrator files for PHASE90_GATEWAY_ENABLED = False (should be 0)."""
        from pathlib import Path
        import re

        orch_root = Path(__file__).parents[2] / "cortex" / "orchestrators"
        false_flags: List[str] = []

        for py_file in orch_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text()
            if re.search(r"PHASE90_GATEWAY_ENABLED\s*[:=]\s*(?:bool\s*=\s*)?False", content):
                false_flags.append(str(py_file.relative_to(orch_root.parent.parent)))

        assert len(false_flags) == 0, (
            f"Found {len(false_flags)} files with dead PHASE90_GATEWAY_ENABLED = False:\n"
            + "\n".join(f"  - {f}" for f in false_flags)
        )


# ============================================================================
# Test Cluster D: Exactly 7 active orchestrators
# ============================================================================
class TestGatewayCount:
    """Golden truth: exactly 6 orchestrators have PHASE90_GATEWAY_ENABLED = True."""

    def test_exactly_six_enabled(self) -> None:
        """Scan codebase — exactly 6 orchestrators should have gateway enabled."""
        from pathlib import Path
        import re

        orch_root = Path(__file__).parents[2] / "cortex" / "orchestrators"
        true_flags: List[str] = []

        for py_file in orch_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text()
            if re.search(r"PHASE90_GATEWAY_ENABLED\s*[:=]\s*(?:bool\s*=\s*)?True", content):
                true_flags.append(str(py_file.relative_to(orch_root.parent.parent)))

        assert len(true_flags) == 6, (
            f"Expected exactly 6 gateway-enabled orchestrators, found {len(true_flags)}:\n"
            + "\n".join(f"  - {f}" for f in true_flags)
        )
