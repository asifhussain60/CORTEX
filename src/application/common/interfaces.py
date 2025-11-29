"""CQRS interfaces for commands and queries"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
from dataclasses import dataclass


# Base marker interface for all requests (commands and queries)
class IRequest(ABC):
    """Base interface for all CQRS requests (commands and queries)"""
    pass


# Command marker interface (write operations that may have side effects)
class ICommand(IRequest):
    """Marker interface for commands (write operations)
    
    Commands:
    - Perform write operations (create, update, delete)
    - May have side effects
    - Should not return domain data (only success/failure)
    - Follow imperative naming (CaptureConversation, LearnPattern)
    
    Example:
        @dataclass
        class CaptureConversationCommand(ICommand):
            conversation_id: str
            title: str
            content: str
    """
    pass


# Query interface (read operations that return data)
TResult = TypeVar('TResult')


class IQuery(IRequest, Generic[TResult]):
    """Base interface for queries (read operations)
    
    Queries:
    - Perform read operations only
    - Have no side effects
    - Return domain data
    - Follow interrogative naming (SearchContext, GetConversationQuality)
    
    Example:
        @dataclass
        class SearchContextQuery(IQuery[List[Conversation]]):
            search_text: str
            max_results: int = 10
    """
    pass


# Request handler interface
TRequest = TypeVar('TRequest', bound=IRequest)
TResponse = TypeVar('TResponse')


class IRequestHandler(ABC, Generic[TRequest, TResponse]):
    """Interface for request handlers
    
    Handlers:
    - Process a single request type (command or query)
    - Contain business logic
    - Return Result[TResponse] for explicit success/failure
    
    Example:
        class CaptureConversationHandler(IRequestHandler[CaptureConversationCommand, str]):
            async def handle(self, request: CaptureConversationCommand) -> Result[str]:
                # Process command
                return Result.success(conversation_id)
    """
    
    @abstractmethod
    async def handle(self, request: TRequest) -> TResponse:
        """Handle the request
        
        Args:
            request: The request to handle (command or query)
            
        Returns:
            Response (wrapped in Result for explicit error handling)
        """
        pass


# Pipeline behavior interface (middleware for requests)
class IPipelineBehavior(ABC, Generic[TRequest, TResponse]):
    """Interface for pipeline behaviors (middleware)
    
    Behaviors:
    - Execute before/after handlers
    - Cross-cutting concerns (validation, logging, performance)
    - Can short-circuit the pipeline
    - Execute in registration order
    
    Example:
        class ValidationBehavior(IPipelineBehavior[IRequest, Any]):
            async def handle(self, request, next_handler):
                # Validate request
                if not is_valid(request):
                    return Result.failure("Validation failed")
                return await next_handler()
    """
    
    @abstractmethod
    async def handle(
        self,
        request: TRequest,
        next_handler: Any  # Callable returning TResponse
    ) -> TResponse:
        """Execute behavior
        
        Args:
            request: The request being processed
            next_handler: The next handler in the pipeline (may be another behavior or the actual handler)
            
        Returns:
            Response (may short-circuit by not calling next_handler)
        """
        pass
