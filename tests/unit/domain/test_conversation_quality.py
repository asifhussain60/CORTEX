"""Tests for ConversationQuality value object"""
import pytest
from src.domain.value_objects import ConversationQuality


class TestConversationQualityCreation:
    """Test ConversationQuality creation and validation"""
    
    def test_create_valid_quality(self):
        """Should create quality with valid values"""
        quality = ConversationQuality(
            score=0.75,
            turn_count=10,
            entity_count=15
        )
        assert quality.score == 0.75
        assert quality.turn_count == 10
        assert quality.entity_count == 15
    
    def test_reject_invalid_score(self):
        """Should reject invalid score"""
        with pytest.raises(ValueError, match="ConversationQuality.score must be between"):
            ConversationQuality(score=1.5, turn_count=5, entity_count=10)
    
    def test_reject_negative_turn_count(self):
        """Should reject negative turn count"""
        with pytest.raises(ValueError, match="turn_count must be positive"):
            ConversationQuality(score=0.75, turn_count=-1, entity_count=10)
    
    def test_reject_zero_turn_count(self):
        """Should reject zero turn count"""
        with pytest.raises(ValueError, match="turn_count must be positive"):
            ConversationQuality(score=0.75, turn_count=0, entity_count=10)
    
    def test_reject_negative_entity_count(self):
        """Should reject negative entity count"""
        with pytest.raises(ValueError, match="entity_count cannot be negative"):
            ConversationQuality(score=0.75, turn_count=5, entity_count=-1)
    
    def test_allow_zero_entity_count(self):
        """Should allow zero entity count"""
        quality = ConversationQuality(score=0.50, turn_count=3, entity_count=0)
        assert quality.entity_count == 0


class TestConversationQualityCaptureLogic:
    """Test capture decision logic"""
    
    def test_should_capture_high_quality(self):
        """Should capture high quality conversation (>= 0.70)"""
        quality = ConversationQuality(score=0.85, turn_count=10, entity_count=15)
        assert quality.should_capture
    
    def test_should_capture_boundary(self):
        """Should capture at boundary (0.70)"""
        quality = ConversationQuality(score=0.70, turn_count=5, entity_count=8)
        assert quality.should_capture
    
    def test_should_not_capture_low_quality(self):
        """Should not capture low quality conversation"""
        quality = ConversationQuality(score=0.65, turn_count=5, entity_count=5)
        assert not quality.should_capture
    
    def test_should_not_capture_minimal(self):
        """Should not capture minimal quality"""
        quality = ConversationQuality(score=0.30, turn_count=2, entity_count=1)
        assert not quality.should_capture


class TestConversationQualityRichness:
    """Test richness calculations"""
    
    def test_richness_factor_calculation(self):
        """Should calculate richness factor correctly"""
        quality = ConversationQuality(score=0.80, turn_count=10, entity_count=20)
        # richness = (20 / 10) = 2.0
        assert quality.richness_factor == 2.0
    
    def test_richness_factor_low_entities(self):
        """Should handle low entity/turn ratio"""
        quality = ConversationQuality(score=0.70, turn_count=10, entity_count=5)
        # richness = (5 / 10) = 0.5
        assert quality.richness_factor == 0.5
    
    def test_is_rich_conversation_true(self):
        """Should identify rich conversation (richness >= 1.5)"""
        quality = ConversationQuality(score=0.80, turn_count=10, entity_count=20)
        # richness = 2.0, should be rich
        assert quality.is_rich_conversation
    
    def test_is_rich_conversation_boundary(self):
        """Should identify rich at boundary"""
        quality = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        # richness = 1.5, should be rich
        assert quality.is_rich_conversation
    
    def test_is_not_rich_conversation(self):
        """Should identify non-rich conversation"""
        quality = ConversationQuality(score=0.70, turn_count=10, entity_count=10)
        # richness = 1.0, not rich
        assert not quality.is_rich_conversation


class TestConversationQualityLevels:
    """Test quality level categorization"""
    
    def test_excellent_quality_level(self):
        """Should identify excellent quality (>= 0.85)"""
        quality = ConversationQuality(score=0.90, turn_count=10, entity_count=15)
        assert quality.quality_level == "Excellent"
        assert quality.quality_emoji == "⭐"
    
    def test_excellent_quality_boundary(self):
        """Should identify excellent at boundary"""
        quality = ConversationQuality(score=0.85, turn_count=8, entity_count=12)
        assert quality.quality_level == "Excellent"
    
    def test_good_quality_level(self):
        """Should identify good quality (0.70-0.84)"""
        quality = ConversationQuality(score=0.75, turn_count=8, entity_count=10)
        assert quality.quality_level == "Good"
        assert quality.quality_emoji == "✅"
    
    def test_good_quality_boundaries(self):
        """Should identify good at boundaries"""
        lower = ConversationQuality(score=0.70, turn_count=5, entity_count=8)
        assert lower.quality_level == "Good"
        
        upper = ConversationQuality(score=0.84, turn_count=10, entity_count=15)
        assert upper.quality_level == "Good"
    
    def test_fair_quality_level(self):
        """Should identify fair quality (0.50-0.69)"""
        quality = ConversationQuality(score=0.60, turn_count=5, entity_count=7)
        assert quality.quality_level == "Fair"
        assert quality.quality_emoji == "⚠️"
    
    def test_poor_quality_level(self):
        """Should identify poor quality (< 0.50)"""
        quality = ConversationQuality(score=0.35, turn_count=3, entity_count=2)
        assert quality.quality_level == "Poor"
        assert quality.quality_emoji == "❌"


class TestConversationQualityValueObjectBehavior:
    """Test value object behavior"""
    
    def test_equality_same_values(self):
        """Should be equal with same values"""
        quality1 = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        quality2 = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        assert quality1 == quality2
    
    def test_inequality_different_score(self):
        """Should not be equal with different score"""
        quality1 = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        quality2 = ConversationQuality(score=0.80, turn_count=10, entity_count=15)
        assert quality1 != quality2
    
    def test_inequality_different_counts(self):
        """Should not be equal with different counts"""
        quality1 = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        quality2 = ConversationQuality(score=0.75, turn_count=12, entity_count=15)
        assert quality1 != quality2
    
    def test_hashable(self):
        """Should be hashable"""
        quality1 = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        quality2 = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        
        quality_set = {quality1, quality2}
        assert len(quality_set) == 1  # Duplicates
    
    def test_immutable(self):
        """Should be immutable"""
        quality = ConversationQuality(score=0.75, turn_count=10, entity_count=15)
        with pytest.raises(Exception):
            quality.score = 0.80
