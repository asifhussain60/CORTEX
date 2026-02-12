"""Event bus for feature registry notifications."""

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

    def publish(self, event_type, data):
        """Publish event to subscribers."""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(data)

    def feature_enabled(self, feature_id):
        """Publish feature enabled event."""
        self.publish("feature_enabled", {"feature_id": feature_id})

    def feature_disabled(self, feature_id):
        """Publish feature disabled event."""
        self.publish("feature_disabled", {"feature_id": feature_id})
