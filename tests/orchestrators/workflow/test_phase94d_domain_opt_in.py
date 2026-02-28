"""Phase 94d — Domain orchestrator WorkflowEnforcementMixin opt-in.

RED → GREEN TDD cycle verifying that 9 high-impact operational orchestrators
carry WorkflowEnforcementMixin in their MRO with PHASE90_GATEWAY_ENABLED=False
(advisory mode — safe rollout, no behaviour change until explicitly enabled).

Coverage matrix:
  CLUSTER 1: core/ operational orchestrators (3 tests)
  CLUSTER 2: domain/ operational orchestrators (3 tests)
  CLUSTER 3: support/ + validation/ orchestrators (2 tests)
  CLUSTER 4: git/ orchestrator (1 test)

AC-ID: AC-P94D-001..009
CORE-008: TDD — RED tests written before implementation.
CORE-055: golden-tier contract (advisory enforcement only — False flags).
"""

from __future__ import annotations

import pytest

from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER 1 — core/ operational orchestrators
# ─────────────────────────────────────────────────────────────────────────────

class TestInteractionOrchestratorPhase94D:
    """AC-P94D-001: InteractionOrchestrator carries WorkflowEnforcementMixin."""

    def test_interaction_inherits_enforcement_mixin(self):
        """InteractionOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        assert issubclass(InteractionOrchestrator, WorkflowEnforcementMixin), (
            "InteractionOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_interaction_gateway_enabled_is_false(self):
        """InteractionOrchestrator.PHASE90_GATEWAY_ENABLED must be False (advisory)."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        assert InteractionOrchestrator.PHASE90_GATEWAY_ENABLED is False, (
            "InteractionOrchestrator.PHASE90_GATEWAY_ENABLED must be False — "
            "it is an always-active stage-1 orchestrator; self-gating breaks pipeline"
        )


class TestSecurityOrchestratorPhase94D:
    """AC-P94D-002: SecurityOrchestrator carries WorkflowEnforcementMixin."""

    def test_security_inherits_enforcement_mixin(self):
        """SecurityOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        assert issubclass(SecurityOrchestrator, WorkflowEnforcementMixin), (
            "SecurityOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_security_gateway_enabled_is_false(self):
        """SecurityOrchestrator.PHASE90_GATEWAY_ENABLED must be False (advisory)."""
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        assert SecurityOrchestrator.PHASE90_GATEWAY_ENABLED is False, (
            "SecurityOrchestrator.PHASE90_GATEWAY_ENABLED must be False — advisory mode"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER 2 — domain/ operational orchestrators
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanningOrchestratorPhase94D:
    """AC-P94D-003: PlanningOrchestrator carries WorkflowEnforcementMixin."""

    def test_planning_inherits_enforcement_mixin(self):
        """PlanningOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        assert issubclass(PlanningOrchestrator, WorkflowEnforcementMixin), (
            "PlanningOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_planning_gateway_enabled_is_false(self):
        """PlanningOrchestrator.PHASE90_GATEWAY_ENABLED must be False (advisory)."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        assert PlanningOrchestrator.PHASE90_GATEWAY_ENABLED is False


class TestEnhancedPlanningOrchestratorPhase94D:
    """AC-P94D-004: EnhancedPlanningOrchestrator carries WorkflowEnforcementMixin."""

    def test_enhanced_planning_inherits_enforcement_mixin(self):
        """EnhancedPlanningOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        assert issubclass(EnhancedPlanningOrchestrator, WorkflowEnforcementMixin), (
            "EnhancedPlanningOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_enhanced_planning_gateway_enabled_is_false(self):
        """EnhancedPlanningOrchestrator.PHASE90_GATEWAY_ENABLED must be False."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        assert EnhancedPlanningOrchestrator.PHASE90_GATEWAY_ENABLED is False


class TestSDLCWorkflowOrchestratorPhase94D:
    """AC-P94D-005: SDLCWorkflowOrchestrator carries WorkflowEnforcementMixin."""

    def test_sdlc_inherits_enforcement_mixin(self):
        """SDLCWorkflowOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import SDLCWorkflowOrchestrator
        assert issubclass(SDLCWorkflowOrchestrator, WorkflowEnforcementMixin), (
            "SDLCWorkflowOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_sdlc_gateway_enabled_is_false(self):
        """SDLCWorkflowOrchestrator.PHASE90_GATEWAY_ENABLED must be False (advisory)."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import SDLCWorkflowOrchestrator
        assert SDLCWorkflowOrchestrator.PHASE90_GATEWAY_ENABLED is False, (
            "SDLCWorkflowOrchestrator.PHASE90_GATEWAY_ENABLED must be False — "
            "SDLC orchestrator is a dispatcher; self-gating before template resolution "
            "would create a re-entry loop through WorkflowComposer"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER 3 — support/ + validation/ orchestrators
# ─────────────────────────────────────────────────────────────────────────────

class TestRepositoryOnboardingOrchestratorPhase94D:
    """AC-P94D-006: RepositoryOnboardingOrchestrator carries WorkflowEnforcementMixin."""

    def test_onboarding_inherits_enforcement_mixin(self):
        """RepositoryOnboardingOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator,
        )
        assert issubclass(RepositoryOnboardingOrchestrator, WorkflowEnforcementMixin), (
            "RepositoryOnboardingOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_onboarding_gateway_enabled_is_false(self):
        """RepositoryOnboardingOrchestrator.PHASE90_GATEWAY_ENABLED must be False."""
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator,
        )
        assert RepositoryOnboardingOrchestrator.PHASE90_GATEWAY_ENABLED is False


class TestHolisticValidationOrchestratorPhase94D:
    """AC-P94D-007: HolisticValidationOrchestrator carries WorkflowEnforcementMixin."""

    def test_holistic_validation_inherits_enforcement_mixin(self):
        """HolisticValidationOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.validation.holistic_validation_orchestrator import (
            HolisticValidationOrchestrator,
        )
        assert issubclass(HolisticValidationOrchestrator, WorkflowEnforcementMixin), (
            "HolisticValidationOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_holistic_validation_gateway_enabled_is_false(self):
        """HolisticValidationOrchestrator.PHASE90_GATEWAY_ENABLED must be False."""
        from cortex.orchestrators.validation.holistic_validation_orchestrator import (
            HolisticValidationOrchestrator,
        )
        assert HolisticValidationOrchestrator.PHASE90_GATEWAY_ENABLED is False, (
            "HolisticValidationOrchestrator.PHASE90_GATEWAY_ENABLED must be False — "
            "it IS the pre-execution gate (CORE-048); self-gating = circular dependency"
        )


class TestUpgradeOrchestratorPhase94D:
    """AC-P94D-008: UpgradeOrchestrator carries WorkflowEnforcementMixin."""

    def test_upgrade_inherits_enforcement_mixin(self):
        """UpgradeOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.support.upgrade_orchestrator import UpgradeOrchestrator
        assert issubclass(UpgradeOrchestrator, WorkflowEnforcementMixin), (
            "UpgradeOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_upgrade_gateway_enabled_is_false(self):
        """UpgradeOrchestrator.PHASE90_GATEWAY_ENABLED must be False."""
        from cortex.orchestrators.support.upgrade_orchestrator import UpgradeOrchestrator
        assert UpgradeOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER 4 — git/ orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class TestGitOrchestratorPhase94D:
    """AC-P94D-009: GitOrchestrator carries WorkflowEnforcementMixin."""

    def test_git_inherits_enforcement_mixin(self):
        """GitOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.orchestrators.git.git_orchestrator import GitOrchestrator
        assert issubclass(GitOrchestrator, WorkflowEnforcementMixin), (
            "GitOrchestrator must carry WorkflowEnforcementMixin — Phase 94d"
        )

    def test_git_gateway_enabled_is_false(self):
        """GitOrchestrator.PHASE90_GATEWAY_ENABLED must be False (advisory)."""
        from cortex.orchestrators.git.git_orchestrator import GitOrchestrator
        assert GitOrchestrator.PHASE90_GATEWAY_ENABLED is False, (
            "GitOrchestrator.PHASE90_GATEWAY_ENABLED must be False — "
            "git ops run inside the audit-fix-pipeline; self-gating = re-entry loop"
        )
