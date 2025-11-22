"""Queries for CORTEX read operations"""
from dataclasses import dataclass
from typing import Optional, List
from src.application.common.interfaces import IQuery


# Define result types for queries
@dataclass
class ConversationDto:
    """Data transfer object for conversation"""
    conversation_id: str
    title: str
    content: str
    file_path: str
    quality_score: float
    entity_count: int
    relevance_score: float
    captured_at: str


@dataclass
class PatternDto:
    """Data transfer object for pattern"""
    pattern_id: str
    pattern_name: str
    pattern_type: str
    pattern_content: str
    namespace: str
    confidence_score: float
    observation_count: int
    success_rate: float
    learned_at: str


@dataclass
class ConversationQualityDto:
    """Data transfer object for conversation quality"""
    conversation_id: str
    score: float
    turn_count: int
    entity_count: int
    quality_level: str
    should_capture: bool
    richness_factor: float


# Queries
@dataclass
class SearchContextQuery(IQuery[List[ConversationDto]]):
    """Query to search conversations by text
    
    Purpose: Full-text search across conversation content and titles
    Use Case: User searches for relevant past conversations
    
    Attributes:
        search_text: Text to search for
        namespace_filter: Optional namespace to filter by
        min_relevance: Minimum relevance score (0.0-1.0)
        max_results: Maximum number of results to return
    """
    search_text: str
    namespace_filter: Optional[str] = None
    min_relevance: float = 0.0
    max_results: int = 10


@dataclass
class GetConversationQualityQuery(IQuery[ConversationQualityDto]):
    """Query to get quality metrics for a conversation
    
    Purpose: Assess conversation quality for capture decisions
    Use Case: UI displays quality indicators before capture
    
    Attributes:
        conversation_id: Conversation to assess
    """
    conversation_id: str


@dataclass
class FindSimilarPatternsQuery(IQuery[List[PatternDto]]):
    """Query to find patterns similar to given context
    
    Purpose: Pattern-based recommendations for current situation
    Use Case: User is coding, CORTEX suggests relevant patterns
    
    Attributes:
        context: Current context (code, description, etc.)
        namespace: Namespace to search in
        pattern_type: Optional pattern type filter
        min_confidence: Minimum confidence score (0.0-1.0)
        max_results: Maximum number of results to return
    """
    context: str
    namespace: str
    pattern_type: Optional[str] = None
    min_confidence: float = 0.75
    max_results: int = 5


@dataclass
class GetConversationByIdQuery(IQuery[Optional[ConversationDto]]):
    """Query to get a conversation by ID
    
    Purpose: Retrieve full conversation details
    Use Case: User clicks on conversation to view details
    
    Attributes:
        conversation_id: Conversation to retrieve
    """
    conversation_id: str


@dataclass
class GetPatternByIdQuery(IQuery[Optional[PatternDto]]):
    """Query to get a pattern by ID
    
    Purpose: Retrieve full pattern details
    Use Case: User clicks on pattern to view details
    
    Attributes:
        pattern_id: Pattern to retrieve
    """
    pattern_id: str


@dataclass
class GetRecentConversationsQuery(IQuery[List[ConversationDto]]):
    """Query to get recent conversations
    
    Purpose: Show recently captured conversations
    Use Case: Dashboard shows recent activity
    
    Attributes:
        namespace_filter: Optional namespace to filter by
        max_results: Maximum number of results to return
    """
    namespace_filter: Optional[str] = None
    max_results: int = 20


@dataclass
class GetPatternsByNamespaceQuery(IQuery[List[PatternDto]]):
    """Query to get all patterns in a namespace
    
    Purpose: Browse patterns by namespace
    Use Case: User explores workspace-specific patterns
    
    Attributes:
        namespace: Namespace to query
        min_confidence: Minimum confidence score (0.0-1.0)
        max_results: Maximum number of results to return
    """
    namespace: str
    min_confidence: float = 0.60
    max_results: int = 50
