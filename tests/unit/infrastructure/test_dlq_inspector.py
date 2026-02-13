"""
Unit tests for DLQInspector.

Tests failed event management, analysis, and smart retry logic.

Authority: WAVE-3 Stage 2 - ENH-089 EventBus Debugger
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from cortex.infrastructure.dlq_inspector import (
    DLQInspector,
    RetryStrategy,
    FailedEvent
)
from cortex.core.event_bus import Event


@pytest.fixture
def temp_dlq_file():
    """Create temporary DLQ file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        dlq_file = f.name
    
    yield dlq_file
    
    # Cleanup
    Path(dlq_file).unlink(missing_ok=True)


@pytest.fixture
def dlq_with_events(temp_dlq_file):
    """Create DLQ inspector with test failed events."""
    inspector = DLQInspector(temp_dlq_file)
    
    # Add test failed events
    events = [
        Event(
            type="test.failed",
            payload={"test_id": "test_001"},
            correlation_id="corr-123",
            source="TDDOrchestrator",
            priority=0
        ),
        Event(
            type="deployment.failed",
            payload={"deployment_id": "deploy_001"},
            correlation_id="corr-456",
            source="DeploymentOrchestrator",
            priority=1
        ),
        Event(
            type="validation.timeout",
            payload={"validator": "SecurityValidator"},
            correlation_id="corr-789",
            source="EnforcementAgent",
            priority=2
        )
    ]
    
    errors = [
        "Test assertion failed: expected 5, got 3",
        "Connection timeout to deployment server",
        "Validation timeout after 30 seconds"
    ]
    
    for event, error in zip(events, errors):
        inspector.add_failed_event(event, error)
    
    return inspector


def test_dlq_initialization(temp_dlq_file):
    """Test DLQ inspector initialization."""
    inspector = DLQInspector(temp_dlq_file)
    assert inspector.dlq_file.exists()


def test_add_failed_event(temp_dlq_file):
    """Test adding failed event to DLQ."""
    inspector = DLQInspector(temp_dlq_file)
    
    event = Event(
        type="test.failed",
        payload={"test_id": "test_001"},
        correlation_id="corr-123",
        source="TDDOrchestrator",
        priority=0
    )
    
    inspector.add_failed_event(event, "Test failed")
    
    failed_events = inspector.get_failed_events()
    assert len(failed_events) == 1
    assert failed_events[0].event.type == "test.failed"
    assert failed_events[0].error_message == "Test failed"


def test_get_failed_events_no_filter(dlq_with_events):
    """Test retrieving all failed events."""
    failed_events = dlq_with_events.get_failed_events()
    
    assert len(failed_events) == 3


def test_get_failed_events_by_priority(dlq_with_events):
    """Test filtering failed events by priority."""
    failed_events = dlq_with_events.get_failed_events(priority=0)
    
    assert len(failed_events) == 1
    assert failed_events[0].event.priority == 0


def test_get_failed_events_by_source(dlq_with_events):
    """Test filtering failed events by source."""
    failed_events = dlq_with_events.get_failed_events(source="TDDOrchestrator")
    
    assert len(failed_events) == 1
    assert failed_events[0].event.source == "TDDOrchestrator"


def test_get_failed_events_with_limit(dlq_with_events):
    """Test retrieving failed events with limit."""
    failed_events = dlq_with_events.get_failed_events(limit=2)
    
    assert len(failed_events) == 2


def test_analyze_dlq_empty(temp_dlq_file):
    """Test DLQ analysis with empty queue."""
    inspector = DLQInspector(temp_dlq_file)
    
    analysis = inspector.analyze_dlq()
    
    assert analysis.total_failed == 0
    assert analysis.retry_eligible == 0
    assert "✅ DLQ empty" in analysis.recommendations[0]


def test_analyze_dlq_with_events(dlq_with_events):
    """Test DLQ analysis with failed events."""
    analysis = dlq_with_events.analyze_dlq()
    
    assert analysis.total_failed == 3
    assert analysis.retry_eligible > 0
    assert len(analysis.error_types) > 0
    assert len(analysis.failure_sources) > 0
    assert len(analysis.priority_distribution) > 0


def test_error_categorization(dlq_with_events):
    """Test error message categorization."""
    analysis = dlq_with_events.analyze_dlq()
    
    # Should categorize timeout error
    assert "timeout" in analysis.error_types


def test_smart_retry_default_strategy(dlq_with_events):
    """Test smart retry with default strategy."""
    strategy = RetryStrategy()
    
    result = dlq_with_events.smart_retry(strategy)
    
    assert result["total_eligible"] >= 0
    assert result["retried"] >= 0
    assert result["skipped"] >= 0


def test_retry_strategy_priority_filter():
    """Test retry strategy with priority filtering."""
    strategy = RetryStrategy(
        max_retries=3,
        retry_priorities=[0, 1]  # Only critical and high
    )
    
    assert 0 in strategy.retry_priorities
    assert 1 in strategy.retry_priorities
    assert 2 not in strategy.retry_priorities


def test_recommendations_timeout_pattern(temp_dlq_file):
    """Test recommendations for timeout pattern."""
    inspector = DLQInspector(temp_dlq_file)
    
    # Add multiple timeout failures
    for i in range(6):
        event = Event(
            type="test.timeout",
            payload={"test_id": f"test_{i}"},
            source="TDDOrchestrator",
            priority=1
        )
        inspector.add_failed_event(event, f"Timeout error {i}")
    
    analysis = inspector.analyze_dlq()
    
    # Should recommend timeout threshold increase
    timeout_warning = any("timeout" in r.lower() for r in analysis.recommendations)
    assert timeout_warning
