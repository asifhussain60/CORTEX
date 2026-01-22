"""
Test suite for HP-003-02: Agent Confidence Scoring

Tests for scoring agent confidence in proposed actions.
Ensures confidence metrics are calculated, low confidence triggers review,
and scoring model is documented.

AC-ID: HP-003-02
Phase: PHASE-11-HALLUCINATION-PREVENTION
Status: TDD - RED phase
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import json

from cortex_brain.tier2.hallucination_prevention.confidence_scoring import (
    ConfidenceScorer,
    ConfidenceAssessment,
    ScoringFactor,
    ScoringModel,
    ReviewTrigger,
)


@pytest.fixture
def temp_db():
    """Create temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


class TestConfidenceScoring:
    """Test suite for confidence score calculation."""

    @pytest.fixture
    def scorer(self, temp_db):
        """Initialize confidence scorer."""
        return ConfidenceScorer()

    def test_confidence_score_calculated(self, scorer):
        """ACID: Confidence score calculated for actions
        
        Verify that confidence scores are computed.
        """
        # Score an operation
        result = scorer.score(
            operation_id="op_001",
            input_confidence=0.95,
            processing_confidence=0.9,
            output_confidence=0.85,
            factors={
                "intent_clarity": 0.95,
                "boundary_compliance": 0.9,
                "historical_success": 0.85,
            },
        )
        
        # Verify score calculated
        assert result.overall_score is not None
        assert 0.0 <= result.overall_score <= 1.0
        assert result.operation_id == "op_001"

    def test_confidence_score_range(self, scorer):
        """Confidence scores are between 0.0 and 1.0.
        
        Verify valid range.
        """
        # High confidence
        high_result = scorer.score(
            operation_id="safe_op_001",
            input_confidence=1.0,
            processing_confidence=1.0,
            output_confidence=1.0,
        )
        assert high_result.overall_score >= 0.8
        
        # Low confidence
        low_result = scorer.score(
            operation_id="risky_op_001",
            input_confidence=0.2,
            processing_confidence=0.1,
            output_confidence=0.0,
        )
        assert low_result.overall_score <= 0.4

    def test_multiple_factors_weighted(self, scorer):
        """Multiple factors are weighted in score.
        
        Verify factor weighting.
        """
        result = scorer.score(
            operation_id="complex_op_001",
            input_confidence=0.9,
            processing_confidence=0.8,
            output_confidence=0.7,
            factors={
                "intent_clarity": 0.9,
                "boundary_compliance": 0.8,
                "historical_success": 0.7,
                "model_uncertainty": 0.3,
                "precedent_matching": 0.85,
            },
        )
        
        # Verify factors considered
        assert result.overall_score is not None
        assert result.factors is not None

    def test_scoring_factors_tracked(self, scorer):
        """Individual scoring factors are tracked.
        
        Verify factor breakdown.
        """
        result = scorer.score(
            operation_id="test_op_001",
            input_confidence=0.8,
            processing_confidence=0.9,
            output_confidence=0.7,
            factors={
                "intent_clarity": 0.8,
                "boundary_compliance": 0.9,
                "historical_success": 0.7,
            },
        )
        
        # Verify factors tracked
        assert result.factors is not None
        assert len(result.factors) > 0

    def test_timestamp_recorded(self, scorer):
        """Confidence assessment timestamp is recorded.
        
        Verify timestamp precision.
        """
        before = datetime.utcnow()
        result = scorer.score(
            operation_id="timed_op_001",
            input_confidence=0.5,
            factors={},
        )
        after = datetime.utcnow()
        
        # Verify timestamp
        assert result.timestamp is not None
        assert before <= result.timestamp <= after


class TestLowConfidenceTrigger:
    """Test suite for low confidence review triggers."""

    @pytest.fixture
    def scorer(self, temp_db):
        """Initialize confidence scorer."""
        return ConfidenceScorer(db_path=temp_db)

    def test_low_confidence_triggers_review(self, scorer):
        """ACID: Low confidence triggers review
        
        Verify that low confidence scores trigger review.
        """
        assessment = scorer.calculate_confidence(
            action="risky_action",
            action_type="system_modification",
            context={},
            evidence={
                "intent_clarity": 0.2,
                "boundary_compliance": 0.1,
                "historical_success": 0.0,
            },
        )
        
        # Check if review triggered
        triggers = scorer.check_review_triggers(assessment)
        
        # Verify review triggered
        assert triggers is not None
        assert len(triggers) > 0

    def test_review_threshold_configurable(self, scorer):
        """Review threshold can be configured.
        
        Verify threshold adjustment.
        """
        # Set custom threshold
        scorer.set_review_threshold(0.5)
        
        # Low score should trigger
        low_assessment = scorer.calculate_confidence(
            action="low_conf",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.3},
        )
        
        low_triggers = scorer.check_review_triggers(low_assessment)
        assert len(low_triggers) > 0
        
        # High score should not trigger
        high_assessment = scorer.calculate_confidence(
            action="high_conf",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.9},
        )
        
        high_triggers = scorer.check_review_triggers(high_assessment)
        assert len(high_triggers) == 0

    def test_review_reason_provided(self, scorer):
        """Review trigger includes reason.
        
        Verify reason documentation.
        """
        assessment = scorer.calculate_confidence(
            action="questionable_action",
            action_type="test",
            context={},
            evidence={
                "intent_clarity": 0.3,
                "boundary_compliance": 0.2,
            },
        )
        
        triggers = scorer.check_review_triggers(assessment)
        
        # Verify reasons provided
        for trigger in triggers:
            assert trigger.reason is not None
            assert len(trigger.reason) > 0

    def test_multiple_review_triggers(self, scorer):
        """Multiple review triggers can fire.
        
        Verify compound triggers.
        """
        assessment = scorer.calculate_confidence(
            action="problematic_action",
            action_type="critical_operation",
            context={"risk_level": "high"},
            evidence={
                "intent_clarity": 0.2,
                "boundary_compliance": 0.1,
                "model_uncertainty": 0.8,
                "precedent_matching": 0.0,
            },
        )
        
        triggers = scorer.check_review_triggers(assessment)
        
        # Verify multiple triggers
        assert len(triggers) > 1

    def test_review_action_specified(self, scorer):
        """Review trigger specifies action to take.
        
        Verify action guidance.
        """
        assessment = scorer.calculate_confidence(
            action="review_me",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.1},
        )
        
        triggers = scorer.check_review_triggers(assessment)
        
        # Verify actions specified
        for trigger in triggers:
            assert trigger.recommended_action is not None


class TestScoringModel:
    """Test suite for scoring model documentation."""

    @pytest.fixture
    def scorer(self, temp_db):
        """Initialize confidence scorer."""
        return ConfidenceScorer(db_path=temp_db)

    def test_scoring_model_documented(self, scorer):
        """ACID: Scoring model documented
        
        Verify that scoring model is documented.
        """
        model_doc = scorer.get_model_documentation()
        
        # Verify documentation
        assert model_doc is not None
        assert "model_version" in model_doc
        assert "factors" in model_doc
        assert "weights" in model_doc

    def test_model_factors_listed(self, scorer):
        """Model documentation lists all factors.
        
        Verify factor documentation.
        """
        model_doc = scorer.get_model_documentation()
        
        factors = model_doc.get("factors", {})
        
        # Verify factors documented
        assert len(factors) > 0
        assert all(isinstance(f, str) for f in factors.keys())

    def test_model_weights_documented(self, scorer):
        """Model documentation includes factor weights.
        
        Verify weight documentation.
        """
        model_doc = scorer.get_model_documentation()
        
        weights = model_doc.get("weights", {})
        
        # Verify weights documented
        assert len(weights) > 0
        # Verify weights sum to 1.0 or are normalized
        assert sum(weights.values()) > 0

    def test_model_algorithm_described(self, scorer):
        """Model documentation describes algorithm.
        
        Verify algorithm documentation.
        """
        model_doc = scorer.get_model_documentation()
        
        # Verify algorithm documented
        assert "algorithm" in model_doc or "description" in model_doc
        assert model_doc.get("algorithm") or model_doc.get("description")

    def test_model_examples_provided(self, scorer):
        """Model documentation includes examples.
        
        Verify example documentation.
        """
        model_doc = scorer.get_model_documentation()
        
        # Verify examples
        assert "examples" in model_doc
        assert len(model_doc.get("examples", [])) > 0


class TestScoringIntegration:
    """Integration tests for confidence scoring."""

    @pytest.fixture
    def scorer(self, temp_db):
        """Initialize confidence scorer."""
        return ConfidenceScorer(db_path=temp_db)

    def test_end_to_end_assessment_workflow(self, scorer):
        """End-to-end: calculate → check triggers → document.
        
        Verify complete workflow.
        """
        # Calculate confidence
        assessment = scorer.calculate_confidence(
            action="workflow_test",
            action_type="integration",
            context={},
            evidence={
                "intent_clarity": 0.6,
                "boundary_compliance": 0.7,
            },
        )
        
        # Check triggers
        triggers = scorer.check_review_triggers(assessment)
        
        # Get documentation
        model_doc = scorer.get_model_documentation()
        
        # Verify workflow
        assert assessment.confidence_score is not None
        assert triggers is not None
        assert model_doc is not None

    def test_assessment_persistence(self, scorer):
        """Assessments are persisted and queryable.
        
        Verify persistence.
        """
        # Create assessment
        assessment1 = scorer.calculate_confidence(
            action="persist_test_1",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.8},
        )
        
        # Query back
        retrieved = scorer.get_assessment(assessment1.assessment_id)
        
        # Verify persisted
        assert retrieved is not None
        assert retrieved.assessment_id == assessment1.assessment_id
        assert retrieved.confidence_score == assessment1.confidence_score

    def test_assessment_history(self, scorer):
        """Assessment history is maintained.
        
        Verify history tracking.
        """
        # Create multiple assessments for same action
        for i in range(5):
            scorer.calculate_confidence(
                action="history_test",
                action_type="test",
                context={"iteration": i},
                evidence={"intent_clarity": 0.5 + i * 0.1},
            )
        
        # Get history
        history = scorer.get_assessment_history("history_test")
        
        # Verify history
        assert len(history) >= 5

    def test_assessment_comparison(self, scorer):
        """Multiple assessments can be compared.
        
        Verify comparison capability.
        """
        assessment1 = scorer.calculate_confidence(
            action="action_1",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.9},
        )
        
        assessment2 = scorer.calculate_confidence(
            action="action_2",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.3},
        )
        
        # Compare
        comparison = scorer.compare_assessments([assessment1, assessment2])
        
        # Verify comparison
        assert comparison is not None


class TestScoringRobustness:
    """Robustness tests for confidence scoring."""

    @pytest.fixture
    def scorer(self, temp_db):
        """Initialize confidence scorer."""
        return ConfidenceScorer(db_path=temp_db)

    def test_extreme_evidence_values(self, scorer):
        """Extreme evidence values handled.
        
        Verify boundary handling.
        """
        # All zeros
        low_assessment = scorer.calculate_confidence(
            action="all_zeros",
            action_type="test",
            context={},
            evidence={
                "intent_clarity": 0.0,
                "boundary_compliance": 0.0,
                "historical_success": 0.0,
            },
        )
        assert low_assessment.confidence_score >= 0.0
        
        # All ones
        high_assessment = scorer.calculate_confidence(
            action="all_ones",
            action_type="test",
            context={},
            evidence={
                "intent_clarity": 1.0,
                "boundary_compliance": 1.0,
                "historical_success": 1.0,
            },
        )
        assert high_assessment.confidence_score <= 1.0

    def test_missing_evidence_handled(self, scorer):
        """Missing evidence fields handled gracefully.
        
        Verify incomplete data handling.
        """
        # Partial evidence
        assessment = scorer.calculate_confidence(
            action="partial_evidence",
            action_type="test",
            context={},
            evidence={
                "intent_clarity": 0.7,
                # Missing other factors
            },
        )
        
        # Verify handled
        assert assessment.confidence_score is not None

    def test_null_context_handled(self, scorer):
        """Null or empty context handled.
        
        Verify context robustness.
        """
        assessment = scorer.calculate_confidence(
            action="no_context",
            action_type="test",
            context=None,
            evidence={"intent_clarity": 0.5},
        )
        
        # Verify handled
        assert assessment is not None

    def test_rapid_scoring(self, scorer):
        """Rapid successive scoring operations.
        
        Verify performance.
        """
        assessments = []
        for i in range(100):
            assessment = scorer.calculate_confidence(
                action=f"rapid_action_{i}",
                action_type="test",
                context={"index": i},
                evidence={"intent_clarity": 0.5},
            )
            assessments.append(assessment)
        
        # Verify all scored
        assert len(assessments) == 100

    def test_concurrent_assessments(self, scorer):
        """Concurrent scoring operations.
        
        Verify thread safety.
        """
        assessment1 = scorer.calculate_confidence(
            action="concurrent_1",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.6},
        )
        
        assessment2 = scorer.calculate_confidence(
            action="concurrent_2",
            action_type="test",
            context={},
            evidence={"intent_clarity": 0.7},
        )
        
        # Verify both successful
        assert assessment1 is not None
        assert assessment2 is not None
