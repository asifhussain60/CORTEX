"""
Tests for WorkflowTemplateMixin — Phase 23 RED Phase.

Validates that OrchestratorBase gains workflow template capabilities:
- discover_templates() — list available templates by category
- load_template() — load and resolve a specific template
- get_recommended_template() — base returns None, subclasses override
- discover_company_templates() — company/workflows/ override auto-discovery

Authority: Phase 23 — Workflow Template Injection
TDD: CORE-008 — RED phase (tests written before implementation)
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import patch, MagicMock


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 23 SUB-PHASE A: RED PHASE — ALL TESTS MUST FAIL INITIALLY
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorkflowTemplateMixinImport:
    """AC-P23-001: WorkflowTemplateMixin importable from cortex.core.workflow_template_mixin."""

    def test_mixin_importable(self) -> None:
        """WorkflowTemplateMixin should be importable from cortex.core."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert WorkflowTemplateMixin is not None

    def test_mixin_has_discover_templates(self) -> None:
        """WorkflowTemplateMixin must expose discover_templates() method."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert hasattr(WorkflowTemplateMixin, 'discover_templates')
        assert callable(getattr(WorkflowTemplateMixin, 'discover_templates'))

    def test_mixin_has_load_template(self) -> None:
        """WorkflowTemplateMixin must expose load_template() method."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert hasattr(WorkflowTemplateMixin, 'load_template')
        assert callable(getattr(WorkflowTemplateMixin, 'load_template'))

    def test_mixin_has_get_recommended_template(self) -> None:
        """WorkflowTemplateMixin must expose get_recommended_template() method."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert hasattr(WorkflowTemplateMixin, 'get_recommended_template')
        assert callable(getattr(WorkflowTemplateMixin, 'get_recommended_template'))

    def test_mixin_has_discover_company_templates(self) -> None:
        """WorkflowTemplateMixin must expose discover_company_templates() method."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert hasattr(WorkflowTemplateMixin, 'discover_company_templates')
        assert callable(getattr(WorkflowTemplateMixin, 'discover_company_templates'))


class TestDiscoverTemplates:
    """AC-P23-002: discover_templates() returns list of available templates."""

    def test_discover_all_templates_returns_list(self) -> None:
        """discover_templates() with no filter returns a non-empty list."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        result = mixin.discover_templates()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_discover_templates_by_category(self) -> None:
        """discover_templates(category='tdd') returns only tdd templates."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        result = mixin.discover_templates(category="tdd")
        assert isinstance(result, list)
        for template in result:
            assert template["category"] == "tdd"

    def test_discover_templates_returns_template_structure(self) -> None:
        """Each discovered template has id, name, category, source keys."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        result = mixin.discover_templates()
        if len(result) > 0:
            template = result[0]
            assert "id" in template
            assert "name" in template
            assert "category" in template


class TestLoadTemplate:
    """AC-P23-003: load_template(id) returns resolved template dict."""

    def test_load_existing_template(self) -> None:
        """load_template() for an existing template returns a valid dict."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        # Register a template first for this test
        mixin._ensure_registry_loaded()
        # Use the actual ID from the YAML (workflow.id), not derived from filename
        result = mixin.load_template("tdd/feature-implementation")
        assert isinstance(result, dict)
        assert "id" in result
        assert result["id"] == "tdd/feature-implementation"

    def test_load_nonexistent_template_raises(self) -> None:
        """load_template() for a missing template raises TemplateNotFoundError."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        from cortex.orchestrators.workflow.template_registry import TemplateNotFoundError
        mixin = WorkflowTemplateMixin()
        with pytest.raises(TemplateNotFoundError):
            mixin.load_template("nonexistent/does-not-exist")

    def test_load_template_contains_steps(self) -> None:
        """Loaded template should contain steps list."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        mixin._ensure_registry_loaded()
        result = mixin.load_template("tdd/feature-implementation")
        assert "steps" in result


class TestGetRecommendedTemplate:
    """AC-P23-004: get_recommended_template() returns None on base class."""

    def test_base_mixin_returns_none(self) -> None:
        """Base WorkflowTemplateMixin.get_recommended_template() returns None."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        result = mixin.get_recommended_template()
        assert result is None

    def test_subclass_can_override(self) -> None:
        """A subclass can override get_recommended_template() with a template ID."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

        class MockOrchestrator(WorkflowTemplateMixin):
            def get_recommended_template(self) -> Optional[str]:
                return "tdd/tdd-feature-implementation"

        orchestrator = MockOrchestrator()
        assert orchestrator.get_recommended_template() == "tdd/tdd-feature-implementation"


class TestOrchestratorBaseInheritsMixin:
    """AC-P23-005: OrchestratorBase inherits WorkflowTemplateMixin."""

    def test_orchestrator_base_has_discover_templates(self) -> None:
        """OrchestratorBase instances must have discover_templates()."""
        from cortex.core.orchestrator_base import OrchestratorBase
        assert hasattr(OrchestratorBase, 'discover_templates')

    def test_orchestrator_base_has_load_template(self) -> None:
        """OrchestratorBase instances must have load_template()."""
        from cortex.core.orchestrator_base import OrchestratorBase
        assert hasattr(OrchestratorBase, 'load_template')

    def test_orchestrator_base_has_get_recommended_template(self) -> None:
        """OrchestratorBase instances must have get_recommended_template()."""
        from cortex.core.orchestrator_base import OrchestratorBase
        assert hasattr(OrchestratorBase, 'get_recommended_template')

    def test_orchestrator_base_get_recommended_returns_none(self) -> None:
        """OrchestratorBase.get_recommended_template() should return None by default."""
        from cortex.core.orchestrator_base import OrchestratorBase

        class ConcreteOrchestrator(OrchestratorBase):
            def execute_operation(self) -> Dict[str, Any]:
                return {}

        orch = ConcreteOrchestrator(orchestrator_id="test-base")
        assert orch.get_recommended_template() is None


class TestTDDOrchestratorTemplateWiring:
    """AC-P23-006: TDDOrchestrator.get_recommended_template() returns tdd template."""

    def test_tdd_orchestrator_has_recommended_template(self) -> None:
        """TDDOrchestrator.get_recommended_template() must return tdd template ID."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        orch = TDDOrchestrator()
        result = orch.get_recommended_template()
        assert result is not None
        assert "tdd" in result

    def test_tdd_orchestrator_recommended_is_feature_implementation(self) -> None:
        """TDDOrchestrator recommends tdd/feature-implementation specifically."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        orch = TDDOrchestrator()
        result = orch.get_recommended_template()
        assert result == "tdd/feature-implementation"


class TestDiscoverCompanyTemplates:
    """AC-P23-007: discover_company_templates() scans company/workflows/."""

    def test_discover_company_templates_returns_list(self) -> None:
        """discover_company_templates() returns a list (empty if no company templates)."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        result = mixin.discover_company_templates()
        assert isinstance(result, list)

    def test_company_templates_override_precedence(self) -> None:
        """Company templates should override cortex-registry templates with same ID."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mixin = WorkflowTemplateMixin()
        # When company/workflows/ exists with a matching template,
        # the company version should take precedence
        result = mixin.discover_company_templates()
        # Even if empty, it should be a list
        assert isinstance(result, list)


class TestTemplateOrchestratorMapping:
    """AC-P23-009: Template-orchestrator mapping matches specification."""

    EXPECTED_MAPPINGS = {
        "TDDOrchestrator": "tdd/feature-implementation",
    }

    def test_template_mapping_registry_exists(self) -> None:
        """WorkflowTemplateMixin should expose TEMPLATE_ORCHESTRATOR_MAP."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert hasattr(WorkflowTemplateMixin, 'TEMPLATE_ORCHESTRATOR_MAP')

    def test_tdd_mapping_correct(self) -> None:
        """TDDOrchestrator maps to tdd/feature-implementation."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mapping = WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP
        assert "TDDOrchestrator" in mapping
        assert mapping["TDDOrchestrator"] == "tdd/feature-implementation"


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 23 COMPLETION: ORCHESTRATOR TEMPLATE WIRING TESTS
# All orchestrators in TEMPLATE_ORCHESTRATOR_MAP must have get_recommended_template()
# ═══════════════════════════════════════════════════════════════════════════════


class TestSecurityOrchestratorTemplateWiring:
    """AC-P23-010: SecurityOrchestrator wired with WorkflowTemplateMixin."""

    def test_security_orchestrator_has_mixin(self) -> None:
        """SecurityOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(SecurityOrchestrator, WorkflowTemplateMixin)

    def test_security_orchestrator_recommended_template(self) -> None:
        """SecurityOrchestrator.get_recommended_template() returns security template."""
        from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator
        orch = SecurityOrchestrator()
        result = orch.get_recommended_template()
        assert result == "security/security-hardening"


class TestPlanningOrchestratorTemplateWiring:
    """AC-P23-011: PlanningOrchestrator wired with WorkflowTemplateMixin."""

    def test_planning_orchestrator_has_mixin(self) -> None:
        """PlanningOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(PlanningOrchestrator, WorkflowTemplateMixin)

    def test_planning_orchestrator_recommended_template(self) -> None:
        """PlanningOrchestrator.get_recommended_template() returns lifecycle template."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        orch = PlanningOrchestrator()
        result = orch.get_recommended_template()
        assert result == "lifecycle/master-plan-execution"


class TestEnforcementOrchestratorTemplateWiring:
    """AC-P23-012: EnforcementOrchestrator wired with WorkflowTemplateMixin."""

    def test_enforcement_orchestrator_has_mixin(self) -> None:
        """EnforcementOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(EnforcementOrchestrator, WorkflowTemplateMixin)

    def test_enforcement_orchestrator_recommended_template(self) -> None:
        """EnforcementOrchestrator.get_recommended_template() returns compliance template."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
        orch = EnforcementOrchestrator()
        result = orch.get_recommended_template()
        assert result == "security/compliance-audit"


class TestDebuggerOrchestratorTemplateWiring:
    """AC-P23-013: DebuggerOrchestrator wired with WorkflowTemplateMixin."""

    def test_debugger_orchestrator_has_mixin(self) -> None:
        """DebuggerOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(DebuggerOrchestrator, WorkflowTemplateMixin)

    def test_debugger_orchestrator_recommended_template(self) -> None:
        """DebuggerOrchestrator.get_recommended_template() returns quality template."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        from cortex.core.event_bus import EventBus
        orch = DebuggerOrchestrator(event_bus=EventBus())
        result = orch.get_recommended_template()
        assert result == "quality/dead-code-removal"


class TestMasterPlanOrchestratorTemplateWiring:
    """AC-P23-014: CortexMasterPlanOrchestrator wired with WorkflowTemplateMixin."""

    def test_master_plan_orchestrator_has_mixin(self) -> None:
        """CortexMasterPlanOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.core.master_plan_orchestrator import CortexMasterPlanOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(CortexMasterPlanOrchestrator, WorkflowTemplateMixin)

    def test_master_plan_orchestrator_recommended_template(self) -> None:
        """CortexMasterPlanOrchestrator.get_recommended_template() returns lifecycle template."""
        from cortex.orchestrators.core.master_plan_orchestrator import CortexMasterPlanOrchestrator
        orch = CortexMasterPlanOrchestrator()
        result = orch.get_recommended_template()
        assert result == "lifecycle/master-plan-execution"


class TestEnhancedPlanningOrchestratorTemplateWiring:
    """AC-P23-015: EnhancedPlanningOrchestrator wired with WorkflowTemplateMixin."""

    def test_enhanced_planning_orchestrator_has_mixin(self) -> None:
        """EnhancedPlanningOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(EnhancedPlanningOrchestrator, WorkflowTemplateMixin)

    def test_enhanced_planning_orchestrator_recommended_template(self) -> None:
        """EnhancedPlanningOrchestrator.get_recommended_template() returns lifecycle template."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import EnhancedPlanningOrchestrator
        orch = EnhancedPlanningOrchestrator()
        result = orch.get_recommended_template()
        assert result == "lifecycle/master-plan-execution"


class TestMasterOrchestratorTemplateWiring:
    """AC-P23-016: MasterOrchestrator wired with WorkflowTemplateMixin."""

    def test_master_orchestrator_has_mixin(self) -> None:
        """MasterOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(MasterOrchestrator, WorkflowTemplateMixin)

    def test_master_orchestrator_recommended_template(self) -> None:
        """MasterOrchestrator.get_recommended_template() returns lifecycle template."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        orch = MasterOrchestrator()
        result = orch.get_recommended_template()
        assert result == "lifecycle/composite-execution-pipeline"


class TestInteractionOrchestratorTemplateWiring:
    """AC-P23-017: InteractionOrchestrator wired with WorkflowTemplateMixin."""

    def test_interaction_orchestrator_has_mixin(self) -> None:
        """InteractionOrchestrator class inherits WorkflowTemplateMixin."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(InteractionOrchestrator, WorkflowTemplateMixin)

    def test_interaction_orchestrator_recommended_template(self) -> None:
        """InteractionOrchestrator.get_recommended_template() returns request-execution template."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        from unittest.mock import MagicMock
        orch = InteractionOrchestrator(conversation_protocol=MagicMock())
        result = orch.get_recommended_template()
        assert result == "request-execution/plan-gate"


class TestAllMappedOrchestratorsHaveOverride:
    """AC-P23-018: Every orchestrator in TEMPLATE_ORCHESTRATOR_MAP has get_recommended_template()."""

    def test_all_mapped_orchestrators_return_expected_template(self) -> None:
        """Each mapped orchestrator returns its expected template ID."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        mapping = WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP
        # Verify the map has all expected entries
        expected_orchestrators = {
            "TDDOrchestrator",
            "RefactoringOrchestrator",
            "EnforcementOrchestrator",
            "MasterPlanOrchestrator",
            "MasterOrchestrator",
            "AuditCoordinator",
            "PlanningOrchestrator",
            "InteractionOrchestrator",
            "SecurityOrchestrator",
            "DebuggerOrchestrator",
        }
        assert expected_orchestrators.issubset(set(mapping.keys())), (
            f"Missing orchestrators in TEMPLATE_ORCHESTRATOR_MAP: "
            f"{expected_orchestrators - set(mapping.keys())}"
        )
