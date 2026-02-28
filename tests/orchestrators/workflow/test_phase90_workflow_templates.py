"""
Phase 90 — Workflow Template Completeness (RED tests).

Verifies that:
1. tdd/tdd-workflow.yaml exists as mode dispatcher
2. primitives/execution/review-and-cleanup.yaml exists
3. Every code-touching mode workflow includes review-and-cleanup as final step
4. All mode workflows declare convergence_gate with correct primitives

CORE-008: TDD mandatory — RED before GREEN
AC-ID: AC-P90-TPL-001
"""
from __future__ import annotations

import pytest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: tdd/tdd-workflow.yaml exists and is valid
# ════════════════════════════════════════════════════════════════════════════

class TestTDDWorkflowDispatcher:
    """tdd/tdd-workflow.yaml must exist as a mode-dispatching composite."""

    @pytest.fixture
    def tdd_workflow_path(self) -> Path:
        return TEMPLATES_ROOT / "tdd" / "tdd-workflow.yaml"

    def test_tdd_workflow_yaml_exists(self, tdd_workflow_path: Path) -> None:
        assert tdd_workflow_path.exists(), (
            "tdd/tdd-workflow.yaml must exist as TDDOrchestrator entry-point template"
        )

    def test_tdd_workflow_yaml_valid(self, tdd_workflow_path: Path) -> None:
        content = yaml.safe_load(tdd_workflow_path.read_text())
        assert content is not None, "tdd/tdd-workflow.yaml must be valid YAML"

    def test_tdd_workflow_has_mode_dispatch(self, tdd_workflow_path: Path) -> None:
        content = yaml.safe_load(tdd_workflow_path.read_text())
        workflow = content.get("workflow", content)
        # Must reference both implement and fix workflows
        text = tdd_workflow_path.read_text()
        assert "sdlc/implement-workflow" in text, (
            "tdd/tdd-workflow.yaml must dispatch to sdlc/implement-workflow for IMPLEMENT mode"
        )
        assert "sdlc/fix-workflow" in text, (
            "tdd/tdd-workflow.yaml must dispatch to sdlc/fix-workflow for FIX mode"
        )

    def test_tdd_workflow_has_workflow_id(self, tdd_workflow_path: Path) -> None:
        content = yaml.safe_load(tdd_workflow_path.read_text())
        workflow = content.get("workflow", content)
        wf_id = workflow.get("id", "")
        assert wf_id == "tdd/tdd-workflow", (
            f"tdd/tdd-workflow.yaml workflow.id must be 'tdd/tdd-workflow', got '{wf_id}'"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: review-and-cleanup primitive exists
# ════════════════════════════════════════════════════════════════════════════

class TestReviewAndCleanupPrimitive:
    """primitives/execution/review-and-cleanup.yaml must exist."""

    @pytest.fixture
    def primitive_path(self) -> Path:
        return TEMPLATES_ROOT / "primitives" / "execution" / "review-and-cleanup.yaml"

    def test_review_cleanup_primitive_exists(self, primitive_path: Path) -> None:
        assert primitive_path.exists(), (
            "primitives/execution/review-and-cleanup.yaml must exist — "
            "every code-touching operation needs a mandatory Review+Cleanup step"
        )

    def test_review_cleanup_primitive_valid_yaml(self, primitive_path: Path) -> None:
        content = yaml.safe_load(primitive_path.read_text())
        assert content is not None, "review-and-cleanup.yaml must be valid YAML"

    def test_review_cleanup_has_lens_scan_step(self, primitive_path: Path) -> None:
        text = primitive_path.read_text()
        assert "lens" in text.lower() or "LENS" in text, (
            "review-and-cleanup.yaml must include a LENS scan step (diff review)"
        )

    def test_review_cleanup_has_marker_removal_step(self, primitive_path: Path) -> None:
        text = primitive_path.read_text()
        assert "cleanup" in text.lower() or "marker" in text.lower(), (
            "review-and-cleanup.yaml must include debug marker removal step"
        )

    def test_review_cleanup_has_trace_closure_step(self, primitive_path: Path) -> None:
        text = primitive_path.read_text()
        assert "ac_complete" in text.lower() or "AC_COMPLETE" in text or "trace" in text.lower(), (
            "review-and-cleanup.yaml must close the SQLite trace row (AC_COMPLETE)"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: All code-touching mode workflows include review-and-cleanup
# ════════════════════════════════════════════════════════════════════════════

CODE_TOUCHING_WORKFLOWS = [
    "sdlc/implement-workflow.yaml",
    "sdlc/fix-workflow.yaml",
    "quality/refactor-workflow.yaml",
    "debugging/multi-stack-debug-pipeline.yaml",
    "tdd/tdd-workflow.yaml",
    "maintenance/health-check-workflow.yaml",
    "maintenance/vacuum-workflow.yaml",
    "audit/audit-fix-pipeline.yaml",
]


class TestReviewAndCleanupInjection:
    """Every code-touching mode workflow must include review-and-cleanup as final step."""

    @pytest.mark.parametrize("relative_path", CODE_TOUCHING_WORKFLOWS)
    def test_workflow_includes_review_cleanup(self, relative_path: str) -> None:
        wf_path = TEMPLATES_ROOT / relative_path
        assert wf_path.exists(), f"Workflow template not found: {relative_path}"
        text = wf_path.read_text()
        assert "review-and-cleanup" in text or "review_and_cleanup" in text, (
            f"{relative_path} must include 'review-and-cleanup' as final step "
            "(primitives/execution/review-and-cleanup)"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: All mode workflows have convergence_gate block
# ════════════════════════════════════════════════════════════════════════════

class TestConvergenceGatePresence:
    """Every code-touching mode workflow must declare a convergence_gate."""

    @pytest.mark.parametrize("relative_path", CODE_TOUCHING_WORKFLOWS)
    def test_workflow_has_convergence_gate(self, relative_path: str) -> None:
        wf_path = TEMPLATES_ROOT / relative_path
        if not wf_path.exists():
            pytest.skip(f"Template not yet created: {relative_path}")
        text = wf_path.read_text()
        assert "convergence_gate" in text or "convergence" in text, (
            f"{relative_path} must declare a convergence_gate block (CORE-068)"
        )

    @pytest.mark.parametrize("relative_path", CODE_TOUCHING_WORKFLOWS)
    def test_workflow_convergence_references_detect_fix_rescan(self, relative_path: str) -> None:
        wf_path = TEMPLATES_ROOT / relative_path
        if not wf_path.exists():
            pytest.skip(f"Template not yet created: {relative_path}")
        text = wf_path.read_text()
        assert "detect-fix-rescan-loop" in text or "detect_fix_rescan" in text, (
            f"{relative_path} convergence_gate must reference detect-fix-rescan-loop primitive"
        )
