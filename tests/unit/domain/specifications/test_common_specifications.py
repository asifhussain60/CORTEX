"""
Tests for common domain specifications.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.domain.specifications import (
    HighQualityConversationSpec,
    RecentConversationSpec,
    NamespaceMatchSpec,
    PatternConfidenceSpec,
    MinimumParticipantsSpec,
    EntityCountSpec,
    ContextRelevanceSpec,
    TierSpec,
)


@dataclass
class Conversation:
    """Test conversation entity."""
    conversation_id: str
    quality: float
    captured_at: datetime
    namespace: str
    participant_count: int = 2
    entity_count: int = 5


@dataclass
class Pattern:
    """Test pattern entity."""
    pattern_id: str
    confidence: float
    namespace: str


@dataclass
class ContextItem:
    """Test context item entity."""
    context_id: str
    relevance_score: float
    tier: int


class TestHighQualityConversationSpec:
    """Tests for HighQualityConversationSpec."""
    
    def test_high_quality_satisfied(self):
        """Test specification satisfied for high-quality conversation."""
        spec = HighQualityConversationSpec(min_quality=0.70)
        conv = Conversation("c1", 0.85, datetime.now(), "engineering")
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_high_quality_at_boundary(self):
        """Test specification at exact boundary."""
        spec = HighQualityConversationSpec(min_quality=0.70)
        conv = Conversation("c1", 0.70, datetime.now(), "engineering")
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_low_quality_not_satisfied(self):
        """Test specification not satisfied for low-quality conversation."""
        spec = HighQualityConversationSpec(min_quality=0.70)
        conv = Conversation("c1", 0.50, datetime.now(), "engineering")
        
        assert spec.is_satisfied_by(conv) is False
    
    def test_custom_threshold(self):
        """Test specification with custom quality threshold."""
        spec = HighQualityConversationSpec(min_quality=0.90)
        
        assert spec.is_satisfied_by(Conversation("c1", 0.95, datetime.now(), "eng")) is True
        assert spec.is_satisfied_by(Conversation("c2", 0.85, datetime.now(), "eng")) is False


class TestRecentConversationSpec:
    """Tests for RecentConversationSpec."""
    
    def test_recent_conversation_satisfied(self):
        """Test specification satisfied for recent conversation."""
        spec = RecentConversationSpec(days=7)
        conv = Conversation("c1", 0.80, datetime.now() - timedelta(days=3), "eng")
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_recent_conversation_at_boundary(self):
        """Test specification at exact boundary."""
        spec = RecentConversationSpec(days=7)
        conv = Conversation("c1", 0.80, datetime.now() - timedelta(days=7), "eng")
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_old_conversation_not_satisfied(self):
        """Test specification not satisfied for old conversation."""
        spec = RecentConversationSpec(days=7)
        conv = Conversation("c1", 0.80, datetime.now() - timedelta(days=10), "eng")
        
        assert spec.is_satisfied_by(conv) is False
    
    def test_custom_days(self):
        """Test specification with custom day range."""
        spec = RecentConversationSpec(days=30)
        
        assert spec.is_satisfied_by(
            Conversation("c1", 0.80, datetime.now() - timedelta(days=15), "eng")
        ) is True
        assert spec.is_satisfied_by(
            Conversation("c2", 0.80, datetime.now() - timedelta(days=35), "eng")
        ) is False


class TestNamespaceMatchSpec:
    """Tests for NamespaceMatchSpec."""
    
    def test_namespace_match_satisfied(self):
        """Test specification satisfied for matching namespace."""
        spec = NamespaceMatchSpec("engineering")
        conv = Conversation("c1", 0.80, datetime.now(), "engineering")
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_namespace_case_insensitive(self):
        """Test specification is case-insensitive."""
        spec = NamespaceMatchSpec("Engineering")
        
        assert spec.is_satisfied_by(Conversation("c1", 0.80, datetime.now(), "ENGINEERING")) is True
        assert spec.is_satisfied_by(Conversation("c2", 0.80, datetime.now(), "engineering")) is True
    
    def test_namespace_mismatch_not_satisfied(self):
        """Test specification not satisfied for different namespace."""
        spec = NamespaceMatchSpec("engineering")
        conv = Conversation("c1", 0.80, datetime.now(), "design")
        
        assert spec.is_satisfied_by(conv) is False


class TestPatternConfidenceSpec:
    """Tests for PatternConfidenceSpec."""
    
    def test_high_confidence_satisfied(self):
        """Test specification satisfied for high-confidence pattern."""
        spec = PatternConfidenceSpec(min_confidence=0.75)
        pattern = Pattern("p1", 0.85, "engineering")
        
        assert spec.is_satisfied_by(pattern) is True
    
    def test_low_confidence_not_satisfied(self):
        """Test specification not satisfied for low-confidence pattern."""
        spec = PatternConfidenceSpec(min_confidence=0.75)
        pattern = Pattern("p1", 0.60, "engineering")
        
        assert spec.is_satisfied_by(pattern) is False


class TestMinimumParticipantsSpec:
    """Tests for MinimumParticipantsSpec."""
    
    def test_sufficient_participants_satisfied(self):
        """Test specification satisfied with sufficient participants."""
        spec = MinimumParticipantsSpec(min_participants=2)
        conv = Conversation("c1", 0.80, datetime.now(), "eng", participant_count=3)
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_insufficient_participants_not_satisfied(self):
        """Test specification not satisfied with insufficient participants."""
        spec = MinimumParticipantsSpec(min_participants=3)
        conv = Conversation("c1", 0.80, datetime.now(), "eng", participant_count=2)
        
        assert spec.is_satisfied_by(conv) is False


class TestEntityCountSpec:
    """Tests for EntityCountSpec."""
    
    def test_sufficient_entities_satisfied(self):
        """Test specification satisfied with sufficient entities."""
        spec = EntityCountSpec(min_entities=3)
        conv = Conversation("c1", 0.80, datetime.now(), "eng", entity_count=5)
        
        assert spec.is_satisfied_by(conv) is True
    
    def test_insufficient_entities_not_satisfied(self):
        """Test specification not satisfied with insufficient entities."""
        spec = EntityCountSpec(min_entities=5)
        conv = Conversation("c1", 0.80, datetime.now(), "eng", entity_count=2)
        
        assert spec.is_satisfied_by(conv) is False


class TestContextRelevanceSpec:
    """Tests for ContextRelevanceSpec."""
    
    def test_relevant_context_satisfied(self):
        """Test specification satisfied for relevant context."""
        spec = ContextRelevanceSpec(min_relevance=0.60)
        item = ContextItem("ctx1", 0.75, 1)
        
        assert spec.is_satisfied_by(item) is True
    
    def test_irrelevant_context_not_satisfied(self):
        """Test specification not satisfied for irrelevant context."""
        spec = ContextRelevanceSpec(min_relevance=0.60)
        item = ContextItem("ctx1", 0.40, 1)
        
        assert spec.is_satisfied_by(item) is False


class TestTierSpec:
    """Tests for TierSpec."""
    
    def test_tier_1_match(self):
        """Test specification satisfied for Tier 1."""
        spec = TierSpec(1)
        item = ContextItem("ctx1", 0.75, 1)
        
        assert spec.is_satisfied_by(item) is True
    
    def test_tier_2_match(self):
        """Test specification satisfied for Tier 2."""
        spec = TierSpec(2)
        item = ContextItem("ctx1", 0.75, 2)
        
        assert spec.is_satisfied_by(item) is True
    
    def test_tier_mismatch(self):
        """Test specification not satisfied for different tier."""
        spec = TierSpec(1)
        item = ContextItem("ctx1", 0.75, 2)
        
        assert spec.is_satisfied_by(item) is False
    
    def test_invalid_tier_raises_error(self):
        """Test invalid tier raises ValueError."""
        with pytest.raises(ValueError):
            TierSpec(4)
    
    def test_tier_string_representation(self):
        """Test tier specification has descriptive string representation."""
        spec = TierSpec(1)
        assert "Tier 1" in repr(spec)
        assert "Working Memory" in repr(spec)


class TestSpecificationComposition:
    """Tests for composing domain specifications."""
    
    def test_high_quality_and_recent(self):
        """Test composition of quality and recency specs."""
        spec = HighQualityConversationSpec(0.70) & RecentConversationSpec(7)
        
        # Both conditions met
        conv1 = Conversation("c1", 0.85, datetime.now() - timedelta(days=2), "eng")
        assert spec.is_satisfied_by(conv1) is True
        
        # High quality but old
        conv2 = Conversation("c2", 0.85, datetime.now() - timedelta(days=10), "eng")
        assert spec.is_satisfied_by(conv2) is False
        
        # Recent but low quality
        conv3 = Conversation("c3", 0.50, datetime.now() - timedelta(days=2), "eng")
        assert spec.is_satisfied_by(conv3) is False
    
    def test_namespace_and_quality(self):
        """Test composition of namespace and quality specs."""
        spec = NamespaceMatchSpec("engineering") & HighQualityConversationSpec(0.70)
        
        # Both conditions met
        assert spec.is_satisfied_by(
            Conversation("c1", 0.85, datetime.now(), "engineering")
        ) is True
        
        # Wrong namespace
        assert spec.is_satisfied_by(
            Conversation("c2", 0.85, datetime.now(), "design")
        ) is False
    
    def test_complex_conversation_filter(self):
        """Test complex specification with multiple conditions."""
        spec = (
            HighQualityConversationSpec(0.70)
            & RecentConversationSpec(30)
            & NamespaceMatchSpec("engineering")
            & MinimumParticipantsSpec(2)
        )
        
        # All conditions met
        conv = Conversation(
            "c1",
            0.85,
            datetime.now() - timedelta(days=5),
            "engineering",
            participant_count=3
        )
        assert spec.is_satisfied_by(conv) is True
        
        # One condition fails (low quality)
        conv = Conversation(
            "c2",
            0.50,
            datetime.now() - timedelta(days=5),
            "engineering",
            participant_count=3
        )
        assert spec.is_satisfied_by(conv) is False
