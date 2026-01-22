"""
Tests for conversation protocol observability.

AC-CONV-001-06: Production Observability (10 tests)
"""

import pytest
import logging
from unittest.mock import Mock
import time

from cortex.brain.core.orchestrator.conversation_metrics import (
    ConversationObservability,
    ConversationMetrics,
)


@pytest.fixture
def observability():
    """Create observability instance with test logger."""
    logger = logging.getLogger("test.conversation")
    logger.setLevel(logging.DEBUG)
    return ConversationObservability(logger=logger)


def test_start_conversation(observability):
    """Test starting conversation tracking."""
    observability.start_conversation(
        conversation_id="conv-123",
        orchestrator_name="TestOrchestrator"
    )
    
    metrics = observability.get_metrics("conv-123")
    assert metrics is not None
    assert metrics.conversation_id == "conv-123"
    assert metrics.turn_count == 0


def test_turn_lifecycle(observability):
    """Test complete turn lifecycle tracking."""
    conversation_id = "conv-123"
    observability.start_conversation(conversation_id, "TestOrch")
    
    start_time = observability.start_turn(conversation_id, 1, "Test input")
    time.sleep(0.01)  # Simulate some work
    observability.end_turn(conversation_id, 1, start_time, success=True)
    
    metrics = observability.get_metrics(conversation_id)
    assert metrics.turn_count == 1
    assert metrics.total_duration_ms > 0
    assert metrics.avg_turn_duration_ms > 0


def test_multiple_turns(observability):
    """Test tracking multiple turns."""
    conversation_id = "conv-123"
    observability.start_conversation(conversation_id, "TestOrch")
    
    for i in range(3):
        start_time = observability.start_turn(conversation_id, i+1, f"Input {i+1}")
        time.sleep(0.01)
        observability.end_turn(conversation_id, i+1, start_time)
    
    metrics = observability.get_metrics(conversation_id)
    assert metrics.turn_count == 3
    assert metrics.avg_turn_duration_ms > 0


def test_record_timeout(observability):
    """Test recording turn timeout."""
    conversation_id = "conv-123"
    observability.start_conversation(conversation_id, "TestOrch")
    
    observability.record_timeout(conversation_id, 1)
    
    metrics = observability.get_metrics(conversation_id)
    assert metrics.timeout_count == 1


def test_record_cancellation(observability):
    """Test recording turn cancellation."""
    conversation_id = "conv-123"
    observability.start_conversation(conversation_id, "TestOrch")
    
    observability.record_cancellation(conversation_id, 1)
    
    metrics = observability.get_metrics(conversation_id)
    assert metrics.cancellation_count == 1


def test_success_rate_calculation(observability):
    """Test success rate calculation with errors."""
    conversation_id = "conv-123"
    observability.start_conversation(conversation_id, "TestOrch")
    
    # 2 successful turns
    for i in range(2):
        start_time = observability.start_turn(conversation_id, i+1, "Input")
        observability.end_turn(conversation_id, i+1, start_time, success=True)
    
    # 1 failed turn
    start_time = observability.start_turn(conversation_id, 3, "Input")
    observability.end_turn(conversation_id, 3, start_time, success=False, error="Test error")
    
    metrics = observability.get_metrics(conversation_id)
    assert metrics.turn_count == 3
    assert metrics.error_count == 1
    assert metrics.success_rate == pytest.approx(2/3, 0.01)


def test_end_conversation(observability):
    """Test ending conversation tracking."""
    conversation_id = "conv-123"
    observability.start_conversation(conversation_id, "TestOrch")
    
    start_time = observability.start_turn(conversation_id, 1, "Input")
    observability.end_turn(conversation_id, 1, start_time)
    
    observability.end_conversation(conversation_id, reason="complete")
    
    # Metrics should still be accessible
    metrics = observability.get_metrics(conversation_id)
    assert metrics is not None


def test_get_nonexistent_metrics(observability):
    """Test getting metrics for non-existent conversation."""
    metrics = observability.get_metrics("nonexistent")
    assert metrics is None


def test_get_all_metrics(observability):
    """Test getting all conversation metrics."""
    observability.start_conversation("conv-1", "Orch1")
    observability.start_conversation("conv-2", "Orch2")
    
    all_metrics = observability.get_all_metrics()
    assert len(all_metrics) == 2
    assert "conv-1" in all_metrics
    assert "conv-2" in all_metrics


def test_clear_specific_metrics(observability):
    """Test clearing specific conversation metrics."""
    observability.start_conversation("conv-1", "Orch1")
    observability.start_conversation("conv-2", "Orch2")
    
    observability.clear_metrics("conv-1")
    
    assert observability.get_metrics("conv-1") is None
    assert observability.get_metrics("conv-2") is not None


def test_clear_all_metrics(observability):
    """Test clearing all metrics."""
    observability.start_conversation("conv-1", "Orch1")
    observability.start_conversation("conv-2", "Orch2")
    
    observability.clear_metrics()
    
    assert len(observability.get_all_metrics()) == 0
