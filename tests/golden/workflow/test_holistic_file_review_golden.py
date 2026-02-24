"""
Golden Tests: Holistic File Review Gate — CORE-065

Phase 64 sub-phase 64-G | Closes: REVIEW-GAP-05 (partial), CORE-065 governance rule
Authority: CORE-065 (Holistic File Review Contract), CORE-064 (Sweep Completeness),
           CORE-008 (TDD), CORE-002 (No report files)

6 Acceptance Criteria (AC-64-G-01 through AC-64-G-06):

  AC-64-G-01  test_gate1_blocks_when_files_skipped
              GATE-1 fails when any scope file is absent from post-work snapshot
  AC-64-G-02  test_all_5_gates_pass_when_all_files_reviewed
              All 5 gates pass for a clean BEFORE/AFTER run
  AC-64-G-03  test_gate4_blocks_on_test_regression
              GATE-4 (test count) fails when post_test_count < pre_test_count
  AC-64-G-04  test_gate5_blocks_when_sweep_items_remain
              GATE-5 fails when sweep catalogue has open items
  AC-64-G-05  test_session_resume_starts_at_last_completed_step
              Resume protocol: step_last_completed tracked in SQLite; resume starts there
  AC-64-G-06  test_template_composer_auto_injects_holistic_gate_at_index_0
              TemplateComposer CORE-065 auto-injection: FIX/REFACTOR/IMPLEMENT/AUDIT
              composed templates have holistic_file_review_gate as step index 0

AC_START: AC-64-G-GOLDEN-001
Phase: 64 | Stage: G | Priority: P0
"""

import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml


# =============================================================================
# Helpers — import guard so the test fails fast with a clear message on RED
# =============================================================================

def _import_gate() -> Any:
    """Import HolisticFileReviewGate — fails RED if class not yet implemented."""
    from cortex.governance.holistic_file_review_gate import HolisticFileReviewGate  # noqa: PLC0415
    return HolisticFileReviewGate


def _import_composer() -> Any:
    from cortex.orchestrators.workflow.template_composer import TemplateComposer  # noqa: PLC0415
    return TemplateComposer


def _import_response_validator() -> Any:
    from cortex.governance.response_template_validator import ResponseTemplateValidator  # noqa: PLC0415
    return ResponseTemplateValidator


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture()
def tmp_db(tmp_path: Path) -> sqlite3.Connection:
    """Ephemeral in-memory-backed SQLite for sweep session continuity tests."""
    db_path = tmp_path / "sweeps.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS holistic_review_sessions (
            sweep_id TEXT PRIMARY KEY,
            operation_type TEXT NOT NULL,
            step_last_completed TEXT,
            pre_snapshot_json TEXT,
            post_snapshot_json TEXT,
            gate_results_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


@pytest.fixture()
def pre_snapshot_clean() -> Dict[str, Any]:
    """A clean pre-work snapshot with 3 files, none high-risk."""
    return {
        "files": [
            {
                "path": "cortex/governance/holistic_file_review_gate.py",
                "risk_score": 0.3,
                "open_issues": 0,
                "test_coverage_pct": 85,
            },
            {
                "path": "cortex/orchestrators/workflow/template_composer.py",
                "risk_score": 0.35,
                "open_issues": 0,
                "test_coverage_pct": 78,
            },
            {
                "path": "cortex/core/workflow_engine.py",
                "risk_score": 0.2,
                "open_issues": 0,
                "test_coverage_pct": 90,
            },
        ],
        "pre_lint_errors": 0,
        "pre_test_count": 100,
        "high_risk_files": [],  # none exceed 0.4 threshold
    }


@pytest.fixture()
def post_snapshot_clean(pre_snapshot_clean: Dict[str, Any]) -> Dict[str, Any]:
    """A clean post-work snapshot where all files were reviewed."""
    return {
        "files_reviewed": [
            f["path"] for f in pre_snapshot_clean["files"]
        ],
        "post_lint_errors": 0,
        "post_test_count": 103,  # ≥ pre — no regression
        "high_risk_files_touched": [],
        "sweep_open_items": 0,
    }


@pytest.fixture()
def primitives_dir_with_analysis(tmp_path: Path) -> Path:
    """Minimal primitives directory with one primitive per category."""
    for cat, name in [
        ("analysis", "lens-scan"),
        ("execution", "code-execution"),
        ("validation", "test-validation"),
        ("governance", "sweep-open"),
    ]:
        prim: Dict[str, Any] = {
            "template_id": f"primitives/{cat}/{name}",
            "name": f"{name.replace('-', ' ').title()} Primitive",
            "category": cat,
            "status": "active",
            "metadata": {"tags": [cat, name]},
            "execution": {
                "steps": [
                    {
                        "id": f"{cat}_step",
                        "name": f"{cat} step",
                        "action": f"run_{cat}",
                    }
                ]
            },
        }
        pdir = tmp_path / cat
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / f"{name}.yaml").write_text(yaml.dump(prim))
    return tmp_path


# =============================================================================
# AC-64-G-01  GATE-1 blocks when files are skipped
# =============================================================================

class TestGate1BlocksWhenFilesSkipped:
    """AC-64-G-01: GATE-1 (No Files Skipped) blocks when any scope file absent from post-work."""

    def test_gate1_blocks_when_files_skipped(
        self, pre_snapshot_clean: Dict[str, Any]
    ) -> None:
        """GATE-1 must fail (not pass) when one file from pre-work is absent in post-work."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate()

        # Post snapshot is MISSING the last file — simulates a partial sweep
        post_snapshot_partial: Dict[str, Any] = {
            "files_reviewed": [
                "cortex/governance/holistic_file_review_gate.py",
                # "cortex/orchestrators/workflow/template_composer.py" — SKIPPED
                "cortex/core/workflow_engine.py",
            ],
            "post_lint_errors": 0,
            "post_test_count": 103,
            "high_risk_files_touched": [],
            "sweep_open_items": 0,
        }

        result = gate.evaluate_gates(pre_snapshot_clean, post_snapshot_partial)

        gate1 = result["gates"]["GATE-1"]
        assert gate1["passed"] is False, (
            "GATE-1 must fail when cortex/orchestrators/workflow/template_composer.py "
            "was in pre-work scope but absent from post-work review."
        )
        assert result["all_gates_passed"] is False
        assert "files_skipped" in gate1
        assert len(gate1["files_skipped"]) >= 1

    def test_gate1_passes_when_all_files_reviewed(
        self,
        pre_snapshot_clean: Dict[str, Any],
        post_snapshot_clean: Dict[str, Any],
    ) -> None:
        """GATE-1 passes when all pre-work files appear in post-work reviewed list."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate()

        result = gate.evaluate_gates(pre_snapshot_clean, post_snapshot_clean)

        gate1 = result["gates"]["GATE-1"]
        assert gate1["passed"] is True, (
            "GATE-1 must pass when all 3 scope files were reviewed."
        )


# =============================================================================
# AC-64-G-02  All 5 gates pass for a clean run
# =============================================================================

class TestAllGatesPassCleanRun:
    """AC-64-G-02: All 5 gates pass for a clean BEFORE/AFTER run."""

    def test_all_5_gates_pass_when_all_files_reviewed(
        self,
        pre_snapshot_clean: Dict[str, Any],
        post_snapshot_clean: Dict[str, Any],
    ) -> None:
        """All 5 gates must report passed=True for a clean BEFORE/AFTER run."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate()

        result = gate.evaluate_gates(pre_snapshot_clean, post_snapshot_clean)

        assert result["all_gates_passed"] is True, (
            f"Expected all gates to pass but got: {result['gates']}"
        )
        for gate_id in ["GATE-1", "GATE-2", "GATE-3", "GATE-4", "GATE-5"]:
            assert gate_id in result["gates"], f"Missing {gate_id} in result"
            assert result["gates"][gate_id]["passed"] is True, (
                f"{gate_id} should pass for a clean run but did not: "
                f"{result['gates'][gate_id]}"
            )

    def test_gate_result_structure_is_complete(
        self,
        pre_snapshot_clean: Dict[str, Any],
        post_snapshot_clean: Dict[str, Any],
    ) -> None:
        """Gate result dict must contain: all_gates_passed, gates, files_skipped_count."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate()

        result = gate.evaluate_gates(pre_snapshot_clean, post_snapshot_clean)

        assert "all_gates_passed" in result
        assert "gates" in result
        assert "files_skipped_count" in result
        assert isinstance(result["files_skipped_count"], int)


# =============================================================================
# AC-64-G-03  GATE-4 blocks on test regression
# =============================================================================

class TestGate4BlocksOnTestRegression:
    """AC-64-G-03: GATE-4 (No Test Regression) blocks when post_test_count < pre."""

    def test_gate4_blocks_on_test_regression(
        self, pre_snapshot_clean: Dict[str, Any]
    ) -> None:
        """GATE-4 must fail when post_test_count drops below pre_test_count (CORE-008)."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate()

        post_with_regression: Dict[str, Any] = {
            "files_reviewed": [
                f["path"] for f in pre_snapshot_clean["files"]
            ],
            "post_lint_errors": 0,
            "post_test_count": 95,  # dropped from 100 — regression!
            "high_risk_files_touched": [],
            "sweep_open_items": 0,
        }

        result = gate.evaluate_gates(pre_snapshot_clean, post_with_regression)

        gate4 = result["gates"]["GATE-4"]
        assert gate4["passed"] is False, (
            "GATE-4 must fail: post_test_count=95 < pre_test_count=100 (CORE-008 violation)."
        )
        assert result["all_gates_passed"] is False
        assert "pre_test_count" in gate4
        assert "post_test_count" in gate4


# =============================================================================
# AC-64-G-04  GATE-5 blocks when sweep items remain
# =============================================================================

class TestGate5BlocksWhenSweepItemsRemain:
    """AC-64-G-04: GATE-5 (Sweep Catalogue Exhausted) blocks when open_items > 0."""

    def test_gate5_blocks_when_sweep_items_remain(
        self,
        pre_snapshot_clean: Dict[str, Any],
    ) -> None:
        """GATE-5 must fail when sweep catalogue has open items (CORE-064)."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate()

        post_with_open_items: Dict[str, Any] = {
            "files_reviewed": [
                f["path"] for f in pre_snapshot_clean["files"]
            ],
            "post_lint_errors": 0,
            "post_test_count": 103,
            "high_risk_files_touched": [],
            "sweep_open_items": 3,  # 3 open catalogue items remain
        }

        result = gate.evaluate_gates(pre_snapshot_clean, post_with_open_items)

        gate5 = result["gates"]["GATE-5"]
        assert gate5["passed"] is False, (
            "GATE-5 must fail: 3 sweep catalogue items remain open (CORE-064)."
        )
        assert result["all_gates_passed"] is False


# =============================================================================
# AC-64-G-05  Session resume starts at last completed step
# =============================================================================

class TestSessionResumeStartsAtLastCompletedStep:
    """AC-64-G-05: Multi-session continuity — resume from step_last_completed in SQLite."""

    def test_session_resume_starts_at_last_completed_step(
        self, tmp_db: sqlite3.Connection
    ) -> None:
        """After persisting step_last_completed, resume reads it back correctly."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate(db_connection=tmp_db)

        sweep_id = "SWEEP-64-G-TEST-001"
        # Simulate session 1: persisted step_1_pre_work_inventory as last completed
        gate.persist_session_state(
            sweep_id=sweep_id,
            operation_type="FIX",
            step_last_completed="step_1_pre_work_inventory",
        )

        # Session 2: resume — reads back the last completed step
        state = gate.load_session_state(sweep_id=sweep_id)

        assert state is not None, (
            "load_session_state must return state for a persisted sweep_id."
        )
        assert state["step_last_completed"] == "step_1_pre_work_inventory", (
            f"Expected 'step_1_pre_work_inventory' but got: {state['step_last_completed']}"
        )
        assert state["operation_type"] == "FIX"

    def test_session_resume_returns_none_for_unknown_sweep(
        self, tmp_db: sqlite3.Connection
    ) -> None:
        """load_session_state returns None for a sweep_id that was never persisted."""
        HolisticFileReviewGate = _import_gate()
        gate = HolisticFileReviewGate(db_connection=tmp_db)

        state = gate.load_session_state(sweep_id="SWEEP-NONEXISTENT")

        assert state is None, (
            "load_session_state must return None for an unknown sweep_id."
        )


# =============================================================================
# AC-64-G-06  TemplateComposer auto-injects holistic gate at index 0
# =============================================================================

class TestTemplateComposerAutoInjectsHolisticGate:
    """AC-64-G-06: CORE-065 — TemplateComposer injects holistic_file_review_gate as step[0]."""

    def test_template_composer_auto_injects_holistic_gate_at_index_0(
        self, primitives_dir_with_analysis: Path
    ) -> None:
        """FIX composed template must have holistic_file_review_gate as step[0] (CORE-065)."""
        TemplateComposer = _import_composer()
        composer = TemplateComposer(primitives_dir=primitives_dir_with_analysis)

        result = composer.compose(operation_type="fix", description="Fix missing type hints")

        assert result is not None
        steps = result["steps"]
        assert len(steps) >= 2, "FIX template must have at least 2 steps"
        first_step = steps[0]
        assert first_step["id"] == "holistic_file_review_gate_open", (
            f"CORE-065: first step must be holistic_file_review_gate_open "
            f"but got id='{first_step['id']}'"
        )
        assert first_step.get("governance_rule") == "CORE-065", (
            "First step must carry governance_rule='CORE-065'"
        )

    def test_refactor_template_auto_injects_holistic_gate(
        self, primitives_dir_with_analysis: Path
    ) -> None:
        """REFACTOR composed template must also have holistic gate at index 0."""
        TemplateComposer = _import_composer()
        composer = TemplateComposer(primitives_dir=primitives_dir_with_analysis)

        result = composer.compose(
            operation_type="refactor", description="Refactor auth module"
        )

        assert result is not None
        first_step = result["steps"][0]
        assert first_step["id"] == "holistic_file_review_gate_open", (
            "CORE-065: REFACTOR template must also start with holistic_file_review_gate_open"
        )

    def test_implement_template_auto_injects_holistic_gate(
        self, primitives_dir_with_analysis: Path
    ) -> None:
        """IMPLEMENT composed template must also have holistic gate at index 0 (CORE-065)."""
        TemplateComposer = _import_composer()
        composer = TemplateComposer(primitives_dir=primitives_dir_with_analysis)

        result = composer.compose(
            operation_type="implement", description="Implement new orchestrator"
        )

        assert result is not None
        first_step = result["steps"][0]
        assert first_step["id"] == "holistic_file_review_gate_open", (
            "CORE-065: IMPLEMENT template must also start with holistic_file_review_gate_open"
        )

    def test_composed_metadata_records_core_065_compliant(
        self, primitives_dir_with_analysis: Path
    ) -> None:
        """Composed template metadata must record core_065_compliant=True."""
        TemplateComposer = _import_composer()
        composer = TemplateComposer(primitives_dir=primitives_dir_with_analysis)

        result = composer.compose(operation_type="fix", description="Fix stale imports")

        assert result is not None
        assert result["metadata"].get("core_065_compliant") is True, (
            "Composed template metadata must have core_065_compliant=True (CORE-065 enforcement)"
        )


# =============================================================================
# Integration: WorkflowEngine wires ResponseTemplateValidator post-step hook
# =============================================================================

class TestWorkflowEngineResponseValidatorHook:
    """AC-64-G (integration): WorkflowEngine post-step hook calls ResponseTemplateValidator."""

    def test_workflow_engine_has_response_validator_hook(self) -> None:
        """WorkflowEngine must expose a register_post_step_hook() method (CORE-066)."""
        from cortex.core.workflow_engine import WorkflowEngine  # noqa: PLC0415
        engine = WorkflowEngine()
        assert hasattr(engine, "register_post_step_hook"), (
            "WorkflowEngine must have register_post_step_hook() for CORE-066 "
            "ResponseTemplateValidator wiring."
        )

    def test_response_template_validator_catches_raw_dict_output(self) -> None:
        """ResponseTemplateValidator.validate_output() must flag raw dict output as P1."""
        ResponseTemplateValidator = _import_response_validator()
        validator = ResponseTemplateValidator()

        # Raw dict output — no header, no author line, no progress bar
        raw_output = {"result": "some data", "count": 42}
        result = validator.validate_output(raw_output)

        assert result["valid"] is False, (
            "Raw dict output must be flagged as invalid by ResponseTemplateValidator."
        )
        assert result["severity"] in ("P0", "P1"), (
            f"Raw dict output is a P0/P1 CORE-066 violation, got: {result['severity']}"
        )

    def test_response_template_validator_accepts_canonical_header(self) -> None:
        """ResponseTemplateValidator must accept output with canonical Author header."""
        ResponseTemplateValidator = _import_response_validator()
        validator = ResponseTemplateValidator()

        canonical_output = (
            "## ⚡ CORTEX Architect IMPLEMENT\n"
            "**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅\n\n"
            "---\n\n"
            "## 📋 Summary\nImplementing new feature..."
        )
        result = validator.validate_output(canonical_output)

        assert result["valid"] is True, (
            f"Canonical response with Author header must pass validation: {result}"
        )


# AC_COMPLETE: AC-64-G-GOLDEN-001 ✅ RED phase — all tests written, none pass yet
