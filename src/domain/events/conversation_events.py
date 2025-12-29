"""Domain events for conversation lifecycle"""
from dataclasses import dataclass
from datetime import datetime
from typing import List
from src.domain.common.base_entity import BaseEvent


@dataclass
class ConversationCapturedEvent(BaseEvent):
    """Event raised when a conversation is captured
    
    Triggered when: User captures a conversation for learning
    Purpose: Enables reactive workflows like pattern extraction, notification
    
    Attributes:
        conversation_id: Unique identifier for the conversation
        title: Conversation title
        quality_score: Quality score (0.0-1.0)
        entity_count: Number of entities extracted
        file_path: Source file path
        captured_at: When the conversation was captured
    """
    conversation_id: str
    title: str
    quality_score: float
    entity_count: int
    file_path: str
    captured_at: datetime


@dataclass
class PatternLearnedEvent(BaseEvent):
    """Event raised when a new pattern is learned
    
    Triggered when: Pattern extraction identifies a new reusable pattern
    Purpose: Updates knowledge graph, triggers similar pattern search
    
    Attributes:
        pattern_id: Unique identifier for the pattern
        pattern_type: Type of pattern (e.g., "code_structure", "decision_pattern")
        confidence: Confidence score (0.0-1.0)
        source_conversation_id: Conversation that produced the pattern
        pattern_name: Human-readable pattern name
        learned_at: When the pattern was learned
    """
    pattern_id: str
    pattern_type: str
    confidence: float
    source_conversation_id: str
    pattern_name: str
    learned_at: datetime


@dataclass
class BrainRuleViolatedEvent(BaseEvent):
    """Event raised when a brain protection rule is violated
    
    Triggered when: Operation attempts to violate SKULL protection rules
    Purpose: Logging, alerting, prevention of unsafe operations
    
    Attributes:
        rule_id: Unique identifier for the violated rule
        rule_name: Human-readable rule name
        violation_details: Description of what was violated
        severity: Severity level ("critical", "high", "medium", "low")
        attempted_operation: What operation was attempted
        detected_at: When the violation was detected
    """
    rule_id: str
    rule_name: str
    violation_details: str
    severity: str
    attempted_operation: str
    detected_at: datetime


@dataclass
class ContextRelevanceUpdatedEvent(BaseEvent):
    """Event raised when context relevance score changes
    
    Triggered when: Conversation relevance is recalculated
    Purpose: Updates search indexes, triggers re-ranking
    
    Attributes:
        conversation_id: Conversation whose relevance changed
        old_score: Previous relevance score
        new_score: New relevance score
        reason: Why relevance changed
        affected_queries: Queries affected by this change
        updated_at: When the update occurred
    """
    conversation_id: str
    old_score: float
    new_score: float
    reason: str
    affected_queries: List[str]
    updated_at: datetime


@dataclass
class PatternMatchedEvent(BaseEvent):
    """Event raised when a pattern is successfully matched
    
    Triggered when: Current situation matches a known pattern
    Purpose: Enables pattern-based recommendations
    
    Attributes:
        pattern_id: Pattern that was matched
        context_id: Context where pattern was matched
        match_confidence: How well the pattern matched (0.0-1.0)
        matched_at: When the match occurred
    """
    pattern_id: str
    context_id: str
    match_confidence: float
    matched_at: datetime


@dataclass
class NamespaceIsolationViolatedEvent(BaseEvent):
    """Event raised when namespace isolation is violated
    
    Triggered when: Cross-namespace access violates isolation rules
    Purpose: Security, auditing, namespace integrity
    
    Attributes:
        source_namespace: Namespace attempting access
        target_namespace: Namespace being accessed
        violation_type: Type of violation
        detected_at: When the violation was detected
    """
    source_namespace: str
    target_namespace: str
    violation_type: str
    detected_at: datetime
