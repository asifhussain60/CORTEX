"""Event bus for feature registry notifications and orchestrator communication."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Event:
    """Event data structure for EventBus communication."""
    type: str
    payload: Dict[str, Any]


class EventBus:
    """Publish/subscribe event bus for feature changes."""

    def __init__(self):
        """Initialize event bus."""
        self.subscribers = {}

    def subscribe(self, event_type, handler):
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event):
        """
        Publish event to subscribers.
        
        Args:
            event: Event object or event_type string (for backward compatibility)
        """
        # Support both Event objects and legacy (event_type, data) format
        if isinstance(event, Event):
            event_type = event.type
            data = event.payload
        else:
            # Legacy format: publish(event_type, data)
            event_type = event
            data = {}
        
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                # Pass Event object to new handlers, data to legacy handlers
                try:
                    if isinstance(event, Event):
                        handler(event)
                    else:
                        handler(data)
                except TypeError:
                    # Handler expects data, not Event
                    handler(data)

    def feature_enabled(self, feature_id):
        """Publish feature enabled event."""
        self.publish("feature_enabled", {"feature_id": feature_id})

    def feature_disabled(self, feature_id):
        """Publish feature disabled event."""
        self.publish("feature_disabled", {"feature_id": feature_id})
