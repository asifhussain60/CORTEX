"""Domain events module"""
from .conversation_events import (
    ConversationCapturedEvent,
    PatternLearnedEvent,
    BrainRuleViolatedEvent,
    ContextRelevanceUpdatedEvent,
    PatternMatchedEvent,
    NamespaceIsolationViolatedEvent,
)

__all__ = [
    'ConversationCapturedEvent',
    'PatternLearnedEvent',
    'BrainRuleViolatedEvent',
    'ContextRelevanceUpdatedEvent',
    'PatternMatchedEvent',
    'NamespaceIsolationViolatedEvent',
]
