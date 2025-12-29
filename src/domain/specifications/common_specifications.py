"""
Common domain specifications for CORTEX.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from datetime import datetime, timedelta
from typing import Optional
from .specification import Specification


class HighQualityConversationSpec(Specification):
    """
    Specification for high-quality conversations.
    Conversations must meet minimum quality threshold.
    """
    
    def __init__(self, min_quality: float = 0.70):
        """
        Initialize specification.
        
        Args:
            min_quality: Minimum quality score (0.0 to 1.0), default 0.70
        """
        self.min_quality = min_quality
    
    def is_satisfied_by(self, conversation) -> bool:
        """Check if conversation meets quality threshold."""
        return hasattr(conversation, 'quality') and conversation.quality >= self.min_quality
    
    def __repr__(self) -> str:
        return f"HighQualityConversation(>={self.min_quality})"


class RecentConversationSpec(Specification):
    """
    Specification for recent conversations.
    Conversations must be captured within specified days.
    """
    
    def __init__(self, days: int = 7):
        """
        Initialize specification.
        
        Args:
            days: Number of days to consider recent, default 7
        """
        self.days = days
        self.cutoff = datetime.now() - timedelta(days=days)
    
    def is_satisfied_by(self, conversation) -> bool:
        """Check if conversation was captured recently."""
        if not hasattr(conversation, 'captured_at'):
            return False
        return conversation.captured_at >= self.cutoff
    
    def __repr__(self) -> str:
        return f"RecentConversation(last {self.days} days)"


class NamespaceMatchSpec(Specification):
    """
    Specification for matching namespace.
    Entity must belong to the specified namespace.
    """
    
    def __init__(self, namespace: str):
        """
        Initialize specification.
        
        Args:
            namespace: Namespace to match
        """
        self.namespace = namespace.lower()
    
    def is_satisfied_by(self, entity) -> bool:
        """Check if entity belongs to namespace."""
        if not hasattr(entity, 'namespace'):
            return False
        return entity.namespace.lower() == self.namespace
    
    def __repr__(self) -> str:
        return f"NamespaceMatch('{self.namespace}')"


class PatternConfidenceSpec(Specification):
    """
    Specification for pattern confidence level.
    Patterns must meet minimum confidence threshold.
    """
    
    def __init__(self, min_confidence: float = 0.75):
        """
        Initialize specification.
        
        Args:
            min_confidence: Minimum confidence score (0.0 to 1.0), default 0.75
        """
        self.min_confidence = min_confidence
    
    def is_satisfied_by(self, pattern) -> bool:
        """Check if pattern meets confidence threshold."""
        return hasattr(pattern, 'confidence') and pattern.confidence >= self.min_confidence
    
    def __repr__(self) -> str:
        return f"PatternConfidence(>={self.min_confidence})"


class MinimumParticipantsSpec(Specification):
    """
    Specification for minimum participant count.
    Conversations must have at least N participants.
    """
    
    def __init__(self, min_participants: int = 2):
        """
        Initialize specification.
        
        Args:
            min_participants: Minimum number of participants, default 2
        """
        self.min_participants = min_participants
    
    def is_satisfied_by(self, conversation) -> bool:
        """Check if conversation has minimum participants."""
        if not hasattr(conversation, 'participant_count'):
            return False
        return conversation.participant_count >= self.min_participants
    
    def __repr__(self) -> str:
        return f"MinimumParticipants(>={self.min_participants})"


class EntityCountSpec(Specification):
    """
    Specification for entity count in conversations.
    Conversations must have at least N entities extracted.
    """
    
    def __init__(self, min_entities: int = 3):
        """
        Initialize specification.
        
        Args:
            min_entities: Minimum number of entities, default 3
        """
        self.min_entities = min_entities
    
    def is_satisfied_by(self, conversation) -> bool:
        """Check if conversation has minimum entities."""
        if not hasattr(conversation, 'entity_count'):
            return False
        return conversation.entity_count >= self.min_entities
    
    def __repr__(self) -> str:
        return f"EntityCount(>={self.min_entities})"


class ContextRelevanceSpec(Specification):
    """
    Specification for context item relevance.
    Context items must meet minimum relevance score.
    """
    
    def __init__(self, min_relevance: float = 0.60):
        """
        Initialize specification.
        
        Args:
            min_relevance: Minimum relevance score (0.0 to 1.0), default 0.60
        """
        self.min_relevance = min_relevance
    
    def is_satisfied_by(self, context_item) -> bool:
        """Check if context item meets relevance threshold."""
        if not hasattr(context_item, 'relevance_score'):
            return False
        return context_item.relevance_score >= self.min_relevance
    
    def __repr__(self) -> str:
        return f"ContextRelevance(>={self.min_relevance})"


class TierSpec(Specification):
    """
    Specification for memory tier.
    Items must belong to the specified tier (1, 2, or 3).
    """
    
    def __init__(self, tier: int):
        """
        Initialize specification.
        
        Args:
            tier: Memory tier (1=Working Memory, 2=Knowledge Graph, 3=Development Context)
        """
        if tier not in (1, 2, 3):
            raise ValueError("Tier must be 1, 2, or 3")
        self.tier = tier
    
    def is_satisfied_by(self, item) -> bool:
        """Check if item belongs to tier."""
        if not hasattr(item, 'tier'):
            return False
        return item.tier == self.tier
    
    def __repr__(self) -> str:
        tier_names = {1: "Tier 1 (Working Memory)", 2: "Tier 2 (Knowledge Graph)", 3: "Tier 3 (Development Context)"}
        return tier_names.get(self.tier, f"Tier {self.tier}")
