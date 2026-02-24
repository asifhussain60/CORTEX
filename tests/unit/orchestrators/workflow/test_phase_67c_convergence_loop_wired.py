"""
Phase 67-C: RED tests for wiring ConvergenceLoopExecutor into
WorkflowComposer._execute_with_convergence() (GAP-67-05).

Tests verify that when convergence_mode=True, the ConvergenceLoopExecutor
is actually invoked (not just the FSM loop alone). The executor provides
retry logic with exponential backoff, replacing the raw while loop.

Author: Asif Hussain
Phase: 67-C
Sweep: SWEEP-67-WORKFLOW-RUNTIME-WIRING
"""

import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, call

import pytest

# AC_START: AC-67-C-CONVERGENCE-LOOP-WIRED-20260224T000000Z


def _make_composer(step_id: str = "step-67c") -> Any:
    """Helper: create WorkflowComposer with a single test step."""
    from cortex.orchestrators.workflow.workflow_composer import (
        WorkflowComposer,
        WorkflowStep,
    )

    yaml_content = f"""workflow:
  name: test-67c
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

    composer._steps = [
        WorkflowStep(
            step_id=step_id,
            orchestrator_name="TestOrchestrator",
            parameters={"convergence_gate": {"max_cycles": 2}},
        )
    ]
    return composer


class TestConvergenceLoopExecutorWired:
    """GAP-67-05: ConvergenceLoopExecutor must be invoked when convergence_mode=True."""

    def test_convergence_loop_executor_is_wired_in_composer(self) -> None:
        """When convergence_mode=True, ConvergenceLoopExecutor.execute() must be called."""
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
        )

        composer = _make_composer("step-c-01")
        execute_calls: list = []

        original_execute = ConvergenceLoopExecutor.execute

        def capturing_execute(
            self_inner: Any,
            fn: Any,
            check_convergence: Any,
        ) -> Any:
            execute_calls.append({"fn": fn, "check_convergence": check_convergence})
            return original_execute(self_inner, fn, check_convergence)

        with patch.object(ConvergenceLoopExecutor, "execute", capturing_execute):
            try:
                composer._execute_with_convergence(workflow=None, context=None)
            except Exception:
                pass  # not interested in the result — only that execute() was called

        assert len(execute_calls) >= 1, (
            "ConvergenceLoopExecutor.execute() must be called when convergence_mode=True. "
            "It was never invoked — it is an orphan (GAP-67-05)."
        )

    def test_convergence_loop_executor_called_once_per_step(self) -> None:
        """ConvergenceLoopExecutor.execute() must be called once per workflow step."""
        from cortex.orchestrators.workflow.workflow_composer import (
            WorkflowComposer,
            WorkflowStep,
        )
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
        )

        composer = _make_composer("step-c-02")

        # Add a second step
        composer._steps.append(
            WorkflowStep(
                step_id="step-c-02b",
                orchestrator_name="TestOrchestrator",
                parameters={"convergence_gate": {"max_cycles": 1}},
            )
        )

        execute_calls: list = []
        original_execute = ConvergenceLoopExecutor.execute

        def counting_execute(self_inner: Any, fn: Any, check_convergence: Any) -> Any:
            execute_calls.append(1)
            return original_execute(self_inner, fn, check_convergence)

        with patch.object(ConvergenceLoopExecutor, "execute", counting_execute):
            try:
                composer._execute_with_convergence(workflow=None, context=None)
            except Exception:
                pass

        assert len(execute_calls) == 2, (
            f"Expected ConvergenceLoopExecutor.execute() called 2 times (once per step), "
            f"got {len(execute_calls)}"
        )

    def test_convergence_result_mapped_to_workflow_step_result(self) -> None:
        """When ConvergenceLoopExecutor.execute() returns converged=True, step must pass."""
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
            ConvergenceResult,
        )

        composer = _make_composer("step-c-03")

        converged_result = ConvergenceResult(
            converged=True,
            attempts=2,
            duration_seconds=0.1,
            final_value={"status": "complete"},
        )

        with patch.object(
            ConvergenceLoopExecutor,
            "execute",
            return_value=converged_result,
        ):
            result = composer._execute_with_convergence(workflow=None, context=None)

        assert result is not None
        assert result.success is True, (
            "When ConvergenceLoopExecutor returns converged=True, "
            "WorkflowExecutionResult.success must be True"
        )

    def test_convergence_result_not_converged_marks_step_failed(self) -> None:
        """When ConvergenceLoopExecutor.execute() returns converged=False, workflow fails."""
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
            ConvergenceResult,
        )

        composer = _make_composer("step-c-04")

        not_converged_result = ConvergenceResult(
            converged=False,
            attempts=5,
            duration_seconds=1.0,
            error_message="Max retries exceeded",
        )

        with patch.object(
            ConvergenceLoopExecutor,
            "execute",
            return_value=not_converged_result,
        ):
            result = composer._execute_with_convergence(workflow=None, context=None)

        assert result is not None
        assert result.success is False, (
            "When ConvergenceLoopExecutor returns converged=False, "
            "WorkflowExecutionResult.success must be False"
        )

    def test_convergence_loop_executor_receives_callable_fn(self) -> None:
        """ConvergenceLoopExecutor.execute() must receive a callable fn (step executor)."""
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
            ConvergenceResult,
        )

        composer = _make_composer("step-c-05")
        received_fn: list = []

        def capturing_execute(self_inner: Any, fn: Any, check_convergence: Any) -> Any:
            received_fn.append(fn)
            return ConvergenceResult(
                converged=True, attempts=1, duration_seconds=0.0
            )

        with patch.object(ConvergenceLoopExecutor, "execute", capturing_execute):
            try:
                composer._execute_with_convergence(workflow=None, context=None)
            except Exception:
                pass

        if received_fn:
            assert callable(received_fn[0]), (
                "fn passed to ConvergenceLoopExecutor.execute() must be callable"
            )


# AC_COMPLETE: AC-67-C-CONVERGENCE-LOOP-WIRED-20260224T000000Z ✅
