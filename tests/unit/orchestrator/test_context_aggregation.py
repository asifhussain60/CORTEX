"""
Tests for context aggregation across turns.

AC-CONV-001-02: Context Aggregation and Carryover (10 tests)
"""

import pytest
from datetime import datetime

from cortex.brain.core.orchestrator.context_aggregator import (
    ContextAggregator,
    TurnContext,
)


@pytest.fixture
def aggregator():
    """Create a context aggregator."""
    return ContextAggregator(max_history_turns=5)


def test_add_single_turn(aggregator):
    """Test adding a single turn to history."""
    aggregator.add_turn(
        turn_number=1,
        user_input="Fix authentication",
        orchestrator_output={"intent_type": "FIX", "confidence": 1.0},
        context={"phase": "comprehension"}
    )
    
    assert aggregator.get_history_length() == 1


def test_aggregate_context_with_history(aggregator):
    """Test aggregating context with turn history."""
    # Add a turn
    aggregator.add_turn(
        turn_number=1,
        user_input="Fix authentication",
        orchestrator_output={"intent_type": "FIX", "confidence": 1.0},
        context={"phase": "comprehension"}
    )
    
    # Aggregate for next turn
    aggregated = aggregator.aggregate_context("Show me the results")
    
    assert "conversation_history" in aggregated
    assert len(aggregated["conversation_history"]) == 1
    assert aggregated["conversation_history"][0]["turn"] == 1
    assert aggregated["current_user_input"] == "Show me the results"
    assert aggregated["total_turns_in_conversation"] == 1


def test_previous_output_carryover(aggregator):
    """Test that previous output is carried over."""
    aggregator.add_turn(
        turn_number=1,
        user_input="Create user model",
        orchestrator_output={"created": "User", "fields": ["name", "email"]},
        context={"domain": "user_management"}
    )
    
    aggregated = aggregator.aggregate_context("Now add validation")
    
    assert "previous_output" in aggregated
    assert aggregated["previous_output"]["created"] == "User"
    assert "previous_context" in aggregated
    assert aggregated["previous_context"]["domain"] == "user_management"


def test_multiple_turn_history(aggregator):
    """Test maintaining history across multiple turns."""
    for i in range(3):
        aggregator.add_turn(
            turn_number=i + 1,
            user_input=f"Request {i+1}",
            orchestrator_output={"step": i+1},
            context={"phase": f"phase_{i+1}"}
        )
    
    aggregated = aggregator.aggregate_context("Final request")
    
    assert len(aggregated["conversation_history"]) == 3
    assert aggregated["conversation_history"][0]["turn"] == 1
    assert aggregated["conversation_history"][2]["turn"] == 3


def test_max_history_limit(aggregator):
    """Test that history is limited to max_history_turns."""
    # Add more turns than max_history_turns (5)
    for i in range(10):
        aggregator.add_turn(
            turn_number=i + 1,
            user_input=f"Request {i+1}",
            orchestrator_output={},
            context={}
        )
    
    assert aggregator.get_history_length() == 5
    
    # Should have turns 6-10
    aggregated = aggregator.aggregate_context("Check history")
    assert len(aggregated["conversation_history"]) == 5
    assert aggregated["conversation_history"][0]["turn"] == 6


def test_user_corrections_detection(aggregator):
    """Test detecting user corrections in conversation."""
    aggregator.add_turn(
        turn_number=1,
        user_input="Create user model",
        orchestrator_output={},
        context={}
    )
    
    aggregator.add_turn(
        turn_number=2,
        user_input="No, I meant create a product model",
        orchestrator_output={},
        context={}
    )
    
    aggregated = aggregator.aggregate_context("Continue")
    
    assert "user_corrections" in aggregated
    assert len(aggregated["user_corrections"]) == 1
    assert aggregated["user_corrections"][0]["turn"] == 2


def test_get_turn_by_number(aggregator):
    """Test retrieving a specific turn by number."""
    for i in range(3):
        aggregator.add_turn(
            turn_number=i + 1,
            user_input=f"Request {i+1}",
            orchestrator_output={"step": i+1},
            context={}
        )
    
    turn = aggregator.get_turn_by_number(2)
    assert turn is not None
    assert turn.turn_number == 2
    assert turn.user_input == "Request 2"


def test_get_turn_nonexistent(aggregator):
    """Test retrieving a turn that doesn't exist."""
    aggregator.add_turn(1, "Request", {}, {})
    
    turn = aggregator.get_turn_by_number(99)
    assert turn is None


def test_get_recent_turns(aggregator):
    """Test getting recent turns."""
    for i in range(5):
        aggregator.add_turn(i + 1, f"Request {i+1}", {}, {})
    
    recent = aggregator.get_recent_turns(n=3)
    assert len(recent) == 3
    assert recent[0].turn_number == 3
    assert recent[2].turn_number == 5


def test_clear_history(aggregator):
    """Test clearing conversation history."""
    for i in range(3):
        aggregator.add_turn(i + 1, f"Request {i+1}", {}, {})
    
    assert aggregator.get_history_length() == 3
    
    aggregator.clear_history()
    assert aggregator.get_history_length() == 0
