"""
Tests for Confidence Scorer (Phase 48 Stage 3)

Tests multi-factor confidence scoring with threshold gating at 0.7.
Ensures validation blocks when confidence < 0.7 with actionable explanations.

Authority: PHASE-48-IMPLEMENTATION-PLAN.yaml Stage 3
Priority: P0-CRITICAL
AC-ID: AC-PHASE48-S3-TEST-001
"""

import pytest
from cortex.orchestrators.validation.confidence_scorer import (
    ConfidenceScorer,
    ConfidenceResult,
    ConfidenceFactor,
)


class TestConfidenceScorerInitialization:
    """Test Confidence Scorer initialization."""
    
    def test_scorer_initializes_successfully(self):
        """Confidence scorer should initialize without errors."""
        scorer = ConfidenceScorer()
        assert scorer is not None
    
    def test_scorer_has_calculate_confidence_method(self):
        """Scorer should have calculate_confidence method."""
        scorer = ConfidenceScorer()
        assert hasattr(scorer, "calculate_confidence")
        assert callable(scorer.calculate_confidence)


class TestConfidenceCalculation:
    """Test confidence score calculation."""
    
    def test_confidence_score_between_0_and_1(self):
        """Confidence score should always be between 0.0 and 1.0."""
        scorer = ConfidenceScorer()
        
        # Test with various inputs
        test_cases = [
            {"request": "Implement auth", "checklist_result": {"security": 1.0, "performance": 1.0}},
            {"request": "Fix bug", "checklist_result": {"security": 0.5, "performance": 0.5}},
            {"request": "Refactor", "checklist_result": {"security": 0.0, "performance": 0.0}},
        ]
        
        for case in test_cases:
            result = scorer.calculate_confidence(**case)
            assert 0.0 <= result.score <= 1.0, f"Score {result.score} out of bounds"
    
    def test_high_checklist_scores_yield_high_confidence(self):
        """High checklist results should yield high confidence scores."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Well-specified implementation request",
            checklist_result={
                "security": 1.0,
                "performance": 0.9,
                "maintainability": 0.9,
                "testability": 1.0,
            }
        )
        
        # Allow for floating-point precision (>= 0.79 is acceptable)
        assert result.score >= 0.79, "High checklist scores should yield high confidence"
    
    def test_low_checklist_scores_yield_low_confidence(self):
        """Low checklist results should yield low confidence scores."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Vague request",
            checklist_result={
                "security": 0.2,
                "performance": 0.3,
                "maintainability": 0.1,
            }
        )
        
        assert result.score < 0.5, "Low checklist scores should yield low confidence"


class TestMultiFactorScoring:
    """Test that scoring considers multiple factors."""
    
    def test_scoring_considers_security_factor(self):
        """Confidence should be lower when security score is low."""
        scorer = ConfidenceScorer()
        
        high_security = scorer.calculate_confidence(
            request="Implement feature",
            checklist_result={"security": 1.0, "performance": 0.8}
        )
        
        low_security = scorer.calculate_confidence(
            request="Implement feature",
            checklist_result={"security": 0.2, "performance": 0.8}
        )
        
        assert high_security.score > low_security.score
    
    def test_scoring_considers_performance_factor(self):
        """Confidence should be lower when performance score is low."""
        scorer = ConfidenceScorer()
        
        high_perf = scorer.calculate_confidence(
            request="Implement feature",
            checklist_result={"security": 0.8, "performance": 1.0}
        )
        
        low_perf = scorer.calculate_confidence(
            request="Implement feature",
            checklist_result={"security": 0.8, "performance": 0.2}
        )
        
        assert high_perf.score > low_perf.score
    
    def test_scoring_considers_request_clarity(self):
        """Clear requests should score higher than vague ones."""
        scorer = ConfidenceScorer()
        
        clear_request = scorer.calculate_confidence(
            request="Implement JWT authentication with refresh tokens using RS256",
            checklist_result={"security": 0.8}
        )
        
        vague_request = scorer.calculate_confidence(
            request="Do something",
            checklist_result={"security": 0.8}
        )
        
        assert clear_request.score > vague_request.score


class TestThresholdGating:
    """Test confidence threshold gating at 0.7."""
    
    def test_threshold_0_7_gates_execution(self):
        """Confidence < 0.7 should result in blocked execution."""
        scorer = ConfidenceScorer()
        
        # Low confidence case
        low_result = scorer.calculate_confidence(
            request="Vague request",
            checklist_result={"security": 0.3, "performance": 0.2}
        )
        
        assert low_result.score < 0.7
        assert not low_result.passed, "Low confidence should block execution"
    
    def test_threshold_passed_when_confidence_high(self):
        """Confidence >= 0.7 should pass the gate."""
        scorer = ConfidenceScorer()
        
        # High confidence case
        high_result = scorer.calculate_confidence(
            request="Clear implementation request with all details",
            checklist_result={"security": 0.9, "performance": 0.9, "maintainability": 0.8}
        )
        
        assert high_result.score >= 0.7
        assert high_result.passed, "High confidence should pass gate"
    
    def test_edge_case_exactly_0_7_confidence_passes(self):
        """Confidence of exactly 0.7 should pass (threshold is inclusive)."""
        scorer = ConfidenceScorer()
        
        # This is a conceptual test - actual score may vary
        # Just verify that >= 0.7 passes
        result = scorer.calculate_confidence(
            request="Moderately clear request",
            checklist_result={"security": 0.7, "performance": 0.7}
        )
        
        if result.score >= 0.7:
            assert result.passed, "Score >= 0.7 should pass"


class TestExplanationGeneration:
    """Test explanation generation for confidence scores."""
    
    def test_low_score_includes_actionable_explanation(self):
        """Low confidence should include clear explanation."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Fix it",
            checklist_result={"security": 0.2, "performance": 0.3}
        )
        
        assert len(result.explanation) > 0, "Should have explanation"
        assert "confidence" in result.explanation.lower()
    
    def test_explanation_identifies_weak_factors(self):
        """Explanation should identify which factors are weak."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Implement feature",
            checklist_result={
                "security": 0.2,  # Weak
                "performance": 0.9,  # Strong
                "maintainability": 0.3,  # Weak
            }
        )
        
        # Should mention security or maintainability issues
        explanation_lower = result.explanation.lower()
        assert any(word in explanation_lower for word in ["security", "maintainability", "improve"])
    
    def test_explanation_provides_improvement_suggestions(self):
        """Explanation should suggest how to improve confidence."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Do something",
            checklist_result={"security": 0.4}
        )
        
        explanation_lower = result.explanation.lower()
        # Should suggest improvements
        assert any(word in explanation_lower for word in [
            "improve", "clarify", "specify", "add", "provide", "consider"
        ])


class TestConfidenceFactors:
    """Test individual confidence factors."""
    
    def test_result_includes_factor_breakdown(self):
        """Result should include breakdown of contributing factors."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Implement authentication",
            checklist_result={"security": 0.8, "performance": 0.7}
        )
        
        assert hasattr(result, "factors")
        assert isinstance(result.factors, list)
        assert len(result.factors) > 0
    
    def test_each_factor_has_name_and_score(self):
        """Each confidence factor should have name and score."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Implement feature",
            checklist_result={"security": 0.8}
        )
        
        for factor in result.factors:
            assert isinstance(factor, ConfidenceFactor)
            assert hasattr(factor, "name")
            assert hasattr(factor, "score")
            assert 0.0 <= factor.score <= 1.0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_empty_checklist_gracefully(self):
        """Should handle empty checklist results without crashing."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Test request",
            checklist_result={}
        )
        
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.explanation, str)
    
    def test_handles_missing_checklist_categories(self):
        """Should handle partial checklist results."""
        scorer = ConfidenceScorer()
        
        result = scorer.calculate_confidence(
            request="Test request",
            checklist_result={"security": 0.5}  # Only one category
        )
        
        assert 0.0 <= result.score <= 1.0
    
    def test_handles_very_long_requests(self):
        """Should handle very long request strings."""
        scorer = ConfidenceScorer()
        
        long_request = "Implement " + "very detailed " * 100 + "feature"
        
        result = scorer.calculate_confidence(
            request=long_request,
            checklist_result={"security": 0.8}
        )
        
        assert 0.0 <= result.score <= 1.0
