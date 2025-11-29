"""Tests for RelevanceScore value object"""
import pytest
from src.domain.value_objects import RelevanceScore


class TestRelevanceScoreCreation:
    """Test RelevanceScore creation and validation"""
    
    def test_create_valid_score(self):
        """Should create score with valid value"""
        score = RelevanceScore(value=0.75)
        assert score.value == 0.75
    
    def test_create_minimum_score(self):
        """Should create score at minimum boundary"""
        score = RelevanceScore(value=0.0)
        assert score.value == 0.0
    
    def test_create_maximum_score(self):
        """Should create score at maximum boundary"""
        score = RelevanceScore(value=1.0)
        assert score.value == 1.0
    
    def test_reject_negative_score(self):
        """Should reject negative score"""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            RelevanceScore(value=-0.1)
    
    def test_reject_score_above_one(self):
        """Should reject score above 1.0"""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            RelevanceScore(value=1.5)


class TestRelevanceScoreQualityThresholds:
    """Test quality threshold properties"""
    
    def test_high_quality_threshold(self):
        """Should identify high quality (>= 0.80)"""
        score = RelevanceScore(value=0.85)
        assert score.is_high
        assert not score.is_medium
        assert not score.is_low
    
    def test_high_quality_boundary(self):
        """Should identify high quality at boundary"""
        score = RelevanceScore(value=0.80)
        assert score.is_high
    
    def test_medium_quality_threshold(self):
        """Should identify medium quality (0.50-0.79)"""
        score = RelevanceScore(value=0.65)
        assert not score.is_high
        assert score.is_medium
        assert not score.is_low
    
    def test_medium_quality_boundaries(self):
        """Should identify medium quality at boundaries"""
        lower = RelevanceScore(value=0.50)
        assert lower.is_medium
        
        upper = RelevanceScore(value=0.79)
        assert upper.is_medium
    
    def test_low_quality_threshold(self):
        """Should identify low quality (< 0.50)"""
        score = RelevanceScore(value=0.35)
        assert not score.is_high
        assert not score.is_medium
        assert score.is_low
    
    def test_low_quality_boundary(self):
        """Should identify low quality at boundary"""
        score = RelevanceScore(value=0.49)
        assert score.is_low


class TestRelevanceScoreLabels:
    """Test quality label and emoji properties"""
    
    def test_high_quality_label(self):
        """Should return 'High' label for high scores"""
        score = RelevanceScore(value=0.90)
        assert score.quality_label == "High"
        assert score.quality_emoji == "🟢"
    
    def test_medium_quality_label(self):
        """Should return 'Medium' label for medium scores"""
        score = RelevanceScore(value=0.60)
        assert score.quality_label == "Medium"
        assert score.quality_emoji == "🟡"
    
    def test_low_quality_label(self):
        """Should return 'Low' label for low scores"""
        score = RelevanceScore(value=0.30)
        assert score.quality_label == "Low"
        assert score.quality_emoji == "🔴"


class TestRelevanceScoreMethods:
    """Test RelevanceScore methods"""
    
    def test_percentage_conversion(self):
        """Should convert score to percentage"""
        score = RelevanceScore(value=0.75)
        assert score.percentage == 75.0
    
    def test_exceeds_threshold_true(self):
        """Should return True when score exceeds threshold"""
        score = RelevanceScore(value=0.85)
        assert score.exceeds_threshold(0.70)
    
    def test_exceeds_threshold_false(self):
        """Should return False when score below threshold"""
        score = RelevanceScore(value=0.65)
        assert not score.exceeds_threshold(0.70)
    
    def test_exceeds_threshold_equal(self):
        """Should return True when score equals threshold"""
        score = RelevanceScore(value=0.70)
        assert score.exceeds_threshold(0.70)


class TestRelevanceScoreValueObjectBehavior:
    """Test value object behavior (equality, hashing)"""
    
    def test_equality_same_value(self):
        """Should be equal with same value"""
        score1 = RelevanceScore(value=0.75)
        score2 = RelevanceScore(value=0.75)
        assert score1 == score2
    
    def test_inequality_different_values(self):
        """Should not be equal with different values"""
        score1 = RelevanceScore(value=0.75)
        score2 = RelevanceScore(value=0.80)
        assert score1 != score2
    
    def test_inequality_different_types(self):
        """Should not be equal to different types"""
        score = RelevanceScore(value=0.75)
        assert not (score == 0.75)
        assert not (score == "0.75")
    
    def test_hashable(self):
        """Should be hashable and usable in sets"""
        score1 = RelevanceScore(value=0.75)
        score2 = RelevanceScore(value=0.75)
        score3 = RelevanceScore(value=0.80)
        
        score_set = {score1, score2, score3}
        assert len(score_set) == 2  # score1 and score2 are duplicate
    
    def test_immutable(self):
        """Should be immutable"""
        score = RelevanceScore(value=0.75)
        with pytest.raises(Exception):  # dataclass frozen=True raises FrozenInstanceError
            score.value = 0.80
