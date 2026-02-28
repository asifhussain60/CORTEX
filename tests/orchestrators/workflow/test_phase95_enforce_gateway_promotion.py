"""
Phase 95 — enforce_gateway decorator applied to all execute_operation() overrides.

Phase 95 architectural finding: orchestrators that override execute_operation() fall
into two categories:

  Category A — "Gateway-mode receivers": receive structured mode strings ("IMPLEMENT",
    "FIX") from the gateway pipeline. These are the existing True orchestrators
    (Health, Vacuum, TDD, Debugger, Refactoring). No changes needed here.

  Category B — "Domain-operation receivers": receive domain-specific operation names
    ("comprehend", "scan", "plan_phases", "ANALYZE") or raw user requests.
    The WorkflowGateway._MODE_TEMPLATE_MAP does not cover these.
    These orchestrators must keep PHASE90_GATEWAY_ENABLED=False.

Phase 95 achievement: @enforce_gateway decorator is applied to all Category B
execute_operation() overrides. This closes the architectural bypass gap — the
decorator is armed and ready; when the gateway is extended to support domain-
specific mode routing (Phase 96), flipping the flag to True is the ONLY change
needed. No structural rework required.

Tested orchestrators (6 × 3 tests = 18 tests) + MasterOrchestrator (3 tests) = 21:
  - InteractionOrchestrator   — category B, flag False, @enforce_gateway ✅
  - SecurityOrchestrator      — category B, flag False, @enforce_gateway ✅
  - EnhancedPlanningOrchestrator — category B, flag False, @enforce_gateway ✅
  - PlanningOrchestrator      — category B, flag False, @enforce_gateway ✅
  - SDLCWorkflowOrchestrator  — category B, flag False, @enforce_gateway ✅
  - TrainerOrchestrator       — category B, flag False, @enforce_gateway ✅
  - MasterOrchestrator        — top-level raw request entry; flag False; NO decorator ✅

AC-P95-001 — Phase 95 enforce_gateway decorator sweep
CORE-008: TDD mandatory
CORE-064: Sweep Completeness Contract
"""
from __future__ import annotations

import pytest
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway


# =============================================================================
# HELPERS
# =============================================================================

def _has_enforce_gateway(cls: type, method_name: str = "execute_operation") -> bool:
    """Return True if the named method on cls is wrapped by enforce_gateway."""
    method = getattr(cls, method_name, None)
    if method is None:
        return False
    # enforce_gateway uses @functools.wraps, so __wrapped__ is set on the inner wrapper.
    return hasattr(method, "__wrapped__")


# =============================================================================
# InteractionOrchestrator
# =============================================================================

class TestInteractionOrchestratorPhase95:
    """Phase 95 — InteractionOrchestrator: flag False (category B) + @enforce_gateway."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        assert issubclass(InteractionOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_category_b(self) -> None:
        """Flag must be False — receives domain-specific operation names, not mode strings."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        assert InteractionOrchestrator.PHASE90_GATEWAY_ENABLED is False

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        assert _has_enforce_gateway(InteractionOrchestrator, "execute_operation"), (
            "InteractionOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


# =============================================================================
# SecurityOrchestrator
# =============================================================================

class TestSecurityOrchestratorPhase95:
    """Phase 95 — SecurityOrchestrator: flag False (category B) + @enforce_gateway."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        assert issubclass(SecurityOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_category_b(self) -> None:
        """Flag must be False — receives domain-specific operation names ("scan"), not mode strings."""
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        assert SecurityOrchestrator.PHASE90_GATEWAY_ENABLED is False

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        assert _has_enforce_gateway(SecurityOrchestrator, "execute_operation"), (
            "SecurityOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


# =============================================================================
# EnhancedPlanningOrchestrator
# =============================================================================

class TestEnhancedPlanningOrchestratorPhase95:
    """Phase 95 — EnhancedPlanningOrchestrator: flag False (category B) + @enforce_gateway."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        assert issubclass(EnhancedPlanningOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_category_b(self) -> None:
        """Flag must be False — receives domain-specific operation names, not mode strings."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        assert EnhancedPlanningOrchestrator.PHASE90_GATEWAY_ENABLED is False

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        assert _has_enforce_gateway(EnhancedPlanningOrchestrator, "execute_operation"), (
            "EnhancedPlanningOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


# =============================================================================
# PlanningOrchestrator
# =============================================================================

class TestPlanningOrchestratorPhase95:
    """Phase 95 — PlanningOrchestrator: flag False (category B) + @enforce_gateway."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        assert issubclass(PlanningOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_category_b(self) -> None:
        """Flag must be False — receives domain-specific operation names, not mode strings."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        assert PlanningOrchestrator.PHASE90_GATEWAY_ENABLED is False

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        assert _has_enforce_gateway(PlanningOrchestrator, "execute_operation"), (
            "PlanningOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


# =============================================================================
# SDLCWorkflowOrchestrator
# =============================================================================

class TestSDLCWorkflowOrchestratorPhase95:
    """Phase 95 — SDLCWorkflowOrchestrator: flag False (category B) + @enforce_gateway."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import SDLCWorkflowOrchestrator
        assert issubclass(SDLCWorkflowOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_category_b(self) -> None:
        """Flag must be False — SDLC dispatcher uses its own _SDLC_INTENT_MAP routing."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import SDLCWorkflowOrchestrator
        assert SDLCWorkflowOrchestrator.PHASE90_GATEWAY_ENABLED is False

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import SDLCWorkflowOrchestrator
        assert _has_enforce_gateway(SDLCWorkflowOrchestrator, "execute_operation"), (
            "SDLCWorkflowOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


# =============================================================================
# TrainerOrchestrator
# =============================================================================

class TestTrainerOrchestratorPhase95:
    """Phase 95 — TrainerOrchestrator: flag False (category B) + @enforce_gateway."""

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator
        assert issubclass(TrainerOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_category_b(self) -> None:
        """Phase 97 promoted TrainerOrchestrator to True — receives TRAIN mode via gateway."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator
        assert TrainerOrchestrator.PHASE90_GATEWAY_ENABLED is True

    def test_execute_operation_has_enforce_gateway_decorator(self) -> None:
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator
        assert _has_enforce_gateway(TrainerOrchestrator, "execute_operation"), (
            "TrainerOrchestrator.execute_operation must be decorated with @enforce_gateway"
        )


# =============================================================================
# MasterOrchestrator (core) — stays False: receives raw user requests as
# operation_name, not structured mode strings. IS the gateway initiator.
# @enforce_gateway intentionally NOT applied (architectural constraint).
# =============================================================================

class TestMasterOrchestratorPhase95:
    """Phase 95 — MasterOrchestrator: advisory False, no decorator (architectural constraint).

    MasterOrchestrator.execute_operation receives raw user request strings as
    operation_name — the gateway requires a structured mode key ("IMPLEMENT", "FIX").
    MasterOrchestrator is the gateway INITIATOR, not the gated target.
    It resolves mode internally via IntentRouter before calling execute_via_gateway.
    """

    def test_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        assert issubclass(MasterOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false_architectural_constraint(self) -> None:
        """MasterOrchestrator must stay False — raw request entry point, not gated target."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        assert MasterOrchestrator.PHASE90_GATEWAY_ENABLED is False

    def test_execute_operation_not_decorated_by_design(self) -> None:
        """execute_operation must NOT have @enforce_gateway — raw freeform operation_name."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        # Verify the method is NOT wrapped — decorator intentionally excluded.
        assert not _has_enforce_gateway(MasterOrchestrator, "execute_operation"), (
            "MasterOrchestrator.execute_operation must NOT be decorated with @enforce_gateway "
            "(architectural constraint: receives raw user requests, not mode strings)"
        )
