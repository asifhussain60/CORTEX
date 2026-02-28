"""
Phase 90 — WorkflowEnforcementMixin: Mandatory Gateway Opt-in (RED tests).

Verifies that orchestrators inheriting WorkflowEnforcementMixin cannot
call execute_operation() without routing through WorkflowGateway first.

CORE-008: TDD mandatory — RED before GREEN
AC-ID: AC-P90-WEM-001
"""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Any, Dict


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: Mixin imports + API contract
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowEnforcementMixinImport:
    """WorkflowEnforcementMixin must be importable from cortex.core."""

    def test_mixin_importable(self) -> None:
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert WorkflowEnforcementMixin is not None

    def test_mixin_has_execute_via_gateway(self) -> None:
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert hasattr(WorkflowEnforcementMixin, "execute_via_gateway"), (
            "WorkflowEnforcementMixin must expose execute_via_gateway()"
        )

    def test_mixin_has_phase90_gate_flag(self) -> None:
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert hasattr(WorkflowEnforcementMixin, "PHASE90_GATEWAY_ENABLED"), (
            "WorkflowEnforcementMixin must have PHASE90_GATEWAY_ENABLED flag"
        )

    def test_phase90_gate_defaults_false(self) -> None:
        """Default must be False — opt-in only, zero big-bang risk."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert WorkflowEnforcementMixin.PHASE90_GATEWAY_ENABLED is False, (
            "Default must be False — orchestrators opt in explicitly"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: execute_via_gateway routes through WorkflowGateway
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowEnforcementMixinRouting:
    """When PHASE90_GATEWAY_ENABLED=True, execute_via_gateway must call WorkflowGateway."""

    @pytest.fixture
    def mixin_class(self) -> Any:
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin

        class ConcreteOrchestrator(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = True
            _orch_name = "ConcreteOrchestrator"

            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Any:
                return {"result": "direct_bypass"}

        return ConcreteOrchestrator

    def test_execute_via_gateway_calls_gateway_not_direct(self, mixin_class: Any) -> None:
        """execute_via_gateway must call WorkflowGateway.execute_gated, not execute_operation directly."""
        instance = mixin_class()

        mock_gateway = MagicMock()
        mock_gateway.execute_gated.return_value = {
            "status": "complete",
            "template_id": "sdlc/implement-workflow",
        }
        instance._gateway = mock_gateway

        result = instance.execute_via_gateway(
            mode="IMPLEMENT",
            parameters={"request_summary": "add feature"},
        )

        mock_gateway.execute_gated.assert_called_once()
        assert result.get("template_id") == "sdlc/implement-workflow"

    def test_execute_via_gateway_disabled_falls_through(self, mixin_class: Any) -> None:
        """When PHASE90_GATEWAY_ENABLED=False, execute_via_gateway calls execute_operation directly."""
        mixin_class.PHASE90_GATEWAY_ENABLED = False
        instance = mixin_class()

        result = instance.execute_via_gateway(
            mode="IMPLEMENT",
            parameters={"request_summary": "add feature"},
        )

        # Falls through to concrete execute_operation
        assert result == {"result": "direct_bypass"}

    def test_execute_via_gateway_passes_mode_to_gateway(self, mixin_class: Any) -> None:
        """The mode must be forwarded to WorkflowGateway.execute_gated."""
        instance = mixin_class()
        mock_gateway = MagicMock()
        mock_gateway.execute_gated.return_value = {"status": "complete", "template_id": "sdlc/fix-workflow"}
        instance._gateway = mock_gateway

        instance.execute_via_gateway(mode="FIX", parameters={})

        call_kwargs = mock_gateway.execute_gated.call_args
        # mode must appear in call args or kwargs
        call_repr = str(call_kwargs)
        assert "FIX" in call_repr, "mode=FIX must be forwarded to WorkflowGateway"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: Health + Vacuum orchestrators inherit the mixin
# ════════════════════════════════════════════════════════════════════════════

class TestHealthVacuumMixinInheritance:
    """HealthOrchestrator and VacuumOrchestrator must inherit WorkflowEnforcementMixin."""

    def test_health_orchestrator_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(HealthOrchestrator, WorkflowEnforcementMixin), (
            "HealthOrchestrator must inherit WorkflowEnforcementMixin (Phase 90)"
        )

    def test_vacuum_orchestrator_inherits_enforcement_mixin(self) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(VacuumOrchestrator, WorkflowEnforcementMixin), (
            "VacuumOrchestrator must inherit WorkflowEnforcementMixin (Phase 90)"
        )

    def test_health_orchestrator_in_template_map(self) -> None:
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert "HealthOrchestrator" in WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP, (
            "HealthOrchestrator must be in TEMPLATE_ORCHESTRATOR_MAP"
        )

    def test_vacuum_orchestrator_in_template_map(self) -> None:
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert "VacuumOrchestrator" in WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP, (
            "VacuumOrchestrator must be in TEMPLATE_ORCHESTRATOR_MAP"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: get_recommended_template correctness
# ════════════════════════════════════════════════════════════════════════════

class TestGetRecommendedTemplateCorrectness:
    """All operational orchestrators must return correct template IDs."""

    def test_tdd_orchestrator_returns_tdd_workflow(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        orch = TDDOrchestrator()
        template = orch.get_recommended_template()
        assert template in ("tdd/tdd-workflow", "sdlc/implement-workflow", "sdlc/fix-workflow"), (
            f"TDDOrchestrator.get_recommended_template() returned '{template}', "
            "expected tdd/tdd-workflow, sdlc/implement-workflow, or sdlc/fix-workflow"
        )

    def test_debugger_orchestrator_returns_debug_pipeline(self) -> None:
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        from cortex.core.event_bus import EventBus
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator

        eb = EventBus()
        orch = DebuggerOrchestrator(eb)
        template = orch.get_recommended_template()
        assert template == "debugging/multi-stack-debug-pipeline", (
            f"DebuggerOrchestrator.get_recommended_template() returned '{template}', "
            "expected debugging/multi-stack-debug-pipeline"
        )

    def test_health_orchestrator_has_get_recommended_template(self) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        from pathlib import Path

        orch = HealthOrchestrator(Path("."))
        assert hasattr(orch, "get_recommended_template"), (
            "HealthOrchestrator must expose get_recommended_template()"
        )
        template = orch.get_recommended_template()
        assert template == "maintenance/health-check-workflow", (
            f"HealthOrchestrator.get_recommended_template() returned '{template}'"
        )

    def test_vacuum_orchestrator_has_get_recommended_template(self) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        from pathlib import Path

        orch = VacuumOrchestrator(Path("."))
        assert hasattr(orch, "get_recommended_template"), (
            "VacuumOrchestrator must expose get_recommended_template()"
        )
        template = orch.get_recommended_template()
        assert template == "maintenance/vacuum-workflow", (
            f"VacuumOrchestrator.get_recommended_template() returned '{template}'"
        )
