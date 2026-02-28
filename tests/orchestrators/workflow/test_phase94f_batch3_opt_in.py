"""Phase 94f — Batch 3 Domain Opt-in Tests.

Validates that the remaining 24 operational orchestrators are wired with
WorkflowEnforcementMixin (advisory, PHASE90_GATEWAY_ENABLED=False).

Orchestrators covered:
  core/:
    - BrainHealthOrchestrator
    - CentralBrainOrchestrator
    - ConversationOrchestrator
    - ObservabilityOrchestrator
    - PhaseOrchestrator            (phase_executors/)
    - StateOrchestrator
  domain/:
    - InquiryOrchestrator
  git/:
    - GitPublishOrchestrator
  intelligence/:
    - TechIntelligenceOrchestrator
    - TrainerOrchestrator
  persona/:
    - MasterOrchestrator           (persona master — distinct from core master)
  support/:
    - AutoHealingMCPOrchestrator
    - BulkDigestOrchestrator
    - ContextAssemblyOrchestrator
    - CortexDocsOrchestrator
    - LENSVisualizationOrchestrator
    - PlanRegistrySyncOrchestrator
    - PhaseCompletionOrchestrator
    - PlanOrchestrator
    - RepoDetectionOrchestrator
    - SetupOrchestrator
    - TestClassifierOrchestrator
    - VacuumOrchestrator           (support/ adapter — inherits from health/)
  validation/:
    - SOLIDOrchestrator
"""
import pytest

from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin


# ---------------------------------------------------------------------------
# BrainHealthOrchestrator
# ---------------------------------------------------------------------------

class TestBrainHealthOrchestratorGateway:
    """Phase 94f: BrainHealthOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.brain_health_orchestrator import BrainHealthOrchestrator
        assert issubclass(BrainHealthOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.brain_health_orchestrator import BrainHealthOrchestrator
        assert BrainHealthOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# CentralBrainOrchestrator
# ---------------------------------------------------------------------------

class TestCentralBrainOrchestratorGateway:
    """Phase 94f: CentralBrainOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.central_brain_orchestrator import CentralBrainOrchestrator
        assert issubclass(CentralBrainOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.central_brain_orchestrator import CentralBrainOrchestrator
        assert CentralBrainOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# ConversationOrchestrator
# ---------------------------------------------------------------------------

class TestConversationOrchestratorGateway:
    """Phase 94f: ConversationOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.conversation_orchestrator import ConversationOrchestrator
        assert issubclass(ConversationOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.conversation_orchestrator import ConversationOrchestrator
        assert ConversationOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# ObservabilityOrchestrator
# ---------------------------------------------------------------------------

class TestObservabilityOrchestratorGateway:
    """Phase 94f: ObservabilityOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.observability_orchestrator import ObservabilityOrchestrator
        assert issubclass(ObservabilityOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.observability_orchestrator import ObservabilityOrchestrator
        assert ObservabilityOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# PhaseOrchestrator
# ---------------------------------------------------------------------------

class TestPhaseOrchestratorGateway:
    """Phase 94f: PhaseOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.phase_executors.phase_orchestrator import PhaseOrchestrator
        assert issubclass(PhaseOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.phase_executors.phase_orchestrator import PhaseOrchestrator
        assert PhaseOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# StateOrchestrator
# ---------------------------------------------------------------------------

class TestStateOrchestratorGateway:
    """Phase 94f: StateOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.core.state_orchestrator import StateOrchestrator
        assert issubclass(StateOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.core.state_orchestrator import StateOrchestrator
        assert StateOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# InquiryOrchestrator
# ---------------------------------------------------------------------------

class TestInquiryOrchestratorGateway:
    """Phase 94f: InquiryOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.domain.inquiry_orchestrator import InquiryOrchestrator
        assert issubclass(InquiryOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.domain.inquiry_orchestrator import InquiryOrchestrator
        assert InquiryOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# GitPublishOrchestrator
# ---------------------------------------------------------------------------

class TestGitPublishOrchestratorGateway:
    """Phase 94f: GitPublishOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.git.git_publish_orchestrator import GitPublishOrchestrator
        assert issubclass(GitPublishOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.git.git_publish_orchestrator import GitPublishOrchestrator
        assert GitPublishOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# TechIntelligenceOrchestrator
# ---------------------------------------------------------------------------

class TestTechIntelligenceOrchestratorGateway:
    """Phase 94f: TechIntelligenceOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import TechIntelligenceOrchestrator
        assert issubclass(TechIntelligenceOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import TechIntelligenceOrchestrator
        assert TechIntelligenceOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# TrainerOrchestrator
# ---------------------------------------------------------------------------

class TestTrainerOrchestratorGateway:
    """Phase 94f: TrainerOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator
        assert issubclass(TrainerOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator
        assert TrainerOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# Persona MasterOrchestrator
# ---------------------------------------------------------------------------

class TestPersonaMasterOrchestratorGateway:
    """Phase 94f: Persona MasterOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
        assert issubclass(MasterOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
        assert MasterOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# AutoHealingMCPOrchestrator
# ---------------------------------------------------------------------------

class TestAutoHealingMCPOrchestratorGateway:
    """Phase 94f: AutoHealingMCPOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.auto_healing_mcp_orchestrator import AutoHealingMCPOrchestrator
        assert issubclass(AutoHealingMCPOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.auto_healing_mcp_orchestrator import AutoHealingMCPOrchestrator
        assert AutoHealingMCPOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# BulkDigestOrchestrator
# ---------------------------------------------------------------------------

class TestBulkDigestOrchestratorGateway:
    """Phase 94f: BulkDigestOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        assert issubclass(BulkDigestOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        assert BulkDigestOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# ContextAssemblyOrchestrator
# ---------------------------------------------------------------------------

class TestContextAssemblyOrchestratorGateway:
    """Phase 94f: ContextAssemblyOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.context_assembly_orchestrator import ContextAssemblyOrchestrator
        assert issubclass(ContextAssemblyOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.context_assembly_orchestrator import ContextAssemblyOrchestrator
        assert ContextAssemblyOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# CortexDocsOrchestrator
# ---------------------------------------------------------------------------

class TestCortexDocsOrchestratorGateway:
    """Phase 94f: CortexDocsOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.cortex_docs_orchestrator import CortexDocsOrchestrator
        assert issubclass(CortexDocsOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.cortex_docs_orchestrator import CortexDocsOrchestrator
        assert CortexDocsOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# LENSVisualizationOrchestrator
# ---------------------------------------------------------------------------

class TestLENSVisualizationOrchestratorGateway:
    """Phase 94f: LENSVisualizationOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.lens_visualization_orchestrator import LENSVisualizationOrchestrator
        assert issubclass(LENSVisualizationOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.lens_visualization_orchestrator import LENSVisualizationOrchestrator
        assert LENSVisualizationOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# PlanRegistrySyncOrchestrator
# ---------------------------------------------------------------------------

class TestPlanRegistrySyncOrchestratorGateway:
    """Phase 94f: PlanRegistrySyncOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.phase_completion_orchestrator import PlanRegistrySyncOrchestrator
        assert issubclass(PlanRegistrySyncOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.phase_completion_orchestrator import PlanRegistrySyncOrchestrator
        assert PlanRegistrySyncOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# PhaseCompletionOrchestrator
# ---------------------------------------------------------------------------

class TestPhaseCompletionOrchestratorGateway:
    """Phase 94f: PhaseCompletionOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        assert issubclass(PhaseCompletionOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
        assert PhaseCompletionOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# PlanOrchestrator
# ---------------------------------------------------------------------------

class TestPlanOrchestratorGateway:
    """Phase 94f: PlanOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator
        assert issubclass(PlanOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator
        assert PlanOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# RepoDetectionOrchestrator
# ---------------------------------------------------------------------------

class TestRepoDetectionOrchestratorGateway:
    """Phase 94f: RepoDetectionOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.repo_detection_orchestrator import RepoDetectionOrchestrator
        assert issubclass(RepoDetectionOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.repo_detection_orchestrator import RepoDetectionOrchestrator
        assert RepoDetectionOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# SetupOrchestrator
# ---------------------------------------------------------------------------

class TestSetupOrchestratorGateway:
    """Phase 94f: SetupOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.setup_orchestrator import SetupOrchestrator
        assert issubclass(SetupOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.setup_orchestrator import SetupOrchestrator
        assert SetupOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# TestClassifierOrchestrator
# ---------------------------------------------------------------------------

class TestTestClassifierOrchestratorGateway:
    """Phase 94f: TestClassifierOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.test_classifier_orchestrator import TestClassifierOrchestrator
        assert issubclass(TestClassifierOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.test_classifier_orchestrator import TestClassifierOrchestrator
        assert TestClassifierOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# VacuumOrchestrator (support/ adapter)
# ---------------------------------------------------------------------------

class TestSupportVacuumOrchestratorGateway:
    """Phase 94f: support/VacuumOrchestrator gateway wiring (adapter over health/)."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator
        assert issubclass(VacuumOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator
        # support/ adapter — advisory False; health/ VacuumOrchestrator is True
        assert VacuumOrchestrator.PHASE90_GATEWAY_ENABLED is False


# ---------------------------------------------------------------------------
# SOLIDOrchestrator
# ---------------------------------------------------------------------------

class TestSOLIDOrchestratorGateway:
    """Phase 94f: SOLIDOrchestrator gateway wiring."""

    def test_inherits_enforcement_mixin(self):
        from cortex.orchestrators.validation.solid_orchestrator import SOLIDOrchestrator
        assert issubclass(SOLIDOrchestrator, WorkflowEnforcementMixin)

    def test_gateway_enabled_is_false(self):
        from cortex.orchestrators.validation.solid_orchestrator import SOLIDOrchestrator
        assert SOLIDOrchestrator.PHASE90_GATEWAY_ENABLED is False
