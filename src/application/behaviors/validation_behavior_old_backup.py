"""Validation Behavior - Input Validation Pipeline"""
from typing import Callable, Awaitable
import logging
from src.application.common.interfaces import IPipelineBehavior, IRequest
from src.application.common.result import Result
from src.application.validation import get_validator_registry

logger = logging.getLogger(__name__)


class ValidationBehavior(IPipelineBehavior):
    """Pipeline behavior for request validation
    
    This behavior runs BEFORE the handler to validate requests using
    the FluentValidation-style validator framework.
    
    Benefits:
    - Automatic validator discovery via registry
    - Consistent validation across all requests
    - Detailed error messages with property names
    - Early failure detection before handler execution
    - No need to manually wire validators to requests
    
    Usage:
        The behavior automatically finds validators registered in ValidatorRegistry.
        If no validator exists for a request type, validation is skipped.
    """
    
    def __init__(self):
        """Initialize validation behavior"""
        self._registry = get_validator_registry()
    
    async def handle(
        self,
        request: IRequest,
        next_handler: Callable[[IRequest], Awaitable[Result]]
    ) -> Result:
        """Validate request before processing
        
        Args:
            request: The request to validate
            next_handler: Next handler in pipeline
            
        Returns:
            Result from next handler or failure if validation fails
        """
        try:
            # Try to find validator for this request type
            validator = self._registry.get_validator(request)
            
            if validator is None:
                # No validator registered, skip validation
                logger.debug(
                    f"⏭️  No validator registered for {request.__class__.__name__}, "
                    "skipping validation"
                )
                return await next_handler(request)
            
            # Run validation
            validation_result = validator.validate(request)
            
            if not validation_result.is_valid:
                # Validation failed
                error_messages = [error.message for error in validation_result.errors]
                logger.warning(
                    f"❌ Validation failed for {request.__class__.__name__}: "
                    f"{', '.join(error_messages)}"
                )
                return Result.failure(error_messages)
            
            # Validation passed
            logger.debug(f"✅ Validation passed for {request.__class__.__name__}")
            return await next_handler(request)
            
        except Exception as e:
            logger.error(f"Validation behavior error: {e}", exc_info=True)
            return Result.failure([f"Validation check failed: {str(e)}"])
                validation_errors.extend(self._validate_learn_pattern(request))
            elif self._is_update_relevance_command(request):
                validation_errors.extend(self._validate_update_relevance(request))
            elif self._is_search_query(request):
                validation_errors.extend(self._validate_search_query(request))
            
            # If validation errors, return failure
            if validation_errors:
                logger.warning(
                    f"❌ Validation failed for {request.__class__.__name__}: "
                    f"{', '.join(validation_errors)}"
                )
                return Result.failure(validation_errors)
            
            # Validation passed, proceed
            logger.debug(f"✅ Validation passed for {request.__class__.__name__}")
            return await next_handler(request)
            
        except Exception as e:
            logger.error(f"Validation behavior error: {e}", exc_info=True)
            return Result.failure([f"Validation check failed: {str(e)}"])
    
    def _validate_common_fields(self, request: IRequest) -> list[str]:
        """Validate fields common to many requests"""
        errors = []
        
        # Validate IDs if present
        for id_field in ['conversation_id', 'pattern_id', 'context_id']:
            if hasattr(request, id_field):
                value = getattr(request, id_field)
                if not value or not isinstance(value, str) or not value.strip():
                    errors.append(f"{id_field} cannot be empty")
        
        # Validate scores if present
        for score_field in ['quality_score', 'confidence_score', 'relevance_score', 'new_relevance_score']:
            if hasattr(request, score_field):
                value = getattr(request, score_field)
                if value is not None:  # Allow None for optional scores
                    if not isinstance(value, (int, float)):
                        errors.append(f"{score_field} must be a number")
                    elif value < 0.0 or value > 1.0:
                        errors.append(f"{score_field} must be between 0.0 and 1.0")
        
        # Validate title if present
        if hasattr(request, 'title'):
            title = getattr(request, 'title')
            if not title or not title.strip():
                errors.append("title cannot be empty")
            elif len(title) > 500:
                errors.append("title cannot exceed 500 characters")
        
        # Validate content if present  
        if hasattr(request, 'content'):
            content = getattr(request, 'content')
            if not content or not content.strip():
                errors.append("content cannot be empty")
            elif len(content) < 10:
                errors.append("content must be at least 10 characters")
        
        # Validate search_text if present
        if hasattr(request, 'search_text'):
            search_text = getattr(request, 'search_text')
            if not search_text or not search_text.strip():
                errors.append("search_text cannot be empty")
            elif len(search_text) < 2:
                errors.append("search_text must be at least 2 characters")
            elif len(search_text) > 500:
                errors.append("search_text cannot exceed 500 characters")
        
        # Validate max_results if present
        if hasattr(request, 'max_results'):
            max_results = getattr(request, 'max_results')
            if max_results <= 0:
                errors.append("max_results must be positive")
            elif max_results > 100:
                errors.append("max_results cannot exceed 100")
        
        return errors
    
    def _validate_capture_conversation(self, request) -> list[str]:
        """Validate CaptureConversationCommand"""
        errors = []
        
        if not request.title or not request.title.strip():
            errors.append("title cannot be empty")
        elif len(request.title) > 500:
            errors.append("title cannot exceed 500 characters")
            
        if not request.content or not request.content.strip():
            errors.append("content cannot be empty")
        elif len(request.content) < 10:
            errors.append("content must be at least 10 characters")
            
        if hasattr(request, 'entity_count') and request.entity_count is not None:
            if request.entity_count < 0:
                errors.append("entity_count cannot be negative")
                
        return errors
    
    def _validate_learn_pattern(self, request) -> list[str]:
        """Validate LearnPatternCommand"""
        errors = []
        
        if not request.pattern_name or not request.pattern_name.strip():
            errors.append("pattern_name cannot be empty")
        elif len(request.pattern_name) > 200:
            errors.append("pattern_name cannot exceed 200 characters")
            
        if not request.pattern_content or not request.pattern_content.strip():
            errors.append("pattern_content cannot be empty")
            
        if not request.namespace or not request.namespace.strip():
            errors.append("namespace cannot be empty")
            
        # Validate pattern type if it's an enum
        if hasattr(request, 'pattern_type') and request.pattern_type:
            valid_types = [
                'code_structure', 'architecture', 'best_practice',
                'anti_pattern', 'optimization', 'bug_fix'
            ]
            if request.pattern_type not in valid_types:
                errors.append(
                    f"pattern_type must be one of: {', '.join(valid_types)}"
                )
        
        return errors
    
    def _validate_update_relevance(self, request) -> list[str]:
        """Validate UpdateContextRelevanceCommand"""
        errors = []
        
        if hasattr(request, 'new_relevance_score'):
            score = request.new_relevance_score
            if score < 0.0 or score > 1.0:
                errors.append("new_relevance_score must be between 0.0 and 1.0")
        
        if hasattr(request, 'reason') and request.reason:
            if len(request.reason) > 1000:
                errors.append("reason cannot exceed 1000 characters")
        
        return errors
    
    def _validate_search_query(self, request) -> list[str]:
        """Validate SearchContextQuery"""
        errors = []
        
        if hasattr(request, 'search_text'):
            if not request.search_text or not request.search_text.strip():
                errors.append("search_text cannot be empty")
            elif len(request.search_text) < 2:
                errors.append("search_text must be at least 2 characters")
            elif len(request.search_text) > 500:
                errors.append("search_text cannot exceed 500 characters")
        
        if hasattr(request, 'max_results'):
            if request.max_results <= 0:
                errors.append("max_results must be positive")
            elif request.max_results > 100:
                errors.append("max_results cannot exceed 100")
        
        return errors
    
    def _is_capture_conversation_command(self, request) -> bool:
        """Check if request is CaptureConversationCommand"""
        return request.__class__.__name__ == 'CaptureConversationCommand'
    
    def _is_learn_pattern_command(self, request) -> bool:
        """Check if request is LearnPatternCommand"""
        return request.__class__.__name__ == 'LearnPatternCommand'
    
    def _is_update_relevance_command(self, request) -> bool:
        """Check if request is UpdateContextRelevanceCommand"""
        return request.__class__.__name__ == 'UpdateContextRelevanceCommand'
    
    def _is_search_query(self, request) -> bool:
        """Check if request is SearchContextQuery"""
        return request.__class__.__name__ == 'SearchContextQuery'
