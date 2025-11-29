"""
Tests for ConversationLifecycleManager - CORTEX 3.0 conversation lifecycle.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import os

from src.tier1.lifecycle import ConversationLifecycleManager, WorkflowState
from src.tier1.working_memory import WorkingMemory


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield Path(path)
    # Cleanup
    if Path(path).exists():
        Path(path).unlink()


@pytest.fixture
def lifecycle_manager(temp_db):
    """Create ConversationLifecycleManager instance."""
    return ConversationLifecycleManager(temp_db)


@pytest.fixture
def working_memory(temp_db):
    """Create WorkingMemory instance for integration tests."""
    return WorkingMemory(db_path=temp_db)


class TestConversationLifecycleManager:
    """Test suite for ConversationLifecycleManager."""
    
    def test_init_creates_schema(self, temp_db):
        """Test that initializing creates lifecycle events table."""
        manager = ConversationLifecycleManager(temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_lifecycle_events'")
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_detect_new_conversation_command(self, lifecycle_manager):
        """Test detection of 'new conversation' commands."""
        test_cases = [
            ("new conversation please", "new_conversation", 0.9),
            ("start fresh", "new_conversation", 0.9),
            ("let's begin a new topic", "new_conversation", 0.9),
            ("fresh start now", "new_conversation", 0.9),
            ("continue working", "continue", 0.85),
            ("keep going", "continue", 0.85),
            ("resume please", "continue", 0.85),
            ("add a button", "none", 0.0)
        ]
        
        for request, expected_intent, min_confidence in test_cases:
            intent, confidence = lifecycle_manager.detect_command_intent(request)
            assert intent == expected_intent
            if expected_intent != "none":
                assert confidence >= min_confidence
    
    def test_infer_workflow_state(self, lifecycle_manager):
        """Test workflow state inference from user requests."""
        test_cases = [
            ("let's plan the architecture", WorkflowState.PLANNING),
            ("how should we design this?", WorkflowState.PLANNING),
            ("add a purple button", WorkflowState.EXECUTING),
            ("create a new file", WorkflowState.EXECUTING),
            ("test this feature", WorkflowState.TESTING),
            ("review the code", WorkflowState.VALIDATING),
        ]
        
        for request, expected_state in test_cases:
            state = lifecycle_manager.infer_workflow_state(request)
            assert state == expected_state, f"For '{request}', expected {expected_state} but got {state}"
    
    def test_workflow_state_progression(self, lifecycle_manager):
        """Test default workflow state progression."""
        # PLANNING → EXECUTING
        state = lifecycle_manager.infer_workflow_state(
            "add something",
            current_state=WorkflowState.PLANNING
        )
        assert state == WorkflowState.EXECUTING
        
        # EXECUTING → TESTING
        state = lifecycle_manager.infer_workflow_state(
            "check it",
            current_state=WorkflowState.EXECUTING
        )
        assert state == WorkflowState.TESTING
        
        # TESTING → VALIDATING
        state = lifecycle_manager.infer_workflow_state(
            "inspect",
            current_state=WorkflowState.TESTING
        )
        assert state == WorkflowState.VALIDATING
        
        # VALIDATING → COMPLETE
        state = lifecycle_manager.infer_workflow_state(
            "done",
            current_state=WorkflowState.VALIDATING
        )
        assert state == WorkflowState.COMPLETE
    
    def test_should_create_conversation_no_active(self, lifecycle_manager):
        """Test should create conversation when none active."""
        should_create, reason = lifecycle_manager.should_create_conversation(
            session_id="session_1",
            user_request="add a button",
            has_active_conversation=False
        )
        
        assert should_create is True
        assert reason == "no_active_conversation"
    
    def test_should_create_conversation_explicit_new(self, lifecycle_manager):
        """Test should create when user says 'new conversation'."""
        should_create, reason = lifecycle_manager.should_create_conversation(
            session_id="session_1",
            user_request="new conversation - let's work on auth",
            has_active_conversation=True
        )
        
        assert should_create is True
        assert reason == "explicit_command"
    
    def test_should_not_create_conversation_explicit_continue(self, lifecycle_manager):
        """Test should not create when user says 'continue'."""
        should_create, reason = lifecycle_manager.should_create_conversation(
            session_id="session_1",
            user_request="continue with the button",
            has_active_conversation=True
        )
        
        assert should_create is False
        assert reason == "explicit_continue"
    
    def test_should_not_create_conversation_default_continuation(self, lifecycle_manager):
        """Test default behavior is to continue existing conversation."""
        should_create, reason = lifecycle_manager.should_create_conversation(
            session_id="session_1",
            user_request="make it bigger",
            has_active_conversation=True
        )
        
        assert should_create is False
        assert reason == "default_continuation"
    
    def test_should_close_conversation_workflow_complete(self, lifecycle_manager):
        """Test conversation closes when workflow complete."""
        should_close, reason = lifecycle_manager.should_close_conversation(
            conversation_id="conv_1",
            current_state=WorkflowState.COMPLETE
        )
        
        assert should_close is True
        assert reason == "workflow_complete"
    
    def test_should_close_conversation_new_requested(self, lifecycle_manager):
        """Test conversation closes when new conversation requested."""
        should_close, reason = lifecycle_manager.should_close_conversation(
            conversation_id="conv_1",
            current_state=WorkflowState.EXECUTING,
            user_request="new conversation please"
        )
        
        assert should_close is True
        assert reason == "new_conversation_requested"
    
    def test_log_conversation_created(self, lifecycle_manager, temp_db):
        """Test logging conversation creation."""
        lifecycle_manager.log_conversation_created(
            conversation_id="conv_test",
            session_id="session_test",
            trigger="no_active_conversation",
            initial_state=WorkflowState.PLANNING
        )
        
        # Verify event logged
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type, conversation_id, session_id, new_state, trigger
            FROM conversation_lifecycle_events
            WHERE conversation_id = ?
        """, ("conv_test",))
        
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[0] == "created"
        assert row[1] == "conv_test"
        assert row[2] == "session_test"
        assert row[3] == "PLANNING"
        assert row[4] == "no_active_conversation"
    
    def test_get_conversation_history(self, working_memory):
        """Test retrieving conversation lifecycle history."""
        # Create a conversation first using working memory
        result = working_memory.handle_user_request(
            user_request="add a button",
            workspace_path="/projects/test"
        )
        
        conv_id = result["conversation_id"]
        session_id = result["session_id"]
        
        # Progress through states
        working_memory.handle_user_request(
            user_request="create the file",
            workspace_path="/projects/test"
        )
        
        working_memory.handle_user_request(
            user_request="test the feature",
            workspace_path="/projects/test"
        )
        
        # Get history
        history = working_memory.get_conversation_lifecycle_history(conv_id)
        
        assert len(history) >= 1  # At least creation event
        assert history[0].event_type == "created"
        assert history[0].conversation_id == conv_id


class TestWorkingMemoryIntegration:
    """Integration tests for WorkingMemory with lifecycle management."""
    
    def test_handle_user_request_creates_session_and_conversation(self, working_memory):
        """Test that handle_user_request creates session and conversation."""
        result = working_memory.handle_user_request(
            user_request="add a purple button",
            workspace_path="/projects/test"
        )
        
        assert result["session_id"] is not None
        assert result["conversation_id"] is not None
        assert result["is_new_session"] is True
        assert result["is_new_conversation"] is True
        assert result["workflow_state"] == "EXECUTING"
    
    def test_handle_user_request_continues_conversation(self, working_memory):
        """Test that subsequent requests continue same conversation."""
        # First request
        result1 = working_memory.handle_user_request(
            user_request="add a button",
            workspace_path="/projects/test"
        )
        
        conv_id_1 = result1["conversation_id"]
        
        # Second request
        result2 = working_memory.handle_user_request(
            user_request="make it bigger",
            workspace_path="/projects/test"
        )
        
        # Should be same conversation
        assert result2["conversation_id"] == conv_id_1
        assert result2["is_new_conversation"] is False
        assert result2["lifecycle_event"] == "continuation"
    
    def test_handle_user_request_explicit_new_conversation(self, working_memory):
        """Test explicit 'new conversation' command creates new conversation."""
        # First request
        result1 = working_memory.handle_user_request(
            user_request="add a button",
            workspace_path="/projects/test"
        )
        
        conv_id_1 = result1["conversation_id"]
        
        # Explicit new conversation
        result2 = working_memory.handle_user_request(
            user_request="new conversation - add authentication",
            workspace_path="/projects/test"
        )
        
        # Should be different conversation
        assert result2["conversation_id"] != conv_id_1
        assert result2["is_new_conversation"] is True
        assert result2["lifecycle_event"] == "explicit_command"
    
    def test_handle_user_request_workflow_progression(self, working_memory):
        """Test workflow state progression through lifecycle."""
        # Planning
        result1 = working_memory.handle_user_request(
            user_request="let's plan the architecture",
            workspace_path="/projects/test"
        )
        assert result1["workflow_state"] == "PLANNING"
        
        # Executing
        result2 = working_memory.handle_user_request(
            user_request="create the main file",
            workspace_path="/projects/test"
        )
        assert result2["workflow_state"] == "EXECUTING"
        assert result2["conversation_id"] == result1["conversation_id"]
        
        # Testing
        result3 = working_memory.handle_user_request(
            user_request="run the tests",
            workspace_path="/projects/test"
        )
        assert result3["workflow_state"] == "TESTING"
        assert result3["conversation_id"] == result1["conversation_id"]
    
    def test_handle_user_request_with_assistant_response(self, working_memory):
        """Test storing assistant response."""
        result = working_memory.handle_user_request(
            user_request="add a button",
            workspace_path="/projects/test",
            assistant_response="I'll create that button with purple styling"
        )
        
        # Get messages
        messages = working_memory.get_messages(result["conversation_id"])
        
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "add a button"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "I'll create that button with purple styling"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
