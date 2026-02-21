"""Event bus for feature registry notifications and orchestrator communication."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
import uuid


@dataclass
class Event:
    """
    Event data structure for EventBus communication with debugging support.
    
    Attributes:
        type: Event type identifier (e.g., 'feature.enabled', 'test.failed')
        payload: Event data dictionary
        correlation_id: Request correlation ID for distributed tracing
        event_id: Unique event identifier for deduplication
        source: Originating component (e.g., 'TDDOrchestrator', 'EnforcementAgent')
        priority: Event priority (0=critical, 1=high, 2=normal, 3=low)
        timestamp: Event creation timestamp
    """
    type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: Optional[str] = None
    priority: int = 2  # 0=critical, 1=high, 2=normal, 3=low
    timestamp: datetime = field(default_factory=datetime.now)


class EventBus:
    """Publish/subscribe event bus for feature changes with audit trail logging."""

    def __init__(self, log_file: Optional[str] = None) -> None:
        """
        Initialize event bus with optional event logging.
        
        Args:
            log_file: Optional path to JSONL file for event audit trail.
                      If provided, all events will be logged for audit purposes.
        """
        self.subscribers = {}
        self.log_file = log_file
        self.logging_enabled = log_file is not None
        
        if self.logging_enabled:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

    def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: object, data: object = None) -> None:
        """
        Publish event to subscribers with audit trail logging.
        
        Args:
            event: Event object or event_type string (for backward compatibility)
            data: Event data (for backward compatibility with legacy format)
        """
        # Support both Event objects and legacy (event_type, data) format
        if isinstance(event, Event):
            event_type = event.type
            payload = event.payload
        else:
            # Legacy format: publish(event_type, data)
            event_type = event
            payload = data or {}
        
        # Log event for audit trail
        if self.logging_enabled:
            self._log_event(event_type, payload)
        
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                # Pass Event object to new handlers, data to legacy handlers
                try:
                    if isinstance(event, Event):
                        handler(event)
                    else:
                        handler(payload)
                except TypeError:
                    # Handler expects data, not Event
                    handler(payload)
                except Exception as e:
                    # Don't let handler errors break event delivery
                    print(f"Warning: Event handler error for {event_type}: {e}")
    
    def _log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Log event to audit trail file.
        
        Args:
            event_type: Type of event
            payload: Event payload data
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": event_type,
                "payload": payload
            }
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            # Don't let logging errors break event delivery
            print(f"Warning: Event logging error: {e}")

    def feature_enabled(self, feature_id: str) -> None:
        """Publish feature enabled event."""
        self.publish("feature_enabled", {"feature_id": feature_id})

    def feature_disabled(self, feature_id: str) -> None:
        """Publish feature disabled event."""
        self.publish("feature_disabled", {"feature_id": feature_id})