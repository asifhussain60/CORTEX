"""
End-to-End Event Dispatching Integration Tests

Tests event dispatching workflow:
- Commands raise domain events
- Events are dispatched to handlers
- Event handlers process events correctly
- Multiple event handlers for same event

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import pytest
from typing import List

from src.domain.events.conversation_events import (
    ConversationCapturedEvent,
    PatternLearnedEvent
)
from src.application.events.event_dispatcher import EventDispatcher, IEventHandler


class TestEventHandler(IEventHandler[ConversationCapturedEvent]):
    """Test event handler for captured conversations."""
    
    def __init__(self):
        self.handled_events: List[ConversationCapturedEvent] = []
    
    async def handle(self, event: ConversationCapturedEvent) -> None:
        """Record event for verification."""
        self.handled_events.append(event)


class PatternTestEventHandler(IEventHandler[PatternLearnedEvent]):
    """Test event handler for learned patterns."""
    
    def __init__(self):
        self.handled_events: List[PatternLearnedEvent] = []
    
    async def handle(self, event: PatternLearnedEvent) -> None:
        """Record event for verification."""
        self.handled_events.append(event)


class MultipleHandler1(IEventHandler[ConversationCapturedEvent]):
    """First handler for testing multiple handlers."""
    
    def __init__(self):
        self.call_count = 0
    
    async def handle(self, event: ConversationCapturedEvent) -> None:
        self.call_count += 1


class MultipleHandler2(IEventHandler[ConversationCapturedEvent]):
    """Second handler for testing multiple handlers."""
    
    def __init__(self):
        self.call_count = 0
    
    async def handle(self, event: ConversationCapturedEvent) -> None:
        self.call_count += 1


class TestEventDispatchingWorkflow:
    """End-to-end event dispatching workflow tests."""
    
    def test_dispatch_single_event(self):
        """Test: Dispatch event → Handler receives event."""
        dispatcher = EventDispatcher()
        handler = TestEventHandler()
        
        # Register handler
        dispatcher.register(ConversationCapturedEvent, handler)
        
        # Create and dispatch event
        event = ConversationCapturedEvent(
            conversation_id="conv_event_001",
            title="Test Event",
            quality=0.85,
            captured_at="2025-11-22T10:00:00"
        )
        
        asyncio.run(dispatcher.dispatch(event))
        
        # Verify handler received event
        assert len(handler.handled_events) == 1
        assert handler.handled_events[0].conversation_id == "conv_event_001"
        assert handler.handled_events[0].title == "Test Event"
        assert handler.handled_events[0].quality == 0.85
    
    def test_dispatch_multiple_events_same_type(self):
        """Test: Dispatch multiple events → Handler receives all."""
        dispatcher = EventDispatcher()
        handler = TestEventHandler()
        
        dispatcher.register(ConversationCapturedEvent, handler)
        
        # Dispatch multiple events
        events = [
            ConversationCapturedEvent(
                conversation_id=f"conv_{i}",
                title=f"Event {i}",
                quality=0.70 + (i * 0.05),
                captured_at="2025-11-22T10:00:00"
            )
            for i in range(3)
        ]
        
        for event in events:
            asyncio.run(dispatcher.dispatch(event))
        
        # Verify all events received
        assert len(handler.handled_events) == 3
        assert handler.handled_events[0].conversation_id == "conv_0"
        assert handler.handled_events[1].conversation_id == "conv_1"
        assert handler.handled_events[2].conversation_id == "conv_2"
    
    def test_dispatch_different_event_types(self):
        """Test: Dispatch different event types → Correct handlers invoked."""
        dispatcher = EventDispatcher()
        conv_handler = TestEventHandler()
        pattern_handler = PatternTestEventHandler()
        
        # Register different handlers for different events
        dispatcher.register(ConversationCapturedEvent, conv_handler)
        dispatcher.register(PatternLearnedEvent, pattern_handler)
        
        # Dispatch conversation event
        conv_event = ConversationCapturedEvent(
            conversation_id="conv_001",
            title="Conversation",
            quality=0.80,
            captured_at="2025-11-22T10:00:00"
        )
        asyncio.run(dispatcher.dispatch(conv_event))
        
        # Dispatch pattern event
        pattern_event = PatternLearnedEvent(
            pattern_id="pattern_001",
            pattern_name="Test Pattern",
            pattern_type="design_pattern",
            confidence=0.85,
            learned_at="2025-11-22T10:05:00"
        )
        asyncio.run(dispatcher.dispatch(pattern_event))
        
        # Verify correct handlers received correct events
        assert len(conv_handler.handled_events) == 1
        assert conv_handler.handled_events[0].conversation_id == "conv_001"
        
        assert len(pattern_handler.handled_events) == 1
        assert pattern_handler.handled_events[0].pattern_id == "pattern_001"
    
    def test_multiple_handlers_for_same_event(self):
        """Test: Multiple handlers registered → All invoked for same event."""
        dispatcher = EventDispatcher()
        handler1 = MultipleHandler1()
        handler2 = MultipleHandler2()
        
        # Register multiple handlers for same event type
        dispatcher.register(ConversationCapturedEvent, handler1)
        dispatcher.register(ConversationCapturedEvent, handler2)
        
        # Dispatch event
        event = ConversationCapturedEvent(
            conversation_id="conv_multi",
            title="Multi Handler Test",
            quality=0.80,
            captured_at="2025-11-22T10:00:00"
        )
        asyncio.run(dispatcher.dispatch(event))
        
        # Verify both handlers were invoked
        assert handler1.call_count == 1
        assert handler2.call_count == 1
    
    def test_dispatch_with_no_handlers(self):
        """Test: Dispatch event with no registered handlers → No error."""
        dispatcher = EventDispatcher()
        
        # Dispatch event without handlers (should not raise exception)
        event = ConversationCapturedEvent(
            conversation_id="conv_no_handler",
            title="No Handler Test",
            quality=0.75,
            captured_at="2025-11-22T10:00:00"
        )
        
        # Should complete without error
        asyncio.run(dispatcher.dispatch(event))
    
    def test_event_data_integrity(self):
        """Test: Event data remains unchanged during dispatch."""
        dispatcher = EventDispatcher()
        handler = TestEventHandler()
        
        dispatcher.register(ConversationCapturedEvent, handler)
        
        # Create event with specific data
        original_data = {
            "conversation_id": "conv_integrity",
            "title": "Data Integrity Test",
            "quality": 0.92,
            "captured_at": "2025-11-22T10:00:00"
        }
        
        event = ConversationCapturedEvent(**original_data)
        asyncio.run(dispatcher.dispatch(event))
        
        # Verify data integrity
        received_event = handler.handled_events[0]
        assert received_event.conversation_id == original_data["conversation_id"]
        assert received_event.title == original_data["title"]
        assert received_event.quality == original_data["quality"]
        assert received_event.captured_at == original_data["captured_at"]
