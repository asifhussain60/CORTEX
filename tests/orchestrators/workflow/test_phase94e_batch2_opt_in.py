"""Phase 94e — Batch 2 Domain Opt-in Tests.

Validates that 14 additional operational orchestrators are wired with
WorkflowEnforcementMixin (advisory, PHASE90_GATEWAY_ENABLED=False).

Orchestrators covered:
  - CortexMasterPlanOrchestrator  (core/)
  - ReviewOrchestrator            (core/)
  - WorkflowOrchestrator          (core/)
  - RequestRephraseOrchestrator   (core/)
  - DomainOrchestrator            (domain/)
  - ServiceDecompositionOrchestrator (domain/)
  - DashboardOrchestrator         (domain/)
  - DigestSessionOrchestrator     (support/)
  - UnifiedQualityAssuranceOrchestrator (support/)
  - SweepCatalogueOrchestrator    (support/)
  - SecurityVulnerabilityOrchestrator (validation/)
  - IntelligenceOrchestrator      (intelligence/)
  - PreCommitEnforcementOrchestrator  (git/)
  - SanitizationOrchestrator      (git/)
"""
import pytest

from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin


# ---------------------------------------------------------------------------
# CortexMasterPlanOrchestrator
# ---------------------------------------------------------------------------

class TestMasterPlanOrchestratorGateway:
    """Phase 94e: CortexMasterPlanOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.master_plan_orchestrator import CortexMasterPlanOrchestrator
        assert issubclass(CortexMasterPlanOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.master_plan_orchestrator import CortexMasterPlanOrchestrator
        assert CortexMasterPlanOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# ReviewOrchestrator
# ---------------------------------------------------------------------------

class TestReviewOrchestratorGateway:
    """Phase 94e: ReviewOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.review_orchestrator import ReviewOrchestrator
        assert issubclass(ReviewOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.review_orchestrator import ReviewOrchestrator
        assert ReviewOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# WorkflowOrchestrator
# ---------------------------------------------------------------------------

class TestWorkflowOrchestratorGateway:
    """Phase 94e: WorkflowOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator
        assert issubclass(WorkflowOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator
        assert WorkflowOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# RequestRephraseOrchestrator
# ---------------------------------------------------------------------------

class TestRequestRephraseOrchestratorGateway:
    """Phase 94e: RequestRephraseOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.request_rephrase_orchestrator import RequestRephraseOrchestrator
        assert issubclass(RequestRephraseOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.request_rephrase_orchestrator import RequestRephraseOrchestrator
        assert RequestRephraseOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# DomainOrchestrator
# ---------------------------------------------------------------------------

class TestDomainOrchestratorGateway:
    """Phase 94e: DomainOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.domain.domain_orchestrator import DomainOrchestrator
        assert issubclass(DomainOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.domain.domain_orchestrator import DomainOrchestrator
        assert DomainOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# ServiceDecompositionOrchestrator
# ---------------------------------------------------------------------------

class TestServiceDecompositionOrchestratorGateway:
    """Phase 94e: ServiceDecompositionOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.domain.service_decomposition_orchestrator import ServiceDecompositionOrchestrator
        assert issubclass(ServiceDecompositionOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.domain.service_decomposition_orchestrator import ServiceDecompositionOrchestrator
        assert ServiceDecompositionOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# DashboardOrchestrator
# ---------------------------------------------------------------------------

class TestDashboardOrchestratorGateway:
    """Phase 94e: DashboardOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.domain.dashboard_orchestrator import DashboardOrchestrator
        assert issubclass(DashboardOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.domain.dashboard_orchestrator import DashboardOrchestrator
        assert DashboardOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# DigestSessionOrchestrator
# ---------------------------------------------------------------------------

class TestDigestSessionOrchestratorGateway:
    """Phase 94e: DigestSessionOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.digest_session_orchestrator import DigestSessionOrchestrator
        assert issubclass(DigestSessionOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.digest_session_orchestrator import DigestSessionOrchestrator
        assert DigestSessionOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# UnifiedQualityAssuranceOrchestrator
# ---------------------------------------------------------------------------

class TestUnifiedQualityAssuranceOrchestratorGateway:
    """Phase 94e: UnifiedQualityAssuranceOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.unified_quality_orchestrator import UnifiedQualityAssuranceOrchestrator
        assert issubclass(UnifiedQualityAssuranceOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.unified_quality_orchestrator import UnifiedQualityAssuranceOrchestrator
        assert UnifiedQualityAssuranceOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# SweepCatalogueOrchestrator
# ---------------------------------------------------------------------------

class TestSweepCatalogueOrchestratorGateway:
    """Phase 94e: SweepCatalogueOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepCatalogueOrchestrator
        assert issubclass(SweepCatalogueOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepCatalogueOrchestrator
        assert SweepCatalogueOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# SecurityVulnerabilityOrchestrator
# ---------------------------------------------------------------------------

class TestSecurityVulnerabilityOrchestratorGateway:
    """Phase 94e: SecurityVulnerabilityOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import SecurityVulnerabilityOrchestrator
        assert issubclass(SecurityVulnerabilityOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import SecurityVulnerabilityOrchestrator
        assert SecurityVulnerabilityOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# IntelligenceOrchestrator
# ---------------------------------------------------------------------------

class TestIntelligenceOrchestratorGateway:
    """Phase 94e: IntelligenceOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.intelligence.intelligence_orchestrator import IntelligenceOrchestrator
        assert issubclass(IntelligenceOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.intelligence.intelligence_orchestrator import IntelligenceOrchestrator
        assert IntelligenceOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# PreCommitEnforcementOrchestrator
# ---------------------------------------------------------------------------

class TestPreCommitEnforcementOrchestratorGateway:
    """Phase 94e: PreCommitEnforcementOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.git.git_enforcement_orchestrator import PreCommitEnforcementOrchestrator
        assert issubclass(PreCommitEnforcementOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.git.git_enforcement_orchestrator import PreCommitEnforcementOrchestrator
        assert PreCommitEnforcementOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# SanitizationOrchestrator
# ---------------------------------------------------------------------------

class TestSanitizationOrchestratorGateway:
    """Phase 94e: SanitizationOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        assert issubclass(SanitizationOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        assert SanitizationOrchestrator.PHASE90_GATEWAY_ENABLED is False
