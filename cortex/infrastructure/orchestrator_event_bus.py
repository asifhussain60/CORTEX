"""
Orchestrator Event Bus for event-driven orchestrator communication.

Purpose: Extends base EventBus with orchestrator-specific features
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 1
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Features:
- OrchestratorEvent publishing with typed events
- Event history persistence for audit trail
- Correlation ID tracking for event chains
- Async handler support
- Dead letter queue for failed handlers
- Event replay for recovery
"""

import asyncio
import inspect
import logging
from collections import deque
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional, Union
from uuid import uuid4

from cortex.core.event_bus import EventBus
from cortex.models.event_models import EventType, OrchestratorEvent

logger = logging.getLogger(__name__)


class OrchestratorEventBus(EventBus):
    """Event bus for orchestrator communication with advanced features.
    
    Extends the base EventBus with:
    - OrchestratorEvent support with EventType enums
    - Event history for audit trail and debugging
    - Correlation ID tracking to link related events
    - Async handler support for non-blocking processing
    - Dead letter queue for failed handler events
    - Event replay for recovery scenarios
    
    Attributes:
        max_history_size: Maximum events to keep in history
        _event_history: Deque storing recent events
        _dead_letter_queue: List of failed handler events
    
    Example:
        >>> bus = OrchestratorEventBus()
        >>> bus.subscribe(EventType.INTENT_CLASSIFIED, my_handler)
        >>> event = OrchestratorEvent(
        ...     event_type=EventType.INTENT_CLASSIFIED,
        ...     source_orchestrator="IntentRouter",
        ...     payload={"intent": "IMPLEMENT"}
        ... )
        >>> bus.publish_event(event)
    """
    
    def __init__(self, max_history_size: int = 1000) -> None:
        """Initialize OrchestratorEventBus.
        
        Args:
            max_history_size: Maximum number of events to retain in history.
                              Oldest events are removed when limit exceeded.
        """
        super().__init__()
        self.max_history_size = max_history_size
        self._event_history: Deque[OrchestratorEvent] = deque(maxlen=max_history_size)
        self._dead_letter_queue: List[Dict[str, Any]] = []
    
    def publish_event(self, event: OrchestratorEvent) -> None:
        """Publish an OrchestratorEvent to all subscribers.
        
        Stores event in history before notifying subscribers.
        Failed handlers are captured in dead letter queue.
        
        Args:
            event: The OrchestratorEvent to publish
        """
        # Store in history
        self._event_history.append(event)
        
        # Get handlers for this event type
        handlers = self.subscribers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # For async handlers in sync context, run in event loop
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(event))
                    except RuntimeError:
                        # No running loop, use asyncio.run
                        asyncio.run(handler(event))
                else:
                    handler(event)
            except Exception as e:
                # Capture in dead letter queue
                self._dead_letter_queue.append({
                    "event": event,
                    "handler": handler.__name__ if hasattr(handler, "__name__") else str(handler),
                    "error": f"{type(e).__name__}: {str(e)}",
                    "timestamp": datetime.now()
                })
                logger.warning(f"Handler {handler} failed for event {event.event_id}: {e}")
    
    async def publish_event_async(self, event: OrchestratorEvent) -> None:
        """Publish an OrchestratorEvent asynchronously.
        
        Properly awaits async handlers and runs sync handlers.
        
        Args:
            event: The OrchestratorEvent to publish
        """
        # Store in history
        self._event_history.append(event)
        
        # Get handlers for this event type
        handlers = self.subscribers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self._dead_letter_queue.append({
                    "event": event,
                    "handler": handler.__name__ if hasattr(handler, "__name__") else str(handler),
                    "error": f"{type(e).__name__}: {str(e)}",
                    "timestamp": datetime.now()
                })
                logger.warning(f"Handler {handler} failed for event {event.event_id}: {e}")
    
    def subscribe(
        self, 
        event_type: Union[EventType, str], 
        handler: Callable[[OrchestratorEvent], None]
    ) -> None:
        """Subscribe a handler to an event type.
        
        Supports both EventType enums and string event types (for backward
        compatibility with base EventBus).
        
        Args:
            event_type: EventType enum or string event name
            handler: Callable that receives the event
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(
        self, 
        event_type: Union[EventType, str], 
        handler: Callable
    ) -> None:
        """Unsubscribe a handler from an event type.
        
        Safe to call even if handler was never subscribed.
        
        Args:
            event_type: EventType enum or string event name
            handler: The handler to remove
        """
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(handler)
            except ValueError:
                pass  # Handler wasn't subscribed, that's OK
    
    def get_event_history(
        self, 
        since: Optional[datetime] = None
    ) -> List[OrchestratorEvent]:
        """Get event history, optionally filtered by timestamp.
        
        Args:
            since: Optional timestamp to filter events after
        
        Returns:
            List of OrchestratorEvent objects in chronological order
        """
        if since is None:
            return list(self._event_history)
        
        return [
            event for event in self._event_history 
            if event.timestamp >= since
        ]
    
    def get_event_chain(self, correlation_id: str) -> List[OrchestratorEvent]:
        """Get all events in a chain by correlation ID.
        
        Returns events in chronological order (by timestamp).
        
        Args:
            correlation_id: The correlation ID linking events
        
        Returns:
            List of events with matching correlation_id
        """
        chain = [
            event for event in self._event_history
            if event.correlation_id == correlation_id
        ]
        # Sort by timestamp to ensure chronological order
        return sorted(chain, key=lambda e: e.timestamp)
    
    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for linking events.
        
        Returns:
            A unique string ID (UUID4 format)
        """
        return str(uuid4())
    
    def get_dead_letter_queue(self) -> List[Dict[str, Any]]:
        """Get events that failed handler processing.
        
        Returns:
            List of dicts with event, handler, error, timestamp
        """
        return self._dead_letter_queue.copy()
    
    def clear_dead_letter_queue(self) -> int:
        """Clear the dead letter queue.
        
        Returns:
            Number of items cleared
        """
        count = len(self._dead_letter_queue)
        self._dead_letter_queue.clear()
        return count
    
    def replay_events(
        self, 
        from_event_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> int:
        """Replay events from history to current subscribers.
        
        Useful for recovery scenarios or catching up new subscribers.
        
        Args:
            from_event_id: Start replay from this event (inclusive)
            correlation_id: Only replay events with this correlation_id
        
        Returns:
            Number of events replayed
        """
        events_to_replay = []
        found_start = from_event_id is None
        
        for event in self._event_history:
            if not found_start:
                if event.event_id == from_event_id:
                    found_start = True
                else:
                    continue
            
            if correlation_id is not None and event.correlation_id != correlation_id:
                continue
            
            events_to_replay.append(event)
        
        # Replay without storing again in history
        for event in events_to_replay:
            handlers = self.subscribers.get(event.event_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.run(handler(event))
                    else:
                        handler(event)
                except Exception as e:
                    logger.warning(f"Replay handler failed: {e}")
        
        return len(events_to_replay)


# Singleton instance for global access
_global_event_bus: Optional[OrchestratorEventBus] = None


def get_orchestrator_event_bus() -> OrchestratorEventBus:
    """Get the global OrchestratorEventBus instance.
    
    Creates a new instance if one doesn't exist.
    
    Returns:
        The global OrchestratorEventBus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = OrchestratorEventBus()
    return _global_event_bus


def reset_orchestrator_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _global_event_bus
    _global_event_bus = None
