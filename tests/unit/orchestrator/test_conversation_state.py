"""
Tests for conversation state persistence.

AC-CONV-001-01: Conversation State Persistence (12 tests)
"""

import pytest
from datetime import datetime
from pathlib import Path
from uuid import UUID
import tempfile

from cortex.brain.core.orchestrator.conversation_state import (
    ConversationState,
    ConversationStateManager,
    TurnRecord,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Close any connections before cleanup
    import gc
    gc.collect()
    import time
    time.sleep(0.1)
    try:
        if db_path.exists():
            db_path.unlink()
    except PermissionError:
        pass  # File still in use, skip cleanup


@pytest.fixture
def state_manager(temp_db):
    """Create state manager with temp database."""
    return ConversationStateManager(db_path=temp_db)


def test_create_conversation(state_manager):
    """Test creating a new conversation."""
    conversation_id = state_manager.create_conversation("MasterOrchestrator")
    
    assert isinstance(conversation_id, UUID)
    
    # Verify it was saved
    state = state_manager.load_conversation(conversation_id)
    assert state is not None
    assert state.orchestrator_name == "MasterOrchestrator"
    assert state.total_turns == 0
    assert state.total_tokens == 0
    assert state.is_complete is False


def test_save_turn_record(state_manager):
    """Test saving a turn record."""
    conversation_id = state_manager.create_conversation("TestOrchestrator")
    
    turn_record = TurnRecord(
        turn_number=1,
        user_input="Fix authentication bug",
        orchestrator_output={"intent_type": "FIX", "confidence": 1.0},
        context_state={"phase": "comprehension"},
        timestamp=datetime.now(),
        duration_ms=150.5,
        tokens_used=250,
        continuation_reason="NEEDS_MORE_INFO"
    )
    
    state_manager.save_turn(conversation_id, turn_record)
    
    # Verify turn was saved
    state = state_manager.load_conversation(conversation_id)
    assert len(state.turn_history) == 1
    assert state.turn_history[0].turn_number == 1
    assert state.turn_history[0].user_input == "Fix authentication bug"


def test_update_conversation_metadata(state_manager):
    """Test updating conversation metadata."""
    conversation_id = state_manager.create_conversation("TestOrchestrator")
    
    state = state_manager.load_conversation(conversation_id)
    state.total_turns = 5
    state.total_tokens = 1000
    state.is_complete = True
    state.context_state = {"final_phase": "complete"}
    
    state_manager.update_conversation(state)
    
    # Verify updates
    reloaded = state_manager.load_conversation(conversation_id)
    assert reloaded.total_turns == 5
    assert reloaded.total_tokens == 1000
    assert reloaded.is_complete is True
    assert reloaded.context_state["final_phase"] == "complete"


def test_load_nonexistent_conversation(state_manager):
    """Test loading a conversation that doesn't exist."""
    fake_id = UUID("00000000-0000-0000-0000-000000000000")
    state = state_manager.load_conversation(fake_id)
    assert state is None


def test_multiple_turn_records(state_manager):
    """Test saving multiple turn records."""
    conversation_id = state_manager.create_conversation("TestOrchestrator")
    
    for i in range(3):
        turn_record = TurnRecord(
            turn_number=i + 1,
            user_input=f"Request {i+1}",
            orchestrator_output={"turn": i+1},
            context_state={"step": i+1},
            timestamp=datetime.now(),
            duration_ms=100.0,
            tokens_used=200,
            continuation_reason="CONTINUE"
        )
        state_manager.save_turn(conversation_id, turn_record)
    
    state = state_manager.load_conversation(conversation_id)
    assert len(state.turn_history) == 3
    assert state.turn_history[0].turn_number == 1
    assert state.turn_history[1].turn_number == 2
    assert state.turn_history[2].turn_number == 3


def test_list_conversations_empty(state_manager):
    """Test listing conversations when none exist."""
    conversations = state_manager.list_conversations()
    assert len(conversations) == 0


def test_list_conversations_with_data(state_manager):
    """Test listing conversations."""
    # Create multiple conversations
    id1 = state_manager.create_conversation("Orchestrator1")
    id2 = state_manager.create_conversation("Orchestrator2")
    id3 = state_manager.create_conversation("Orchestrator3")
    
    conversations = state_manager.list_conversations()
    assert len(conversations) == 3
    
    # Should be ordered by updated_at DESC (most recent first)
    assert conversations[0].conversation_id == id3
    assert conversations[1].conversation_id == id2
    assert conversations[2].conversation_id == id1


def test_list_conversations_exclude_completed(state_manager):
    """Test listing only incomplete conversations."""
    id1 = state_manager.create_conversation("Orchestrator1")
    id2 = state_manager.create_conversation("Orchestrator2")
    
    # Mark one as complete
    state = state_manager.load_conversation(id1)
    state.is_complete = True
    state_manager.update_conversation(state)
    
    # List incomplete only
    conversations = state_manager.list_conversations(include_completed=False)
    assert len(conversations) == 1
    assert conversations[0].conversation_id == id2


def test_list_conversations_limit(state_manager):
    """Test limiting conversation results."""
    for i in range(10):
        state_manager.create_conversation(f"Orchestrator{i}")
    
    conversations = state_manager.list_conversations(limit=5)
    assert len(conversations) == 5


def test_turn_record_ordering(state_manager):
    """Test that turn records are ordered by turn_number."""
    conversation_id = state_manager.create_conversation("TestOrchestrator")
    
    # Save turns out of order
    for turn_num in [3, 1, 2]:
        turn_record = TurnRecord(
            turn_number=turn_num,
            user_input=f"Turn {turn_num}",
            orchestrator_output={},
            context_state={},
            timestamp=datetime.now(),
            duration_ms=100.0,
            tokens_used=100,
            continuation_reason="CONTINUE"
        )
        state_manager.save_turn(conversation_id, turn_record)
    
    state = state_manager.load_conversation(conversation_id)
    assert state.turn_history[0].turn_number == 1
    assert state.turn_history[1].turn_number == 2
    assert state.turn_history[2].turn_number == 3


def test_context_state_json_serialization(state_manager):
    """Test that complex context state is properly serialized."""
    conversation_id = state_manager.create_conversation("TestOrchestrator")
    
    complex_context = {
        "nested": {"data": [1, 2, 3]},
        "string": "value",
        "number": 42,
        "boolean": True,
        "null_value": None
    }
    
    state = state_manager.load_conversation(conversation_id)
    state.context_state = complex_context
    state_manager.update_conversation(state)
    
    reloaded = state_manager.load_conversation(conversation_id)
    assert reloaded.context_state == complex_context


def test_conversation_timestamps(state_manager):
    """Test that created_at and updated_at timestamps work correctly."""
    conversation_id = state_manager.create_conversation("TestOrchestrator")
    
    state = state_manager.load_conversation(conversation_id)
    created_at = state.created_at
    
    # Wait a bit and update
    import time
    time.sleep(0.1)
    
    state.total_turns = 1
    state_manager.update_conversation(state)
    
    reloaded = state_manager.load_conversation(conversation_id)
    assert reloaded.created_at == created_at
    assert reloaded.updated_at > created_at
