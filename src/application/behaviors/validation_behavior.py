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
                error_messages = [error.error_message for error in validation_result.errors]
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
