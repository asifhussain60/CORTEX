"""
Phase 64-C Golden Tests: Workflow Runtime Execution.

Authority: Phase 64 sub-phase 64-C — AC-64-01-A/B/C
Closes: GAP-64-01 (Workflow template runtime never executed in golden tests)

Contract:
  - StepStateMachine FSM traversal verified at golden tier (AC-64-01-A)
  - ConvergenceLoopExecutor convergence loop verified — terminates at p0=0, p1=0 (AC-64-01-B)
  - workflow_runs DDL schema contract verified from detect-fix-rescan-loop YAML (AC-64-01-C)

Architecture note:
  StepStateMachine: FSM-based step execution (states: PENDING → RUNNING → CHECKING → PASSED|RETRYING|FAILED|SKIPPED)
  ConvergenceLoopExecutor: retry loop with exponential backoff, convergence predicate
  workflow_runs: SQLite schema defined in cortex-registry/workflows/templates/primitives/validation/
                 detect-fix-rescan-loop.yaml — not yet written by Python code, so verified as data contract

CORE-008: Tests written BEFORE implementation (RED → GREEN → REFACTOR).

AC_START: AC-64-C-GOLDEN-001
"""
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import pytest
import yaml

from cortex.orchestrators.workflow.step_state_machine import (
    ConvergenceGateConfig,
    StepState,
    StepStateMachine,
)
from cortex.orchestrators.workflow.convergence_loop_executor import (
    ConvergenceConfig,
    ConvergenceLoopExecutor,
    ConvergenceResult,
)

# ---------------------------------------------------------------------------
# AC-64-01-A: StepStateMachine FSM traversal golden tests
# ---------------------------------------------------------------------------

_DETECT_FIX_RESCAN_YAML = (
    Path(__file__).parents[3]
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "primitives"
    / "validation"
    / "detect-fix-rescan-loop.yaml"
)


def _make_config(max_cycles: int = 3) -> ConvergenceGateConfig:
    """Helper: build a minimal ConvergenceGateConfig."""
    return ConvergenceGateConfig(
        max_cycles=max_cycles,
        success_criteria={"done": True},
        convergence_predicate="done",
        scan_function="check_done",
        backoff_strategy="none",
    )


class TestStepStateMachineExecution:
    """
    AC-64-01-A: StepStateMachine transitions PENDING → RUNNING → CHECKING → PASSED.

    Verifies the full happy-path FSM traversal and retry path without external deps.
    """

    def test_initial_state_is_pending(self) -> None:
        """StepStateMachine starts in PENDING state."""
        fsm = StepStateMachine(step_id="init-test", convergence_config=_make_config())
        assert fsm.state == StepState.PENDING.value, (
            f"Expected initial state PENDING, got {fsm.state}"
        )

    def test_start_transitions_pending_to_running(self) -> None:
        """AC-64-01-A: start() transitions PENDING → RUNNING."""
        fsm = StepStateMachine(step_id="start-test", convergence_config=_make_config())
        fsm.start()
        assert fsm.state == StepState.RUNNING.value, (
            f"Expected RUNNING after start(), got {fsm.state}"
        )

    def test_check_transitions_running_to_checking(self) -> None:
        """AC-64-01-A: check() transitions RUNNING → CHECKING."""
        fsm = StepStateMachine(step_id="check-test", convergence_config=_make_config())
        fsm.start()
        fsm.check()
        assert fsm.state == StepState.CHECKING.value, (
            f"Expected CHECKING after check(), got {fsm.state}"
        )

    def test_pass_gate_transitions_checking_to_passed(self) -> None:
        """AC-64-01-A: pass_gate() transitions CHECKING → PASSED."""
        fsm = StepStateMachine(step_id="pass-test", convergence_config=_make_config())
        fsm.start()
        fsm.check()
        fsm.pass_gate()
        assert fsm.state == StepState.PASSED.value, (
            f"Expected PASSED after pass_gate(), got {fsm.state}"
        )

    def test_full_happy_path_pending_to_passed(self) -> None:
        """AC-64-01-A: full FSM traversal PENDING → RUNNING → CHECKING → PASSED in one sequence."""
        fsm = StepStateMachine(step_id="happy-path", convergence_config=_make_config())

        assert fsm.state == StepState.PENDING.value
        fsm.start()
        assert fsm.state == StepState.RUNNING.value
        fsm.check()
        assert fsm.state == StepState.CHECKING.value
        converged = fsm._check_convergence({"done": True})
        assert converged, "Default convergence check must return True"
        fsm.pass_gate()
        assert fsm.state == StepState.PASSED.value
        assert fsm.cycle_count == 0, f"No retries expected, got cycle_count={fsm.cycle_count}"

    def test_retry_increments_cycle_count(self) -> None:
        """AC-64-01-A: retry() increments cycle_count and transitions CHECKING → RETRYING."""
        fsm = StepStateMachine(step_id="retry-test", convergence_config=_make_config(max_cycles=3))
        fsm.start()
        fsm.check()
        fsm.retry()
        assert fsm.state == StepState.RETRYING.value
        assert fsm.cycle_count == 1, f"Expected cycle_count=1, got {fsm.cycle_count}"

    def test_re_execute_transitions_retrying_to_running(self) -> None:
        """AC-64-01-A: re_execute() transitions RETRYING → RUNNING for next iteration."""
        fsm = StepStateMachine(step_id="reexec-test", convergence_config=_make_config())
        fsm.start()
        fsm.check()
        fsm.retry()
        assert fsm.state == StepState.RETRYING.value
        fsm.re_execute()
        assert fsm.state == StepState.RUNNING.value

    def test_fail_transitions_checking_to_failed(self) -> None:
        """AC-64-01-A: fail() transitions CHECKING → FAILED (max_cycles exceeded)."""
        fsm = StepStateMachine(step_id="fail-test", convergence_config=_make_config(max_cycles=1))
        fsm.start()
        fsm.check()
        fsm.fail()
        assert fsm.state == StepState.FAILED.value

    def test_skip_transitions_pending_to_skipped(self) -> None:
        """AC-64-01-A: skip() transitions PENDING → SKIPPED (optional step)."""
        fsm = StepStateMachine(step_id="skip-test", convergence_config=_make_config())
        fsm.skip()
        assert fsm.state == StepState.SKIPPED.value

    def test_should_retry_under_max_cycles(self) -> None:
        """AC-64-01-A: should_retry() returns True when cycle_count < max_cycles."""
        fsm = StepStateMachine(step_id="retry-check", convergence_config=_make_config(max_cycles=3))
        assert fsm.should_retry() is True, "should_retry must be True at cycle_count=0, max_cycles=3"
        fsm.start()
        fsm.check()
        fsm.retry()
        assert fsm.should_retry() is True, "should_retry must be True at cycle_count=1, max_cycles=3"

    def test_should_retry_false_at_max_cycles(self) -> None:
        """AC-64-01-A: should_retry() returns False when cycle_count >= max_cycles."""
        fsm = StepStateMachine(step_id="max-cycles", convergence_config=_make_config(max_cycles=1))
        fsm.start()
        fsm.check()
        fsm.retry()
        assert fsm.should_retry() is False, (
            f"should_retry must be False at cycle_count=1, max_cycles=1. Got: {fsm.should_retry()}"
        )

    def test_retry_then_converge_full_path(self) -> None:
        """AC-64-01-A: full retry path — RUNNING→CHECKING→RETRYING→RUNNING→CHECKING→PASSED."""
        fsm = StepStateMachine(step_id="retry-converge", convergence_config=_make_config(max_cycles=3))
        # Iteration 1 — not converged
        fsm.start()
        fsm.check()
        fsm.retry()
        fsm.re_execute()
        assert fsm.state == StepState.RUNNING.value
        assert fsm.cycle_count == 1
        # Iteration 2 — converged
        fsm.check()
        fsm.pass_gate()
        assert fsm.state == StepState.PASSED.value
        assert fsm.cycle_count == 1  # only 1 retry was needed

    def test_backoff_delay_none_strategy(self) -> None:
        """AC-64-01-A: 'none' backoff strategy returns 0.0 delay."""
        config = ConvergenceGateConfig(
            max_cycles=3,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="none",
        )
        fsm = StepStateMachine(step_id="backoff-none", convergence_config=config)
        assert fsm.get_backoff_delay() == 0.0

    def test_backoff_delay_linear_strategy(self) -> None:
        """AC-64-01-A: 'linear' backoff strategy returns cycle_count as delay."""
        config = ConvergenceGateConfig(
            max_cycles=5,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="linear",
        )
        fsm = StepStateMachine(step_id="backoff-linear", convergence_config=config)
        fsm.start()
        fsm.check()
        fsm.retry()
        assert fsm.get_backoff_delay() == 1.0, f"Linear backoff at cycle 1 must be 1.0"

    def test_backoff_delay_exponential_strategy(self) -> None:
        """AC-64-01-A: 'exponential' backoff strategy returns 2^cycle_count."""
        config = ConvergenceGateConfig(
            max_cycles=5,
            success_criteria={},
            convergence_predicate="",
            scan_function="",
            backoff_strategy="exponential",
        )
        fsm = StepStateMachine(step_id="backoff-exp", convergence_config=config)
        assert fsm.get_backoff_delay() == 1.0  # 2^0
        fsm.start()
        fsm.check()
        fsm.retry()
        assert fsm.get_backoff_delay() == 2.0  # 2^1


# ---------------------------------------------------------------------------
# AC-64-01-B: ConvergenceLoopExecutor — convergence loop terminates at p0=0, p1=0
# ---------------------------------------------------------------------------


class TestConvergenceLoopExecutor:
    """
    AC-64-01-B: ConvergenceLoopExecutor converges when p0=0 and p1=0.

    Verifies the detect→fix→rescan pattern terminates without infinite loops.
    """

    def _make_executor(self, max_retries: int = 5) -> ConvergenceLoopExecutor:
        """Helper: create executor with zero backoff for fast tests."""
        return ConvergenceLoopExecutor(
            ConvergenceConfig(
                max_retries=max_retries,
                initial_backoff_seconds=0.0,
                backoff_multiplier=1.0,
            )
        )

    def test_converges_immediately_when_p0_and_p1_are_zero(self) -> None:
        """AC-64-01-B: converges on first attempt when p0=0, p1=0."""
        executor = self._make_executor()

        def scan() -> Dict[str, int]:
            return {"p0_count": 0, "p1_count": 0}

        result = executor.execute(
            fn=scan,
            check_convergence=lambda v: v["p0_count"] == 0 and v["p1_count"] == 0,
        )
        assert result.converged is True, "Must converge immediately when p0=0, p1=0"
        assert result.attempts == 1, f"Expected 1 attempt, got {result.attempts}"
        assert result.final_value == {"p0_count": 0, "p1_count": 0}

    def test_converges_after_reducing_violations(self) -> None:
        """AC-64-01-B: converges after violations are fixed across iterations."""
        executor = self._make_executor(max_retries=5)
        violations = [3]  # Start with 3 violations, reduce by 1 each scan

        def scan() -> Dict[str, int]:
            violations[0] = max(0, violations[0] - 1)
            return {"p0_count": violations[0], "p1_count": 0}

        result = executor.execute(
            fn=scan,
            check_convergence=lambda v: v["p0_count"] == 0,
        )
        assert result.converged is True, f"Must converge after fixing violations. Got: {result}"
        assert result.attempts == 3, f"Expected 3 attempts (3 violations → 2 → 1 → 0), got {result.attempts}"

    def test_does_not_loop_infinitely_when_max_retries_exceeded(self) -> None:
        """AC-64-01-B: stops at max_retries without infinite loop."""
        executor = self._make_executor(max_retries=3)
        call_count = [0]

        def scan() -> Dict[str, int]:
            call_count[0] += 1
            return {"p0_count": 1, "p1_count": 0}  # Never converges

        result = executor.execute(
            fn=scan,
            check_convergence=lambda v: v["p0_count"] == 0,
        )
        assert result.converged is False, "Must not converge when violations persist"
        assert call_count[0] == 3, f"Must stop at max_retries=3. Called {call_count[0]} times"
        assert result.attempts == 3

    def test_result_has_required_fields(self) -> None:
        """AC-64-01-B: ConvergenceResult has all required fields."""
        executor = self._make_executor()
        result = executor.execute(fn=lambda: 42, check_convergence=lambda v: v == 42)
        assert isinstance(result, ConvergenceResult)
        assert hasattr(result, "converged")
        assert hasattr(result, "attempts")
        assert hasattr(result, "duration_seconds")
        assert hasattr(result, "final_value")
        assert hasattr(result, "error_message")

    def test_duration_seconds_is_non_negative(self) -> None:
        """AC-64-01-B: duration_seconds is always non-negative."""
        executor = self._make_executor()
        result = executor.execute(fn=lambda: None, check_convergence=lambda v: True)
        assert result.duration_seconds >= 0.0, (
            f"duration_seconds must be ≥ 0. Got: {result.duration_seconds}"
        )

    def test_backoff_calculation_is_exponential(self) -> None:
        """AC-64-01-B: _calculate_backoff returns exponentially increasing delays."""
        executor = ConvergenceLoopExecutor(
            ConvergenceConfig(
                max_retries=5,
                initial_backoff_seconds=1.0,
                backoff_multiplier=2.0,
                max_backoff_seconds=60.0,
            )
        )
        assert executor._calculate_backoff(1) == 1.0   # 1.0 * 2^0
        assert executor._calculate_backoff(2) == 2.0   # 1.0 * 2^1
        assert executor._calculate_backoff(3) == 4.0   # 1.0 * 2^2
        assert executor._calculate_backoff(4) == 8.0   # 1.0 * 2^3

    def test_backoff_capped_at_max_backoff(self) -> None:
        """AC-64-01-B: backoff does not exceed max_backoff_seconds."""
        executor = ConvergenceLoopExecutor(
            ConvergenceConfig(
                max_retries=10,
                initial_backoff_seconds=1.0,
                backoff_multiplier=2.0,
                max_backoff_seconds=5.0,
            )
        )
        # After many retries, backoff should be capped at 5.0
        assert executor._calculate_backoff(10) == 5.0, (
            f"Backoff must be capped at max_backoff_seconds=5.0, got {executor._calculate_backoff(10)}"
        )

    def test_convergence_loop_emits_final_value(self) -> None:
        """AC-64-01-B: final_value is the last scan result on convergence."""
        executor = self._make_executor()
        scan_results = [{"p0_count": 2}, {"p0_count": 0}]
        call_idx = [0]

        def scan() -> Dict[str, int]:
            val = scan_results[min(call_idx[0], len(scan_results) - 1)]
            call_idx[0] += 1
            return val

        result = executor.execute(fn=scan, check_convergence=lambda v: v["p0_count"] == 0)
        assert result.converged is True
        assert result.final_value == {"p0_count": 0}, (
            f"final_value must be the converged scan result. Got: {result.final_value}"
        )

    def test_single_retry_then_converge_pattern(self) -> None:
        """AC-64-01-B: detect-fix-rescan pattern: 1 violation → fix → 0 violations."""
        executor = self._make_executor(max_retries=5)
        fixed = [False]

        def detect_and_maybe_fix() -> int:
            if not fixed[0]:
                fixed[0] = True  # Simulate fix applied
                return 1  # Still 1 violation on this scan (fix applied, re-scan next)
            return 0  # Violation resolved

        result = executor.execute(
            fn=detect_and_maybe_fix,
            check_convergence=lambda v: v == 0,
        )
        assert result.converged is True
        assert result.attempts == 2, f"Expected 2 attempts (detect→fix→rescan), got {result.attempts}"


# ---------------------------------------------------------------------------
# AC-64-01-C: workflow_runs DDL schema data-contract
# ---------------------------------------------------------------------------


class TestWorkflowRunsSchemaContract:
    """
    AC-64-01-C: workflow_runs DDL schema defined in detect-fix-rescan-loop.yaml.

    Verifies the structural prerequisite for SQLite persistence: the schema
    definition is present in the canonical YAML template. Once ConvergenceLoopExecutor
    writes rows, this contract guarantees the table structure is stable.
    """

    @pytest.fixture(scope="class")
    def yaml_template(self) -> Dict[str, Any]:
        """Load the detect-fix-rescan-loop.yaml template."""
        assert _DETECT_FIX_RESCAN_YAML.exists(), (
            f"detect-fix-rescan-loop.yaml must exist at {_DETECT_FIX_RESCAN_YAML}"
        )
        with open(_DETECT_FIX_RESCAN_YAML) as f:
            return yaml.safe_load(f)

    def test_workflow_runs_table_defined_in_yaml(self, yaml_template: Dict[str, Any]) -> None:
        """AC-64-01-C: workflow_runs table is defined in the YAML template."""
        # The schema section may be nested under sqlite_schema, schema, or persistence
        template_str = str(yaml_template)
        assert "workflow_runs" in template_str, (
            "detect-fix-rescan-loop.yaml must define workflow_runs table schema"
        )

    def test_workflow_runs_has_run_id_column(self, yaml_template: Dict[str, Any]) -> None:
        """AC-64-01-C: workflow_runs DDL includes run_id column."""
        template_str = str(yaml_template)
        assert "run_id" in template_str, "workflow_runs DDL must include run_id column"

    def test_workflow_runs_has_template_id_column(self, yaml_template: Dict[str, Any]) -> None:
        """AC-64-01-C: workflow_runs DDL includes template_id column."""
        template_str = str(yaml_template)
        assert "template_id" in template_str, "workflow_runs DDL must include template_id column"

    def test_workflow_runs_has_exit_reason_column(self, yaml_template: Dict[str, Any]) -> None:
        """AC-64-01-C: workflow_runs DDL includes exit_reason column."""
        template_str = str(yaml_template)
        assert "exit_reason" in template_str, "workflow_runs DDL must include exit_reason column"

    def test_workflow_runs_has_final_predicate_column(self, yaml_template: Dict[str, Any]) -> None:
        """AC-64-01-C: workflow_runs DDL includes final_predicate column."""
        template_str = str(yaml_template)
        assert "final_predicate" in template_str, (
            "workflow_runs DDL must include final_predicate column (1=clean exit, 0=max_cycles)"
        )

    def test_workflow_runs_sqlite_is_creatable(self) -> None:
        """AC-64-01-C: workflow_runs DDL can create a real SQLite table (smoke test)."""
        ddl = """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            run_id          TEXT PRIMARY KEY,
            template_id     TEXT NOT NULL,
            label           TEXT NOT NULL,
            caller          TEXT,
            total_cycles    INTEGER NOT NULL,
            total_issues_fixed INTEGER NOT NULL,
            final_predicate INTEGER NOT NULL,
            exit_reason     TEXT NOT NULL,
            started_at      TEXT NOT NULL,
            completed_at    TEXT NOT NULL,
            duration_ms     INTEGER NOT NULL
        )
        """
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)
        try:
            conn.execute(ddl)
            conn.commit()
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE name='workflow_runs'")
            assert cursor.fetchone() is not None, "workflow_runs table must be creatable"

            # Insert a test row to verify the schema is valid
            conn.execute("""
                INSERT INTO workflow_runs VALUES (
                    'run-001', 'detect-fix-rescan', 'test run', 'test-orchestrator',
                    1, 0, 1, 'predicate_true',
                    '2026-02-25T00:00:00Z', '2026-02-25T00:00:01Z', 1000
                )
            """)
            conn.commit()
            cursor = conn.execute("SELECT exit_reason FROM workflow_runs WHERE run_id='run-001'")
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == "predicate_true", f"exit_reason must be 'predicate_true', got {row[0]}"
        finally:
            conn.close()
            Path(db_path).unlink(missing_ok=True)


# AC_COMPLETE: AC-64-C-GOLDEN-001 ✅
