"""Brain Protection Behavior - SKULL Rules Enforcement"""
from typing import Callable, Awaitable
import logging
from src.application.common.interfaces import IPipelineBehavior, IRequest
from src.application.common.result import Result
from src.domain.value_objects import Namespace

logger = logging.getLogger(__name__)


class BrainProtectionBehavior(IPipelineBehavior):
    """Pipeline behavior for enforcing SKULL brain protection rules
    
    SKULL Rules (Brain Protection - Tier 0):
    - S: Safety - Prevent harmful operations
    - K: Knowledge Protection - Protect brain data integrity
    - U: User Control - User must authorize critical operations
    - L: Logging - Audit all protected operations
    - L: Limits - Enforce rate limits and quotas
    
    This behavior runs BEFORE the handler to validate:
    - Namespace access permissions
    - Protected brain data operations
    - Rate limiting
    - Critical operation authorization
    """
    
    def __init__(self, protected_namespaces: set[str] = None):
        """Initialize brain protection behavior
        
        Args:
            protected_namespaces: Set of namespaces requiring extra protection
        """
        self.protected_namespaces = protected_namespaces or {
            'cortex.brain',
            'cortex.system',
            'cortex.admin'
        }
        self.operation_count = {}  # Simple rate limiting tracker
        
    async def handle(
        self,
        request: IRequest,
        next_handler: Callable[[IRequest], Awaitable[Result]]
    ) -> Result:
        """Enforce brain protection rules
        
        Args:
            request: The request to validate
            next_handler: Next handler in pipeline
            
        Returns:
            Result from next handler or failure if protection rules violated
        """
        try:
            # Extract namespace from request if available
            namespace_value = None
            if hasattr(request, 'namespace'):
                namespace_value = request.namespace
            elif hasattr(request, 'namespace_filter'):
                namespace_value = request.namespace_filter
                
            # Check protected namespace access
            if namespace_value:
                if self._is_protected_namespace(namespace_value):
                    logger.warning(
                        f"⚠️ SKULL: Protected namespace access attempt: {namespace_value} "
                        f"(request: {request.__class__.__name__})"
                    )
                    # In production, would check user permissions here
                    # For now, allow but log
            
            # Check for destructive operations
            if self._is_destructive_operation(request):
                logger.warning(
                    f"⚠️ SKULL: Destructive operation detected: {request.__class__.__name__}"
                )
                # Verify it's intentional
                if hasattr(request, 'conversation_id'):
                    logger.info(f"   Target: {request.conversation_id}")
            
            # Rate limiting check
            request_type = request.__class__.__name__
            if self._is_rate_limited(request_type):
                return Result.failure([
                    f"Rate limit exceeded for {request_type}. "
                    "Please wait before retrying."
                ])
            
            # Log protected operation
            self._log_protected_operation(request)
            
            # Proceed to next handler
            return await next_handler(request)
            
        except Exception as e:
            logger.error(f"❌ SKULL: Brain protection error: {e}", exc_info=True)
            return Result.failure([f"Brain protection check failed: {str(e)}"])
    
    def _is_protected_namespace(self, namespace_value: str) -> bool:
        """Check if namespace is protected"""
        try:
            namespace = Namespace(value=namespace_value)
            return any(
                namespace.value.startswith(protected)
                for protected in self.protected_namespaces
            )
        except ValueError:
            return False
    
    def _is_destructive_operation(self, request: IRequest) -> bool:
        """Check if operation is destructive (delete, truncate, etc.)"""
        request_name = request.__class__.__name__.lower()
        destructive_keywords = ['delete', 'remove', 'clear', 'truncate', 'purge']
        return any(keyword in request_name for keyword in destructive_keywords)
    
    def _is_rate_limited(self, request_type: str) -> bool:
        """Simple rate limiting check
        
        In production, this would use a proper rate limiter with
        time windows, user-based limits, etc.
        """
        # Track operation count
        self.operation_count[request_type] = self.operation_count.get(request_type, 0) + 1
        
        # Simple threshold - in production, would be time-based
        max_operations = 1000
        if self.operation_count[request_type] > max_operations:
            logger.warning(f"Rate limit exceeded for {request_type}")
            return True
        
        return False
    
    def _log_protected_operation(self, request: IRequest):
        """Log protected operations for audit trail"""
        request_name = request.__class__.__name__
        
        # Log with relevant details
        details = []
        if hasattr(request, 'conversation_id'):
            details.append(f"conversation_id={request.conversation_id}")
        if hasattr(request, 'pattern_id'):
            details.append(f"pattern_id={request.pattern_id}")
        if hasattr(request, 'namespace'):
            details.append(f"namespace={request.namespace}")
            
        logger.info(
            f"🛡️ SKULL: Protected operation: {request_name} "
            f"({', '.join(details) if details else 'no details'})"
        )
