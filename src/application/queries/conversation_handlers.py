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
            
            # TODO: Execute search in database
            # For now, return mock results
            logger.info(
                f"Searching context: '{request.search_text}' "
                f"(namespace: {request.namespace_filter}, "
                f"min_relevance: {request.min_relevance}, "
                f"max_results: {request.max_results})"
            )
            
            # Mock results
            results = [
                ConversationDto(
                    conversation_id="conv-001",
                    title="Sample conversation 1",
                    content="This is a sample conversation matching the search",
                    file_path="/path/to/conv1.json",
                    quality_score=0.85,
                    entity_count=15,
                    relevance_score=0.90,
                    captured_at="2024-12-20T10:00:00Z"
                )
            ]
            
            return Result.success(results)
            
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
            
            # TODO: Get conversation from database
            logger.info(f"Getting conversation: {request.conversation_id}")
            
            # Mock result
            conversation = ConversationDto(
                conversation_id=request.conversation_id,
                title="Sample conversation",
                content="This is a sample conversation",
                file_path="/path/to/conv.json",
                quality_score=0.85,
                entity_count=15,
                relevance_score=0.90,
                captured_at="2024-12-20T10:00:00Z"
            )
            
            return Result.success(conversation)
            
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
            
            # TODO: Get pattern from database
            logger.info(f"Getting pattern: {request.pattern_id}")
            
            # Mock result
            pattern = PatternDto(
                pattern_id=request.pattern_id,
                pattern_name="Sample Pattern",
                pattern_type="code_structure",
                pattern_content="# Sample pattern\n...",
                namespace="workspace.sample",
                confidence_score=0.85,
                observation_count=15,
                success_rate=0.90,
                learned_at="2024-12-15T10:00:00Z"
            )
            
            return Result.success(pattern)
            
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
            
            # TODO: Get recent conversations from database
            logger.info(
                f"Getting recent conversations: namespace={request.namespace_filter}, "
                f"max={request.max_results}"
            )
            
            # Mock results
            results = []
            
            return Result.success(results)
            
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
            
            # TODO: Get patterns from database
            logger.info(
                f"Getting patterns for namespace: {namespace.value} "
                f"(min_confidence={request.min_confidence})"
            )
            
            # Mock results
            results = []
            
            return Result.success(results)
            
        except ValueError as e:
            logger.error(f"Validation error getting patterns: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error getting patterns: {e}", exc_info=True)
            return Result.failure([f"Failed to get patterns: {str(e)}"])
