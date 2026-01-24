"""
BRT-023: Event Streaming Pattern

Implements async event-driven operations and event propagation throughout
the resilience framework.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any, Callable, Set
from threading import Lock, Event, Condition
from queue import Queue
import time
import uuid


class EventType(Enum):
    """Types of events in resilience framework."""
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    CIRCUIT_BREAKER_CLOSED = "circuit_breaker_closed"
    RETRY_ATTEMPTED = "retry_attempted"
    TIMEOUT_OCCURRED = "timeout_occurred"
    DEGRADATION_STARTED = "degradation_started"
    DEGRADATION_ENDED = "degradation_ended"
    HEALTH_CHECK_FAILED = "health_check_failed"
    BULKHEAD_EXHAUSTED = "bulkhead_exhausted"
    RECOVERY_INITIATED = "recovery_initiated"


@dataclass
class Event:
    """Event in the resilience stream."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.RATE_LIMIT_EXCEEDED
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)
    source: str = ""  # Service/component that generated event
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical
    correlation_id: Optional[str] = None  # Trace correlation
    
    def get_id(self) -> str:
        """Get event ID."""
        return self.event_id
    
    def get_type(self) -> EventType:
        """Get event type."""
        return self.event_type
    
    def get_data(self) -> Dict[str, Any]:
        """Get event data."""
        return self.data
    
    def age_ms(self) -> float:
        """Get age of event in milliseconds."""
        return time.time() * 1000 - self.timestamp_ms


class EventFilter:
    """Filters events by type, source, severity."""
    
    def __init__(
        self,
        event_types: Optional[Set[EventType]] = None,
        sources: Optional[Set[str]] = None,
        min_severity: str = "info"
    ):
        self.event_types = event_types
        self.sources = sources
        self.min_severity = min_severity
        self._severity_order = {"info": 0, "warning": 1, "error": 2, "critical": 3}
    
    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria."""
        # Check type
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check source
        if self.sources and event.source not in self.sources:
            return False
        
        # Check severity
        if self._severity_order.get(event.severity, 0) < \
           self._severity_order.get(self.min_severity, 0):
            return False
        
        return True


class EventHandler:
    """Base class for event handlers."""
    
    def __init__(self, name: str):
        self.name = name
        self._enabled = True
    
    def handle(self, event: Event) -> bool:
        """Handle an event. Return True if processed."""
        raise NotImplementedError()
    
    def enable(self):
        """Enable handler."""
        self._enabled = True
    
    def disable(self):
        """Disable handler."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if handler is enabled."""
        return self._enabled


class CallbackEventHandler(EventHandler):
    """Event handler with callback function."""
    
    def __init__(self, name: str, callback: Callable[[Event], None]):
        super().__init__(name)
        self.callback = callback
    
    def handle(self, event: Event) -> bool:
        """Call the callback with the event."""
        if self._enabled:
            self.callback(event)
            return True
        return False


class LoggingEventHandler(EventHandler):
    """Event handler that logs events."""
    
    def __init__(self, name: str = "logger"):
        super().__init__(name)
        self.events: List[Event] = []
    
    def handle(self, event: Event) -> bool:
        """Log the event."""
        if self._enabled:
            self.events.append(event)
            return True
        return False
    
    def get_events(self) -> List[Event]:
        """Get logged events."""
        return list(self.events)
    
    def clear(self):
        """Clear logged events."""
        self.events.clear()


class EventStream:
    """Main event stream for resilience framework."""
    
    def __init__(self, max_buffer_size: int = 10000):
        self._queue: Queue[Event] = Queue(maxsize=max_buffer_size)
        self._handlers: Dict[str, EventHandler] = {}
        self._filters: List[EventFilter] = []
        self._lock = Lock()
        self._event_count = 0
        self._condition = Condition(self._lock)
    
    def publish(self, event: Event) -> bool:
        """Publish event to stream."""
        with self._lock:
            # Check if event matches any filter
            if self._filters:
                if not any(f.matches(event) for f in self._filters):
                    return False
            
            try:
                self._queue.put_nowait(event)
                self._event_count += 1
                self._condition.notify_all()
                return True
            except Exception:
                return False
    
    def subscribe(self, handler: EventHandler, event_filter: Optional[EventFilter] = None):
        """Subscribe handler to events."""
        with self._lock:
            self._handlers[handler.name] = handler
            if event_filter:
                self._filters.append(event_filter)
    
    def unsubscribe(self, handler_name: str) -> bool:
        """Unsubscribe handler."""
        with self._lock:
            if handler_name in self._handlers:
                del self._handlers[handler_name]
                return True
            return False
    
    def get_pending_events(self) -> List[Event]:
        """Get all pending events."""
        events = []
        with self._lock:
            while not self._queue.empty():
                try:
                    events.append(self._queue.get_nowait())
                except Exception:
                    break
        return events
    
    def process_events(self) -> int:
        """Process all pending events through handlers."""
        processed = 0
        events = self.get_pending_events()
        
        for event in events:
            for handler in self._handlers.values():
                if handler.handle(event):
                    processed += 1
        
        return processed
    
    def get_event_count(self) -> int:
        """Get total number of events published."""
        with self._lock:
            return self._event_count
    
    def wait_for_events(self, timeout_ms: int = 1000) -> int:
        """Wait for events to arrive."""
        with self._condition:
            self._condition.wait(timeout=timeout_ms / 1000.0)
            return self._queue.qsize()


class EventCorrelation:
    """Correlates events by trace/request ID."""
    
    def __init__(self):
        self._correlations: Dict[str, List[Event]] = {}
        self._lock = Lock()
    
    def add_event(self, correlation_id: str, event: Event):
        """Add event to correlation group."""
        with self._lock:
            if correlation_id not in self._correlations:
                self._correlations[correlation_id] = []
            self._correlations[correlation_id].append(event)
    
    def get_events_for_correlation(self, correlation_id: str) -> List[Event]:
        """Get all events for a correlation ID."""
        with self._lock:
            return list(self._correlations.get(correlation_id, []))
    
    def get_correlation_path(self, correlation_id: str) -> List[tuple]:
        """Get event path (sequence of type, source, timestamp)."""
        events = self.get_events_for_correlation(correlation_id)
        return [(e.event_type, e.source, e.timestamp_ms) for e in events]


class EventMetrics:
    """Tracks metrics on event streams."""
    
    def __init__(self):
        self._counts: Dict[EventType, int] = {}
        self._sources: Dict[str, int] = {}
        self._lock = Lock()
    
    def track_event(self, event: Event):
        """Track an event."""
        with self._lock:
            self._counts[event.event_type] = self._counts.get(event.event_type, 0) + 1
            self._sources[event.source] = self._sources.get(event.source, 0) + 1
    
    def get_count_by_type(self, event_type: EventType) -> int:
        """Get count of events by type."""
        with self._lock:
            return self._counts.get(event_type, 0)
    
    def get_count_by_source(self, source: str) -> int:
        """Get count of events by source."""
        with self._lock:
            return self._sources.get(source, 0)
    
    def get_all_counts(self) -> Dict[EventType, int]:
        """Get all event counts."""
        with self._lock:
            return dict(self._counts)


# ============================================================================
# TEST SUITE
# ============================================================================

class TestEventCreation:
    """Test Event creation and properties."""
    
    def test_create_event(self):
        """Test basic event creation."""
        event = Event(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            source="api-gateway",
            severity="warning"
        )
        assert event.event_type == EventType.RATE_LIMIT_EXCEEDED
        assert event.source == "api-gateway"
        assert event.severity == "warning"
    
    def test_event_with_data(self):
        """Test event with custom data."""
        data = {"requests_per_second": 1000, "limit": 500}
        event = Event(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            source="rate-limiter",
            data=data
        )
        assert event.get_data() == data
    
    def test_event_age(self):
        """Test event age calculation."""
        event = Event()
        time.sleep(0.01)
        age = event.age_ms()
        assert age > 0
        assert age < 100


class TestEventFilter:
    """Test EventFilter functionality."""
    
    def test_filter_by_type(self):
        """Test filtering by event type."""
        filter_ = EventFilter(
            event_types={EventType.RATE_LIMIT_EXCEEDED, EventType.CIRCUIT_BREAKER_OPEN}
        )
        
        matching_event = Event(event_type=EventType.RATE_LIMIT_EXCEEDED)
        non_matching = Event(event_type=EventType.RETRY_ATTEMPTED)
        
        assert filter_.matches(matching_event)
        assert not filter_.matches(non_matching)
    
    def test_filter_by_source(self):
        """Test filtering by source."""
        filter_ = EventFilter(sources={"api-gateway", "rate-limiter"})
        
        matching = Event(source="api-gateway")
        non_matching = Event(source="background-worker")
        
        assert filter_.matches(matching)
        assert not filter_.matches(non_matching)
    
    def test_filter_by_severity(self):
        """Test filtering by severity level."""
        filter_ = EventFilter(min_severity="warning")
        
        info_event = Event(severity="info")
        warning_event = Event(severity="warning")
        error_event = Event(severity="error")
        
        assert not filter_.matches(info_event)
        assert filter_.matches(warning_event)
        assert filter_.matches(error_event)
    
    def test_filter_combined(self):
        """Test combined filter criteria."""
        filter_ = EventFilter(
            event_types={EventType.RATE_LIMIT_EXCEEDED},
            sources={"api-gateway"},
            min_severity="warning"
        )
        
        matching = Event(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            source="api-gateway",
            severity="critical"
        )
        assert filter_.matches(matching)


class TestEventHandlers:
    """Test event handler functionality."""
    
    def test_callback_handler(self):
        """Test callback event handler."""
        handled_events = []
        handler = CallbackEventHandler(
            "test",
            lambda e: handled_events.append(e)
        )
        
        event = Event()
        assert handler.handle(event)
        assert len(handled_events) == 1
    
    def test_logging_handler(self):
        """Test logging event handler."""
        handler = LoggingEventHandler("logger")
        
        event1 = Event(event_type=EventType.RATE_LIMIT_EXCEEDED)
        event2 = Event(event_type=EventType.CIRCUIT_BREAKER_OPEN)
        
        assert handler.handle(event1)
        assert handler.handle(event2)
        
        events = handler.get_events()
        assert len(events) == 2
    
    def test_handler_enable_disable(self):
        """Test handler enable/disable."""
        handled = []
        handler = CallbackEventHandler("test", lambda e: handled.append(e))
        
        event = Event()
        handler.handle(event)
        assert len(handled) == 1
        
        handler.disable()
        handler.handle(event)
        assert len(handled) == 1  # Not incremented
        
        handler.enable()
        handler.handle(event)
        assert len(handled) == 2


class TestEventStream:
    """Test EventStream functionality."""
    
    def test_create_stream(self):
        """Test event stream creation."""
        stream = EventStream()
        assert stream.get_event_count() == 0
    
    def test_publish_event(self):
        """Test publishing event to stream."""
        stream = EventStream()
        event = Event()
        
        assert stream.publish(event)
        assert stream.get_event_count() == 1
    
    def test_subscribe_handler(self):
        """Test subscribing handler."""
        stream = EventStream()
        handler = LoggingEventHandler("logger")
        
        stream.subscribe(handler)
        assert "logger" in stream._handlers
    
    def test_publish_and_process(self):
        """Test publishing and processing events."""
        stream = EventStream()
        handler = LoggingEventHandler()
        stream.subscribe(handler)
        
        event = Event()
        stream.publish(event)
        
        processed = stream.process_events()
        assert processed > 0
        assert len(handler.get_events()) > 0
    
    def test_unsubscribe_handler(self):
        """Test unsubscribing handler."""
        stream = EventStream()
        handler = LoggingEventHandler()
        stream.subscribe(handler)
        
        assert stream.unsubscribe("logger")
        assert "logger" not in stream._handlers
    
    def test_get_pending_events(self):
        """Test getting pending events."""
        stream = EventStream()
        
        for i in range(5):
            stream.publish(Event())
        
        pending = stream.get_pending_events()
        assert len(pending) == 5
    
    def test_wait_for_events(self):
        """Test waiting for events."""
        stream = EventStream()
        
        # Publish event
        stream.publish(Event())
        
        # Wait should return immediately with event
        count = stream.wait_for_events(timeout_ms=100)
        assert count > 0


class TestEventCorrelation:
    """Test EventCorrelation functionality."""
    
    def test_add_event_to_correlation(self):
        """Test adding event to correlation."""
        correlation = EventCorrelation()
        event = Event()
        
        correlation.add_event("trace-123", event)
        events = correlation.get_events_for_correlation("trace-123")
        assert len(events) == 1
    
    def test_multiple_events_same_correlation(self):
        """Test multiple events in same correlation."""
        correlation = EventCorrelation()
        
        for i in range(3):
            event = Event(event_type=EventType.RETRY_ATTEMPTED)
            correlation.add_event("trace-123", event)
        
        events = correlation.get_events_for_correlation("trace-123")
        assert len(events) == 3
    
    def test_correlation_path(self):
        """Test getting correlation path."""
        correlation = EventCorrelation()
        
        event1 = Event(event_type=EventType.RATE_LIMIT_EXCEEDED, source="gateway")
        event2 = Event(event_type=EventType.RETRY_ATTEMPTED, source="client")
        event3 = Event(event_type=EventType.CIRCUIT_BREAKER_OPEN, source="service")
        
        correlation.add_event("trace-123", event1)
        time.sleep(0.01)
        correlation.add_event("trace-123", event2)
        time.sleep(0.01)
        correlation.add_event("trace-123", event3)
        
        path = correlation.get_correlation_path("trace-123")
        assert len(path) == 3
        assert path[0][0] == EventType.RATE_LIMIT_EXCEEDED
        assert path[1][0] == EventType.RETRY_ATTEMPTED
        assert path[2][0] == EventType.CIRCUIT_BREAKER_OPEN


class TestEventMetrics:
    """Test EventMetrics functionality."""
    
    def test_track_event_by_type(self):
        """Test tracking events by type."""
        metrics = EventMetrics()
        
        event1 = Event(event_type=EventType.RATE_LIMIT_EXCEEDED)
        event2 = Event(event_type=EventType.RATE_LIMIT_EXCEEDED)
        event3 = Event(event_type=EventType.CIRCUIT_BREAKER_OPEN)
        
        metrics.track_event(event1)
        metrics.track_event(event2)
        metrics.track_event(event3)
        
        assert metrics.get_count_by_type(EventType.RATE_LIMIT_EXCEEDED) == 2
        assert metrics.get_count_by_type(EventType.CIRCUIT_BREAKER_OPEN) == 1
    
    def test_track_event_by_source(self):
        """Test tracking events by source."""
        metrics = EventMetrics()
        
        event1 = Event(source="gateway")
        event2 = Event(source="gateway")
        event3 = Event(source="service")
        
        metrics.track_event(event1)
        metrics.track_event(event2)
        metrics.track_event(event3)
        
        assert metrics.get_count_by_source("gateway") == 2
        assert metrics.get_count_by_source("service") == 1
    
    def test_get_all_counts(self):
        """Test getting all event counts."""
        metrics = EventMetrics()
        
        metrics.track_event(Event(event_type=EventType.RATE_LIMIT_EXCEEDED))
        metrics.track_event(Event(event_type=EventType.CIRCUIT_BREAKER_OPEN))
        
        counts = metrics.get_all_counts()
        assert len(counts) == 2
        assert counts[EventType.RATE_LIMIT_EXCEEDED] == 1
        assert counts[EventType.CIRCUIT_BREAKER_OPEN] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
