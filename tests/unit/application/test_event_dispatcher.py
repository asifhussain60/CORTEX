"""Tests for event dispatcher"""
import pytest
from src.application.common.event_dispatcher import EventDispatcher, get_event_dispatcher, reset_event_dispatcher
from src.domain.common.base_entity import BaseEvent, BaseEntity
from src.domain.events import ConversationCapturedEvent
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TestEvent(BaseEvent):
    """Test event for dispatcher tests"""
    message: str


@dataclass
class AnotherTestEvent(BaseEvent):
    """Another test event"""
    value: int


class TestEntity(BaseEntity):
    """Test entity that can raise events"""
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def do_something(self):
        """Raise a test event"""
        event = TestEvent(message=f"{self.name} did something")
        self.add_domain_event(event)


class TestEventDispatcherRegistration:
    """Test handler registration"""
    
    def setup_method(self):
        """Create fresh dispatcher for each test"""
        self.dispatcher = EventDispatcher()
    
    def test_register_handler(self):
        """Should register event handler"""
        handler_called = []
        
        def handler(event: TestEvent):
            handler_called.append(event)
        
        self.dispatcher.register(TestEvent, handler)
        assert self.dispatcher.get_handler_count(TestEvent) == 1
    
    def test_register_multiple_handlers_same_event(self):
        """Should register multiple handlers for same event"""
        def handler1(event: TestEvent):
            pass
        
        def handler2(event: TestEvent):
            pass
        
        self.dispatcher.register(TestEvent, handler1)
        self.dispatcher.register(TestEvent, handler2)
        
        assert self.dispatcher.get_handler_count(TestEvent) == 2
    
    def test_register_handlers_different_events(self):
        """Should register handlers for different events"""
        def test_handler(event: TestEvent):
            pass
        
        def another_handler(event: AnotherTestEvent):
            pass
        
        self.dispatcher.register(TestEvent, test_handler)
        self.dispatcher.register(AnotherTestEvent, another_handler)
        
        assert self.dispatcher.get_handler_count(TestEvent) == 1
        assert self.dispatcher.get_handler_count(AnotherTestEvent) == 1
    
    def test_register_global_handler(self):
        """Should register global handler"""
        def global_handler(event: BaseEvent):
            pass
        
        self.dispatcher.register_global(global_handler)
        assert self.dispatcher.get_handler_count() == 1
    
    def test_unregister_handler(self):
        """Should unregister handler"""
        def handler(event: TestEvent):
            pass
        
        self.dispatcher.register(TestEvent, handler)
        assert self.dispatcher.get_handler_count(TestEvent) == 1
        
        self.dispatcher.unregister(TestEvent, handler)
        assert self.dispatcher.get_handler_count(TestEvent) == 0
    
    def test_clear_handlers(self):
        """Should clear all handlers"""
        def handler1(event: TestEvent):
            pass
        
        def handler2(event: AnotherTestEvent):
            pass
        
        self.dispatcher.register(TestEvent, handler1)
        self.dispatcher.register(AnotherTestEvent, handler2)
        
        self.dispatcher.clear_handlers()
        assert self.dispatcher.get_handler_count() == 0


class TestEventDispatching:
    """Test event dispatching"""
    
    def setup_method(self):
        """Create fresh dispatcher for each test"""
        self.dispatcher = EventDispatcher()
    
    def test_dispatch_calls_handler(self):
        """Should call registered handler"""
        received_events = []
        
        def handler(event: TestEvent):
            received_events.append(event)
        
        self.dispatcher.register(TestEvent, handler)
        
        entity = TestEntity("test")
        entity.do_something()
        self.dispatcher.dispatch(entity)
        
        assert len(received_events) == 1
        assert received_events[0].message == "test did something"
    
    def test_dispatch_calls_multiple_handlers(self):
        """Should call all registered handlers"""
        handler1_called = []
        handler2_called = []
        
        def handler1(event: TestEvent):
            handler1_called.append(event)
        
        def handler2(event: TestEvent):
            handler2_called.append(event)
        
        self.dispatcher.register(TestEvent, handler1)
        self.dispatcher.register(TestEvent, handler2)
        
        entity = TestEntity("test")
        entity.do_something()
        self.dispatcher.dispatch(entity)
        
        assert len(handler1_called) == 1
        assert len(handler2_called) == 1
    
    def test_dispatch_multiple_events(self):
        """Should dispatch multiple events from entity"""
        received_events = []
        
        def handler(event: TestEvent):
            received_events.append(event)
        
        self.dispatcher.register(TestEvent, handler)
        
        entity = TestEntity("test")
        entity.do_something()
        entity.do_something()
        self.dispatcher.dispatch(entity)
        
        assert len(received_events) == 2
    
    def test_dispatch_clears_events(self):
        """Should clear entity events after dispatch"""
        def handler(event: TestEvent):
            pass
        
        self.dispatcher.register(TestEvent, handler)
        
        entity = TestEntity("test")
        entity.do_something()
        assert len(entity.domain_events) == 1
        
        self.dispatcher.dispatch(entity)
        assert len(entity.domain_events) == 0
    
    def test_dispatch_calls_global_handlers(self):
        """Should call global handlers for all events"""
        global_received = []
        
        def global_handler(event: BaseEvent):
            global_received.append(event)
        
        self.dispatcher.register_global(global_handler)
        
        entity = TestEntity("test")
        entity.do_something()
        self.dispatcher.dispatch(entity)
        
        assert len(global_received) == 1
        assert isinstance(global_received[0], TestEvent)
    
    def test_dispatch_no_handlers(self):
        """Should handle dispatch with no registered handlers"""
        entity = TestEntity("test")
        entity.do_something()
        
        # Should not raise error
        self.dispatcher.dispatch(entity)
        assert len(entity.domain_events) == 0  # Events cleared
    
    def test_dispatch_empty_entity(self):
        """Should handle entity with no events"""
        def handler(event: TestEvent):
            pytest.fail("Handler should not be called")
        
        self.dispatcher.register(TestEvent, handler)
        
        entity = TestEntity("test")
        # Don't raise any events
        
        self.dispatcher.dispatch(entity)  # Should not fail


class TestEventDispatcherErrorHandling:
    """Test error handling in dispatcher"""
    
    def setup_method(self):
        """Create fresh dispatcher for each test"""
        self.dispatcher = EventDispatcher()
    
    def test_handler_exception_does_not_stop_other_handlers(self):
        """Should continue dispatching even if handler fails"""
        handler1_called = []
        handler2_called = []
        
        def handler1(event: TestEvent):
            raise ValueError("Handler 1 failed")
        
        def handler2(event: TestEvent):
            handler2_called.append(event)
        
        self.dispatcher.register(TestEvent, handler1)
        self.dispatcher.register(TestEvent, handler2)
        
        entity = TestEntity("test")
        entity.do_something()
        self.dispatcher.dispatch(entity)
        
        # Handler 2 should still be called despite handler 1 failing
        assert len(handler2_called) == 1
    
    def test_global_handler_exception_does_not_stop_specific_handlers(self):
        """Should call specific handlers even if global handler fails"""
        specific_called = []
        
        def failing_global_handler(event: BaseEvent):
            raise ValueError("Global handler failed")
        
        def specific_handler(event: TestEvent):
            specific_called.append(event)
        
        self.dispatcher.register_global(failing_global_handler)
        self.dispatcher.register(TestEvent, specific_handler)
        
        entity = TestEntity("test")
        entity.do_something()
        self.dispatcher.dispatch(entity)
        
        assert len(specific_called) == 1


class TestGlobalDispatcherSingleton:
    """Test global dispatcher singleton"""
    
    def test_get_event_dispatcher_returns_singleton(self):
        """Should return same instance"""
        dispatcher1 = get_event_dispatcher()
        dispatcher2 = get_event_dispatcher()
        assert dispatcher1 is dispatcher2
    
    def test_reset_event_dispatcher(self):
        """Should reset global dispatcher"""
        dispatcher1 = get_event_dispatcher()
        reset_event_dispatcher()
        dispatcher2 = get_event_dispatcher()
        assert dispatcher1 is not dispatcher2


class TestEventDispatcherWithRealEvents:
    """Test dispatcher with real CORTEX events"""
    
    def setup_method(self):
        """Create fresh dispatcher"""
        self.dispatcher = EventDispatcher()
    
    def test_dispatch_conversation_captured_event(self):
        """Should dispatch ConversationCapturedEvent"""
        received_events = []
        
        def handler(event: ConversationCapturedEvent):
            received_events.append(event)
        
        self.dispatcher.register(ConversationCapturedEvent, handler)
        
        # Create entity and raise event
        class ConversationEntity(BaseEntity):
            def capture(self):
                event = ConversationCapturedEvent(
                    conversation_id="conv-123",
                    title="Test Conversation",
                    quality_score=0.85,
                    entity_count=10,
                    file_path="/path/to/conversation.json",
                    captured_at=datetime.now()
                )
                self.add_domain_event(event)
        
        entity = ConversationEntity()
        entity.capture()
        self.dispatcher.dispatch(entity)
        
        assert len(received_events) == 1
        assert received_events[0].conversation_id == "conv-123"
        assert received_events[0].quality_score == 0.85
