"""
TDD tests for OrchestratorEventBus - Phase 1 Event Bus Infrastructure.

Tests for: OrchestratorEventBus extending cortex/core/event_bus.py
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 1
Compliance: CORE-008 (TDD - tests BEFORE code), CORE-011 (type hints), CORE-012 (docstrings)
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import asyncio


class TestOrchestratorEventBusBasics(unittest.TestCase):
    """Tests for basic OrchestratorEventBus functionality."""
    
    def test_inherits_from_event_bus(self) -> None:
        """Verify OrchestratorEventBus extends base EventBus."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.core.event_bus import EventBus
        
        bus = OrchestratorEventBus()
        self.assertIsInstance(bus, EventBus)
    
    def test_publish_orchestrator_event(self) -> None:
        """Verify can publish OrchestratorEvent objects."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        handler = Mock()
        bus.subscribe(EventType.REQUEST_RECEIVED, handler)
        
        event = OrchestratorEvent(
            event_type=EventType.REQUEST_RECEIVED,
            source_orchestrator="MasterOrchestrator",
            payload={"request": "test request"}
        )
        
        bus.publish_event(event)
        handler.assert_called_once_with(event)
    
    def test_subscribe_to_event_type_enum(self) -> None:
        """Verify can subscribe using EventType enum values."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import EventType
        
        bus = OrchestratorEventBus()
        handler = Mock()
        
        bus.subscribe(EventType.INTENT_CLASSIFIED, handler)
        
        self.assertIn(EventType.INTENT_CLASSIFIED, bus.subscribers)
    
    def test_multiple_handlers_per_event_type(self) -> None:
        """Verify multiple handlers can subscribe to same event type."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        handler1 = Mock()
        handler2 = Mock()
        
        bus.subscribe(EventType.PLAN_GENERATED, handler1)
        bus.subscribe(EventType.PLAN_GENERATED, handler2)
        
        event = OrchestratorEvent(
            event_type=EventType.PLAN_GENERATED,
            source_orchestrator="PlanningOrchestrator",
            payload={"plan_id": "PLAN-001"}
        )
        
        bus.publish_event(event)
        
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)


class TestEventHistory(unittest.TestCase):
    """Tests for event history persistence."""
    
    def test_event_stored_in_history(self) -> None:
        """Verify published events are stored in history."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        
        event = OrchestratorEvent(
            event_type=EventType.PHASE_STARTED,
            source_orchestrator="WorkflowOrchestrator",
            payload={"phase": 1}
        )
        
        bus.publish_event(event)
        
        history = bus.get_event_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].event_id, event.event_id)
    
    def test_get_event_history_since_timestamp(self) -> None:
        """Verify can filter history by timestamp."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        
        # Create events with different timestamps
        old_event = OrchestratorEvent(
            event_type=EventType.REQUEST_RECEIVED,
            source_orchestrator="Test",
            payload={}
        )
        old_event.timestamp = datetime.now() - timedelta(hours=2)
        
        new_event = OrchestratorEvent(
            event_type=EventType.INTENT_CLASSIFIED,
            source_orchestrator="Test",
            payload={}
        )
        
        bus._event_history.append(old_event)
        bus.publish_event(new_event)
        
        since = datetime.now() - timedelta(hours=1)
        recent_history = bus.get_event_history(since=since)
        
        self.assertEqual(len(recent_history), 1)
        self.assertEqual(recent_history[0].event_type, EventType.INTENT_CLASSIFIED)
    
    def test_event_history_max_size(self) -> None:
        """Verify event history respects max size limit."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus(max_history_size=5)
        
        for i in range(10):
            event = OrchestratorEvent(
                event_type=EventType.PHASE_COMPLETE,
                source_orchestrator="Test",
                payload={"iteration": i}
            )
            bus.publish_event(event)
        
        history = bus.get_event_history()
        self.assertEqual(len(history), 5)
        # Should keep most recent
        self.assertEqual(history[-1].payload["iteration"], 9)


class TestCorrelationTracking(unittest.TestCase):
    """Tests for correlation ID tracking across event chains."""
    
    def test_events_linked_by_correlation_id(self) -> None:
        """Verify events with same correlation_id are linked."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        correlation_id = "task-123"
        
        event1 = OrchestratorEvent(
            event_type=EventType.REQUEST_RECEIVED,
            source_orchestrator="Interaction",
            payload={},
            correlation_id=correlation_id
        )
        
        event2 = OrchestratorEvent(
            event_type=EventType.INTENT_CLASSIFIED,
            source_orchestrator="IntentRouter",
            payload={},
            correlation_id=correlation_id
        )
        
        bus.publish_event(event1)
        bus.publish_event(event2)
        
        chain = bus.get_event_chain(correlation_id)
        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[0].event_type, EventType.REQUEST_RECEIVED)
        self.assertEqual(chain[1].event_type, EventType.INTENT_CLASSIFIED)
    
    def test_get_event_chain_returns_ordered_events(self) -> None:
        """Verify event chain is returned in chronological order."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        correlation_id = "task-456"
        
        # Create events in order
        event_types = [
            EventType.REQUEST_RECEIVED,
            EventType.INTENT_CLASSIFIED,
            EventType.PLANNING_REQUIRED,
            EventType.PLAN_GENERATED
        ]
        
        for et in event_types:
            event = OrchestratorEvent(
                event_type=et,
                source_orchestrator="Test",
                payload={},
                correlation_id=correlation_id
            )
            bus.publish_event(event)
        
        chain = bus.get_event_chain(correlation_id)
        
        for i, event in enumerate(chain):
            self.assertEqual(event.event_type, event_types[i])
    
    def test_generate_correlation_id(self) -> None:
        """Verify can generate unique correlation IDs."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        
        bus = OrchestratorEventBus()
        
        id1 = bus.generate_correlation_id()
        id2 = bus.generate_correlation_id()
        
        self.assertIsInstance(id1, str)
        self.assertNotEqual(id1, id2)


class TestUnsubscribe(unittest.TestCase):
    """Tests for unsubscribing from events."""
    
    def test_unsubscribe_handler(self) -> None:
        """Verify handler can be unsubscribed."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        handler = Mock()
        
        bus.subscribe(EventType.PHASE_COMPLETE, handler)
        bus.unsubscribe(EventType.PHASE_COMPLETE, handler)
        
        event = OrchestratorEvent(
            event_type=EventType.PHASE_COMPLETE,
            source_orchestrator="Test",
            payload={}
        )
        bus.publish_event(event)
        
        handler.assert_not_called()
    
    def test_unsubscribe_nonexistent_handler_is_safe(self) -> None:
        """Verify unsubscribing nonexistent handler doesn't error."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import EventType
        
        bus = OrchestratorEventBus()
        handler = Mock()
        
        # Should not raise
        bus.unsubscribe(EventType.ERROR_OCCURRED, handler)


class TestAsyncHandlers(unittest.TestCase):
    """Tests for async handler support."""
    
    def test_async_handler_called(self) -> None:
        """Verify async handlers are awaited."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        results = []
        
        async def async_handler(event):
            results.append(event.event_id)
        
        bus.subscribe(EventType.FINAL_REVIEW_COMPLETE, async_handler)
        
        event = OrchestratorEvent(
            event_type=EventType.FINAL_REVIEW_COMPLETE,
            source_orchestrator="ReviewOrchestrator",
            payload={}
        )
        
        # Use asyncio to run publish
        asyncio.run(bus.publish_event_async(event))
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], event.event_id)
    
    def test_mixed_sync_async_handlers(self) -> None:
        """Verify can mix sync and async handlers."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        results = []
        
        def sync_handler(event):
            results.append(("sync", event.event_id))
        
        async def async_handler(event):
            results.append(("async", event.event_id))
        
        bus.subscribe(EventType.IMPLEMENTATION_COMPLETE, sync_handler)
        bus.subscribe(EventType.IMPLEMENTATION_COMPLETE, async_handler)
        
        event = OrchestratorEvent(
            event_type=EventType.IMPLEMENTATION_COMPLETE,
            source_orchestrator="TDDOrchestrator",
            payload={}
        )
        
        asyncio.run(bus.publish_event_async(event))
        
        self.assertEqual(len(results), 2)


class TestDeadLetterQueue(unittest.TestCase):
    """Tests for dead letter queue (failed handlers)."""
    
    def test_failed_handler_event_goes_to_dlq(self) -> None:
        """Verify events with failed handlers go to dead letter queue."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        
        def failing_handler(event):
            raise ValueError("Handler failed")
        
        bus.subscribe(EventType.ERROR_OCCURRED, failing_handler)
        
        event = OrchestratorEvent(
            event_type=EventType.ERROR_OCCURRED,
            source_orchestrator="Test",
            payload={}
        )
        
        # Should not raise, but store in DLQ
        bus.publish_event(event)
        
        dlq = bus.get_dead_letter_queue()
        self.assertEqual(len(dlq), 1)
        self.assertEqual(dlq[0]["event"].event_id, event.event_id)
        self.assertIn("ValueError", dlq[0]["error"])
    
    def test_other_handlers_still_called_after_failure(self) -> None:
        """Verify other handlers run even if one fails."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        results = []
        
        def failing_handler(event):
            raise ValueError("I fail")
        
        def working_handler(event):
            results.append(event.event_id)
        
        bus.subscribe(EventType.GATE_DECISION_MADE, failing_handler)
        bus.subscribe(EventType.GATE_DECISION_MADE, working_handler)
        
        event = OrchestratorEvent(
            event_type=EventType.GATE_DECISION_MADE,
            source_orchestrator="Test",
            payload={}
        )
        
        bus.publish_event(event)
        
        # Working handler should still be called
        self.assertEqual(len(results), 1)


class TestEventReplay(unittest.TestCase):
    """Tests for event replay functionality."""
    
    def test_replay_events_from_history(self) -> None:
        """Verify can replay events from a specific point."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        bus = OrchestratorEventBus()
        results = []
        
        # Publish some events
        event1 = OrchestratorEvent(
            event_type=EventType.PHASE_STARTED,
            source_orchestrator="Test",
            payload={"phase": 1}
        )
        event2 = OrchestratorEvent(
            event_type=EventType.PHASE_COMPLETE,
            source_orchestrator="Test",
            payload={"phase": 1}
        )
        
        bus.publish_event(event1)
        bus.publish_event(event2)
        
        # Subscribe after events published
        def handler(event):
            results.append(event.event_id)
        
        bus.subscribe(EventType.PHASE_STARTED, handler)
        bus.subscribe(EventType.PHASE_COMPLETE, handler)
        
        # Replay all events
        bus.replay_events(from_event_id=event1.event_id)
        
        self.assertEqual(len(results), 2)


class TestBackwardCompatibility(unittest.TestCase):
    """Tests for backward compatibility with base EventBus."""
    
    def test_base_publish_still_works(self) -> None:
        """Verify base EventBus publish method still works."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        
        bus = OrchestratorEventBus()
        handler = Mock()
        
        # Use base EventBus style
        bus.subscribe("feature_enabled", handler)
        bus.publish("feature_enabled", {"feature_id": "test"})
        
        handler.assert_called_once_with({"feature_id": "test"})
    
    def test_feature_enabled_convenience_method(self) -> None:
        """Verify feature_enabled convenience method still works."""
        from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
        
        bus = OrchestratorEventBus()
        handler = Mock()
        
        bus.subscribe("feature_enabled", handler)
        bus.feature_enabled("my_feature")
        
        handler.assert_called_once()


if __name__ == "__main__":
    unittest.main()
