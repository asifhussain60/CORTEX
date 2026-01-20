"""Tests for update propagation."""
import pytest
from src.core.knowledge.update_propagation import UpdatePropagator, UpdateEvent, UpdateType

@pytest.fixture
def propagator():
    backends = {"backend_a": {}, "backend_b": {}}
    return UpdatePropagator(backends)

def test_propagate_update_basic(propagator):
    """Test basic update propagation."""
    success = propagator.propagate_update("backend_a", {"key": "value"})
    assert success
    assert len(propagator.update_history) == 1

def test_propagate_update_stores_event(propagator):
    """Test propagate update stores event."""
    propagator.propagate_update("backend_a", {"data": "test"})
    event = propagator.update_history[0]
    assert event.backend == "backend_a"
    assert event.data == {"data": "test"}

def test_batch_update(propagator):
    """Test batch update."""
    updates = [
        {"backend": "backend_a", "data": {"id": 1}},
        {"backend": "backend_b", "data": {"id": 2}},
        {"backend": "backend_a", "data": {"id": 3}}
    ]
    count = propagator.batch_update(updates)
    assert count == 3

def test_batch_update_returns_count(propagator):
    """Test batch update returns count."""
    updates = [{"backend": "backend_a", "data": {}}] * 5
    count = propagator.batch_update(updates)
    assert count == 5
    assert len(propagator.update_history) == 5

def test_check_consistency(propagator):
    """Test consistency check."""
    result = propagator.check_consistency()
    assert isinstance(result, bool)

def test_check_consistency_specific_backend(propagator):
    """Test consistency check for specific backend."""
    result = propagator.check_consistency("backend_a")
    assert isinstance(result, bool)

def test_get_update_history_all(propagator):
    """Test get all update history."""
    propagator.propagate_update("backend_a", {"v": 1})
    propagator.propagate_update("backend_b", {"v": 2})
    history = propagator.get_update_history()
    assert len(history) == 2

def test_get_update_history_by_backend(propagator):
    """Test get update history by backend."""
    propagator.propagate_update("backend_a", {"v": 1})
    propagator.propagate_update("backend_a", {"v": 2})
    propagator.propagate_update("backend_b", {"v": 3})
    history_a = propagator.get_update_history("backend_a")
    assert len(history_a) == 2
    assert all(e.backend == "backend_a" for e in history_a)

def test_get_update_history_with_limit(propagator):
    """Test update history with limit."""
    for i in range(10):
        propagator.propagate_update("backend_a", {"count": i})
    history = propagator.get_update_history(limit=3)
    assert len(history) == 3

def test_register_consistency_check(propagator):
    """Test register custom consistency check."""
    def check_fn():
        return True
    propagator.register_consistency_check("backend_a", check_fn)
    assert "backend_a" in propagator.consistency_checks

def test_subscribe_to_updates(propagator):
    """Test subscribe to updates."""
    events = []
    def listener(event):
        events.append(event)
    propagator.subscribe_to_updates(listener)
    propagator.propagate_update("backend_a", {})
    assert len(events) == 1

def test_listener_notification(propagator):
    """Test listener gets notified of updates."""
    received = []
    def listener(event):
        received.append(event.backend)
    propagator.subscribe_to_updates(listener)
    propagator.propagate_update("backend_a", {"test": "data"})
    assert "backend_a" in received

def test_get_update_statistics(propagator):
    """Test update statistics."""
    propagator.propagate_update("backend_a", {})
    propagator.propagate_update("backend_a", {})
    propagator.propagate_update("backend_b", {})
    stats = propagator.get_update_statistics()
    assert stats["total_updates"] == 3
    assert stats["by_backend"]["backend_a"] == 2
    assert stats["by_backend"]["backend_b"] == 1

def test_update_type_enum(propagator):
    """Test update type enumeration."""
    propagator.propagate_update("backend_a", {"v": 1}, "batch")
    event = propagator.update_history[0]
    assert hasattr(event, "update_type")

def test_multiple_listeners(propagator):
    """Test multiple listeners."""
    events1 = []
    events2 = []
    propagator.subscribe_to_updates(lambda e: events1.append(e))
    propagator.subscribe_to_updates(lambda e: events2.append(e))
    propagator.propagate_update("backend_a", {})
    assert len(events1) == 1
    assert len(events2) == 1

def test_event_id_uniqueness(propagator):
    """Test event IDs are unique."""
    propagator.propagate_update("backend_a", {})
    propagator.propagate_update("backend_a", {})
    event_ids = [e.event_id for e in propagator.update_history]
    assert len(set(event_ids)) == 2

def test_get_update_dependencies(propagator):
    """Test get update dependencies."""
    propagator.propagate_update("backend_a", {})
    deps = propagator.get_update_dependencies("nonexistent")
    assert len(deps) == 0
