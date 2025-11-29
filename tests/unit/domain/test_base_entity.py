"""Unit tests for BaseEntity domain event support"""
import pytest
from dataclasses import dataclass
from src.domain.common.base_entity import BaseEntity, BaseEvent


@dataclass
class TestEvent(BaseEvent):
    """Test event for unit tests"""
    message: str


class TestEntity(BaseEntity):
    """Test entity for unit tests"""
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def do_something(self):
        """Simulate domain operation that raises event"""
        self.add_domain_event(TestEvent("Something happened"))


class TestBaseEntity:
    """Test BaseEntity domain event functionality"""
    
    def test_entity_starts_with_no_events(self):
        """Test entity initializes with empty event list"""
        entity = TestEntity("test")
        
        assert len(entity.domain_events) == 0
    
    def test_can_add_domain_event(self):
        """Test adding domain events to entity"""
        entity = TestEntity("test")
        event = TestEvent("test event")
        
        entity.add_domain_event(event)
        
        assert len(entity.domain_events) == 1
        assert entity.domain_events[0] == event
    
    def test_can_add_multiple_events(self):
        """Test adding multiple domain events"""
        entity = TestEntity("test")
        
        entity.add_domain_event(TestEvent("event 1"))
        entity.add_domain_event(TestEvent("event 2"))
        entity.add_domain_event(TestEvent("event 3"))
        
        assert len(entity.domain_events) == 3
    
    def test_can_remove_domain_event(self):
        """Test removing specific domain event"""
        entity = TestEntity("test")
        event1 = TestEvent("event 1")
        event2 = TestEvent("event 2")
        
        entity.add_domain_event(event1)
        entity.add_domain_event(event2)
        entity.remove_domain_event(event1)
        
        assert len(entity.domain_events) == 1
        assert entity.domain_events[0] == event2
    
    def test_can_clear_all_events(self):
        """Test clearing all domain events"""
        entity = TestEntity("test")
        
        entity.add_domain_event(TestEvent("event 1"))
        entity.add_domain_event(TestEvent("event 2"))
        entity.clear_domain_events()
        
        assert len(entity.domain_events) == 0
    
    def test_domain_events_returns_copy(self):
        """Test domain_events property returns a copy (not reference)"""
        entity = TestEntity("test")
        entity.add_domain_event(TestEvent("event 1"))
        
        events = entity.domain_events
        events.append(TestEvent("event 2"))  # Modify the copy
        
        # Original should be unchanged
        assert len(entity.domain_events) == 1
    
    def test_domain_operation_raises_event(self):
        """Test domain operations can raise events"""
        entity = TestEntity("test")
        
        entity.do_something()
        
        assert len(entity.domain_events) == 1
        assert entity.domain_events[0].message == "Something happened"
