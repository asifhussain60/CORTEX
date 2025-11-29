"""Commands for CORTEX write operations"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from src.application.common.interfaces import ICommand


@dataclass
class CaptureConversationCommand(ICommand):
    """Command to capture a conversation for learning
    
    Triggered when: User captures a conversation from GitHub Copilot chat
    Purpose: Store conversation in Tier 1 Working Memory for future learning
    
    Attributes:
        conversation_id: Unique identifier for the conversation
        title: Conversation title/summary
        content: Full conversation content (JSON or text)
        file_path: Source file path where conversation was captured
        quality_score: Optional quality score (0.0-1.0)
        entity_count: Optional number of entities extracted
        captured_at: When the conversation was captured
    """
    conversation_id: str
    title: str
    content: str
    file_path: str
    quality_score: Optional[float] = None
    entity_count: Optional[int] = None
    captured_at: Optional[datetime] = None


@dataclass
class LearnPatternCommand(ICommand):
    """Command to learn a new pattern from conversation
    
    Triggered when: Pattern extraction identifies a reusable pattern
    Purpose: Store pattern in Tier 2 Knowledge Graph for recommendations
    
    Attributes:
        pattern_id: Unique identifier for the pattern
        pattern_name: Human-readable pattern name
        pattern_type: Type of pattern (e.g., "code_structure", "decision_pattern")
        pattern_content: The pattern itself (code, text, or structured data)
        source_conversation_id: Conversation that produced this pattern
        namespace: Namespace for pattern isolation (e.g., "workspace.auth")
        confidence_score: Initial confidence score (0.0-1.0)
        tags: Optional tags for categorization
        learned_at: When the pattern was learned
    """
    pattern_id: str
    pattern_name: str
    pattern_type: str
    pattern_content: str
    source_conversation_id: str
    namespace: str
    confidence_score: float
    tags: Optional[list[str]] = None
    learned_at: Optional[datetime] = None


@dataclass
class UpdateContextRelevanceCommand(ICommand):
    """Command to update context relevance score
    
    Triggered when: User interaction signals relevance change (feedback, reuse)
    Purpose: Update relevance scores for better search ranking
    
    Attributes:
        conversation_id: Conversation whose relevance changed
        new_relevance_score: New relevance score (0.0-1.0)
        reason: Why relevance changed (e.g., "user_feedback", "pattern_reuse")
        updated_by: Optional user identifier
        updated_at: When the update occurred
    """
    conversation_id: str
    new_relevance_score: float
    reason: str
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class UpdatePatternConfidenceCommand(ICommand):
    """Command to update pattern confidence based on observation
    
    Triggered when: Pattern is recommended and user accepts/rejects
    Purpose: Track pattern reliability over time
    
    Attributes:
        pattern_id: Pattern whose confidence changed
        was_successful: Whether the pattern recommendation was successful
        context_id: Context where pattern was used
        feedback: Optional user feedback
        updated_at: When the observation occurred
    """
    pattern_id: str
    was_successful: bool
    context_id: str
    feedback: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class DeleteConversationCommand(ICommand):
    """Command to delete a conversation
    
    Triggered when: User explicitly deletes a conversation
    Purpose: Remove conversation from storage (with cascade to related patterns)
    
    Attributes:
        conversation_id: Conversation to delete
        delete_related_patterns: Whether to delete patterns learned from this conversation
        deleted_by: Optional user identifier
        deleted_at: When the deletion occurred
    """
    conversation_id: str
    delete_related_patterns: bool = False
    deleted_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
