"""
test_interaction_readiness_tracker.py — Unit tests for InteractionReadinessTracker.

Covers:
- All 10 readiness dimensions are tracked
- Weighted composite DoR % is computed deterministically
- Gate opens ONLY at 100%
- Blockers force gate to remain closed at any score
- update_dimension rejects unknown keys (ValueError)
- get_missing_dimensions / get_open_questions / get_next_question
- Footer line format matches spec
- reset() clears all state
- Edge cases: partial update, single dimension, max score

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
import pytest

from cortex.orchestrators.core.interaction_readiness_tracker import (
    DIMENSION_WEIGHTS,
    DOR_GATE_THRESHOLD,
    InteractionReadinessTracker,
    ReadinessDimension,
    ReadinessState,
)


class TestInteractionReadinessTrackerConstruction:
    """Tests for initial state after construction."""

    def test_all_dimensions_present_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        assert set(tracker._dimensions.keys()) == set(DIMENSION_WEIGHTS.keys())

    def test_all_dimension_scores_zero_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in tracker._dimensions.values():
            assert dim.score == 0, f"Expected 0 for {dim.name}"

    def test_all_dimensions_missing_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in tracker._dimensions.values():
            assert dim.missing is True

    def test_no_blockers_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        assert tracker._blockers == []

    def test_composite_is_zero_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        assert tracker.compute_dor_percentage() == 0

    def test_gate_is_closed_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        assert tracker.is_gate_open() is False

    def test_weights_sum_to_one(self) -> None:
        total = sum(DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, expected 1.0"


class TestUpdateDimension:
    """Tests for update_dimension()."""

    def test_update_known_dimension_sets_score(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=80, evidence="Auth service")
        assert tracker._dimensions["objective_clarity"].score == 80

    def test_update_sets_evidence(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("scope_clarity", score=50, evidence="In scope: API layer")
        assert tracker._dimensions["scope_clarity"].evidence == "In scope: API layer"

    def test_update_clears_open_question_when_score_100(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension(
            "objective_clarity", score=0, open_question="What's the goal?"
        )
        tracker.update_dimension("objective_clarity", score=100, evidence="Done")
        assert tracker._dimensions["objective_clarity"].open_question is None

    def test_update_keeps_open_question_when_score_less_than_100(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension(
            "objective_clarity", score=50, open_question="What's the goal?"
        )
        assert tracker._dimensions["objective_clarity"].open_question == "What's the goal?"

    def test_update_sets_missing_false_when_score_100(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=100)
        assert tracker._dimensions["objective_clarity"].missing is False

    def test_update_keeps_missing_true_when_score_less_than_100(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=99)
        assert tracker._dimensions["objective_clarity"].missing is True

    def test_update_clamps_score_below_zero(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=-10)
        assert tracker._dimensions["objective_clarity"].score == 0

    def test_update_clamps_score_above_100(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=200)
        assert tracker._dimensions["objective_clarity"].score == 100

    def test_update_unknown_dimension_raises_valueerror(self) -> None:
        tracker = InteractionReadinessTracker()
        with pytest.raises(ValueError, match="Unknown readiness dimension"):
            tracker.update_dimension("nonexistent_dim", score=100)


class TestDorComputation:
    """Tests for compute_dor_percentage()."""

    def test_single_dimension_objective_clarity_at_100(self) -> None:
        """objective_clarity weight=0.20 → 100*0.20 = 20 total score."""
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=100)
        result = tracker.compute_dor_percentage()
        assert result == 20  # 100 * 0.20

    def test_all_at_100_returns_100(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        assert tracker.compute_dor_percentage() == 100

    def test_all_at_50_returns_50(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=50)
        result = tracker.compute_dor_percentage()
        assert result == 50

    def test_all_at_0_returns_0(self) -> None:
        tracker = InteractionReadinessTracker()
        assert tracker.compute_dor_percentage() == 0

    def test_blocker_forces_score_to_zero(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        tracker.add_blocker("External team dependency unresolved")
        assert tracker.compute_dor_percentage() == 0

    def test_score_is_deterministic_across_calls(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=60)
        tracker.update_dimension("scope_clarity", score=80)
        a = tracker.compute_dor_percentage()
        b = tracker.compute_dor_percentage()
        assert a == b


class TestGate:
    """Tests for is_gate_open()."""

    def test_gate_closed_at_zero(self) -> None:
        tracker = InteractionReadinessTracker()
        assert tracker.is_gate_open() is False

    def test_gate_closed_at_99(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        # Force one dimension back to 99 to simulate near-complete
        tracker.update_dimension("ownership", score=99)
        assert tracker.is_gate_open() is False

    def test_gate_open_at_100(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        assert tracker.is_gate_open() is True

    def test_gate_closed_when_blocker_present_even_if_100(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        tracker.add_blocker("critical dependency missing")
        assert tracker.is_gate_open() is False

    def test_gate_opens_after_blocker_cleared(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        tracker.add_blocker("temp blocker")
        tracker.clear_blocker("temp blocker")
        assert tracker.is_gate_open() is True


class TestMissingDimensions:
    """Tests for get_missing_dimensions() and get_open_questions()."""

    def test_all_dimensions_missing_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        missing = tracker.get_missing_dimensions()
        assert len(missing) == len(DIMENSION_WEIGHTS)

    def test_resolved_dimensions_not_in_missing(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=100)
        missing = tracker.get_missing_dimensions()
        assert "Objective Clarity" not in missing

    def test_open_questions_empty_on_init(self) -> None:
        tracker = InteractionReadinessTracker()
        assert tracker.get_open_questions() == []

    def test_open_questions_includes_seeded_questions(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension(
            "objective_clarity", score=0, open_question="What is the goal?"
        )
        questions = tracker.get_open_questions()
        assert "What is the goal?" in questions

    def test_get_next_question_returns_highest_weight(self) -> None:
        tracker = InteractionReadinessTracker()
        # Seed two questions — objective_clarity (weight 0.20) and ownership (weight 0.05)
        tracker.update_dimension(
            "objective_clarity", score=0, open_question="What is the goal?"
        )
        tracker.update_dimension(
            "ownership", score=0, open_question="Who owns this?"
        )
        next_q = tracker.get_next_question()
        # Should pick objective_clarity (highest weight)
        assert next_q == "What is the goal?"

    def test_get_next_question_returns_none_when_all_resolved(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        assert tracker.get_next_question() is None


class TestReadinessState:
    """Tests for get_state()."""

    def test_state_has_all_required_fields(self) -> None:
        tracker = InteractionReadinessTracker()
        state = tracker.get_state()
        assert hasattr(state, "dimensions")
        assert hasattr(state, "composite_pct")
        assert hasattr(state, "gate_open")
        assert hasattr(state, "missing_dimensions")
        assert hasattr(state, "open_questions")
        assert hasattr(state, "blockers")

    def test_state_gate_open_false_when_incomplete(self) -> None:
        tracker = InteractionReadinessTracker()
        state = tracker.get_state()
        assert state.gate_open is False

    def test_state_gate_open_true_when_complete(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        state = tracker.get_state()
        assert state.gate_open is True


class TestReset:
    """Tests for reset()."""

    def test_reset_clears_scores(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=100)
        tracker.reset()
        assert tracker._dimensions["objective_clarity"].score == 0

    def test_reset_clears_blockers(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.add_blocker("blocker one")
        tracker.reset()
        assert tracker._blockers == []

    def test_reset_makes_gate_closed(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        tracker.reset()
        assert tracker.is_gate_open() is False


class TestFooterLine:
    """Tests for get_footer_line()."""

    def test_footer_contains_dor_percentage(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=100)
        footer = tracker.get_footer_line(workflow_name="feature-planning")
        assert "DoR" in footer

    def test_footer_contains_gate_locked_when_incomplete(self) -> None:
        tracker = InteractionReadinessTracker()
        footer = tracker.get_footer_line()
        assert "LOCKED" in footer

    def test_footer_contains_gate_open_when_complete(self) -> None:
        tracker = InteractionReadinessTracker()
        for dim in DIMENSION_WEIGHTS:
            tracker.update_dimension(dim, score=100)
        footer = tracker.get_footer_line()
        assert "OPEN" in footer

    def test_footer_contains_workflow_name(self) -> None:
        tracker = InteractionReadinessTracker()
        footer = tracker.get_footer_line(workflow_name="bug-investigation")
        assert "bug-investigation" in footer

    def test_footer_is_single_line(self) -> None:
        tracker = InteractionReadinessTracker()
        footer = tracker.get_footer_line(workflow_name="general-inquiry")
        assert "\n" not in footer

    def test_footer_contains_question_count(self) -> None:
        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=0, open_question="Q1?")
        footer = tracker.get_footer_line()
        assert "1 questions" in footer or "questions" in footer

    def test_footer_middle_dot_separator(self) -> None:
        tracker = InteractionReadinessTracker()
        footer = tracker.get_footer_line(workflow_name="test")
        assert "·" in footer, "Footer must use middle dot separator"
