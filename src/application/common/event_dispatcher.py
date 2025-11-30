"""Event dispatcher for domain events"""
from typing import Dict, List, Callable, Type, Any
from src.domain.common.base_entity import BaseEvent, BaseEntity
import logging

logger = logging.getLogger(__name__)


class EventDispatcher:
    """Dispatches domain events to registered handlers
    
    The dispatcher maintains a registry of event handlers and routes
    events to the appropriate handlers when entities are saved.
    
    Example:
        dispatcher = EventDispatcher()
        
        # Register handler
        def handle_conversation_captured(event: ConversationCapturedEvent):
            print(f"Conversation captured: {event.title}")
        
        dispatcher.register(ConversationCapturedEvent, handle_conversation_captured)
        
        # Dispatch events from entity
        conversation = Conversation("Test")
        conversation.capture()
        dispatcher.dispatch(conversation)  # Handler called
    """
    
    def __init__(self):
        self._handlers: Dict[Type[BaseEvent], List[Callable]] = {}
        self._global_handlers: List[Callable] = []
    
    def register(self, event_type: Type[BaseEvent], handler: Callable[[BaseEvent], Any]) -> None:
        """Register an event handler for a specific event type
        
        Args:
            event_type: The type of event to handle
            handler: Callable that takes the event as parameter
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type.__name__}")
    
    def register_global(self, handler: Callable[[BaseEvent], Any]) -> None:
        """Register a global handler that receives all events
        
        Useful for logging, metrics, or audit trails.
        
        Args:
            handler: Callable that takes any event as parameter
        """
        self._global_handlers.append(handler)
        logger.debug("Registered global event handler")
    
    def unregister(self, event_type: Type[BaseEvent], handler: Callable) -> None:
        """Unregister a specific event handler
        
        Args:
            event_type: The type of event
            handler: The handler to remove
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for {event_type.__name__}")
            except ValueError:
                pass  # Handler not in list
    
    def dispatch(self, entity: BaseEntity) -> None:
        """Dispatch all events from an entity
        
        Calls all registered handlers for each event, then clears
        the entity's events.
        
        Args:
            entity: Entity with domain events to dispatch
        """
        events = entity.domain_events
        
        if not events:
            return
        
        # Clear events first to prevent infinite loops
        entity.clear_domain_events()
        
        # Dispatch each event
        for event in events:
            self._dispatch_event(event)
    
    def _dispatch_event(self, event: BaseEvent) -> None:
        """Dispatch a single event to all registered handlers
        
        Args:
            event: The event to dispatch
        """
        event_type = type(event)
        
        # Call specific handlers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(
                        f"Error in handler for {event_type.__name__}: {e}",
                        exc_info=True
                    )
        
        # Call global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Error in global handler for {event_type.__name__}: {e}",
                    exc_info=True
                )
        
        logger.debug(f"Dispatched {event_type.__name__}")
    
    def clear_handlers(self) -> None:
        """Clear all registered handlers"""
        self._handlers.clear()
        self._global_handlers.clear()
        logger.debug("Cleared all event handlers")
    
    def get_handler_count(self, event_type: Type[BaseEvent] = None) -> int:
        """Get count of registered handlers
        
        Args:
            event_type: Optional event type to count handlers for.
                       If None, returns total handler count.
        
        Returns:
            Number of registered handlers
        """
        if event_type is None:
            # Count all handlers
            specific_count = sum(len(handlers) for handlers in self._handlers.values())
            return specific_count + len(self._global_handlers)
        
        return len(self._handlers.get(event_type, []))


# Global singleton dispatcher instance
_global_dispatcher: EventDispatcher = None


def get_event_dispatcher() -> EventDispatcher:
    """Get the global event dispatcher instance
    
    Returns:
        Global EventDispatcher instance
    """
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = EventDispatcher()
    return _global_dispatcher


def reset_event_dispatcher() -> None:
    """Reset the global event dispatcher (mainly for testing)"""
    global _global_dispatcher
    _global_dispatcher = None
