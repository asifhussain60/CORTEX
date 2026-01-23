"""
Tests for Intent Disambiguation - AC-PHX-007-03

Test disambiguation logic including confidence thresholding,
context-aware disambiguation, and fallback suggestions.

"""

import pytest
from cortex.intent_router.disambiguator import IntentDisambiguator
from cortex.intent_router.classifier import (
    IntentClassifier,
    IntentCategory,
    ClassificationResult,
    IntentSignal,
)


class TestDisambiguatorInitialization:
    """Test disambiguator initialization."""
    
    def test_init_creates_disambiguator(self) -> None:
        """Should initialize successfully."""
        disambiguator = IntentDisambiguator()
        assert disambiguator is not None
    
    def test_init_sets_thresholds(self) -> None:
        """Should set confidence thresholds."""
        disambiguator = IntentDisambiguator()
        assert disambiguator.CONFIDENCE_THRESHOLD > 0
        assert disambiguator.MIN_CONFIDENCE_GAP > 0


class TestAmbiguityDetection:
    """Test ambiguity detection."""
    
    def test_detect_low_confidence_ambiguity(self) -> None:
        """Should detect low confidence as ambiguous."""
        disambiguator = IntentDisambiguator()
        
        # Create low-confidence classification
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.3,  # Below threshold
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        is_ambiguous = disambiguator._is_ambiguous(result)
        assert is_ambiguous is True
    
    def test_detect_close_alternatives_ambiguity(self) -> None:
        """Should detect close alternatives as ambiguous."""
        disambiguator = IntentDisambiguator()
        
        # Create classification with close alternatives
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.65,
            secondary_intents=[
                (IntentCategory.MODIFY, 0.60),  # Very close
            ],
            detected_signals=[],
            keywords=[]
        )
        
        is_ambiguous = disambiguator._is_ambiguous(result)
        assert is_ambiguous is True
    
    def test_detect_clear_intent_not_ambiguous(self) -> None:
        """Should detect clear intent as not ambiguous."""
        disambiguator = IntentDisambiguator()
        
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.95,  # High confidence
            secondary_intents=[
                (IntentCategory.MODIFY, 0.10),  # Far gap
            ],
            detected_signals=[],
            keywords=[]
        )
        
        is_ambiguous = disambiguator._is_ambiguous(result)
        assert is_ambiguous is False


class TestDisambiguation:
    """Test disambiguation process."""
    
    def test_disambiguate_low_confidence(self) -> None:
        """Should disambiguate low confidence."""
        disambiguator = IntentDisambiguator()
        
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.3,
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        disambiguation = disambiguator.disambiguate(result)
        assert disambiguation.is_ambiguous is True
    
    def test_disambiguate_clear_intent(self) -> None:
        """Should not disambiguate clear intent."""
        disambiguator = IntentDisambiguator()
        
        result = ClassificationResult(
            primary_intent=IntentCategory.FIX,
            confidence_score=0.95,
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        disambiguation = disambiguator.disambiguate(result)
        assert disambiguation.is_ambiguous is False


class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendation_for_clear_intent(self) -> None:
        """Should recommend proceeding for clear intent."""
        disambiguator = IntentDisambiguator()
        
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.95,
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        disambiguation = disambiguator.disambiguate(result)
        assert "PROCEED" in disambiguation.recommendation
    
    def test_recommendation_for_ambiguous_intent(self) -> None:
        """Should provide alternatives for ambiguous."""
        disambiguator = IntentDisambiguator()
        
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.5,
            secondary_intents=[
                (IntentCategory.MODIFY, 0.4),
            ],
            detected_signals=[],
            keywords=[]
        )
        
        disambiguation = disambiguator.disambiguate(result)
        assert "AMBIGUOUS" in disambiguation.recommendation


class TestMetrics:
    """Test metrics tracking."""
    
    def test_metrics_track_disambiguations(self) -> None:
        """Should track total disambiguations."""
        disambiguator = IntentDisambiguator()
        
        result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.95,
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        disambiguator.disambiguate(result)
        metrics = disambiguator.get_metrics()
        assert metrics["total_disambiguations"] == 1
    
    def test_metrics_track_ambiguous_cases(self) -> None:
        """Should track ambiguous cases."""
        disambiguator = IntentDisambiguator()
        
        # Low confidence - ambiguous
        ambig_result = ClassificationResult(
            primary_intent=IntentCategory.CREATE,
            confidence_score=0.3,
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        # High confidence - clear
        clear_result = ClassificationResult(
            primary_intent=IntentCategory.FIX,
            confidence_score=0.95,
            secondary_intents=[],
            detected_signals=[],
            keywords=[]
        )
        
        disambiguator.disambiguate(ambig_result)
        disambiguator.disambiguate(clear_result)
        
        metrics = disambiguator.get_metrics()
        assert metrics["ambiguous_cases"] >= 1
        assert metrics["total_disambiguations"] == 2
