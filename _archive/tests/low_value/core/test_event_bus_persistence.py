"""
Tests for EventBus event persistence layer.
Authority: WAVE-1 Foundation - Event Infrastructure
"""

import pytest
from datetime import datetime
from pathlib import Path
import json
from cortex.core.event_bus import EventBus, Event


class TestEventPersistence:
    """Test event persistence for audit trail."""
    
    def test_event_logging_enabled(self, tmp_path):
        """Test that event logging can be enabled."""
        # AC_START: AC-WAVE1-TEST-001
        log_file = tmp_path / "events.jsonl"
        bus = EventBus(log_file=str(log_file))
        
        assert bus.logging_enabled is True
        assert bus.log_file == str(log_file)
        # AC_COMPLETE: AC-WAVE1-TEST-001 ✅
    
    def test_event_logged_on_publish(self, tmp_path):
        """Test that events are logged when published."""
        # AC_START: AC-WAVE1-TEST-002
        log_file = tmp_path / "events.jsonl"
        bus = EventBus(log_file=str(log_file))
        
        event = Event(type="test_event", payload={"data": "value"})
        bus.publish(event)
        
        # Verify event was logged
        with open(log_file) as f:
            logged_event = json.loads(f.readline())
        
        assert logged_event["type"] == "test_event"
        assert logged_event["payload"] == {"data": "value"}
        assert "timestamp" in logged_event
        # AC_COMPLETE: AC-WAVE1-TEST-002 ✅
    
    def test_multiple_events_logged(self, tmp_path):
        """Test that multiple events are logged sequentially."""
        # AC_START: AC-WAVE1-TEST-003
        log_file = tmp_path / "events.jsonl"
        bus = EventBus(log_file=str(log_file))
        
        bus.publish(Event(type="event1", payload={"id": 1}))
        bus.publish(Event(type="event2", payload={"id": 2}))
        bus.publish(Event(type="event3", payload={"id": 3}))
        
        # Verify all events logged
        with open(log_file) as f:
            events = [json.loads(line) for line in f]
        
        assert len(events) == 3
        assert events[0]["payload"]["id"] == 1
        assert events[1]["payload"]["id"] == 2
        assert events[2]["payload"]["id"] == 3
        # AC_COMPLETE: AC-WAVE1-TEST-003 ✅
    
    def test_event_logging_optional(self):
        """Test that event logging is optional (disabled by default)."""
        # AC_START: AC-WAVE1-TEST-004
        bus = EventBus()  # No log_file provided
        
        assert bus.logging_enabled is False
        
        # Should not raise error when logging disabled
        event = Event(type="test", payload={})
        bus.publish(event)  # Should succeed without logging
        # AC_COMPLETE: AC-WAVE1-TEST-004 ✅
    
    def test_event_timestamp_format(self, tmp_path):
        """Test that event timestamps are ISO 8601 format."""
        # AC_START: AC-WAVE1-TEST-005
        log_file = tmp_path / "events.jsonl"
        bus = EventBus(log_file=str(log_file))
        
        bus.publish(Event(type="test", payload={}))
        
        with open(log_file) as f:
            logged_event = json.loads(f.readline())
        
        # Verify timestamp is ISO 8601
        timestamp = logged_event["timestamp"]
        datetime.fromisoformat(timestamp)  # Should not raise
        # AC_COMPLETE: AC-WAVE1-TEST-005 ✅
    
    def test_event_log_creates_directory(self, tmp_path):
        """Test that log directory is created if it doesn't exist."""
        # AC_START: AC-WAVE1-TEST-006
        log_dir = tmp_path / "logs" / "events"
        log_file = log_dir / "events.jsonl"
        
        assert not log_dir.exists()
        
        bus = EventBus(log_file=str(log_file))
        bus.publish(Event(type="test", payload={}))
        
        assert log_dir.exists()
        assert log_file.exists()
        # AC_COMPLETE: AC-WAVE1-TEST-006 ✅
    
    def test_event_log_append_mode(self, tmp_path):
        """Test that events are appended to existing log file."""
        # AC_START: AC-WAVE1-TEST-007
        log_file = tmp_path / "events.jsonl"
        
        # First bus instance
        bus1 = EventBus(log_file=str(log_file))
        bus1.publish(Event(type="event1", payload={}))
        
        # Second bus instance (simulates restart)
        bus2 = EventBus(log_file=str(log_file))
        bus2.publish(Event(type="event2", payload={}))
        
        # Verify both events present
        with open(log_file) as f:
            events = [json.loads(line) for line in f]
        
        assert len(events) == 2
        assert events[0]["type"] == "event1"
        assert events[1]["type"] == "event2"
        # AC_COMPLETE: AC-WAVE1-TEST-007 ✅
    
    def test_legacy_publish_format_logged(self, tmp_path):
        """Test that legacy publish format is also logged."""
        # AC_START: AC-WAVE1-TEST-008
        log_file = tmp_path / "events.jsonl"
        bus = EventBus(log_file=str(log_file))
        
        # Legacy format: publish(event_type, data)
        bus.publish("legacy_event", {"key": "value"})
        
        with open(log_file) as f:
            logged_event = json.loads(f.readline())
        
        assert logged_event["type"] == "legacy_event"
        assert logged_event["payload"] == {"key": "value"}
        # AC_COMPLETE: AC-WAVE1-TEST-008 ✅
    
    def test_event_log_error_handling(self, tmp_path):
        """Test that logging errors don't break event delivery."""
        # AC_START: AC-WAVE1-TEST-009
        log_file = tmp_path / "readonly" / "events.jsonl"
        log_file.parent.mkdir()
        log_file.parent.chmod(0o444)  # Read-only directory
        
        bus = EventBus(log_file=str(log_file))
        
        # Handler to verify event was still delivered
        delivered = []
        bus.subscribe("test", lambda e: delivered.append(e))
        
        # Should not raise even if logging fails
        event = Event(type="test", payload={})
        bus.publish(event)
        
        # Event should still be delivered to subscribers
        assert len(delivered) == 1
        # AC_COMPLETE: AC-WAVE1-TEST-009 ✅
    
    def test_event_log_rotation_not_implemented(self, tmp_path):
        """Test that log rotation is not yet implemented (future enhancement)."""
        # AC_START: AC-WAVE1-TEST-010
        log_file = tmp_path / "events.jsonl"
        bus = EventBus(log_file=str(log_file))
        
        # Log rotation would be a future enhancement
        # For now, logs append indefinitely
        assert not hasattr(bus, 'rotate_log')
        # AC_COMPLETE: AC-WAVE1-TEST-010 ✅
