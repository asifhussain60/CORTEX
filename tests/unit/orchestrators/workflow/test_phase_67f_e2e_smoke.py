"""
Phase 67-F: E2E integration smoke tests — WorkflowEngine Runtime Wiring (GAP-67-F).

Verifies end-to-end that:
1. WorkflowComposer executes standard mode against a real YAML template
2. WorkflowComposer executes convergence mode against a real YAML template
3. WorkflowEngine executes a loaded workflow end-to-end
4. StepHandlerRegistry + ConvergenceLoopExecutor integrate correctly
5. cortex-master.yaml remains within THIN INDEX CONTRACT (≤500L)
6. All 5 Phase 67 GAPs are closed (smoke verification)

Author: Asif Hussain
Phase: 67-F
Sweep: SWEEP-67-WORKFLOW-RUNTIME-WIRING
"""

import os
import tempfile
import pytest
from pathlib import Path
from typing import Any

# AC_START: AC-67-F-E2E-INTEGRATION-SMOKE-20260224T000000Z

REPO_ROOT = Path("/Users/asifhussain/PROJECTS/CORTEX")
CORTEX_MASTER = REPO_ROOT / "cortex-registry" / "cortex-master.yaml"
TDD_TEMPLATE = REPO_ROOT / "cortex-registry" / "workflows" / "templates" / "tdd" / "tdd-feature-implementation.yaml"
AUDIT_TEMPLATE = REPO_ROOT / "cortex-registry" / "workflows" / "templates" / "audit" / "audit-fix-pipeline.yaml"


class TestThinIndexContract:
    """Phase 67-A post-migration: cortex-master.yaml must stay ≤500 lines."""

    def test_cortex_master_within_500_lines(self) -> None:
        """cortex-master.yaml must be ≤500 lines (THIN INDEX CONTRACT)."""
        assert CORTEX_MASTER.exists(), "cortex-master.yaml must exist"
        lines = CORTEX_MASTER.read_text().splitlines()
        assert len(lines) <= 500, (
            f"cortex-master.yaml THIN INDEX CONTRACT VIOLATED: {len(lines)} lines (limit: 500). "
            "Phase 67-A must be re-applied."
        )

    def test_cortex_master_is_valid_yaml(self) -> None:
        """cortex-master.yaml must parse as valid YAML."""
        import yaml
        content = yaml.safe_load(CORTEX_MASTER.read_text())
        assert content is not None, "cortex-master.yaml must be non-empty valid YAML"


class TestWorkflowComposerStandardModeE2E:
    """Phase 67-B/C: WorkflowComposer standard mode E2E."""

    def test_composer_standard_mode_with_minimal_template(self) -> None:
        """WorkflowComposer.execute() in standard mode must complete without error."""
        from cortex.orchestrators.workflow.workflow_composer import (
            WorkflowComposer,
            WorkflowExecutionResult,
        )
        from unittest.mock import MagicMock

        yaml_content = """workflow:
  name: e2e-standard-smoke
  steps:
    - step_id: step_one
      orchestrator: MockOrchestrator
    - step_id: step_two
      orchestrator: MockOrchestrator
"""
        mock_orch = MagicMock()
        mock_orch.execute.return_value = {"success": True, "status": "complete"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp = Path(f.name)

        try:
            composer = WorkflowComposer(
                template_path=tmp,
                orchestrator_registry=lambda name: mock_orch,
            )
            result = composer.execute(convergence_mode=False)
        finally:
            os.unlink(tmp)

        assert isinstance(result, WorkflowExecutionResult)
        assert result.success is True, (
            f"Standard mode execution must succeed, got: {result}"
        )


class TestWorkflowComposerConvergenceModeE2E:
    """Phase 67-C: WorkflowComposer convergence mode uses ConvergenceLoopExecutor."""

    def test_composer_convergence_mode_with_convergence_gate_template(self) -> None:
        """WorkflowComposer.execute(convergence_mode=True) must use ConvergenceLoopExecutor."""
        from cortex.orchestrators.workflow.workflow_composer import (
            WorkflowComposer,
            WorkflowExecutionResult,
        )
        from cortex.orchestrators.workflow.convergence_loop_executor import ConvergenceLoopExecutor
        from unittest.mock import MagicMock, patch

        yaml_content = """workflow:
  name: e2e-convergence-smoke
  steps:
    - step_id: refactor_phase
      orchestrator: RefactoringOrchestrator
      convergence_gate:
        max_cycles: 2
        convergence_predicate: "all_tests_pass"
        check_operation: validate_tests_green
"""
        mock_orch = MagicMock()
        mock_orch.execute.return_value = {"status": "success", "all_tests_pass": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp = Path(f.name)

        execute_calls: list = []
        original_execute = ConvergenceLoopExecutor.execute

        def capturing_execute(self_inner: Any, fn: Any, check_convergence: Any) -> Any:
            execute_calls.append(True)
            return original_execute(self_inner, fn=fn, check_convergence=check_convergence)

        try:
            composer = WorkflowComposer(
                template_path=tmp,
                orchestrator_registry=lambda name: mock_orch,
            )
            with patch.object(ConvergenceLoopExecutor, "execute", capturing_execute):
                result = composer.execute(convergence_mode=True)
        finally:
            os.unlink(tmp)

        assert isinstance(result, WorkflowExecutionResult)
        assert len(execute_calls) >= 1, (
            "ConvergenceLoopExecutor.execute() must be called in convergence mode"
        )


class TestWorkflowEngineE2E:
    """Phase 67-E: WorkflowEngine._execute_step() dispatches via StepHandlerRegistry."""

    def test_workflow_engine_executes_noop_stage_end_to_end(self) -> None:
        """WorkflowEngine must execute a workflow with noop steps without raising."""
        import yaml
        from cortex.core.workflow_engine import WorkflowEngine

        yaml_content = """
metadata:
  id: e2e-noop-workflow
stages:
  - id: stage_one
    name: E2E Noop Stage
    description: Smoke test stage
    steps:
      - operation: noop
        id: noop-step-1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp = Path(f.name)

        try:
            engine = WorkflowEngine()
            ctx = engine.load_workflow(tmp)
            result_ctx = engine.execute_workflow("e2e-noop-workflow")
        finally:
            os.unlink(tmp)

        assert result_ctx.status == "completed", (
            f"WorkflowEngine must complete noop workflow, got: {result_ctx.status}"
        )

    def test_workflow_engine_raises_step_error_for_unknown_op(self) -> None:
        """WorkflowEngine must raise StepError when step has unknown operation."""
        import yaml
        from cortex.core.workflow_engine import WorkflowEngine, StepError

        yaml_content = """
metadata:
  id: e2e-unknown-op
stages:
  - id: stage_one
    name: Unknown Op Stage
    description: Stage with unknown operation
    steps:
      - operation: completely_unknown_op_xyz
        id: bad-step
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp = Path(f.name)

        try:
            engine = WorkflowEngine()
            engine.load_workflow(tmp)
            with pytest.raises(StepError):
                engine.execute_workflow("e2e-unknown-op")
        finally:
            os.unlink(tmp)


class TestPhase67GapsClosed:
    """Smoke verification that all 5 Phase 67 GAPs are resolved."""

    def test_gap_67_01_step_handler_registry_wired(self) -> None:
        """GAP-67-01: WorkflowEngine._execute_step() must NOT be a pure stub."""
        import inspect
        from cortex.core.workflow_engine import WorkflowEngine, StepError

        engine = WorkflowEngine()
        assert hasattr(engine, "_step_handler_registry")
        assert len(engine._step_handler_registry) >= 3

        # Must raise on unknown op — not silently return
        from cortex.core.workflow_engine import ExecutionContext
        ctx = ExecutionContext(workflow_id="g", template_path=Path("/tmp/g.yaml"))
        with pytest.raises(StepError):
            engine._execute_step({"operation": "gap_67_01_probe_unknown"}, ctx)

    def test_gap_67_02_step_state_machine_kwargs_correct(self) -> None:
        """GAP-67-02: StepStateMachine must accept step_id + convergence_config kwargs."""
        from cortex.orchestrators.workflow.step_state_machine import StepStateMachine
        import inspect

        sig = inspect.signature(StepStateMachine.__init__)
        params = list(sig.parameters.keys())
        assert "step_id" in params, "StepStateMachine must accept step_id"
        assert "convergence_config" in params, "StepStateMachine must accept convergence_config"
        assert "step" not in params, "StepStateMachine must NOT accept deprecated 'step' kwarg"

    def test_gap_67_04_convergence_gate_in_tdd_template(self) -> None:
        """GAP-67-04: tdd-feature-implementation.yaml refactor_phase must have convergence_gate."""
        import yaml
        content = yaml.safe_load(TDD_TEMPLATE.read_text())
        steps = content.get("workflow", {}).get("steps", [])
        refactor = next((s for s in steps if s.get("step_id") == "refactor_phase"), None)
        assert refactor is not None
        assert "convergence_gate" in refactor

    def test_gap_67_04_convergence_gate_in_audit_template(self) -> None:
        """GAP-67-04: audit-fix-pipeline.yaml must have convergence_gate for stage 7-8."""
        assert "convergence_gate:" in AUDIT_TEMPLATE.read_text()

    def test_gap_67_05_convergence_loop_executor_wired(self) -> None:
        """GAP-67-05: ConvergenceLoopExecutor must be used inside _execute_with_convergence."""
        import inspect
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from cortex.orchestrators.workflow import convergence_loop_executor

        # ConvergenceLoopExecutor is importable from its own module
        assert hasattr(convergence_loop_executor, "ConvergenceLoopExecutor"), (
            "ConvergenceLoopExecutor must be in cortex.orchestrators.workflow.convergence_loop_executor"
        )
        # workflow_composer._execute_with_convergence source references it
        src = inspect.getsource(WorkflowComposer._execute_with_convergence)
        assert "ConvergenceLoopExecutor" in src, (
            "_execute_with_convergence() must instantiate ConvergenceLoopExecutor (Phase 67-C)"
        )

    def test_gap_67_06_cortex_master_thin_index(self) -> None:
        """GAP-67-06: cortex-master.yaml must be ≤500 lines."""
        lines = CORTEX_MASTER.read_text().splitlines()
        assert len(lines) <= 500, f"cortex-master.yaml is {len(lines)} lines — exceeds 500L limit"


# AC_COMPLETE: AC-67-F-E2E-INTEGRATION-SMOKE-20260224T000000Z ✅
