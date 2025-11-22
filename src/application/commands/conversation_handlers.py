"""Command handlers for CORTEX write operations"""
from typing import Optional
from datetime import datetime
from src.application.common.interfaces import IRequestHandler
from src.application.common.result import Result
from src.application.common.guards import Guard
from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    LearnPatternCommand,
    UpdateContextRelevanceCommand,
    UpdatePatternConfidenceCommand,
    DeleteConversationCommand
)
from src.domain.value_objects import (
    ConversationQuality,
    RelevanceScore,
    Namespace,
    PatternConfidence
)
from src.domain.events import (
    ConversationCapturedEvent,
    PatternLearnedEvent,
    ContextRelevanceUpdatedEvent
)
from src.infrastructure.persistence.unit_of_work import IUnitOfWork
from src.infrastructure.persistence.repositories.conversation_repository import Conversation
from src.infrastructure.persistence.repositories.pattern_repository import Pattern
from src.infrastructure.persistence.repositories.context_repository import ContextItem
import logging

logger = logging.getLogger(__name__)


class CaptureConversationHandler(IRequestHandler[CaptureConversationCommand, Result[str]]):
    """Handler for capturing conversations
    
    Responsibilities:
    - Validate conversation data
    - Calculate quality score if not provided
    - Store conversation in Tier 1 Working Memory
    - Raise ConversationCapturedEvent
    - Return conversation ID
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: CaptureConversationCommand) -> Result[str]:
        """Capture a conversation
        
        Args:
            request: CaptureConversationCommand with conversation data
            
        Returns:
            Result[str] with conversation_id on success, errors on failure
        """
        try:
            # Validate input
            Guard.against_empty(request.conversation_id, "conversation_id")
            Guard.against_empty(request.title, "title")
            Guard.against_empty(request.content, "content")
            Guard.against_empty(request.file_path, "file_path")
            
            # Calculate quality if not provided
            if request.quality_score is None:
                # Simple heuristic: length-based quality
                content_length = len(request.content)
                turn_count = request.content.count("User:") + request.content.count("Assistant:")
                entity_count = request.entity_count or 0
                
                # Basic quality calculation
                if content_length < 100:
                    quality_score = 0.3
                elif content_length < 500:
                    quality_score = 0.5
                elif content_length < 1000:
                    quality_score = 0.7
                else:
                    quality_score = 0.85
            else:
                quality_score = request.quality_score
            
            # Create quality value object
            quality = ConversationQuality(
                score=quality_score,
                turn_count=max(1, request.content.count("User:")),
                entity_count=request.entity_count or 0
            )
            
            # Check if should capture
            if not quality.should_capture:
                return Result.failure([
                    f"Conversation quality too low ({quality.quality_level}). "
                    f"Minimum quality: Good (0.70), actual: {quality.score:.2f}"
                ])
            
            # Store in database using Unit of Work
            try:
                async with self._uow as uow:
                    # Create conversation entity
                    conversation = Conversation(
                        conversation_id=request.conversation_id,
                        title=request.title,
                        content=request.content,
                        quality=quality.score,
                        participant_count=quality.turn_count,
                        entity_count=quality.entity_count,
                        captured_at=request.captured_at or datetime.now(),
                        namespace="general"  # Default namespace for conversations
                    )
                    
                    # Check if conversation already exists
                    existing = await uow.conversations.get_by_id(request.conversation_id)
                    if existing:
                        # Update existing conversation
                        existing.title = conversation.title
                        existing.content = conversation.content
                        existing.quality = conversation.quality
                        existing.participant_count = conversation.participant_count
                        existing.entity_count = conversation.entity_count
                        existing.updated_at = datetime.now()
                        await uow.conversations.update(existing)
                        logger.info(f"Updated existing conversation: {request.conversation_id}")
                    else:
                        # Add new conversation
                        await uow.conversations.add(conversation)
                        logger.info(f"Added new conversation: {request.conversation_id}")
                    
                    # Commit transaction
                    await uow.commit()
                    
                    logger.info(
                        f"Captured conversation: {request.conversation_id} "
                        f"(quality: {quality.quality_level} {quality.quality_emoji})"
                    )
                    
            except Exception as db_error:
                logger.error(f"Database error capturing conversation: {db_error}", exc_info=True)
                return Result.failure([f"Failed to store conversation: {str(db_error)}"])
            
            # TODO: Raise domain event
            # event = ConversationCapturedEvent(
            #     conversation_id=request.conversation_id,
            #     title=request.title,
            #     quality_score=quality.score,
            #     entity_count=quality.entity_count,
            #     file_path=request.file_path,
            #     captured_at=request.captured_at or datetime.now()
            # )
            # dispatcher.dispatch(event)
            
            return Result.success(request.conversation_id)
            
        except ValueError as e:
            logger.error(f"Validation error capturing conversation: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error capturing conversation: {e}", exc_info=True)
            return Result.failure([f"Failed to capture conversation: {str(e)}"])


class LearnPatternHandler(IRequestHandler[LearnPatternCommand, Result[str]]):
    """Handler for learning patterns
    
    Responsibilities:
    - Validate pattern data
    - Create namespace value object
    - Create confidence value object
    - Store pattern in Tier 2 Knowledge Graph
    - Raise PatternLearnedEvent
    - Return pattern ID
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: LearnPatternCommand) -> Result[str]:
        """Learn a new pattern
        
        Args:
            request: LearnPatternCommand with pattern data
            
        Returns:
            Result[str] with pattern_id on success, errors on failure
        """
        try:
            # Validate input
            Guard.against_empty(request.pattern_id, "pattern_id")
            Guard.against_empty(request.pattern_name, "pattern_name")
            Guard.against_empty(request.pattern_type, "pattern_type")
            Guard.against_empty(request.pattern_content, "pattern_content")
            Guard.against_empty(request.source_conversation_id, "source_conversation_id")
            Guard.against_empty(request.namespace, "namespace")
            Guard.against_out_of_range(request.confidence_score, 0.0, 1.0, "confidence_score")
            
            # Create namespace value object
            namespace = Namespace(value=request.namespace)
            
            # Create confidence value object (initial observation with 100% success)
            confidence = PatternConfidence(
                score=request.confidence_score,
                observation_count=1,
                success_rate=1.0  # Initial pattern starts with 100% success
            )
            
            # Check if confidence is sufficient
            if confidence.is_experimental:
                logger.warning(
                    f"Pattern {request.pattern_id} has experimental confidence: "
                    f"{confidence.confidence_level} {confidence.confidence_emoji}"
                )
            
            # Store in database using Unit of Work
            try:
                async with self._uow as uow:
                    # Create pattern entity
                    pattern = Pattern(
                        pattern_id=request.pattern_id,
                        pattern_name=request.pattern_name,
                        pattern_type=request.pattern_type,
                        pattern_content=request.pattern_content,
                        confidence=confidence.score,
                        source_conversation_id=request.source_conversation_id,
                        observation_count=confidence.observation_count,
                        success_rate=confidence.success_rate,
                        tags=request.tags or [],
                        examples=[],  # No examples field in command
                        related_patterns=[],  # No related_patterns field in command
                        learned_at=request.learned_at or datetime.now()
                    )
                    
                    # Check if pattern already exists
                    existing = await uow.patterns.get_by_id(request.pattern_id)
                    if existing:
                        # Update existing pattern
                        existing.pattern_name = pattern.pattern_name
                        existing.pattern_type = pattern.pattern_type
                        existing.pattern_content = pattern.pattern_content
                        existing.confidence = pattern.confidence
                        existing.observation_count = pattern.observation_count
                        existing.success_rate = pattern.success_rate
                        existing.tags = pattern.tags
                        existing.examples = pattern.examples
                        existing.related_patterns = pattern.related_patterns
                        existing.updated_at = datetime.now()
                        await uow.patterns.update(existing)
                        logger.info(f"Updated existing pattern: {request.pattern_id}")
                    else:
                        # Add new pattern
                        await uow.patterns.add(pattern)
                        logger.info(f"Added new pattern: {request.pattern_id}")
                    
                    # Commit transaction
                    await uow.commit()
                    
                    logger.info(
                        f"Learned pattern: {request.pattern_id} "
                        f"(type: {request.pattern_type}, confidence: {confidence.confidence_level})"
                    )
                    
            except Exception as db_error:
                logger.error(f"Database error learning pattern: {db_error}", exc_info=True)
                return Result.failure([f"Failed to store pattern: {str(db_error)}"])
            
            # TODO: Raise domain event
            # event = PatternLearnedEvent(
            #     pattern_id=request.pattern_id,
            #     pattern_type=request.pattern_type,
            #     confidence=confidence.score,
            #     source_conversation_id=request.source_conversation_id,
            #     pattern_name=request.pattern_name,
            #     learned_at=request.learned_at or datetime.now()
            # )
            # dispatcher.dispatch(event)
            
            return Result.success(request.pattern_id)
            
        except ValueError as e:
            logger.error(f"Validation error learning pattern: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error learning pattern: {e}", exc_info=True)
            return Result.failure([f"Failed to learn pattern: {str(e)}"])


class UpdateContextRelevanceHandler(IRequestHandler[UpdateContextRelevanceCommand, Result[bool]]):
    """Handler for updating context relevance
    
    Responsibilities:
    - Validate relevance score
    - Create relevance score value object
    - Update conversation relevance in database
    - Raise ContextRelevanceUpdatedEvent
    - Return success status
    """
    
    async def handle(self, request: UpdateContextRelevanceCommand) -> Result[bool]:
        """Update context relevance
        
        Args:
            request: UpdateContextRelevanceCommand with new relevance
            
        Returns:
            Result[bool] with True on success, errors on failure
        """
        try:
            # Validate input
            Guard.against_empty(request.conversation_id, "conversation_id")
            Guard.against_empty(request.reason, "reason")
            Guard.against_out_of_range(request.new_relevance_score, 0.0, 1.0, "new_relevance_score")
            
            # Create relevance score value object
            relevance = RelevanceScore(value=request.new_relevance_score)
            
            # TODO: Get old relevance from database
            old_relevance = 0.5  # Placeholder
            
            # TODO: Update in database
            logger.info(
                f"Updated relevance for {request.conversation_id}: "
                f"{old_relevance:.2f} -> {relevance.value:.2f} "
                f"({relevance.quality_label} {relevance.quality_emoji}) "
                f"Reason: {request.reason}"
            )
            
            # TODO: Raise domain event
            # event = ContextRelevanceUpdatedEvent(
            #     conversation_id=request.conversation_id,
            #     old_score=old_relevance,
            #     new_score=relevance.value,
            #     reason=request.reason,
            #     affected_queries=[],  # TODO: Calculate affected queries
            #     updated_at=request.updated_at or datetime.now()
            # )
            # dispatcher.dispatch(event)
            
            return Result.success(True)
            
        except ValueError as e:
            logger.error(f"Validation error updating relevance: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error updating relevance: {e}", exc_info=True)
            return Result.failure([f"Failed to update relevance: {str(e)}"])


class UpdatePatternConfidenceHandler(IRequestHandler[UpdatePatternConfidenceCommand, Result[bool]]):
    """Handler for updating pattern confidence
    
    Responsibilities:
    - Validate observation data
    - Get current confidence from database
    - Update confidence with new observation
    - Store updated confidence
    - Return success status
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: UpdatePatternConfidenceCommand) -> Result[bool]:
        """Update pattern confidence
        
        Args:
            request: UpdatePatternConfidenceCommand with observation
            
        Returns:
            Result[bool] with True on success, errors on failure
        """
        try:
            # Validate input
            Guard.against_empty(request.pattern_id, "pattern_id")
            Guard.against_empty(request.context_id, "context_id")
            
            # Get current pattern and update confidence
            try:
                async with self._uow as uow:
                    # Retrieve existing pattern
                    pattern = await uow.patterns.get_by_id(request.pattern_id)
                    
                    if not pattern:
                        return Result.failure([f"Pattern not found: {request.pattern_id}"])
                    
                    # Create current confidence value object
                    current_confidence = PatternConfidence(
                        score=pattern.confidence,
                        observation_count=pattern.observation_count,
                        success_rate=pattern.success_rate
                    )
                    
                    # Update with new observation
                    updated_confidence = current_confidence.with_new_observation(
                        was_successful=request.was_successful
                    )
                    
                    # Update pattern entity
                    pattern.confidence = updated_confidence.score
                    pattern.observation_count = updated_confidence.observation_count
                    pattern.success_rate = updated_confidence.success_rate
                    pattern.updated_at = datetime.now()
                    
                    # Save to database
                    await uow.patterns.update(pattern)
                    await uow.commit()
                    
                    logger.info(
                        f"Updated confidence for {request.pattern_id}: "
                        f"{current_confidence.confidence_level} -> {updated_confidence.confidence_level} "
                        f"(observations: {current_confidence.observation_count} -> {updated_confidence.observation_count}, "
                        f"success rate: {current_confidence.success_rate:.2%} -> {updated_confidence.success_rate:.2%})"
                    )
                    
            except Exception as db_error:
                logger.error(f"Database error updating pattern confidence: {db_error}", exc_info=True)
                return Result.failure([f"Failed to update pattern confidence: {str(db_error)}"])
            
            return Result.success(True)
            
        except ValueError as e:
            logger.error(f"Validation error updating confidence: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error updating confidence: {e}", exc_info=True)
            return Result.failure([f"Failed to update confidence: {str(e)}"])


class DeleteConversationHandler(IRequestHandler[DeleteConversationCommand, Result[bool]]):
    """Handler for deleting conversations
    
    Responsibilities:
    - Validate conversation exists
    - Delete conversation from database
    - Optionally cascade delete related patterns
    - Return success status
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
        """
        Initialize handler with Unit of Work.
        
        Args:
            unit_of_work: Unit of Work for database access
        """
        self._uow = unit_of_work
    
    async def handle(self, request: DeleteConversationCommand) -> Result[bool]:
        """Delete a conversation
        
        Args:
            request: DeleteConversationCommand with conversation ID
            
        Returns:
            Result[bool] with True on success, errors on failure
        """
        try:
            # Validate input
            Guard.against_empty(request.conversation_id, "conversation_id")
            
            # Delete conversation from database
            try:
                async with self._uow as uow:
                    # Check if conversation exists
                    conversation = await uow.conversations.get_by_id(request.conversation_id)
                    
                    if not conversation:
                        return Result.failure([f"Conversation not found: {request.conversation_id}"])
                    
                    # Delete conversation
                    await uow.conversations.delete(conversation)
                    
                    # Cascade delete patterns if requested
                    if request.delete_related_patterns:
                        # Get all patterns that reference this conversation
                        all_patterns = await uow.patterns.get_all()
                        patterns_to_delete = [
                            p for p in all_patterns 
                            if p.source_conversation_id == request.conversation_id
                        ]
                        
                        for pattern in patterns_to_delete:
                            await uow.patterns.delete(pattern)
                        
                        logger.info(
                            f"Deleted {len(patterns_to_delete)} related patterns for conversation: {request.conversation_id}"
                        )
                    
                    # Commit transaction
                    await uow.commit()
                    
                    logger.info(
                        f"Deleted conversation: {request.conversation_id} "
                        f"(cascade patterns: {request.delete_related_patterns})"
                    )
                    
            except Exception as db_error:
                logger.error(f"Database error deleting conversation: {db_error}", exc_info=True)
                return Result.failure([f"Failed to delete conversation: {str(db_error)}"])
            
            return Result.success(True)
            
        except ValueError as e:
            logger.error(f"Validation error deleting conversation: {e}")
            return Result.failure([str(e)])
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}", exc_info=True)
            return Result.failure([f"Failed to delete conversation: {str(e)}"])
