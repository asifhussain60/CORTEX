"""Query handlers for CORTEX read operations"""
from typing import List, Optional
from datetime import datetime
from src.application.common.interfaces import IRequestHandler
from src.application.common.result import Result
from src.application.common.guards import Guard
from src.application.queries.conversation_queries import (
    SearchContextQuery,
    GetConversationQualityQuery,
    FindSimilarPatternsQuery,
    GetConversationByIdQuery,
    GetPatternByIdQuery,
    GetRecentConversationsQuery,
    GetPatternsByNamespaceQuery,
    ConversationDto,
    PatternDto,
    ConversationQualityDto
)
from src.domain.value_objects import (
    ConversationQuality,
    RelevanceScore,
    Namespace,
    PatternConfidence
)
from src.infrastructure.persistence.unit_of_work import IUnitOfWork
import logging

logger = logging.getLogger(__name__)


class SearchContextHandler(IRequestHandler[SearchContextQuery, Result[List[ConversationDto]]]):
    """Handler for searching conversations
    
    Responsibilities:
    - Validate search parameters
    - Execute full-text search
    - Filter by namespace and relevance
    - Return ranked results
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: SearchContextQuery) -> Result[List[ConversationDto]]:
        """Search conversations by text
        
        Args:
            request: SearchContextQuery with search criteria
            
        Returns:
            Result[List[ConversationDto]] with matching conversations
        """
        try:
            # Validate input
            Guard.against_empty(request.search_text, "search_text")
            Guard.against_out_of_range(request.min_relevance, 0.0, 1.0, "min_relevance")
            Guard.against_negative_or_zero(request.max_results, "max_results")
            
            # Validate namespace if provided
            if request.namespace_filter:
                namespace = Namespace(value=request.namespace_filter)
            
            # Search conversations in database
            try:
                async with self._uow as uow:
                    # Get high-quality conversations first
                    conversations = await uow.conversations.get_high_quality(request.min_relevance)
                    
                    # Filter by namespace if specified
                    if request.namespace_filter:
                        conversations = [c for c in conversations if c.namespace == request.namespace_filter]
                    
                    # Simple text search (filter by title/content containing search text)
                    search_lower = request.search_text.lower()
                    filtered_conversations = [
                        c for c in conversations
                        if search_lower in c.title.lower() or search_lower in c.content.lower()
                    ]
                    
                    # Sort by quality (best first) and limit results
                    filtered_conversations.sort(key=lambda c: c.quality, reverse=True)
                    results = filtered_conversations[:request.max_results]
                    
                    # Convert to DTOs
                    dtos = [
                        ConversationDto(
                            conversation_id=c.conversation_id,
                            title=c.title,
                            content=c.content[:500],  # Truncate content for preview
                            file_path=f"tier1/{c.namespace}/{c.conversation_id}.json",
                            quality_score=c.quality,
                            entity_count=c.entity_count,
                            relevance_score=c.quality,  # Use quality as relevance proxy
                            captured_at=c.captured_at.isoformat()
                        )
                        for c in results
                    ]
                    
                    logger.info(
                        f"Searching context: '{request.search_text}' "
                        f"(namespace: {request.namespace_filter}, "
                        f"min_relevance: {request.min_relevance}, "
                        f"found: {len(dtos)}/{len(conversations)} conversations)"
                    )
                    
                    return Result.success(dtos)
                    
            except Exception as db_error:
                logger.error(f"Database error searching context: {db_error}", exc_info=True)
                return Result.failure([f"Failed to search conversations: {str(db_error)}"])
            
        except ValueError as e:
            logger.error(f"Validation error searching context: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error searching context: {e}", exc_info=True)
            return Result.failure([f"Failed to search context: {str(e)}"])


class GetConversationQualityHandler(IRequestHandler[GetConversationQualityQuery, Result[ConversationQualityDto]]):
    """Handler for getting conversation quality
    
    Responsibilities:
    - Validate conversation ID
    - Retrieve conversation from database
    - Calculate quality metrics
    - Return quality assessment
    """
    
    async def handle(self, request: GetConversationQualityQuery) -> Result[ConversationQualityDto]:
        """Get conversation quality
        
        Args:
            request: GetConversationQualityQuery with conversation ID
            
        Returns:
            Result[ConversationQualityDto] with quality metrics
        """
        try:
            # Validate input
            Guard.against_empty(request.conversation_id, "conversation_id")
            
            # TODO: Get conversation from database
            # For now, return mock quality
            logger.info(f"Getting quality for conversation: {request.conversation_id}")
            
            # Create quality value object
            quality = ConversationQuality(
                score=0.85,
                turn_count=10,
                entity_count=20
            )
            
            # Convert to DTO
            dto = ConversationQualityDto(
                conversation_id=request.conversation_id,
                score=quality.score,
                turn_count=quality.turn_count,
                entity_count=quality.entity_count,
                quality_level=quality.quality_level,
                should_capture=quality.should_capture,
                richness_factor=quality.richness_factor
            )
            
            return Result.success(dto)
            
        except ValueError as e:
            logger.error(f"Validation error getting quality: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error getting quality: {e}", exc_info=True)
            return Result.failure([f"Failed to get quality: {str(e)}"])


class FindSimilarPatternsHandler(IRequestHandler[FindSimilarPatternsQuery, Result[List[PatternDto]]]):
    """Handler for finding similar patterns
    
    Responsibilities:
    - Validate search parameters
    - Validate namespace
    - Execute similarity search
    - Filter by confidence and pattern type
    - Return ranked results
    """
    
    async def handle(self, request: FindSimilarPatternsQuery) -> Result[List[PatternDto]]:
        """Find similar patterns
        
        Args:
            request: FindSimilarPatternsQuery with search criteria
            
        Returns:
            Result[List[PatternDto]] with matching patterns
        """
        try:
            # Validate input
            Guard.against_empty(request.context, "context")
            Guard.against_empty(request.namespace, "namespace")
            Guard.against_out_of_range(request.min_confidence, 0.0, 1.0, "min_confidence")
            Guard.against_negative_or_zero(request.max_results, "max_results")
            
            # Validate namespace
            namespace = Namespace(value=request.namespace)
            
            # TODO: Execute similarity search in database
            logger.info(
                f"Finding similar patterns: namespace={namespace.value}, "
                f"type={request.pattern_type}, "
                f"min_confidence={request.min_confidence}"
            )
            
            # Mock results
            results = [
                PatternDto(
                    pattern_id="pat-001",
                    pattern_name="Authentication Pattern",
                    pattern_type="code_structure",
                    pattern_content="# JWT authentication pattern\n...",
                    namespace=namespace.value,
                    confidence_score=0.85,
                    observation_count=15,
                    success_rate=0.90,
                    learned_at="2024-12-15T10:00:00Z"
                )
            ]
            
            return Result.success(results)
            
        except ValueError as e:
            logger.error(f"Validation error finding patterns: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error finding patterns: {e}", exc_info=True)
            return Result.failure([f"Failed to find patterns: {str(e)}"])


class GetConversationByIdHandler(IRequestHandler[GetConversationByIdQuery, Result[Optional[ConversationDto]]]):
    """Handler for getting conversation by ID
    
    Responsibilities:
    - Validate conversation ID
    - Retrieve conversation from database
    - Return conversation details
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: GetConversationByIdQuery) -> Result[Optional[ConversationDto]]:
        """Get conversation by ID
        
        Args:
            request: GetConversationByIdQuery with conversation ID
            
        Returns:
            Result[Optional[ConversationDto]] with conversation or None
        """
        try:
            # Validate input
            Guard.against_empty(request.conversation_id, "conversation_id")
            
            # Get conversation from database
            try:
                async with self._uow as uow:
                    conversation = await uow.conversations.get_by_id(request.conversation_id)
                    
                    if not conversation:
                        logger.info(f"Conversation not found: {request.conversation_id}")
                        return Result.success(None)
                    
                    # Convert to DTO
                    dto = ConversationDto(
                        conversation_id=conversation.conversation_id,
                        title=conversation.title,
                        content=conversation.content,
                        file_path=f"tier1/{conversation.namespace}/{conversation.conversation_id}.json",
                        quality_score=conversation.quality,
                        entity_count=conversation.entity_count,
                        relevance_score=conversation.quality,
                        captured_at=conversation.captured_at.isoformat()
                    )
                    
                    logger.info(f"Retrieved conversation: {request.conversation_id}")
                    return Result.success(dto)
                    
            except Exception as db_error:
                logger.error(f"Database error getting conversation: {db_error}", exc_info=True)
                return Result.failure([f"Failed to get conversation: {str(db_error)}"])
            
        except ValueError as e:
            logger.error(f"Validation error getting conversation: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error getting conversation: {e}", exc_info=True)
            return Result.failure([f"Failed to get conversation: {str(e)}"])


class GetPatternByIdHandler(IRequestHandler[GetPatternByIdQuery, Result[Optional[PatternDto]]]):
    """Handler for getting pattern by ID
    
    Responsibilities:
    - Validate pattern ID
    - Retrieve pattern from database
    - Return pattern details
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: GetPatternByIdQuery) -> Result[Optional[PatternDto]]:
        """Get pattern by ID
        
        Args:
            request: GetPatternByIdQuery with pattern ID
            
        Returns:
            Result[Optional[PatternDto]] with pattern or None
        """
        try:
            # Validate input
            Guard.against_empty(request.pattern_id, "pattern_id")
            
            # Get pattern from database
            try:
                async with self._uow as uow:
                    pattern = await uow.patterns.get_by_id(request.pattern_id)
                    
                    if not pattern:
                        logger.info(f"Pattern not found: {request.pattern_id}")
                        return Result.success(None)
                    
                    # Convert to DTO
                    dto = PatternDto(
                        pattern_id=pattern.pattern_id,
                        pattern_name=pattern.pattern_name,
                        pattern_type=pattern.pattern_type,
                        pattern_content=pattern.pattern_content,
                        namespace="tier2.knowledge_graph",  # Patterns are in Tier 2
                        confidence_score=pattern.confidence,
                        observation_count=pattern.observation_count,
                        success_rate=pattern.success_rate,
                        learned_at=pattern.learned_at.isoformat()
                    )
                    
                    logger.info(f"Retrieved pattern: {request.pattern_id}")
                    return Result.success(dto)
                    
            except Exception as db_error:
                logger.error(f"Database error getting pattern: {db_error}", exc_info=True)
                return Result.failure([f"Failed to get pattern: {str(db_error)}"])
            
        except ValueError as e:
            logger.error(f"Validation error getting pattern: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error getting pattern: {e}", exc_info=True)
            return Result.failure([f"Failed to get pattern: {str(e)}"])


class GetRecentConversationsHandler(IRequestHandler[GetRecentConversationsQuery, Result[List[ConversationDto]]]):
    """Handler for getting recent conversations
    
    Responsibilities:
    - Validate parameters
    - Retrieve recent conversations from database
    - Filter by namespace if provided
    - Return sorted results
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: GetRecentConversationsQuery) -> Result[List[ConversationDto]]:
        """Get recent conversations
        
        Args:
            request: GetRecentConversationsQuery with filters
            
        Returns:
            Result[List[ConversationDto]] with recent conversations
        """
        try:
            # Validate input
            Guard.against_negative_or_zero(request.max_results, "max_results")
            
            # Validate namespace if provided
            if request.namespace_filter:
                namespace = Namespace(value=request.namespace_filter)
            
            # Get recent conversations from database
            try:
                async with self._uow as uow:
                    # Get all conversations
                    conversations = await uow.conversations.get_all()
                    
                    # Filter by namespace if specified
                    if request.namespace_filter:
                        conversations = [c for c in conversations if c.namespace == request.namespace_filter]
                    
                    # Sort by captured_at (most recent first)
                    conversations.sort(key=lambda c: c.captured_at, reverse=True)
                    
                    # Limit results
                    results = conversations[:request.max_results]
                    
                    # Convert to DTOs
                    dtos = [
                        ConversationDto(
                            conversation_id=c.conversation_id,
                            title=c.title,
                            content=c.content[:200],  # Preview only
                            file_path=f"tier1/{c.namespace}/{c.conversation_id}.json",
                            quality_score=c.quality,
                            entity_count=c.entity_count,
                            relevance_score=c.quality,
                            captured_at=c.captured_at.isoformat()
                        )
                        for c in results
                    ]
                    
                    logger.info(
                        f"Retrieved {len(dtos)} recent conversations "
                        f"(namespace={request.namespace_filter})"
                    )
                    
                    return Result.success(dtos)
                    
            except Exception as db_error:
                logger.error(f"Database error getting recent conversations: {db_error}", exc_info=True)
                return Result.failure([f"Failed to get recent conversations: {str(db_error)}"])
            
        except ValueError as e:
            logger.error(f"Validation error getting recent conversations: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error getting recent conversations: {e}", exc_info=True)
            return Result.failure([f"Failed to get recent conversations: {str(e)}"])


class GetPatternsByNamespaceHandler(IRequestHandler[GetPatternsByNamespaceQuery, Result[List[PatternDto]]]):
    """Handler for getting patterns by namespace
    
    Responsibilities:
    - Validate namespace
    - Retrieve patterns from database
    - Filter by confidence
    - Return sorted results
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: GetPatternsByNamespaceQuery) -> Result[List[PatternDto]]:
        """Get patterns by namespace
        
        Args:
            request: GetPatternsByNamespaceQuery with namespace
            
        Returns:
            Result[List[PatternDto]] with patterns in namespace
        """
        try:
            # Validate input
            Guard.against_empty(request.namespace, "namespace")
            Guard.against_out_of_range(request.min_confidence, 0.0, 1.0, "min_confidence")
            Guard.against_negative_or_zero(request.max_results, "max_results")
            
            # Validate namespace
            namespace = Namespace(value=request.namespace)
            
            # Get patterns from database
            try:
                async with self._uow as uow:
                    # Get patterns with minimum confidence
                    patterns = await uow.patterns.get_by_confidence(request.min_confidence)
                    
                    # Sort by confidence (highest first) and limit results
                    patterns.sort(key=lambda p: p.confidence, reverse=True)
                    results = patterns[:request.max_results]
                    
                    # Convert to DTOs
                    dtos = [
                        PatternDto(
                            pattern_id=p.pattern_id,
                            pattern_name=p.pattern_name,
                            pattern_type=p.pattern_type,
                            pattern_content=p.pattern_content,
                            namespace="tier2.knowledge_graph",
                            confidence_score=p.confidence,
                            observation_count=p.observation_count,
                            success_rate=p.success_rate,
                            learned_at=p.learned_at.isoformat()
                        )
                        for p in results
                    ]
                    
                    logger.info(
                        f"Retrieved {len(dtos)} patterns for namespace: {namespace.value} "
                        f"(min_confidence={request.min_confidence})"
                    )
                    
                    return Result.success(dtos)
                    
            except Exception as db_error:
                logger.error(f"Database error getting patterns: {db_error}", exc_info=True)
                return Result.failure([f"Failed to get patterns: {str(db_error)}"])
            
        except ValueError as e:
            logger.error(f"Validation error getting patterns: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error getting patterns: {e}", exc_info=True)
            return Result.failure([f"Failed to get patterns: {str(e)}"])
