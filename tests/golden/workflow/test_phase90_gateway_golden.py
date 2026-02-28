"""
Golden Tests — Phase 90 + 91: WorkflowGateway + Enforcement Contract

GW-001 .. GW-020: Regression guard for the mandatory gateway infrastructure.
These tests are the final authority on Phase 90/91 correctness and must NEVER
be weakened without explicit Phase governance approval.

Coverage clusters:
  A: WorkflowGateway._MODE_TEMPLATE_MAP completeness (GW-001..GW-008)
  B: WorkflowGateway.resolve_template() contract (GW-009..GW-012)
  C: WorkflowEnforcementMixin contract (GW-013..GW-016)
  D: All 8 mode-workflow templates contain review-and-cleanup (GW-017..GW-019)
  E: tdd/tdd-workflow.yaml composite dispatcher structure (GW-020..GW-024)
  F: primitives/execution/review-and-cleanup.yaml schema (GW-025..GW-027)

Phase 91 changes to golden truth:
  - INVESTIGATE promoted from exempt (None) to active template (lifecycle/investigate-workflow)
  - lifecycle/investigate-workflow.yaml added to review-and-cleanup template set
  - TrainerOrchestrator.PHASE90_GATEWAY_ENABLED = True
  - primitives/intelligence/activity-log-query.yaml created

Phase 97 changes to golden truth:
  - RCA promoted from exempt (None) to active template (rca/rca-analysis-workflow)
  - DIGEST promoted from exempt (None) to active template (lifecycle/digest-workflow)

Phase: 90 | Updated: 97 | Priority: P0
Authority: CORE-008 (TDD), CORE-055 (golden test tier), CORE-064 (sweep)
AC_START: AC-P90-GOLDEN-WFG-001
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import yaml

ROOT = Path(__file__).parents[3]
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"

# ─────────────────────────────────────────────────────────────────────────────
# Expected canonical state — single golden truth for Phase 90
# ─────────────────────────────────────────────────────────────────────────────
_CODE_TOUCHING_MODES: Dict[str, str] = {
    "IMPLEMENT":      "sdlc/implement-workflow",
    "FIX":            "sdlc/fix-workflow",
    "REFACTOR":       "quality/refactor-workflow",
    "DEBUG":          "debugging/multi-stack-debug-pipeline",
    "AUDIT":          "audit/audit-fix-pipeline",
    "HEALTH":         "maintenance/health-check-workflow",
    "VACUUM":         "maintenance/vacuum-workflow",
    "TDD":            "tdd/tdd-workflow",
    "TOTALRECALL":    "lifecycle/totalrecall-workflow",
    "SYNC":           "lifecycle/sync-workflow",
    "TRAIN":          "lifecycle/train-workflow",
    "GOLDEN_TEST":    "tdd/tdd-workflow",
    "WORKFLOW_COMPOSE": "tdd/tdd-workflow",
    # Phase 91: INVESTIGATE promoted from exempt → active read-only mode workflow
    "INVESTIGATE":    "lifecycle/investigate-workflow",
    # Phase 97: RCA + DIGEST promoted from exempt → active read-only mode workflows
    "RCA":            "rca/rca-analysis-workflow",
    "DIGEST":         "lifecycle/digest-workflow",
}

_EXEMPT_MODES = ["QUERY", "DESIGN", "PLAN", "REPHRASE"]

# The 8 templates that MUST contain review-and-cleanup injection
# Phase 91: lifecycle/investigate-workflow.yaml added (has read_only_mode review-and-cleanup)
_REVIEW_AND_CLEANUP_TEMPLATES = [
    "sdlc/implement-workflow.yaml",
    "sdlc/fix-workflow.yaml",
    "quality/refactor-workflow.yaml",
    "maintenance/health-check-workflow.yaml",
    "maintenance/vacuum-workflow.yaml",
    "audit/audit-fix-pipeline.yaml",
    "debugging/multi-stack-debug-pipeline.yaml",
    "lifecycle/investigate-workflow.yaml",
]


# ─────────────────────────────────────────────────────────────────────────────
# Cluster A: _MODE_TEMPLATE_MAP completeness
# ─────────────────────────────────────────────────────────────────────────────

class TestGatewayModeMapCompleteness:
    """GW-001..GW-008: _MODE_TEMPLATE_MAP covers all required modes correctly."""

    def _get_mode_map(self) -> Dict[str, Optional[str]]:
        from cortex.orchestrators.workflow.workflow_gateway import _MODE_TEMPLATE_MAP
        return _MODE_TEMPLATE_MAP

    def test_all_code_touching_modes_present(self) -> None:
        """GW-001: Every code-touching mode is in _MODE_TEMPLATE_MAP."""
        mode_map = self._get_mode_map()
        missing = [m for m in _CODE_TOUCHING_MODES if m not in mode_map]
        assert missing == [], f"Missing modes from _MODE_TEMPLATE_MAP: {missing}"

    def test_all_exempt_modes_present(self) -> None:
        """GW-002: Every exempt (WC-005) mode maps to None in _MODE_TEMPLATE_MAP."""
        mode_map = self._get_mode_map()
        missing = [m for m in _EXEMPT_MODES if m not in mode_map]
        assert missing == [], f"Exempt modes not in _MODE_TEMPLATE_MAP: {missing}"

    def test_exempt_modes_map_to_none(self) -> None:
        """GW-003: Exempt modes must map to None — not to any template string."""
        mode_map = self._get_mode_map()
        non_none = [m for m in _EXEMPT_MODES if mode_map.get(m) is not None]
        assert non_none == [], (
            f"Exempt modes incorrectly mapped to a template: {non_none}"
        )

    def test_code_touching_modes_have_correct_templates(self) -> None:
        """GW-004: Each code-touching mode maps to its golden canonical template ID."""
        mode_map = self._get_mode_map()
        wrong = {}
        for mode, expected in _CODE_TOUCHING_MODES.items():
            actual = mode_map.get(mode)
            if actual != expected:
                wrong[mode] = {"expected": expected, "actual": actual}
        assert wrong == {}, f"Incorrect template mappings: {wrong}"

    def test_implement_maps_to_sdlc_implement(self) -> None:
        """GW-005: IMPLEMENT → sdlc/implement-workflow (non-negotiable P0 contract)."""
        mode_map = self._get_mode_map()
        assert mode_map["IMPLEMENT"] == "sdlc/implement-workflow"

    def test_tdd_maps_to_tdd_workflow_composite(self) -> None:
        """GW-006: TDD → tdd/tdd-workflow (Phase 90 composite dispatcher)."""
        mode_map = self._get_mode_map()
        assert mode_map["TDD"] == "tdd/tdd-workflow"

    def test_debug_maps_to_multi_stack_pipeline(self) -> None:
        """GW-007: DEBUG → debugging/multi-stack-debug-pipeline."""
        mode_map = self._get_mode_map()
        assert mode_map["DEBUG"] == "debugging/multi-stack-debug-pipeline"

    def test_health_vacuum_have_distinct_templates(self) -> None:
        """GW-008: HEALTH and VACUUM map to different maintenance templates."""
        mode_map = self._get_mode_map()
        assert mode_map["HEALTH"] != mode_map["VACUUM"]
        assert mode_map["HEALTH"] == "maintenance/health-check-workflow"
        assert mode_map["VACUUM"] == "maintenance/vacuum-workflow"


# ─────────────────────────────────────────────────────────────────────────────
# Cluster B: WorkflowGateway.resolve_template() contract
# ─────────────────────────────────────────────────────────────────────────────

class TestWorkflowGatewayResolveTemplate:
    """GW-009..GW-012: resolve_template() returns correct IDs and None for exempt modes."""

    @pytest.fixture
    def gateway(self, tmp_path: Path) -> Any:
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        db = tmp_path / "traces.db"
        return WorkflowGateway(db_path=db)

    def test_resolve_returns_template_for_implement(self, gateway: Any) -> None:
        """GW-009: resolve_template("IMPLEMENT") → sdlc/implement-workflow."""
        result = gateway.resolve_template("IMPLEMENT", {})
        assert result == "sdlc/implement-workflow"

    def test_resolve_returns_none_for_query(self, gateway: Any) -> None:
        """GW-010: resolve_template("QUERY") → None (exempt mode)."""
        result = gateway.resolve_template("QUERY", {})
        assert result is None

    def test_resolve_is_case_insensitive(self, gateway: Any) -> None:
        """GW-011: resolve_template accepts lowercase mode strings."""
        result = gateway.resolve_template("fix", {})
        assert result == "sdlc/fix-workflow"

    @pytest.mark.parametrize("mode,expected_template", list(_CODE_TOUCHING_MODES.items()))
    def test_resolve_all_code_touching_modes(
        self, gateway: Any, mode: str, expected_template: str
    ) -> None:
        """GW-012: All code-touching modes resolve to their canonical template."""
        result = gateway.resolve_template(mode, {})
        assert result == expected_template, (
            f"Mode {mode!r}: expected {expected_template!r}, got {result!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster C: WorkflowEnforcementMixin contract
# ─────────────────────────────────────────────────────────────────────────────

class TestWorkflowEnforcementMixinContract:
    """GW-013..GW-016: WorkflowEnforcementMixin safe-rollout + gateway routing."""

    def test_default_gateway_enabled_is_false(self) -> None:
        """GW-013: PHASE90_GATEWAY_ENABLED defaults to False — safe rollout contract."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert WorkflowEnforcementMixin.PHASE90_GATEWAY_ENABLED is False, (
            "Default must be False — changing to True is a breaking migration step "
            "that requires per-orchestrator opt-in approval"
        )

    def test_mixin_falls_through_when_disabled(self, tmp_path: Path) -> None:
        """GW-014: When gateway disabled, execute_via_gateway calls execute_operation."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin

        calls: list = []

        class StubOrchestrator(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = False

            def execute_operation(self, mode: str, params: Dict) -> str:
                calls.append((mode, params))
                return "direct-result"

        orch = StubOrchestrator()
        result = orch.execute_via_gateway("IMPLEMENT", {"x": 1})
        assert result == "direct-result"
        assert calls == [("IMPLEMENT", {"x": 1})]

    def test_mixin_routes_through_gateway_when_enabled(self, tmp_path: Path) -> None:
        """GW-015: When PHASE90_GATEWAY_ENABLED=True, execute_via_gateway uses WorkflowGateway."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway_calls: list = []

        class MockGateway:
            def execute_gated(self, orchestrator_name, mode, context):
                gateway_calls.append((orchestrator_name, mode))
                return {"status": "COMPLETED", "template_id": "sdlc/implement-workflow",
                        "steps_completed": 1, "run_id": "test-run-001"}

        class EnabledOrchestrator(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = True

            def execute_operation(self, mode, params):
                raise AssertionError("Should not be called when gateway enabled")

        orch = EnabledOrchestrator()
        orch._gateway = MockGateway()  # inject mock
        result = orch.execute_via_gateway("IMPLEMENT", {})
        assert result["status"] == "COMPLETED"
        assert gateway_calls == [("EnabledOrchestrator", "IMPLEMENT")]

    def test_get_gateway_returns_workflow_gateway_instance(self, tmp_path: Path) -> None:
        """GW-016: get_gateway() returns a WorkflowGateway instance (lazy init)."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        class TestOrchestrator(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = True

        orch = TestOrchestrator()
        # Inject a tmp_path-based db so we don't write to .cortex-runtime
        gateway = WorkflowGateway(db_path=tmp_path / "traces.db")
        orch._gateway = gateway
        result = orch.get_gateway()
        assert isinstance(result, WorkflowGateway)


# ─────────────────────────────────────────────────────────────────────────────
# Cluster D: All 7 mode workflows contain review-and-cleanup
# ─────────────────────────────────────────────────────────────────────────────

class TestReviewAndCleanupInjection:
    """GW-017..GW-019: Every code-touching workflow template references review-and-cleanup."""

    @pytest.fixture(params=_REVIEW_AND_CLEANUP_TEMPLATES)
    def template_path(self, request: pytest.FixtureRequest) -> Path:
        return TEMPLATES_ROOT / request.param

    def test_template_exists(self, template_path: Path) -> None:
        """GW-017: All 7 mode-workflow template files exist on disk."""
        assert template_path.exists(), (
            f"Workflow template missing: {template_path.relative_to(ROOT)}"
        )

    def test_template_references_review_and_cleanup(self, template_path: Path) -> None:
        """GW-018: Each mode workflow template contains a reference to review-and-cleanup."""
        content = template_path.read_text(errors="replace")
        assert "review-and-cleanup" in content, (
            f"{template_path.relative_to(ROOT)} does not reference "
            "'review-and-cleanup' primitive — Phase 90 injection missing"
        )

    def test_review_and_cleanup_primitive_exists(self) -> None:
        """GW-019: primitives/execution/review-and-cleanup.yaml is on disk."""
        primitive = TEMPLATES_ROOT / "primitives" / "execution" / "review-and-cleanup.yaml"
        assert primitive.exists(), (
            "primitives/execution/review-and-cleanup.yaml is missing — "
            "the primitive that ALL mode workflows depend on does not exist"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster E: tdd/tdd-workflow.yaml composite dispatcher structure
# ─────────────────────────────────────────────────────────────────────────────

class TestTddWorkflowCompositeDispatcher:
    """GW-020..GW-024: tdd/tdd-workflow.yaml is a valid, complete composite dispatcher."""

    @pytest.fixture
    def tdd_workflow(self) -> Dict[str, Any]:
        path = TEMPLATES_ROOT / "tdd" / "tdd-workflow.yaml"
        assert path.exists(), "tdd/tdd-workflow.yaml must exist (Phase 90)"
        with open(path) as f:
            return yaml.safe_load(f)

    def test_workflow_id_is_canonical(self, tdd_workflow: Dict) -> None:
        """GW-020: workflow.id == 'tdd/tdd-workflow' (canonical Phase 90 ID)."""
        wf = tdd_workflow.get("workflow", tdd_workflow)
        wf_id = wf.get("id", "")
        assert "tdd-workflow" in wf_id or "tdd/tdd-workflow" in wf_id, (
            f"tdd-workflow.yaml workflow.id should be 'tdd/tdd-workflow', got: {wf_id!r}"
        )

    def test_workflow_references_implement_mode(self, tdd_workflow: Dict) -> None:
        """GW-021: tdd-workflow.yaml dispatches to sdlc/implement-workflow."""
        content = yaml.dump(tdd_workflow)
        assert "implement-workflow" in content or "sdlc/implement" in content, (
            "tdd/tdd-workflow.yaml must dispatch IMPLEMENT mode to sdlc/implement-workflow"
        )

    def test_workflow_references_fix_mode(self, tdd_workflow: Dict) -> None:
        """GW-022: tdd-workflow.yaml dispatches FIX to sdlc/fix-workflow."""
        content = yaml.dump(tdd_workflow)
        assert "fix-workflow" in content or "sdlc/fix" in content, (
            "tdd/tdd-workflow.yaml must dispatch FIX mode to sdlc/fix-workflow"
        )

    def test_workflow_references_review_and_cleanup(self, tdd_workflow: Dict) -> None:
        """GW-023: tdd-workflow.yaml includes review-and-cleanup as final step."""
        content = yaml.dump(tdd_workflow)
        assert "review-and-cleanup" in content, (
            "tdd/tdd-workflow.yaml is missing review-and-cleanup epilogue"
        )

    def test_workflow_is_parseable_yaml(self) -> None:
        """GW-024: tdd/tdd-workflow.yaml parses without YAML errors."""
        path = TEMPLATES_ROOT / "tdd" / "tdd-workflow.yaml"
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            assert data is not None, "YAML parsed to None — file may be empty"
        except yaml.YAMLError as exc:
            pytest.fail(f"tdd/tdd-workflow.yaml is invalid YAML: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Cluster F: primitives/execution/review-and-cleanup.yaml schema
# ─────────────────────────────────────────────────────────────────────────────

class TestReviewAndCleanupPrimitiveSchema:
    """GW-025..GW-027: review-and-cleanup.yaml has correct structure and all 3 phases."""

    @pytest.fixture
    def primitive(self) -> Dict[str, Any]:
        path = TEMPLATES_ROOT / "primitives" / "execution" / "review-and-cleanup.yaml"
        assert path.exists(), "review-and-cleanup.yaml must exist"
        with open(path) as f:
            return yaml.safe_load(f)

    def test_primitive_is_valid_yaml(self) -> None:
        """GW-025: review-and-cleanup.yaml parses without YAML errors."""
        path = TEMPLATES_ROOT / "primitives" / "execution" / "review-and-cleanup.yaml"
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            assert data is not None
        except yaml.YAMLError as exc:
            pytest.fail(f"review-and-cleanup.yaml is invalid YAML: {exc}")

    def test_primitive_references_lens_diff(self, primitive: Dict) -> None:
        """GW-026: Primitive Phase A must reference lens diff review."""
        content = yaml.dump(primitive)
        has_lens = "lens" in content.lower() or "diff" in content.lower()
        assert has_lens, (
            "review-and-cleanup.yaml missing Phase A: LENS diff review step"
        )

    def test_primitive_references_cleanup_or_marker_removal(self, primitive: Dict) -> None:
        """GW-027: Primitive Phase B must reference cleanup or marker removal."""
        content = yaml.dump(primitive)
        has_cleanup = (
            "cleanup" in content.lower()
            or "marker" in content.lower()
            or "auto_cleanup" in content.lower()
        )
        assert has_cleanup, (
            "review-and-cleanup.yaml missing Phase B: marker cleanup step"
        )


# AC_COMPLETE: AC-P90-GOLDEN-WFG-001 ✅ Phase 90 gateway golden tests
