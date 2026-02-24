"""
Phase 67-B: RED tests for WorkflowComposer._execute_with_convergence() StepStateMachine
constructor kwargs fix (GAP-67-02) and AutonomousWorkflowExecutor alignment (GAP-67-03).

Tests verify that StepStateMachine is instantiated with the correct constructor signature:
    StepStateMachine(step_id: str, convergence_config: ConvergenceGateConfig, convergence_neuron=None)

NOT the broken form:
    StepStateMachine(step=step.parameters, convergence_config=..., neuron=None)

Author: Asif Hussain
Phase: 67-B
Sweep: SWEEP-67-WORKFLOW-RUNTIME-WIRING
"""

import pytest
from unittest.mock import MagicMock, patch, call
from typing import Any, Dict

# AC_START: AC-67-B-CONVERGENCE-KWARGS-20260224T000000Z


class TestStepStateMachineConstructorSignature:
    """GAP-67-02: Verify StepStateMachine accepts correct constructor params."""

    def test_step_state_machine_accepts_step_id_kwarg(self) -> None:
        """StepStateMachine must accept step_id (str), not step (dict)."""
        from cortex.orchestrators.workflow.step_state_machine import (
            StepStateMachine,
            ConvergenceGateConfig,
        )
        config = ConvergenceGateConfig(
            max_cycles=3,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="none",
        )
        # Should NOT raise TypeError — step_id is the correct kwarg
        fsm = StepStateMachine(step_id="step-001", convergence_config=config)
        assert fsm.step_id == "step-001"

    def test_step_state_machine_rejects_wrong_step_kwarg(self) -> None:
        """StepStateMachine must reject 'step' kwarg (old broken form)."""
        from cortex.orchestrators.workflow.step_state_machine import (
            StepStateMachine,
            ConvergenceGateConfig,
        )
        config = ConvergenceGateConfig(
            max_cycles=3,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="none",
        )
        with pytest.raises(TypeError):
            StepStateMachine(
                step={"operation": "noop"},  # wrong kwarg
                convergence_config=config,
                neuron=None,  # wrong kwarg
            )

    def test_step_state_machine_rejects_neuron_kwarg(self) -> None:
        """StepStateMachine must reject 'neuron' kwarg — correct is 'convergence_neuron'."""
        from cortex.orchestrators.workflow.step_state_machine import (
            StepStateMachine,
            ConvergenceGateConfig,
        )
        config = ConvergenceGateConfig(
            max_cycles=3,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="none",
        )
        with pytest.raises(TypeError):
            StepStateMachine(
                step_id="step-001",
                convergence_config=config,
                neuron=None,  # wrong kwarg; correct is convergence_neuron
            )

    def test_step_state_machine_accepts_convergence_neuron_kwarg(self) -> None:
        """StepStateMachine must accept 'convergence_neuron' (not 'neuron')."""
        from cortex.orchestrators.workflow.step_state_machine import (
            StepStateMachine,
            ConvergenceGateConfig,
        )
        config = ConvergenceGateConfig(
            max_cycles=3,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="none",
        )
        fsm = StepStateMachine(
            step_id="step-002",
            convergence_config=config,
            convergence_neuron=None,
        )
        assert fsm.step_id == "step-002"
        assert fsm.convergence_neuron is None


class TestWorkflowComposerConvergenceKwargs:
    """GAP-67-02: Verify WorkflowComposer._execute_with_convergence() uses correct kwargs."""

    def _make_composer_with_steps(self, step_id: str = "step-test") -> Any:
        """Build a WorkflowComposer with pre-loaded steps via a temp YAML template."""
        import tempfile
        import os
        from pathlib import Path
        from cortex.orchestrators.workflow.workflow_composer import (
            WorkflowComposer,
            WorkflowStep,
        )

        yaml_content = f"""workflow:
  name: test-workflow
  steps:
    - step_id: {step_id}
      orchestrator: TestOrchestrator
"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        tmp.write(yaml_content)
        tmp.flush()
        tmp.close()
        template = Path(tmp.name)

        try:
            composer = WorkflowComposer(template_path=template)
        finally:
            os.unlink(tmp.name)

        # Override steps with convergence_gate params for the test
        composer._steps = [
            WorkflowStep(
                step_id=step_id,
                orchestrator_name="TestOrchestrator",
                parameters={"convergence_gate": {"max_cycles": 2}},
            )
        ]
        return composer

    def test_execute_with_convergence_creates_fsm_with_step_id(self) -> None:
        """_execute_with_convergence() must pass step_id=step.step_id to StepStateMachine."""
        from cortex.orchestrators.workflow.step_state_machine import StepStateMachine

        composer = self._make_composer_with_steps("step-test")
        captured_calls: list = []

        original_init = StepStateMachine.__init__

        def capturing_init(self_inner: Any, **kwargs: Any) -> None:
            captured_calls.append(dict(kwargs))
            original_init(self_inner, **kwargs)

        with patch.object(StepStateMachine, "__init__", capturing_init):
            try:
                composer._execute_with_convergence(workflow=None, context=None)
            except Exception:
                pass  # We only care about the constructor kwargs

        assert len(captured_calls) >= 1, "StepStateMachine was never instantiated"
        first_call = captured_calls[0]
        assert "step_id" in first_call, (
            f"StepStateMachine must be called with step_id=, got: {list(first_call.keys())}"
        )
        assert "step" not in first_call, (
            "StepStateMachine must NOT be called with step= (broken kwarg)"
        )
        assert "neuron" not in first_call, (
            "StepStateMachine must NOT be called with neuron= (broken kwarg); use convergence_neuron="
        )

    def test_execute_with_convergence_step_id_matches_workflow_step(self) -> None:
        """The step_id passed to StepStateMachine must equal the WorkflowStep.step_id."""
        from cortex.orchestrators.workflow.step_state_machine import StepStateMachine

        composer = self._make_composer_with_steps("my-unique-step-id")
        captured_step_ids: list = []

        original_init = StepStateMachine.__init__

        def capturing_init(self_inner: Any, step_id: str = "", **kwargs: Any) -> None:
            captured_step_ids.append(step_id)
            original_init(self_inner, step_id=step_id, **kwargs)

        with patch.object(StepStateMachine, "__init__", capturing_init):
            try:
                composer._execute_with_convergence(workflow=None, context=None)
            except Exception:
                pass

        if captured_step_ids:
            assert captured_step_ids[0] == "my-unique-step-id", (
                f"step_id must be 'my-unique-step-id', got '{captured_step_ids[0]}'"
            )


class TestAutonomousWorkflowExecutorAlignment:
    """GAP-67-03: Verify AutonomousWorkflowExecutor StepStateMachine usage is aligned."""

    def test_autonomous_executor_imports_step_state_machine(self) -> None:
        """AutonomousWorkflowExecutor must import StepStateMachine without errors."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )
        executor = AutonomousWorkflowExecutor()
        assert executor is not None

    def test_autonomous_executor_convergence_gate_uses_max_cycles(self) -> None:
        """_execute_with_convergence_gate must respect max_cycles from step config."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        step = {"convergence_gate": {"max_cycles": 3}}

        call_count = 0

        def always_failing() -> bool:
            nonlocal call_count
            call_count += 1
            return False

        cycles = executor._execute_with_convergence_gate(step, always_failing)
        assert cycles == 3, f"Expected max_cycles=3, got {cycles}"
        assert call_count == 3, f"Expected 3 calls to convergence_check, got {call_count}"

    def test_autonomous_executor_convergence_gate_stops_on_success(self) -> None:
        """_execute_with_convergence_gate must stop when convergence_check returns True."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        step = {"convergence_gate": {"max_cycles": 10}}

        call_count = 0

        def succeeds_on_third_call() -> bool:
            nonlocal call_count
            call_count += 1
            return call_count >= 3

        cycles = executor._execute_with_convergence_gate(step, succeeds_on_third_call)
        assert cycles == 3, f"Expected convergence on cycle 3, got cycle {cycles}"


# AC_COMPLETE: AC-67-B-CONVERGENCE-KWARGS-20260224T000000Z ✅
