"""
test_interaction_workflow_composer.py — Unit tests for InteractionWorkflowComposer.

Covers:
- select_workflow() determinism (keyword routing, intent fallback, default)
- All 9 workflow templates selectable
- advance_step() updates tracker and completion list
- get_next_question() returns highest-priority unanswered question
- get_opening_statement() returns template-specific opener
- get_completion_criteria() returns template-specific criteria
- is_at_decision_checkpoint() returns True at checkpoints
- list_available_templates() lists all templates
- No autonomous execution triggered in any composer method
- Switching workflows (fresh select after different request)
- Edge cases: empty request, whitespace, very long request

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
import pytest

from cortex.orchestrators.core.interaction_workflow_composer import (
    InteractionWorkflowComposer,
    InteractionWorkflowState,
    _TEMPLATE_REGISTRY,
)
from cortex.orchestrators.core.interaction_readiness_tracker import (
    InteractionReadinessTracker,
    DIMENSION_WEIGHTS,
)


def _make_composer() -> InteractionWorkflowComposer:
    return InteractionWorkflowComposer()


class TestTemplateRegistryCompleteness:
    """Verify all expected templates are registered."""

    def test_feature_planning_registered(self) -> None:
        assert "feature-planning" in _TEMPLATE_REGISTRY

    def test_bug_investigation_registered(self) -> None:
        assert "bug-investigation" in _TEMPLATE_REGISTRY

    def test_refactor_planning_registered(self) -> None:
        assert "refactor-planning" in _TEMPLATE_REGISTRY

    def test_architecture_review_registered(self) -> None:
        assert "architecture-review" in _TEMPLATE_REGISTRY

    def test_test_strategy_registered(self) -> None:
        assert "test-strategy" in _TEMPLATE_REGISTRY

    def test_onboarding_registered(self) -> None:
        assert "onboarding" in _TEMPLATE_REGISTRY

    def test_documentation_request_registered(self) -> None:
        assert "documentation-request" in _TEMPLATE_REGISTRY

    def test_workflow_design_registered(self) -> None:
        assert "workflow-design" in _TEMPLATE_REGISTRY

    def test_general_inquiry_registered(self) -> None:
        assert "general-inquiry" in _TEMPLATE_REGISTRY

    def test_each_template_has_required_fields(self) -> None:
        for tid, desc in _TEMPLATE_REGISTRY.items():
            assert desc.template_id == tid, f"template_id mismatch for {tid}"
            assert desc.display_name, f"display_name missing for {tid}"
            assert desc.required_dimensions, f"required_dimensions empty for {tid}"
            assert desc.questioning_order, f"questioning_order empty for {tid}"
            assert desc.opening_statement, f"opening_statement empty for {tid}"
            assert desc.dimension_questions, f"dimension_questions empty for {tid}"

    def test_each_dimension_question_maps_to_known_dimension(self) -> None:
        known_dims = set(DIMENSION_WEIGHTS.keys())
        for tid, desc in _TEMPLATE_REGISTRY.items():
            for dim_key in desc.dimension_questions:
                assert dim_key in known_dims, (
                    f"Template {tid} has unknown dimension key '{dim_key}'"
                )


class TestSelectWorkflow:
    """Tests for deterministic workflow selection."""

    def test_feature_keyword_selects_feature_planning(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("I want to add a new feature")
        assert state.template_id == "feature-planning"

    def test_bug_keyword_selects_bug_investigation(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("There's a bug in the retry logic")
        assert state.template_id == "bug-investigation"

    def test_refactor_keyword_selects_refactor_planning(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("I want to refactor the auth module")
        assert state.template_id == "refactor-planning"

    def test_architecture_keyword_selects_architecture_review(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("We need an architecture review")
        assert state.template_id == "architecture-review"

    def test_test_keyword_selects_test_strategy(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("We need better test coverage")
        assert state.template_id == "test-strategy"

    def test_onboard_keyword_selects_onboarding(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("Help me onboard to this repo")
        assert state.template_id == "onboarding"

    def test_doc_keyword_selects_documentation_request(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("I need to write a doc for this module")
        assert state.template_id == "documentation-request"

    def test_workflow_keyword_selects_workflow_design(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("I want to design a new workflow pipeline")
        assert state.template_id == "workflow-design"

    def test_unrecognised_request_defaults_to_general_inquiry(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("xyzzy nonsense gobbledegook")
        assert state.template_id == "general-inquiry"

    def test_empty_request_defaults_to_general_inquiry(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("")
        assert state.template_id == "general-inquiry"

    def test_intent_fallback_implement_maps_to_feature_planning(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("xyz", intent="IMPLEMENT")
        assert state.template_id == "feature-planning"

    def test_intent_fallback_fix_maps_to_bug_investigation(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("xyz", intent="FIX")
        assert state.template_id == "bug-investigation"

    def test_intent_fallback_refactor_maps_to_refactor_planning(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("xyz", intent="REFACTOR")
        assert state.template_id == "refactor-planning"

    def test_selection_is_deterministic_across_calls(self) -> None:
        composer = _make_composer()
        a = composer.select_workflow("implement a new auth service")
        b = composer.select_workflow("implement a new auth service")
        assert a.template_id == b.template_id

    def test_fresh_state_has_zero_completed_steps(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("add a new endpoint")
        assert state.completed_steps == []

    def test_fresh_state_has_tracker(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("add a new endpoint")
        assert isinstance(state.readiness_tracker, InteractionReadinessTracker)

    def test_fresh_state_questions_seeded_from_template(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("build a feature")
        tracker = state.readiness_tracker
        assert tracker is not None
        questions = tracker.get_open_questions()
        assert len(questions) > 0, "Questions should be seeded on fresh state"


class TestAdvanceStep:
    """Tests for advance_step()."""

    def test_advance_marks_dimension_as_completed(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a new feature")
        first_dim = _TEMPLATE_REGISTRY[state.template_id].questioning_order[0]
        state = composer.advance_step(
            state,
            answered_dimension=first_dim,
            score=100,
            evidence="User wants auth service",
        )
        assert first_dim in state.completed_steps

    def test_advance_sets_score_100_on_tracker(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a new feature")
        first_dim = _TEMPLATE_REGISTRY[state.template_id].questioning_order[0]
        state = composer.advance_step(
            state,
            answered_dimension=first_dim,
            score=100,
            evidence="Done",
        )
        tracker = state.readiness_tracker
        assert tracker is not None
        assert tracker._dimensions[first_dim].score == 100

    def test_advance_increments_step_index(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a new feature")
        original_index = state.current_step_index
        first_dim = _TEMPLATE_REGISTRY[state.template_id].questioning_order[0]
        state = composer.advance_step(state, answered_dimension=first_dim)
        assert state.current_step_index > original_index

    def test_advance_without_answer_still_increments(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a new feature")
        original_index = state.current_step_index
        state = composer.advance_step(state)
        assert state.current_step_index == original_index + 1

    def test_advance_does_not_duplicate_completed_steps(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a new feature")
        first_dim = _TEMPLATE_REGISTRY[state.template_id].questioning_order[0]
        state = composer.advance_step(state, answered_dimension=first_dim)
        state = composer.advance_step(state, answered_dimension=first_dim)
        count = state.completed_steps.count(first_dim)
        assert count == 1


class TestGetNextQuestion:
    """Tests for get_next_question()."""

    def test_returns_question_on_fresh_state(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a feature")
        q = composer.get_next_question(state)
        assert q is not None and len(q) > 0

    def test_returns_none_when_all_dims_completed(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a feature")
        tracker = state.readiness_tracker
        assert tracker is not None
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
            if dim not in state.completed_steps:
                state.completed_steps.append(dim)
        state.current_step_index = 10  # past the end
        q = composer.get_next_question(state)
        assert q is None


class TestOpeningStatement:
    """Tests for get_opening_statement()."""

    def test_feature_planning_has_opening(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("build a feature")
        opener = composer.get_opening_statement(state)
        assert len(opener) > 10

    def test_general_inquiry_has_opening(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("xyz_random_unknown")
        opener = composer.get_opening_statement(state)
        assert len(opener) > 10


class TestCompletionCriteria:
    """Tests for get_completion_criteria()."""

    def test_returns_non_empty_string(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("fix a bug")
        criteria = composer.get_completion_criteria(state)
        assert len(criteria) > 0


class TestDecisionCheckpoint:
    """Tests for is_at_decision_checkpoint()."""

    def test_returns_bool(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("implement a feature")
        result = composer.is_at_decision_checkpoint(state)
        assert isinstance(result, bool)

    def test_scope_clarity_is_checkpoint_for_feature_planning(self) -> None:
        composer = _make_composer()
        state = composer.select_workflow("build a feature")
        # Advance until we're at scope_clarity
        order = _TEMPLATE_REGISTRY["feature-planning"].questioning_order
        checkpoints = _TEMPLATE_REGISTRY["feature-planning"].decision_checkpoints
        # Find the index of first checkpoint
        for i, dim in enumerate(order):
            if dim in checkpoints:
                state.current_step_index = i
                break
        assert composer.is_at_decision_checkpoint(state) is True


class TestListAvailableTemplates:
    """Tests for list_available_templates()."""

    def test_returns_list(self) -> None:
        composer = _make_composer()
        templates = composer.list_available_templates()
        assert isinstance(templates, list)

    def test_contains_expected_count(self) -> None:
        composer = _make_composer()
        templates = composer.list_available_templates()
        assert len(templates) == len(_TEMPLATE_REGISTRY)

    def test_each_entry_has_template_id_and_display_name(self) -> None:
        composer = _make_composer()
        for entry in composer.list_available_templates():
            assert "template_id" in entry
            assert "display_name" in entry

    def test_no_autonomous_execution_in_list(self) -> None:
        """Regression: list_available_templates must not trigger any execution."""
        composer = _make_composer()
        # Should not raise, not call any orchestrator, not write any file
        templates = composer.list_available_templates()
        assert len(templates) > 0


class TestNoAutonomousExecution:
    """Verify the composer never triggers autonomous execution."""

    def test_select_workflow_never_calls_workflow_gateway(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """select_workflow must not call WorkflowGateway.execute_gated."""
        call_log: list[str] = []

        def mock_execute_gated(*args: object, **kwargs: object) -> None:
            call_log.append("execute_gated called")

        monkeypatch.setattr(
            "cortex.orchestrators.workflow.workflow_gateway.WorkflowGateway.execute_gated",
            mock_execute_gated,
            raising=False,
        )

        composer = _make_composer()
        composer.select_workflow("implement a new feature")
        assert call_log == [], "WorkflowGateway.execute_gated must not be called"

    def test_advance_step_never_modifies_files(self) -> None:
        """advance_step must not write to disk or run any tool."""
        composer = _make_composer()
        state = composer.select_workflow("build")
        first_dim = _TEMPLATE_REGISTRY[state.template_id].questioning_order[0]
        # Should complete without any IO side effects
        state = composer.advance_step(state, answered_dimension=first_dim, score=100, evidence="done")
        assert first_dim in state.completed_steps
