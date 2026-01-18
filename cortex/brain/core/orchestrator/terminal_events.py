"""
Terminal Events and Event Registry for orchestrator break conditions.

Terminal events represent explicit conditions that may halt orchestrator execution.
Each event maps to a ContinuationReason and can be fired to notify listeners.

Listeners can veto continuation by returning False.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Set
from abc import ABC, abstractmethod

from cortex.brain.core.orchestrator.continuation_decision import ContinuationReason


@dataclass
class TerminalEvent(ABC):
    """
    Base class for all terminal events.
    
    Terminal events represent explicit break conditions that may halt
    orchestrator execution.
    """
    
    turn_number: int
    timestamp: datetime = field(default_factory=datetime.now)

    @abstractmethod
    def get_continuation_reason(self) -> ContinuationReason:
        """Get the ContinuationReason that maps to this event."""
        pass


@dataclass
class PhaseCompletedEvent(TerminalEvent):
    """
    Event: Operation phase has completed successfully.
    
    Reason for continuation: Goal achieved, user may be satisfied
    """
    
    operation: str = ""
    result: str = ""
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to COMPLETION."""
        return ContinuationReason.COMPLETION


@dataclass
class UserCancelledEvent(TerminalEvent):
    """
    Event: User explicitly cancelled the operation.
    
    Reason for halt: User explicitly requested cancellation
    """
    
    reason: str = ""
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to USER_REJECTION."""
        return ContinuationReason.USER_REJECTION


@dataclass
class MaxTurnsReachedEvent(TerminalEvent):
    """
    Event: Safety limit on iterations has been reached.
    
    Reason for halt: Prevent infinite loops
    """
    
    max_turns: int = 0
    current_turn: int = 0
    reason: str = ""
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to MAX_ROUNDS_REACHED."""
        return ContinuationReason.MAX_ROUNDS_REACHED


@dataclass
class ErrorOccurredEvent(TerminalEvent):
    """
    Event: An unrecoverable error occurred during execution.
    
    Reason for halt: Cannot continue safely
    """
    
    error_message: str = ""
    error_type: str = ""
    recoverable: bool = False
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to ERROR_UNRECOVERABLE."""
        return ContinuationReason.ERROR_UNRECOVERABLE


@dataclass
class TokenLimitEvent(TerminalEvent):
    """
    Event: Token budget limit is approaching.
    
    Reason for halt: Preserve tokens for other operations
    """
    
    tokens_used: int = 0
    token_limit: int = 0
    percentage_used: float = 0.0
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to TOKEN_LIMIT."""
        return ContinuationReason.TOKEN_LIMIT


@dataclass
class GovernanceViolationEvent(TerminalEvent):
    """
    Event: A governance rule violation was detected.
    
    Reason for halt: Enforce governance compliance (CORE-017)
    """
    
    rule_id: str = ""
    violation_message: str = ""
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to GOVERNANCE_HALT."""
        return ContinuationReason.GOVERNANCE_HALT


@dataclass
class UserApprovalRejectedEvent(TerminalEvent):
    """
    Event: User rejected a result in approval gate.
    
    Reason for halt: Waiting for user approval
    """
    
    approval_request: str = ""
    rejection_reason: str = ""
    
    def get_continuation_reason(self) -> ContinuationReason:
        """Maps to INTERACTION_REQUIRED."""
        return ContinuationReason.INTERACTION_REQUIRED


# Type alias for event listeners
EventListener = Callable[[TerminalEvent], bool]
"""
EventListener: Callable that receives event and returns:
- True: continue processing
- False: halt processing (veto)
"""


class EventRegistry:
    """
    Registry for terminal event listeners.
    
    Listeners can be registered for specific event types.
    When an event is fired, all registered listeners are notified.
    Any listener returning False will veto continuation.
    
    Example:
        registry = EventRegistry()
        
        def on_completion(event: PhaseCompletedEvent) -> bool:
            print(f"Phase completed: {event.result}")
            return True  # Continue
        
        registry.register_listener(PhaseCompletedEvent, on_completion)
        
        event = PhaseCompletedEvent("planning", "done", turn_number=1)
        should_continue = registry.fire_event(event)
        
        if not should_continue:
            # Some listener vetoed continuation
            pass
    """
    
    def __init__(self):
        """Initialize empty listener registry."""
        self._listeners: Dict[type, List[EventListener]] = {}

    def register_listener(
        self, event_type: type, listener: EventListener
    ) -> None:
        """
        Register a listener for a specific event type.
        
        Args:
            event_type: Event class (e.g., PhaseCompletedEvent)
            listener: Callable that handles the event
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append(listener)

    def fire_event(self, event: TerminalEvent) -> bool:
        """
        Fire an event and notify all registered listeners.
        
        Calls all listeners registered for this event type.
        If ANY listener returns False, returns False (veto).
        If ALL listeners return True (or no listeners), returns True.
        
        Args:
            event: The event to fire
        
        Returns:
            True if all listeners allow continuation, False if any veto
        """
        event_type = type(event)
        
        # Get listeners for this event type
        if event_type not in self._listeners:
            # No listeners registered
            return True
        
        listeners = self._listeners[event_type]
        
        # Call all listeners
        for listener in listeners:
            try:
                should_continue = listener(event)
                
                # If any listener returns False, veto continuation
                if not should_continue:
                    return False
            except Exception as e:
                # Listener error - log but don't crash
                # In production, would log to audit trail
                pass
        
        # All listeners approved
        return True

    def register_listener_for_all_events(
        self, listener: EventListener
    ) -> None:
        """
        Register a listener for all event types.
        
        Useful for logging/monitoring listeners.
        
        Args:
            listener: Callable that handles any event
        """
        # Register for all known event types
        event_types = [
            PhaseCompletedEvent,
            UserCancelledEvent,
            MaxTurnsReachedEvent,
            ErrorOccurredEvent,
            TokenLimitEvent,
            GovernanceViolationEvent,
            UserApprovalRejectedEvent,
        ]
        
        for event_type in event_types:
            self.register_listener(event_type, listener)

    def clear_listeners(self, event_type: type = None) -> None:
        """
        Clear listeners.
        
        Args:
            event_type: Specific event type to clear, or None for all
        """
        if event_type is None:
            self._listeners.clear()
        else:
            if event_type in self._listeners:
                del self._listeners[event_type]

    def get_listener_count(self, event_type: type = None) -> int:
        """
        Get count of registered listeners.
        
        Args:
            event_type: Specific event type, or None for total
        
        Returns:
            Number of listeners
        """
        if event_type is None:
            total = 0
            for listeners in self._listeners.values():
                total += len(listeners)
            return total
        else:
            return len(self._listeners.get(event_type, []))
