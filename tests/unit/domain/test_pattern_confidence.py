"""Tests for PatternConfidence value object"""
import pytest
from src.domain.value_objects import PatternConfidence


class TestPatternConfidenceCreation:
    """Test PatternConfidence creation and validation"""
    
    def test_create_valid_confidence(self):
        """Should create confidence with valid values"""
        confidence = PatternConfidence(
            score=0.85,
            observation_count=10,
            success_rate=0.90
        )
        assert confidence.score == 0.85
        assert confidence.observation_count == 10
        assert confidence.success_rate == 0.90
    
    def test_reject_invalid_score(self):
        """Should reject invalid score"""
        with pytest.raises(ValueError, match="PatternConfidence.score must be between"):
            PatternConfidence(score=1.5, observation_count=5, success_rate=0.80)
    
    def test_reject_negative_observations(self):
        """Should reject negative observation count"""
        with pytest.raises(ValueError, match="observation_count cannot be negative"):
            PatternConfidence(score=0.75, observation_count=-1, success_rate=0.80)
    
    def test_allow_zero_observations(self):
        """Should allow zero observations (unproven pattern)"""
        confidence = PatternConfidence(score=0.50, observation_count=0, success_rate=0.0)
        assert confidence.observation_count == 0
    
    def test_reject_invalid_success_rate(self):
        """Should reject invalid success rate"""
        with pytest.raises(ValueError, match="success_rate must be between"):
            PatternConfidence(score=0.75, observation_count=5, success_rate=1.2)


class TestPatternConfidenceLevels:
    """Test confidence level categorization"""
    
    def test_proven_confidence_level(self):
        """Should identify proven patterns (>= 0.90, >= 20 observations)"""
        confidence = PatternConfidence(score=0.95, observation_count=25, success_rate=0.95)
        assert confidence.is_proven
        assert confidence.confidence_level == "Proven"
        assert confidence.confidence_emoji == "💎"
    
    def test_proven_confidence_boundaries(self):
        """Should identify proven at boundaries"""
        # Score boundary
        confidence1 = PatternConfidence(score=0.90, observation_count=20, success_rate=0.90)
        assert confidence1.is_proven
        
        # Observation boundary
        confidence2 = PatternConfidence(score=0.95, observation_count=20, success_rate=0.90)
        assert confidence2.is_proven
    
    def test_not_proven_low_score(self):
        """Should not be proven with low score"""
        confidence = PatternConfidence(score=0.85, observation_count=25, success_rate=0.90)
        assert not confidence.is_proven
    
    def test_not_proven_low_observations(self):
        """Should not be proven with few observations"""
        confidence = PatternConfidence(score=0.95, observation_count=15, success_rate=0.95)
        assert not confidence.is_proven
    
    def test_reliable_confidence_level(self):
        """Should identify reliable patterns (0.75-0.89, >= 10 observations)"""
        confidence = PatternConfidence(score=0.80, observation_count=15, success_rate=0.85)
        assert confidence.is_reliable
        assert confidence.confidence_level == "Reliable"
        assert confidence.confidence_emoji == "✅"
    
    def test_reliable_confidence_boundaries(self):
        """Should identify reliable at boundaries"""
        lower = PatternConfidence(score=0.75, observation_count=10, success_rate=0.80)
        assert lower.is_reliable
        
        upper = PatternConfidence(score=0.89, observation_count=10, success_rate=0.85)
        assert upper.is_reliable
    
    def test_emerging_confidence_level(self):
        """Should identify emerging patterns (0.60-0.74, >= 5 observations)"""
        confidence = PatternConfidence(score=0.65, observation_count=8, success_rate=0.70)
        assert confidence.is_emerging
        assert confidence.confidence_level == "Emerging"
        assert confidence.confidence_emoji == "🌱"
    
    def test_experimental_confidence_level(self):
        """Should identify experimental patterns (< 0.60 or < 5 observations)"""
        # Low score
        confidence1 = PatternConfidence(score=0.50, observation_count=10, success_rate=0.60)
        assert confidence1.is_experimental
        assert confidence1.confidence_level == "Experimental"
        assert confidence1.confidence_emoji == "🧪"
        
        # Few observations
        confidence2 = PatternConfidence(score=0.75, observation_count=3, success_rate=0.80)
        assert confidence2.is_experimental


class TestPatternConfidenceRecommendation:
    """Test recommendation logic"""
    
    def test_should_recommend_proven(self):
        """Should recommend proven patterns"""
        confidence = PatternConfidence(score=0.95, observation_count=25, success_rate=0.95)
        assert confidence.should_recommend
    
    def test_should_recommend_reliable(self):
        """Should recommend reliable patterns"""
        confidence = PatternConfidence(score=0.80, observation_count=15, success_rate=0.85)
        assert confidence.should_recommend
    
    def test_should_not_recommend_emerging(self):
        """Should not recommend emerging patterns"""
        confidence = PatternConfidence(score=0.65, observation_count=8, success_rate=0.70)
        assert not confidence.should_recommend
    
    def test_should_not_recommend_experimental(self):
        """Should not recommend experimental patterns"""
        confidence = PatternConfidence(score=0.50, observation_count=3, success_rate=0.60)
        assert not confidence.should_recommend


class TestPatternConfidenceQuality:
    """Test quality score calculation"""
    
    def test_quality_score_calculation(self):
        """Should calculate quality score correctly"""
        confidence = PatternConfidence(score=0.80, observation_count=10, success_rate=0.90)
        # quality = (0.80 + 0.90) / 2 = 0.85
        assert confidence.quality_score == pytest.approx(0.85, rel=0.01)
    
    def test_quality_score_equal_values(self):
        """Should handle equal score and success rate"""
        confidence = PatternConfidence(score=0.75, observation_count=15, success_rate=0.75)
        assert confidence.quality_score == 0.75
    
    def test_quality_score_different_values(self):
        """Should average different values"""
        confidence = PatternConfidence(score=0.70, observation_count=10, success_rate=0.90)
        # quality = (0.70 + 0.90) / 2 = 0.80
        assert confidence.quality_score == 0.80


class TestPatternConfidenceObservations:
    """Test observation tracking and updates"""
    
    def test_with_new_observation_success(self):
        """Should update confidence with successful observation"""
        confidence = PatternConfidence(score=0.75, observation_count=10, success_rate=0.80)
        updated = confidence.with_new_observation(was_successful=True)
        
        # New observation count
        assert updated.observation_count == 11
        
        # Success rate should increase (8 previous successes -> 9 successes out of 11)
        expected_successes = 9  # 8 previous (0.80 * 10) + 1 new
        expected_rate = expected_successes / 11
        assert updated.success_rate == pytest.approx(expected_rate, rel=0.02)
        
        # Score should be recalculated based on new success rate
        assert updated.score > confidence.score
    
    def test_with_new_observation_failure(self):
        """Should update confidence with failed observation"""
        confidence = PatternConfidence(score=0.80, observation_count=10, success_rate=0.90)
        updated = confidence.with_new_observation(was_successful=False)
        
        # New observation count
        assert updated.observation_count == 11
        
        # Success rate should decrease (9 successes -> 9 successes out of 11)
        expected_successes = 9  # 9 previous + 0 new
        expected_rate = expected_successes / 11
        assert updated.success_rate == pytest.approx(expected_rate, rel=0.01)
        
        # Score should be recalculated based on new success rate
        assert updated.score < confidence.score
    
    def test_with_new_observation_first_observation(self):
        """Should handle first observation correctly"""
        confidence = PatternConfidence(score=0.50, observation_count=0, success_rate=0.0)
        
        # First success
        updated_success = confidence.with_new_observation(was_successful=True)
        assert updated_success.observation_count == 1
        assert updated_success.success_rate == 1.0
        
        # First failure
        updated_failure = confidence.with_new_observation(was_successful=False)
        assert updated_failure.observation_count == 1
        assert updated_failure.success_rate == 0.0
    
    def test_with_new_observation_immutability(self):
        """Should return new instance, not modify original"""
        confidence = PatternConfidence(score=0.75, observation_count=10, success_rate=0.80)
        updated = confidence.with_new_observation(was_successful=True)
        
        # Original unchanged
        assert confidence.observation_count == 10
        assert confidence.success_rate == 0.80
        
        # New instance different
        assert updated.observation_count == 11
        assert updated is not confidence


class TestPatternConfidenceValueObjectBehavior:
    """Test value object behavior"""
    
    def test_equality_same_values(self):
        """Should be equal with same values"""
        confidence1 = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        confidence2 = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        assert confidence1 == confidence2
    
    def test_inequality_different_score(self):
        """Should not be equal with different score"""
        confidence1 = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        confidence2 = PatternConfidence(score=0.85, observation_count=10, success_rate=0.85)
        assert confidence1 != confidence2
    
    def test_inequality_different_counts(self):
        """Should not be equal with different counts"""
        confidence1 = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        confidence2 = PatternConfidence(score=0.80, observation_count=12, success_rate=0.85)
        assert confidence1 != confidence2
    
    def test_hashable(self):
        """Should be hashable"""
        confidence1 = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        confidence2 = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        
        confidence_set = {confidence1, confidence2}
        assert len(confidence_set) == 1
    
    def test_immutable(self):
        """Should be immutable"""
        confidence = PatternConfidence(score=0.80, observation_count=10, success_rate=0.85)
        with pytest.raises(Exception):
            confidence.score = 0.85
