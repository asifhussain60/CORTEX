"""Base entity with domain event support"""
from abc import ABC
from typing import List
from dataclasses import dataclass


@dataclass
class BaseEvent:
    """Base class for all domain events"""
    pass


class BaseEntity(ABC):
    """Base entity with domain event support
    
    Example:
        class Conversation(BaseEntity):
            def capture(self):
                self.add_domain_event(ConversationCapturedEvent(self.id))
    """
    
    def __init__(self):
        self._domain_events: List[BaseEvent] = []
    
    @property
    def domain_events(self) -> List[BaseEvent]:
        """Get copy of domain events"""
        return self._domain_events.copy()
    
    def add_domain_event(self, event: BaseEvent) -> None:
        """Add a domain event to be dispatched"""
        self._domain_events.append(event)
    
    def remove_domain_event(self, event: BaseEvent) -> None:
        """Remove a specific domain event"""
        self._domain_events.remove(event)
    
    def clear_domain_events(self) -> None:
        """Clear all domain events"""
        self._domain_events.clear()
