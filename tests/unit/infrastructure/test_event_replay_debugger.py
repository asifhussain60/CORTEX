"""
Unit tests for EventReplayDebugger.

Tests event filtering, replay, and correlation analysis capabilities.

Authority: WAVE-3 Stage 2 - ENH-089 EventBus Debugger
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import json
import tempfile

from cortex.infrastructure.event_replay_debugger import (
    EventReplayDebugger,
    ReplayFilter,
    ReplayResult
)
from cortex.core.event_bus import Event


@pytest.fixture
def temp_log_file():
    """Create temporary event log file with test data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        log_file = f.name
        
        # Write test events
        now = datetime.now()
        
        events = [
            {
                "timestamp": now.isoformat(),
                "type": "test.started",
                "payload": {
                    "correlation_id": "corr-123",
                    "event_id": "evt-001",
                    "source": "TDDOrchestrator",
                    "priority": 1
                }
            },
            {
                "timestamp": (now + timedelta(seconds=1)).isoformat(),
                "type": "test.passed",
                "payload": {
                    "correlation_id": "corr-123",
                    "event_id": "evt-002",
                    "source": "TDDOrchestrator",
                    "priority": 2
                }
            },
            {
                "timestamp": (now + timedelta(seconds=2)).isoformat(),
                "type": "test.failed",
                "payload": {
                    "correlation_id": "corr-456",
                    "event_id": "evt-003",
                    "source": "EnforcementAgent",
                    "priority": 0
                }
            }
        ]
        
        for event in events:
            f.write(json.dumps(event) + '\n')
    
    yield log_file
    
    # Cleanup
    Path(log_file).unlink(missing_ok=True)


def test_debugger_initialization(temp_log_file):
    """Test EventReplayDebugger initialization."""
    debugger = EventReplayDebugger(temp_log_file)
    assert debugger.log_file.exists()


def test_debugger_missing_log_file():
    """Test initialization with missing log file."""
    with pytest.raises(FileNotFoundError):
        EventReplayDebugger("/nonexistent/file.jsonl")


def test_filter_by_correlation_id(temp_log_file):
    """Test filtering events by correlation ID."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter(correlation_id="corr-123")
    events = debugger.filter_events(replay_filter)
    
    assert len(events) == 2
    assert all(e.correlation_id == "corr-123" for e in events)


def test_filter_by_event_type(temp_log_file):
    """Test filtering events by type."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter(event_types=["test.failed"])
    events = debugger.filter_events(replay_filter)
    
    assert len(events) == 1
    assert events[0].type == "test.failed"


def test_filter_by_source(temp_log_file):
    """Test filtering events by source component."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter(source="TDDOrchestrator")
    events = debugger.filter_events(replay_filter)
    
    assert len(events) == 2
    assert all(e.source == "TDDOrchestrator" for e in events)


def test_filter_by_priority(temp_log_file):
    """Test filtering events by priority."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter(priority=0)
    events = debugger.filter_events(replay_filter)
    
    assert len(events) == 1
    assert events[0].priority == 0


def test_filter_with_limit(temp_log_file):
    """Test filtering with result limit."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter()  # No filters
    events = debugger.filter_events(replay_filter, limit=2)
    
    assert len(events) == 2


def test_replay_events_success(temp_log_file):
    """Test successful event replay."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter()
    events = debugger.filter_events(replay_filter)
    
    processed = []
    def handler(event):
        processed.append(event.event_id)
    
    result = debugger.replay_events(events, handler)
    
    assert result.success
    assert result.events_replayed == 3
    assert result.events_matched == 3
    assert len(result.errors) == 0
    assert len(processed) == 3


def test_replay_events_with_error(temp_log_file):
    """Test event replay with handler error."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter()
    events = debugger.filter_events(replay_filter)
    
    def failing_handler(event):
        if event.type == "test.failed":
            raise ValueError("Handler error")
    
    result = debugger.replay_events(events, failing_handler, stop_on_error=False)
    
    assert not result.success
    assert result.events_replayed == 2  # 2 succeeded before failure
    assert result.events_matched == 3
    assert len(result.errors) == 1


def test_replay_stop_on_error(temp_log_file):
    """Test replay stopping on first error."""
    debugger = EventReplayDebugger(temp_log_file)
    
    replay_filter = ReplayFilter()
    events = debugger.filter_events(replay_filter)
    
    def failing_handler(event):
        if event.type == "test.passed":
            raise ValueError("Stop here")
    
    result = debugger.replay_events(events, failing_handler, stop_on_error=True)
    
    assert not result.success
    assert result.events_replayed == 1  # Only first event processed
    assert len(result.errors) == 1


def test_analyze_correlation(temp_log_file):
    """Test correlation analysis."""
    debugger = EventReplayDebugger(temp_log_file)
    
    analysis = debugger.analyze_correlation("corr-123")
    
    assert analysis["correlation_id"] == "corr-123"
    assert analysis["events_found"] == 2
    assert len(analysis["timeline"]) == 2
    assert "test.started" in analysis["event_types"]
    assert "test.passed" in analysis["event_types"]
    assert "TDDOrchestrator" in analysis["sources"]


def test_analyze_missing_correlation(temp_log_file):
    """Test analysis of non-existent correlation ID."""
    debugger = EventReplayDebugger(temp_log_file)
    
    analysis = debugger.analyze_correlation("corr-999")
    
    assert analysis["correlation_id"] == "corr-999"
    assert analysis["events_found"] == 0
    assert len(analysis["timeline"]) == 0
