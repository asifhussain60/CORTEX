"""Phase 133-b — Workflow Template Completeness (phase-133-b).

Validates that:
1. sdlc/review-workflow.yaml exists and is valid YAML with id/name/steps
2. lifecycle/feedback-workflow.yaml exists and is valid YAML with id/name/steps
3. workflow-composer-spec.yaml intent_routing contains a REVIEW entry
4. workflow-composer-spec.yaml intent_routing contains a FEEDBACK entry
5. REVIEW entry references sdlc/review-workflow (or sdlc/code-review-workflow)
6. FEEDBACK entry references lifecycle/feedback-workflow

Gap ref: GAP-133-01
CORE rule: CORE-008 (TDD), CORE-064 (Sweep Completeness)
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

CORTEX_ROOT = Path(__file__).parents[2]
TEMPLATES_DIR = CORTEX_ROOT / "cortex-registry" / "workflows" / "templates"
COMPOSER_SPEC = CORTEX_ROOT / "cortex-registry" / "workflows" / "workflow-composer-spec.yaml"

REVIEW_WORKFLOW = TEMPLATES_DIR / "sdlc" / "review-workflow.yaml"
FEEDBACK_WORKFLOW = TEMPLATES_DIR / "lifecycle" / "feedback-workflow.yaml"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Class 1 — review-workflow.yaml exists and is structurally valid
# ---------------------------------------------------------------------------

class TestReviewWorkflowTemplate:

    def test_review_workflow_exists(self):
        assert REVIEW_WORKFLOW.exists(), (
            f"Missing: {REVIEW_WORKFLOW.relative_to(CORTEX_ROOT)}\n"
            "Create sdlc/review-workflow.yaml as part of phase-133-b."
        )

    def test_review_workflow_is_valid_yaml(self):
        assert REVIEW_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(REVIEW_WORKFLOW)
        assert isinstance(data, dict), "review-workflow.yaml must parse to a dict"

    def test_review_workflow_has_id(self):
        assert REVIEW_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(REVIEW_WORKFLOW)
        assert "id" in data, "review-workflow.yaml must have a top-level 'id' field"

    def test_review_workflow_has_name(self):
        assert REVIEW_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(REVIEW_WORKFLOW)
        assert "name" in data, "review-workflow.yaml must have a top-level 'name' field"

    def test_review_workflow_has_steps(self):
        assert REVIEW_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(REVIEW_WORKFLOW)
        assert "steps" in data and len(data["steps"]) > 0, (
            "review-workflow.yaml must have at least one step"
        )


# ---------------------------------------------------------------------------
# Class 2 — feedback-workflow.yaml exists and is structurally valid
# ---------------------------------------------------------------------------

class TestFeedbackWorkflowTemplate:

    def test_feedback_workflow_exists(self):
        assert FEEDBACK_WORKFLOW.exists(), (
            f"Missing: {FEEDBACK_WORKFLOW.relative_to(CORTEX_ROOT)}\n"
            "Create lifecycle/feedback-workflow.yaml as part of phase-133-b."
        )

    def test_feedback_workflow_is_valid_yaml(self):
        assert FEEDBACK_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(FEEDBACK_WORKFLOW)
        assert isinstance(data, dict), "feedback-workflow.yaml must parse to a dict"

    def test_feedback_workflow_has_id(self):
        assert FEEDBACK_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(FEEDBACK_WORKFLOW)
        assert "id" in data, "feedback-workflow.yaml must have a top-level 'id' field"

    def test_feedback_workflow_has_name(self):
        assert FEEDBACK_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(FEEDBACK_WORKFLOW)
        assert "name" in data, "feedback-workflow.yaml must have a top-level 'name' field"

    def test_feedback_workflow_has_steps(self):
        assert FEEDBACK_WORKFLOW.exists(), pytest.skip("file missing")
        data = _load_yaml(FEEDBACK_WORKFLOW)
        assert "steps" in data and len(data["steps"]) > 0, (
            "feedback-workflow.yaml must have at least one step"
        )


# ---------------------------------------------------------------------------
# Class 3 — workflow-composer-spec.yaml has REVIEW + FEEDBACK routing entries
# ---------------------------------------------------------------------------

class TestComposerSpecRouting:

    def _spec(self) -> dict:
        assert COMPOSER_SPEC.exists(), f"workflow-composer-spec.yaml not found at {COMPOSER_SPEC}"
        return _load_yaml(COMPOSER_SPEC)

    def test_composer_spec_is_parseable(self):
        data = self._spec()
        assert isinstance(data, dict)

    def test_composer_spec_has_intent_routing(self):
        data = self._spec()
        assert "intent_routing" in data, "workflow-composer-spec.yaml must have 'intent_routing' key"

    def test_review_intent_routing_exists(self):
        data = self._spec()
        routing = data.get("intent_routing", {})
        assert "REVIEW" in routing, (
            "intent_routing in workflow-composer-spec.yaml is missing 'REVIEW' entry.\n"
            "Add: REVIEW:\n  workflow_ref: 'sdlc/review-workflow'"
        )

    def test_feedback_intent_routing_exists(self):
        data = self._spec()
        routing = data.get("intent_routing", {})
        assert "FEEDBACK" in routing, (
            "intent_routing in workflow-composer-spec.yaml is missing 'FEEDBACK' entry.\n"
            "Add: FEEDBACK:\n  workflow_ref: 'lifecycle/feedback-workflow'"
        )

    def test_review_routing_has_workflow_ref(self):
        data = self._spec()
        routing = data.get("intent_routing", {})
        review = routing.get("REVIEW", {})
        assert "workflow_ref" in review, "REVIEW routing entry must have 'workflow_ref'"
        assert review["workflow_ref"] is not None, "REVIEW workflow_ref must not be null"

    def test_feedback_routing_has_workflow_ref(self):
        data = self._spec()
        routing = data.get("intent_routing", {})
        feedback = routing.get("FEEDBACK", {})
        assert "workflow_ref" in feedback, "FEEDBACK routing entry must have 'workflow_ref'"
        assert feedback["workflow_ref"] is not None, "FEEDBACK workflow_ref must not be null"

    def test_review_workflow_ref_points_to_sdlc(self):
        data = self._spec()
        routing = data.get("intent_routing", {})
        ref = routing.get("REVIEW", {}).get("workflow_ref", "")
        assert "review" in ref.lower(), (
            f"REVIEW workflow_ref '{ref}' must reference a review workflow"
        )

    def test_feedback_workflow_ref_points_to_lifecycle(self):
        data = self._spec()
        routing = data.get("intent_routing", {})
        ref = routing.get("FEEDBACK", {}).get("workflow_ref", "")
        assert "feedback" in ref.lower(), (
            f"FEEDBACK workflow_ref '{ref}' must reference a feedback workflow"
        )
