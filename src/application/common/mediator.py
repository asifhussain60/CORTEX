"""Mediator pattern implementation for CQRS"""
from typing import TypeVar, Dict, Type, List, Any, Callable
from src.application.common.interfaces import (
    IRequest, IRequestHandler, IPipelineBehavior
)
from src.application.common.result import Result
import logging

logger = logging.getLogger(__name__)

TRequest = TypeVar('TRequest', bound=IRequest)
TResponse = TypeVar('TResponse')


class Mediator:
    """Mediator for routing requests to handlers
    
    The Mediator pattern decouples request senders from handlers,
    providing a central point for request routing and pipeline execution.
    
    Features:
    - Request routing to appropriate handlers
    - Pipeline behavior execution (middleware)
    - Type-safe handler registration
    - Async support for I/O operations
    
    Example:
        mediator = Mediator()
        
        # Register handler
        mediator.register_handler(
            CaptureConversationCommand,
            CaptureConversationHandler()
        )
        
        # Register behavior
        mediator.register_behavior(ValidationBehavior())
        
        # Send request
        result = await mediator.send(
            CaptureConversationCommand(
                conversation_id="conv-123",
                title="Test"
            )
        )
    """
    
    def __init__(self):
        self._handlers: Dict[Type[IRequest], IRequestHandler] = {}
        self._behaviors: List[IPipelineBehavior] = []
    
    def register_handler(
        self,
        request_type: Type[TRequest],
        handler: IRequestHandler[TRequest, TResponse]
    ) -> None:
        """Register a request handler
        
        Args:
            request_type: The type of request this handler processes
            handler: The handler instance
        """
        if request_type in self._handlers:
            logger.warning(f"Overwriting existing handler for {request_type.__name__}")
        
        self._handlers[request_type] = handler
        logger.debug(f"Registered handler for {request_type.__name__}")
    
    def register_behavior(self, behavior: IPipelineBehavior) -> None:
        """Register a pipeline behavior
        
        Behaviors execute in registration order.
        
        Args:
            behavior: The pipeline behavior instance
        """
        self._behaviors.append(behavior)
        logger.debug(f"Registered behavior: {behavior.__class__.__name__}")
    
    def clear_handlers(self) -> None:
        """Clear all registered handlers (mainly for testing)"""
        self._handlers.clear()
        logger.debug("Cleared all handlers")
    
    def clear_behaviors(self) -> None:
        """Clear all registered behaviors (mainly for testing)"""
        self._behaviors.clear()
        logger.debug("Cleared all behaviors")
    
    async def send(self, request: TRequest) -> TResponse:
        """Send a request through the pipeline
        
        Execution order:
        1. Pipeline behaviors (in registration order)
        2. Request handler
        
        Args:
            request: The request to send (command or query)
            
        Returns:
            Response from handler (wrapped in Result for error handling)
            
        Raises:
            ValueError: If no handler registered for request type
        """
        request_type = type(request)
        
        # Get handler
        if request_type not in self._handlers:
            error_msg = f"No handler registered for {request_type.__name__}"
            logger.error(error_msg)
            # Return failure result instead of raising
            return Result.failure([error_msg])
        
        handler = self._handlers[request_type]
        
        # Build pipeline
        pipeline = self._build_pipeline(request, handler)
        
        # Execute pipeline
        logger.debug(f"Sending {request_type.__name__} through pipeline")
        return await pipeline()
    
    def _build_pipeline(
        self,
        request: TRequest,
        handler: IRequestHandler[TRequest, TResponse]
    ) -> Callable:
        """Build the execution pipeline
        
        Pipeline structure:
        Behavior1 -> Behavior2 -> ... -> BehaviorN -> Handler
        
        Each behavior can:
        - Execute logic before handler
        - Call next behavior/handler
        - Execute logic after handler
        - Short-circuit by not calling next
        
        Args:
            request: The request being processed
            handler: The final handler
            
        Returns:
            Callable that executes the full pipeline
        """
        # Start with the handler
        async def handler_executor(req: IRequest):
            return await handler.handle(req)
        
        # Wrap with behaviors (in reverse order so they execute in registration order)
        pipeline = handler_executor
        for behavior in reversed(self._behaviors):
            # Capture behavior and current pipeline in closure
            current_behavior = behavior
            current_pipeline = pipeline
            
            async def behavior_executor(
                req: IRequest,
                b=current_behavior,
                next_handler=current_pipeline
            ):
                # next_handler already accepts IRequest parameter
                return await b.handle(req, next_handler)
            
            pipeline = behavior_executor
        
        # Return final wrapper that invokes pipeline with request
        async def execute():
            return await pipeline(request)
        
        return execute
    
    def get_handler_count(self) -> int:
        """Get number of registered handlers"""
        return len(self._handlers)
    
    def get_behavior_count(self) -> int:
        """Get number of registered behaviors"""
        return len(self._behaviors)


# Global singleton mediator instance
_global_mediator: Mediator = None


def get_mediator() -> Mediator:
    """Get the global mediator instance
    
    Returns:
        Global Mediator instance
    """
    global _global_mediator
    if _global_mediator is None:
        _global_mediator = Mediator()
    return _global_mediator


def reset_mediator() -> None:
    """Reset the global mediator (mainly for testing)"""
    global _global_mediator
    _global_mediator = None
