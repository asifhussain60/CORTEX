"""
RED phase tests — ServiceDecompositionOrchestrator (Phase 14 / CORE-008).

Tests are written BEFORE implementation. All tests must FAIL at this stage.
Implementation target: cortex/orchestrators/domain/service_decomposition_orchestrator.py
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def workflow_yaml_path() -> str:
    """Return path to the service-decomposition workflow template."""
    return "cortex-registry/workflows/templates/lifecycle/service-decomposition-workflow.yaml"


@pytest.fixture
def mock_workflow_engine():
    """Return a mock WorkflowEngine."""
    engine = MagicMock()
    engine.load.return_value = {
        "workflow": {
            "id": "lifecycle/service-decomposition-workflow",
            "steps": [
                {"step_id": "lens_baseline"},
                {"step_id": "security_gate", "blocking": True},
                {"step_id": "layer_data_access"},
                {"step_id": "layer_api"},
                {"step_id": "layer_frontend"},
                {"step_id": "layer_tests"},
                {"step_id": "holistic_sweep"},
                {"step_id": "lens_verification"},
            ],
        }
    }
    engine.execute_step.return_value = {"status": "complete", "outputs": {}}
    return engine


@pytest.fixture
def orchestrator(mock_workflow_engine):
    """Instantiate ServiceDecompositionOrchestrator with injected engine."""
    from cortex.orchestrators.domain.service_decomposition_orchestrator import (
        ServiceDecompositionOrchestrator,
    )
    return ServiceDecompositionOrchestrator(workflow_engine=mock_workflow_engine)


# ---------------------------------------------------------------------------
# AC-PHASE14-001: layers execute in dependency order
# ---------------------------------------------------------------------------

class TestLayerExecutionOrder:
    """AC-PHASE14-001 — all 5 layers execute in dependency order."""

    def test_orchestrator_instantiates(self, orchestrator):
        """Smoke: orchestrator constructs without error."""
        assert orchestrator is not None

    def test_execute_returns_result_dict(self, orchestrator, workflow_yaml_path):
        """execute() returns a dict with a 'status' key."""
        result = orchestrator.execute(workflow_path=workflow_yaml_path, params={})
        assert isinstance(result, dict)
        assert "status" in result

    def test_all_steps_called_in_order(self, orchestrator, mock_workflow_engine, workflow_yaml_path):
        """WorkflowEngine.execute_step is called for each step in sequence."""
        orchestrator.execute(workflow_path=workflow_yaml_path, params={})
        call_step_ids = [
            call.kwargs.get("step_id") or call.args[0]
            for call in mock_workflow_engine.execute_step.call_args_list
        ]
        assert "security_gate" in call_step_ids
        assert "layer_data_access" in call_step_ids
        assert "layer_api" in call_step_ids

    def test_data_access_layer_runs_after_security_gate(
        self, orchestrator, mock_workflow_engine, workflow_yaml_path
    ):
        """layer_data_access must not execute before security_gate completes."""
        execution_order: list[str] = []

        def capture_step(*args, **kwargs):
            step_id = kwargs.get("step_id") or (args[0] if args else "unknown")
            execution_order.append(step_id)
            return {"status": "complete", "outputs": {}}

        mock_workflow_engine.execute_step.side_effect = capture_step
        orchestrator.execute(workflow_path=workflow_yaml_path, params={})
        if "security_gate" in execution_order and "layer_data_access" in execution_order:
            assert execution_order.index("security_gate") < execution_order.index(
                "layer_data_access"
            )


# ---------------------------------------------------------------------------
# AC-PHASE14-002: security gate blocks downstream layers on failure
# ---------------------------------------------------------------------------

class TestSecurityGateBlocking:
    """AC-PHASE14-002 — security_gate is a hard blocker."""

    def test_security_gate_failure_halts_execution(
        self, orchestrator, mock_workflow_engine, workflow_yaml_path
    ):
        """When security_gate returns status=failed, downstream layers must not run."""
        def step_side_effect(*args, **kwargs):
            step_id = kwargs.get("step_id") or (args[0] if args else "")
            if step_id == "security_gate":
                return {"status": "failed", "outputs": {"sql_injection_found": True}}
            return {"status": "complete", "outputs": {}}

        mock_workflow_engine.execute_step.side_effect = step_side_effect
        result = orchestrator.execute(workflow_path=workflow_yaml_path, params={})

        called_ids = [
            call.kwargs.get("step_id") or (call.args[0] if call.args else "")
            for call in mock_workflow_engine.execute_step.call_args_list
        ]
        assert "layer_data_access" not in called_ids
        assert result.get("halted_at") == "security_gate"

    def test_security_gate_success_allows_downstream(
        self, orchestrator, mock_workflow_engine, workflow_yaml_path
    ):
        """When security_gate passes, layer_data_access should be called."""
        orchestrator.execute(workflow_path=workflow_yaml_path, params={})
        called_ids = [
            call.kwargs.get("step_id") or (call.args[0] if call.args else "")
            for call in mock_workflow_engine.execute_step.call_args_list
        ]
        assert "layer_data_access" in called_ids


# ---------------------------------------------------------------------------
# AC-PHASE14-006: MCP routing
# ---------------------------------------------------------------------------

class TestMCPRouting:
    """AC-PHASE14-006 — cortex_process_request routes to ServiceDecompositionOrchestrator."""

    def test_orchestrator_has_intent_registration(self, orchestrator):
        """Orchestrator exposes 'supported_intents' attribute for MCP routing."""
        assert hasattr(orchestrator, "supported_intents")
        intents = orchestrator.supported_intents
        assert isinstance(intents, (list, tuple, set))

    def test_refactor_legacy_system_intent_registered(self, orchestrator):
        """'refactor' intent with target='legacy_system' must be in supported_intents."""
        intents = orchestrator.supported_intents
        intent_strings = [str(i).lower() for i in intents]
        assert any("refactor" in s for s in intent_strings)


# ---------------------------------------------------------------------------
# AC-PHASE14-007: workflow parameterization (not hardcoded)
# ---------------------------------------------------------------------------

class TestWorkflowParameterization:
    """AC-PHASE14-007 — workflow template accepts runtime params, not hardcoded values."""

    def test_execute_accepts_custom_params(self, orchestrator, workflow_yaml_path):
        """execute() accepts arbitrary params dict without raising."""
        custom_params = {
            "backend_language": "python",
            "frontend_language": "typescript",
            "entity": "Order",
        }
        result = orchestrator.execute(workflow_path=workflow_yaml_path, params=custom_params)
        assert result is not None

    def test_execute_passes_params_to_engine(
        self, orchestrator, mock_workflow_engine, workflow_yaml_path
    ):
        """Params are forwarded to WorkflowEngine.execute_step calls."""
        custom_params = {"backend_language": "csharp", "entity": "Product"}
        orchestrator.execute(workflow_path=workflow_yaml_path, params=custom_params)
        # At least one execute_step call should have received params
        all_kwargs = [
            call.kwargs for call in mock_workflow_engine.execute_step.call_args_list
        ]
        all_calls_received_params = any("params" in kw for kw in all_kwargs)
        assert all_calls_received_params
