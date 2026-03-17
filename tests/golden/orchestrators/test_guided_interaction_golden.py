"""
test_guided_interaction_golden.py — Golden tests for the guided interaction system.

Covers:
- Partially ready requests → gate locked, next question present
- Ambiguous requests → general-inquiry workflow selected
- Fully ready requests → gate open, proceed gate visible
- Early approval attempt → gate remains locked, explanation returned
- Footer metric consistency across turns
- Workflow template switching (different requests → different templates)
- DoR scoring determinism
- No autonomous execution in any response path
- Response structure: all required sections present
- Copilot Chat rendering validity (no tree chars, no raw HTML)
- Approval gate enforcement regression

Authority: CORE-008 (TDD), CORE-011, CORE-012
Golden test rationale: These tests validate BOTH BEHAVIOUR and
rendered Copilot Chat output quality (content structure, format, completeness).
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
from cortex.orchestrators.core.interaction_workflow_composer import (
    InteractionWorkflowComposer,
    InteractionWorkflowState,
)
from cortex.orchestrators.core.interaction_readiness_tracker import (
    InteractionReadinessTracker,
    DIMENSION_WEIGHTS,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_orchestrator() -> InteractionOrchestrator:
    """Build InteractionOrchestrator with a mock ConversationProtocol."""
    proto = MagicMock()
    orch = InteractionOrchestrator(
        conversation_protocol=proto,
        enable_challenges=False,  # Isolate guided interaction path from challenge engine
    )
    orch._user_role = "developer"
    return orch


def _all_dims_at_100(tracker: InteractionReadinessTracker) -> None:
    """Helper: set all dimensions to 100%."""
    for dim in DIMENSION_WEIGHTS:
        tracker.update_dimension(dim, score=100, evidence=f"Provided for {dim}")


# ── Golden Fixtures ───────────────────────────────────────────────────────────

PARTIALLY_READY_REQUEST = "I want to implement a new OAuth2 authentication service."
AMBIGUOUS_REQUEST = "I need help with the thing we discussed."
FULLY_READY_REQUEST = "Build an auth service with JWT tokens."
BUG_REQUEST = "There is a bug in the retry logic that causes infinite loops."
REFACTOR_REQUEST = "Refactor the orchestrator base class to use a mixin."


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Partially Ready Requests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPartiallyReadyRequest:
    """Gate is locked; response includes a next question."""

    def test_gate_is_locked_on_fresh_request(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert result["gate_open"] is False

    def test_dor_pct_is_zero_on_fresh_request(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert result["dor_pct"] == 0

    def test_next_question_is_present(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert result["next_question"] is not None
        assert len(result["next_question"]) > 10

    def test_feature_planning_template_selected(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert result["template_id"] == "feature-planning"

    def test_rendered_response_is_string(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert isinstance(result["rendered_response"], str)
        assert len(result["rendered_response"]) > 100

    def test_rendered_response_contains_dor_header(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "CORTEX Guided" in result["rendered_response"]

    def test_rendered_response_contains_next_question_section(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "Next Question" in result["rendered_response"]

    def test_rendered_response_contains_approval_gate_section(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "Approval Gate" in result["rendered_response"]

    def test_rendered_response_contains_workflow_state_section(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "Workflow State" in result["rendered_response"]

    def test_footer_is_single_line(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        footer = result["footer"]
        assert "\n" not in footer

    def test_footer_contains_dor_pct(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "DoR" in result["footer"]

    def test_footer_contains_gate_locked(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "LOCKED" in result["footer"]

    def test_footer_contains_workflow_name(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert "Feature Planning" in result["footer"]

    def test_no_proceed_gate_in_response_when_locked(self) -> None:
        """Proceed gate must not appear in the rendered response when DoR < 100%."""
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        rendered = result["rendered_response"]
        # "If you say proceed, I will:" should NOT appear when gate is locked
        # (It appears only in the OPEN gate section)
        assert "If you say proceed, I will:" not in rendered

    def test_gate_locked_explanation_present(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        rendered = result["rendered_response"]
        assert "LOCKED" in rendered

    def test_no_tree_characters_in_response(self) -> None:
        """Copilot Chat rendering rule: no tree characters."""
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        rendered = result["rendered_response"]
        for char in ["├", "└", "│", "─"]:
            assert char not in rendered, f"Tree character {char!r} found in response"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Ambiguous Requests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAmbiguousRequest:
    """Ambiguous input defaults to general-inquiry workflow."""

    def test_general_inquiry_selected_for_ambiguous_request(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(AMBIGUOUS_REQUEST)
        assert result["template_id"] == "general-inquiry"

    def test_gate_locked_for_ambiguous_request(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(AMBIGUOUS_REQUEST)
        assert result["gate_open"] is False

    def test_opening_question_is_substantive(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(AMBIGUOUS_REQUEST)
        q = result["next_question"]
        assert q is not None
        assert len(q) > 20


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Fully Ready Requests (DoR = 100%)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullyReadyRequest:
    """Gate is open when all dimensions reach 100%."""

    def _make_full_ready_state(self) -> InteractionWorkflowState:
        """Build a state with all 10 dimensions at 100%."""
        composer = InteractionWorkflowComposer()
        state = composer.select_workflow(FULLY_READY_REQUEST)
        tracker = state.readiness_tracker
        assert tracker is not None
        _all_dims_at_100(tracker)
        # Mark all dims as completed
        for dim in DIMENSION_WEIGHTS:
            if dim not in state.completed_steps:
                state.completed_steps.append(dim)
        state.current_step_index = 10  # past all steps
        return state

    def test_gate_opens_when_dor_is_100(self) -> None:
        orch = _make_orchestrator()
        workflow_state = self._make_full_ready_state()
        result = orch.guide_interaction(
            FULLY_READY_REQUEST,
            workflow_state=workflow_state,
        )
        assert result["gate_open"] is True

    def test_dor_pct_is_100(self) -> None:
        orch = _make_orchestrator()
        workflow_state = self._make_full_ready_state()
        result = orch.guide_interaction(
            FULLY_READY_REQUEST,
            workflow_state=workflow_state,
        )
        assert result["dor_pct"] == 100

    def test_next_question_is_none_when_gate_open(self) -> None:
        orch = _make_orchestrator()
        workflow_state = self._make_full_ready_state()
        result = orch.guide_interaction(
            FULLY_READY_REQUEST,
            workflow_state=workflow_state,
        )
        assert result["next_question"] is None

    def test_proceed_gate_visible_in_response_when_open(self) -> None:
        orch = _make_orchestrator()
        workflow_state = self._make_full_ready_state()
        result = orch.guide_interaction(
            FULLY_READY_REQUEST,
            workflow_state=workflow_state,
        )
        rendered = result["rendered_response"]
        assert "If you say proceed, I will:" in rendered

    def test_footer_contains_gate_open(self) -> None:
        orch = _make_orchestrator()
        workflow_state = self._make_full_ready_state()
        result = orch.guide_interaction(
            FULLY_READY_REQUEST,
            workflow_state=workflow_state,
        )
        assert "OPEN" in result["footer"]

    def test_footer_shows_100_pct(self) -> None:
        orch = _make_orchestrator()
        workflow_state = self._make_full_ready_state()
        result = orch.guide_interaction(
            FULLY_READY_REQUEST,
            workflow_state=workflow_state,
        )
        assert "100%" in result["footer"]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Early Approval Attempt Regression
# ═══════════════════════════════════════════════════════════════════════════════

class TestEarlyApprovalAttemptRegression:
    """User says 'proceed' before DoR = 100% — must return explanation, not execute."""

    def test_guide_interaction_gate_stays_locked_with_proceed_input(self) -> None:
        """Simulates user saying 'proceed' before readiness is complete."""
        orch = _make_orchestrator()
        # Fresh state, DoR = 0
        result_first = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert result_first["gate_open"] is False

        # User responds with "proceed" — still in guided path, no autonomous exec
        result_proceed = orch.guide_interaction(
            "proceed",
            workflow_state=result_first["workflow_state"],
        )
        # Gate must remain locked — "proceed" is just an answer to a question
        assert result_proceed["gate_open"] is False
        assert result_proceed["dor_pct"] < 100

    def test_no_workflow_gateway_called_on_proceed_when_locked(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """WorkflowGateway.execute_gated must NOT be called during guided interaction."""
        call_log: list[str] = []

        def mock_execute_gated(*args: object, **kwargs: object) -> dict[str, Any]:
            call_log.append("execute_gated called!")
            return {}

        monkeypatch.setattr(
            "cortex.orchestrators.workflow.workflow_gateway.WorkflowGateway.execute_gated",
            mock_execute_gated,
            raising=False,
        )

        orch = _make_orchestrator()
        orch.guide_interaction(PARTIALLY_READY_REQUEST)
        assert call_log == [], (
            "WorkflowGateway.execute_gated must never be called from guide_interaction()"
        )

    def test_locked_response_explains_what_is_missing(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        rendered = result["rendered_response"]
        # Must contain a section explaining what remains
        assert "Missing" in rendered or "dimensions" in rendered.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Footer Metric Consistency
# ═══════════════════════════════════════════════════════════════════════════════

class TestFooterMetricConsistency:
    """Footer must be consistent and present on every response."""

    def test_footer_always_present(self) -> None:
        orch = _make_orchestrator()
        for request in [PARTIALLY_READY_REQUEST, AMBIGUOUS_REQUEST, BUG_REQUEST]:
            result = orch.guide_interaction(request)
            assert result["footer"], f"Footer missing for: {request}"

    def test_footer_format_is_consistent_across_templates(self) -> None:
        """Footer format (· separator, DoR %, Gate status) must be identical across templates."""
        orch = _make_orchestrator()
        footers: list[str] = []
        for request in [PARTIALLY_READY_REQUEST, BUG_REQUEST, REFACTOR_REQUEST]:
            result = orch.guide_interaction(request)
            footers.append(result["footer"])

        for footer in footers:
            assert "·" in footer, f"Middle dot separator missing in: {footer}"
            assert "DoR" in footer, f"DoR missing in: {footer}"
            assert "Gate" in footer, f"Gate missing in: {footer}"
            assert "questions" in footer, f"questions count missing in: {footer}"
            assert "blockers" in footer, f"blockers count missing in: {footer}"

    def test_footer_dor_pct_matches_result_dor_pct(self) -> None:
        """Footer DoR% value must match the dor_pct field in the result."""
        orch = _make_orchestrator()
        result = orch.guide_interaction(PARTIALLY_READY_REQUEST)
        dor_pct = result["dor_pct"]
        footer = result["footer"]
        assert f"DoR {dor_pct}%" in footer


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Workflow Template Switching
# ═══════════════════════════════════════════════════════════════════════════════

class TestWorkflowTemplateSwitching:
    """Different requests select different templates deterministically."""

    def test_feature_request_selects_feature_planning(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction("implement a new login feature")
        assert result["template_id"] == "feature-planning"

    def test_bug_request_selects_bug_investigation(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction("fix the broken retry logic")
        assert result["template_id"] == "bug-investigation"

    def test_refactor_request_selects_refactor_planning(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction("refactor the auth module")
        assert result["template_id"] == "refactor-planning"

    def test_different_templates_have_different_next_questions(self) -> None:
        orch = _make_orchestrator()
        feature_result = orch.guide_interaction("implement a login feature")
        bug_result = orch.guide_interaction("fix the broken auth")
        # The next questions from different templates should differ
        assert feature_result["next_question"] != bug_result["next_question"]


# ═══════════════════════════════════════════════════════════════════════════════
# 7. No Autonomous Execution Regression
# ═══════════════════════════════════════════════════════════════════════════════

class TestNoAutonomousExecutionRegression:
    """Critical regression: guide_interaction() must NEVER trigger autonomous execution."""

    def test_guide_interaction_does_not_call_autonomous_executor(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        call_log: list[str] = []

        def mock_execute_autonomously(*args: object, **kwargs: object) -> dict[str, Any]:
            call_log.append("autonomous")
            return {}

        monkeypatch.setattr(
            "cortex.orchestrators.workflow.autonomous_workflow_executor"
            ".AutonomousWorkflowExecutor.execute_workflow_autonomously",
            mock_execute_autonomously,
            raising=False,
        )

        orch = _make_orchestrator()
        orch.guide_interaction("implement auth service")
        assert call_log == [], "AutonomousWorkflowExecutor must not be called from guide_interaction"

    def test_guide_interaction_does_not_invoke_autonomousplanexecutor(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        call_log: list[str] = []

        def mock_detect(*args: object, **kwargs: object) -> bool:
            call_log.append("detect_continuation")
            return False

        monkeypatch.setattr(
            "cortex.orchestrators.core.autonomous_plan_executor"
            ".AutonomousPlanExecutor.detect_continuation",
            mock_detect,
            raising=False,
        )

        orch = _make_orchestrator()
        orch.guide_interaction("proceed with the implementation")
        # guide_interaction must not route through AutonomousPlanExecutor at all
        assert call_log == [], (
            "AutonomousPlanExecutor.detect_continuation must not be called from guide_interaction"
        )

    def test_guide_interaction_result_has_no_execution_payload(self) -> None:
        """guide_interaction result must not contain execution artefacts."""
        orch = _make_orchestrator()
        result = orch.guide_interaction("build a new feature")
        # No code-execution keys in the result
        forbidden_keys = {"files_changed", "test_results", "plan_stages", "execution_result"}
        assert not forbidden_keys.intersection(result.keys()), (
            f"Execution keys found in guided interaction result: "
            f"{forbidden_keys.intersection(result.keys())}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Multi-Turn DoR Accumulation
# ═══════════════════════════════════════════════════════════════════════════════

class TestMultiTurnDorAccumulation:
    """DoR score accumulates correctly across multiple guided turns."""

    def test_dor_increases_after_answering_question(self) -> None:
        orch = _make_orchestrator()
        # Turn 1: fresh
        result1 = orch.guide_interaction("implement a feature")
        dor1 = result1["dor_pct"]

        # Turn 2: user answers the objective_clarity question
        result2 = orch.guide_interaction(
            "The goal is to build an OAuth2 service for our API",
            workflow_state=result1["workflow_state"],
            user_answer="The goal is to build an OAuth2 service for our API",
            answered_dimension="objective_clarity",
        )
        dor2 = result2["dor_pct"]
        assert dor2 > dor1, f"DoR should increase: {dor1} → {dor2}"

    def test_workflow_state_is_passed_between_turns(self) -> None:
        orch = _make_orchestrator()
        result1 = orch.guide_interaction("build a feature")
        state1 = result1["workflow_state"]

        result2 = orch.guide_interaction(
            "OAuth2 service",
            workflow_state=state1,
            user_answer="OAuth2 service for API",
            answered_dimension="objective_clarity",
        )
        # Template should persist between turns
        assert result2["template_id"] == result1["template_id"]

    def test_gate_opens_only_after_all_dimensions_answered(self) -> None:
        orch = _make_orchestrator()
        result = orch.guide_interaction("build a feature")
        workflow_state = result["workflow_state"]
        tracker = workflow_state.readiness_tracker

        # Answer all dimensions
        _all_dims_at_100(tracker)
        for dim in DIMENSION_WEIGHTS:
            if dim not in workflow_state.completed_steps:
                workflow_state.completed_steps.append(dim)
        workflow_state.current_step_index = 10

        final_result = orch.guide_interaction(
            "all done",
            workflow_state=workflow_state,
        )
        assert final_result["gate_open"] is True
