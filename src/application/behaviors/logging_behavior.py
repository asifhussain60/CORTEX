"""Logging Behavior - Request/Response Logging Pipeline"""
from typing import Callable, Awaitable
import logging
import json
from datetime import datetime
from src.application.common.interfaces import IPipelineBehavior, IRequest
from src.application.common.result import Result

logger = logging.getLogger(__name__)


class LoggingBehavior(IPipelineBehavior):
    """Pipeline behavior for request/response logging
    
    This behavior logs:
    - Request details (type, key parameters)
    - Response status (success/failure)
    - Error messages (if any)
    - Timestamps for audit trail
    
    Benefits:
    - Complete audit trail
    - Debug support
    - Security monitoring
    - Compliance requirements
    
    Note: Sensitive data is sanitized before logging
    """
    
    def __init__(self, log_request_data: bool = True, log_response_data: bool = False):
        """Initialize logging behavior
        
        Args:
            log_request_data: Whether to log request details
            log_response_data: Whether to log response data (may contain sensitive info)
        """
        self.log_request_data = log_request_data
        self.log_response_data = log_response_data
        self.sensitive_fields = {
            'password', 'token', 'secret', 'api_key',
            'private_key', 'credit_card', 'ssn'
        }
    
    async def handle(
        self,
        request: IRequest,
        next_handler: Callable[[IRequest], Awaitable[Result]]
    ) -> Result:
        """Log request and response
        
        Args:
            request: The request to log
            next_handler: Next handler in pipeline
            
        Returns:
            Result from next handler with logging performed
        """
        request_type = request.__class__.__name__
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Log request
            if self.log_request_data:
                self._log_request(request_type, request, timestamp)
            
            # Execute handler
            result = await next_handler(request)
            
            # Log response
            self._log_response(request_type, result, timestamp)
            
            return result
            
        except Exception as e:
            # Log exception
            logger.error(
                f"❌ [{timestamp}] Exception in {request_type}: {str(e)}",
                exc_info=True
            )
            raise
    
    def _log_request(self, request_type: str, request: IRequest, timestamp: str):
        """Log request details
        
        Args:
            request_type: Type of request
            request: The request object
            timestamp: Request timestamp
        """
        # Extract request data
        request_data = self._extract_request_data(request)
        
        # Sanitize sensitive data
        sanitized_data = self._sanitize_data(request_data)
        
        # Log request
        logger.info(
            f"📥 [{timestamp}] Request: {request_type} | "
            f"Data: {json.dumps(sanitized_data, default=str)}"
        )
    
    def _log_response(self, request_type: str, result: Result, timestamp: str):
        """Log response details
        
        Args:
            request_type: Type of request
            result: The result object
            timestamp: Request timestamp
        """
        if result.is_success:
            # Log success
            response_info = f"success"
            if self.log_response_data and result.value is not None:
                # Sanitize response data
                response_data = self._sanitize_data({'value': result.value})
                response_info = f"success | Data: {json.dumps(response_data, default=str)}"
            
            logger.info(
                f"📤 [{timestamp}] Response: {request_type} | {response_info}"
            )
        else:
            # Log failure
            errors = ', '.join(result.errors) if result.errors else 'Unknown error'
            logger.warning(
                f"📤 [{timestamp}] Response: {request_type} | "
                f"failure | Errors: {errors}"
            )
    
    def _extract_request_data(self, request: IRequest) -> dict:
        """Extract data from request object
        
        Args:
            request: The request object
            
        Returns:
            Dictionary with request data
        """
        data = {}
        
        # Extract common fields
        for field in ['conversation_id', 'pattern_id', 'context_id', 
                     'namespace', 'search_text', 'title', 'pattern_name']:
            if hasattr(request, field):
                data[field] = getattr(request, field)
        
        # Extract scores
        for field in ['quality_score', 'confidence_score', 'relevance_score']:
            if hasattr(request, field):
                value = getattr(request, field)
                if value is not None:
                    data[field] = value
        
        # Extract counts
        for field in ['max_results', 'entity_count']:
            if hasattr(request, field):
                data[field] = getattr(request, field)
        
        # Don't log large content fields by default
        if hasattr(request, 'content'):
            content = getattr(request, 'content', '')
            if content:
                data['content_length'] = len(content)
                data['content_preview'] = content[:100] + '...' if len(content) > 100 else content
        
        return data
    
    def _sanitize_data(self, data: dict) -> dict:
        """Sanitize sensitive data from dictionary
        
        Args:
            data: Dictionary potentially containing sensitive data
            
        Returns:
            Dictionary with sensitive data masked
        """
        sanitized = {}
        
        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                # Sanitize lists
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
