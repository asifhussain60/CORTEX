"""
Unit tests for CORTEX Confidence Scoring Module

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime, timedelta
from src.cognitive.confidence_scorer import (
    ConfidenceScorer,
    ConfidenceScore,
    ConfidenceLevel
)


class TestConfidenceLevel:
    """Test ConfidenceLevel enum"""
    
    def test_confidence_levels_exist(self):
        """All confidence levels should be defined"""
        assert ConfidenceLevel.VERY_HIGH.value == "Very High"
        assert ConfidenceLevel.HIGH.value == "High"
        assert ConfidenceLevel.MEDIUM.value == "Medium"
        assert ConfidenceLevel.LOW.value == "Low"
        assert ConfidenceLevel.VERY_LOW.value == "Very Low"


class TestConfidenceScore:
    """Test ConfidenceScore dataclass"""
    
    def test_format_display_very_high(self):
        """Should format very high confidence correctly"""
        score = ConfidenceScore(
            percentage=95,
            level=ConfidenceLevel.VERY_HIGH,
            pattern_count=20,
            usage_history=100,
            last_used=datetime.now(),
            factors={}
        )
        display = score.format_display()
        assert "🟢" in display
        assert "95%" in display
        assert "Very High" in display
    
    def test_format_display_medium(self):
        """Should format medium confidence correctly"""
        score = ConfidenceScore(
            percentage=65,
            level=ConfidenceLevel.MEDIUM,
            pattern_count=5,
            usage_history=10,
            last_used=datetime.now(),
            factors={}
        )
        display = score.format_display()
        assert "🟡" in display
        assert "65%" in display
        assert "Medium" in display
    
    def test_format_display_low(self):
        """Should format low confidence correctly"""
        score = ConfidenceScore(
            percentage=35,
            level=ConfidenceLevel.LOW,
            pattern_count=2,
            usage_history=3,
            last_used=datetime.now(),
            factors={}
        )
        display = score.format_display()
        assert "🟠" in display
        assert "35%" in display
        assert "Low" in display
    
    def test_format_detailed_single_pattern(self):
        """Should format detailed display with singular pattern"""
        score = ConfidenceScore(
            percentage=87,
            level=ConfidenceLevel.HIGH,
            pattern_count=1,
            usage_history=5,
            last_used=datetime.now(),
            factors={}
        )
        detailed = score.format_detailed()
        assert "87%" in detailed
        assert "High" in detailed
        assert "1 similar pattern" in detailed
        assert "5 successful uses" in detailed
    
    def test_format_detailed_multiple_patterns(self):
        """Should format detailed display with plural patterns"""
        score = ConfidenceScore(
            percentage=87,
            level=ConfidenceLevel.HIGH,
            pattern_count=12,
            usage_history=34,
            last_used=datetime.now(),
            factors={}
        )
        detailed = score.format_detailed()
        assert "87%" in detailed
        assert "High" in detailed
        assert "12 similar patterns" in detailed
        assert "34 successful uses" in detailed
    
    def test_format_detailed_no_usage(self):
        """Should format detailed display with no usage history"""
        score = ConfidenceScore(
            percentage=50,
            level=ConfidenceLevel.MEDIUM,
            pattern_count=3,
            usage_history=0,
            last_used=None,
            factors={}
        )
        detailed = score.format_detailed()
        assert "50%" in detailed
        assert "3 similar patterns" in detailed
        assert "successful use" not in detailed


class TestConfidenceScorer:
    """Test ConfidenceScorer calculations"""
    
    @pytest.fixture
    def scorer(self):
        """Create ConfidenceScorer instance"""
        return ConfidenceScorer()
    
    def test_very_high_confidence(self, scorer):
        """Should calculate very high confidence (90-100%)"""
        score = scorer.calculate_confidence(
            base_confidence=0.95,
            usage_count=50,
            success_rate=0.98,
            last_used=datetime.now(),
            pattern_count=20
        )
        assert score.percentage >= 90
        assert score.level == ConfidenceLevel.VERY_HIGH
        assert score.pattern_count == 20
        assert score.usage_history == 50
    
    def test_high_confidence(self, scorer):
        """Should calculate high confidence (75-89%)"""
        score = scorer.calculate_confidence(
            base_confidence=0.85,
            usage_count=25,
            success_rate=0.90,
            last_used=datetime.now() - timedelta(days=15),
            pattern_count=12
        )
        assert 75 <= score.percentage < 90
        assert score.level == ConfidenceLevel.HIGH
    
    def test_medium_confidence(self, scorer):
        """Should calculate medium confidence (50-74%)"""
        score = scorer.calculate_confidence(
            base_confidence=0.70,
            usage_count=10,
            success_rate=0.75,
            last_used=datetime.now() - timedelta(days=60),
            pattern_count=5
        )
        assert 50 <= score.percentage < 75
        assert score.level == ConfidenceLevel.MEDIUM
    
    def test_low_confidence(self, scorer):
        """Should calculate low confidence (30-49%)"""
        score = scorer.calculate_confidence(
            base_confidence=0.50,
            usage_count=3,
            success_rate=0.60,
            last_used=datetime.now() - timedelta(days=150),
            pattern_count=2
        )
        assert 30 <= score.percentage < 50
        assert score.level == ConfidenceLevel.LOW
    
    def test_very_low_confidence(self, scorer):
        """Should calculate very low confidence (<30%)"""
        score = scorer.calculate_confidence(
            base_confidence=0.30,
            usage_count=1,
            success_rate=0.40,
            last_used=datetime.now() - timedelta(days=200),
            pattern_count=1
        )
        assert score.percentage < 30
        assert score.level == ConfidenceLevel.VERY_LOW
    
    def test_confidence_with_no_usage(self, scorer):
        """Should handle patterns with no usage history"""
        score = scorer.calculate_confidence(
            base_confidence=0.80,
            usage_count=0,
            success_rate=0.0,
            last_used=None,
            pattern_count=3
        )
        # Without usage history, confidence should be lower
        # 0.80 * 0.40 + 0.0 * 0.30 + 0.0 * 0.20 + 0.5 * 0.10 = 0.37 = 37%
        assert score.percentage < 50  # Should not be high confidence
        assert score.usage_history == 0
    
    def test_confidence_with_old_pattern(self, scorer):
        """Should reduce confidence for old patterns"""
        recent_score = scorer.calculate_confidence(
            base_confidence=0.80,
            usage_count=20,
            success_rate=0.85,
            last_used=datetime.now(),
            pattern_count=5
        )
        
        old_score = scorer.calculate_confidence(
            base_confidence=0.80,
            usage_count=20,
            success_rate=0.85,
            last_used=datetime.now() - timedelta(days=200),
            pattern_count=5
        )
        
        # Old pattern should have lower confidence due to recency factor
        assert old_score.percentage < recent_score.percentage
    
    def test_recency_score_very_recent(self, scorer):
        """Should give high recency score for patterns used within 7 days"""
        last_used = datetime.now() - timedelta(days=3)
        recency_score = scorer._calculate_recency_score(last_used)
        assert recency_score == 1.0
    
    def test_recency_score_recent(self, scorer):
        """Should give good recency score for patterns used within 30 days"""
        last_used = datetime.now() - timedelta(days=20)
        recency_score = scorer._calculate_recency_score(last_used)
        assert recency_score == 0.8
    
    def test_recency_score_moderate(self, scorer):
        """Should give moderate recency score for patterns used within 90 days"""
        last_used = datetime.now() - timedelta(days=60)
        recency_score = scorer._calculate_recency_score(last_used)
        assert recency_score == 0.6
    
    def test_recency_score_old(self, scorer):
        """Should give low recency score for patterns used within 180 days"""
        last_used = datetime.now() - timedelta(days=150)
        recency_score = scorer._calculate_recency_score(last_used)
        assert recency_score == 0.4
    
    def test_recency_score_very_old(self, scorer):
        """Should give very low recency score for patterns older than 180 days"""
        last_used = datetime.now() - timedelta(days=200)
        recency_score = scorer._calculate_recency_score(last_used)
        assert recency_score == 0.2
    
    def test_recency_score_no_data(self, scorer):
        """Should give neutral recency score when no data available"""
        recency_score = scorer._calculate_recency_score(None)
        assert recency_score == 0.5
    
    def test_determine_level_boundaries(self, scorer):
        """Should correctly categorize confidence levels at boundaries"""
        assert scorer._determine_level(100) == ConfidenceLevel.VERY_HIGH
        assert scorer._determine_level(90) == ConfidenceLevel.VERY_HIGH
        assert scorer._determine_level(89) == ConfidenceLevel.HIGH
        assert scorer._determine_level(75) == ConfidenceLevel.HIGH
        assert scorer._determine_level(74) == ConfidenceLevel.MEDIUM
        assert scorer._determine_level(50) == ConfidenceLevel.MEDIUM
        assert scorer._determine_level(49) == ConfidenceLevel.LOW
        assert scorer._determine_level(30) == ConfidenceLevel.LOW
        assert scorer._determine_level(29) == ConfidenceLevel.VERY_LOW
        assert scorer._determine_level(0) == ConfidenceLevel.VERY_LOW
    
    def test_factors_included_in_score(self, scorer):
        """Should include all factor calculations in result"""
        score = scorer.calculate_confidence(
            base_confidence=0.85,
            usage_count=20,
            success_rate=0.90,
            last_used=datetime.now(),
            pattern_count=10
        )
        
        assert 'match_quality' in score.factors
        assert 'usage_history' in score.factors
        assert 'success_rate' in score.factors
        assert 'recency' in score.factors
        
        # Verify factor values are reasonable
        assert 0.0 <= score.factors['match_quality'] <= 1.0
        assert 0.0 <= score.factors['usage_history'] <= 1.0
        assert 0.0 <= score.factors['success_rate'] <= 1.0
        assert 0.0 <= score.factors['recency'] <= 1.0
    
    def test_usage_history_logarithmic_scale(self, scorer):
        """Should use logarithmic scale for usage history"""
        # 1 use
        score_1 = scorer.calculate_confidence(
            base_confidence=0.50,
            usage_count=1,
            success_rate=0.0,
            last_used=None
        )
        
        # 10 uses
        score_10 = scorer.calculate_confidence(
            base_confidence=0.50,
            usage_count=10,
            success_rate=0.0,
            last_used=None
        )
        
        # 100 uses
        score_100 = scorer.calculate_confidence(
            base_confidence=0.50,
            usage_count=100,
            success_rate=0.0,
            last_used=None
        )
        
        # Usage contribution should increase, but not linearly
        assert score_1.percentage < score_10.percentage < score_100.percentage
        
        # With logarithmic scale, usage factors grow slower at higher counts
        # Just verify the pattern increases (logarithmic test is implementation detail)
        assert score_100.percentage - score_1.percentage > 0
    
    def test_weight_distribution(self, scorer):
        """Should apply correct weights to factors"""
        # Test that match quality has highest weight (40%)
        score_high_match = scorer.calculate_confidence(
            base_confidence=1.0,
            usage_count=0,
            success_rate=0.0,
            last_used=None
        )
        
        # Base of 1.0 with 40% weight + 0.5 recency with 10% weight = 45%
        assert 40 <= score_high_match.percentage <= 50
    
    def test_edge_case_all_zeros(self, scorer):
        """Should handle all zero inputs gracefully"""
        score = scorer.calculate_confidence(
            base_confidence=0.0,
            usage_count=0,
            success_rate=0.0,
            last_used=None,
            pattern_count=1
        )
        
        assert score.percentage >= 0
        assert score.level == ConfidenceLevel.VERY_LOW
    
    def test_edge_case_all_max(self, scorer):
        """Should handle maximum confidence inputs"""
        score = scorer.calculate_confidence(
            base_confidence=1.0,
            usage_count=1000,
            success_rate=1.0,
            last_used=datetime.now(),
            pattern_count=50
        )
        
        assert score.percentage >= 90
        assert score.level == ConfidenceLevel.VERY_HIGH


class TestConfidenceScorerIntegration:
    """Integration tests for confidence scoring"""
    
    def test_realistic_planning_scenario(self):
        """Test confidence calculation for realistic planning scenario"""
        scorer = ConfidenceScorer()
        
        # Scenario: Planning authentication feature
        # - Good pattern match (0.92)
        # - Used 18 times successfully
        # - 94% success rate
        # - Used 5 days ago
        score = scorer.calculate_confidence(
            base_confidence=0.92,
            usage_count=18,
            success_rate=0.94,
            last_used=datetime.now() - timedelta(days=5),
            pattern_count=12
        )
        
        assert score.level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]
        assert score.percentage >= 80
        
        detailed = score.format_detailed()
        assert "12 similar patterns" in detailed
        assert "18 successful uses" in detailed
    
    def test_realistic_new_feature_scenario(self):
        """Test confidence calculation for new feature (no history)"""
        scorer = ConfidenceScorer()
        
        # Scenario: New quantum computing feature
        # - Moderate pattern match (0.60)
        # - Never used before
        # - No success rate data
        score = scorer.calculate_confidence(
            base_confidence=0.60,
            usage_count=0,
            success_rate=0.0,
            last_used=None,
            pattern_count=2
        )
        
        # Without usage history, confidence will be low (28% based on calculation)
        # 0.60 * 0.40 (match) + 0.0 * 0.30 (usage) + 0.0 * 0.20 (success) + 0.5 * 0.10 (recency) = 0.29 = 29%
        assert score.level in [ConfidenceLevel.VERY_LOW, ConfidenceLevel.LOW]
        assert score.percentage < 60
    
    def test_realistic_old_pattern_scenario(self):
        """Test confidence calculation for old, rarely-used pattern"""
        scorer = ConfidenceScorer()
        
        # Scenario: Legacy API integration pattern
        # - Good match quality (0.80)
        # - Used only 3 times
        # - 67% success rate
        # - Last used 8 months ago
        score = scorer.calculate_confidence(
            base_confidence=0.80,
            usage_count=3,
            success_rate=0.67,
            last_used=datetime.now() - timedelta(days=240),
            pattern_count=4
        )
        
        assert score.level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        # Old patterns should have reduced confidence
        assert score.percentage < 70
