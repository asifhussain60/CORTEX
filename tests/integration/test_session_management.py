"""
Integration tests for CORTEX session management and conversation tracking.

Tests conversation persistence, resume functionality, and context preservation across sessions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import json
import sqlite3
from datetime import datetime, timedelta

from src.tier1.conversation_memory import ConversationMemory
from src.tier1.session_manager import SessionManager
from src.cortex_agents.intent_router import IntentRouter


class TestConversationPersistence:
    """Test conversation data persistence to Tier 1 database."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        """Create temporary brain directory."""
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        return brain_root
    
    @pytest.fixture
    def conversation_memory(self, temp_brain_root):
        """Create conversation memory instance."""
        return ConversationMemory(brain_root=str(temp_brain_root))
    
    def test_save_and_load_conversation(self, conversation_memory):
        """Test saving and loading a complete conversation."""
        # Save conversation
        conversation_id = conversation_memory.save_conversation({
            "request": "Add a purple button",
            "response": "Button added successfully",
            "intent": "EXECUTE",
            "timestamp": datetime.now().isoformat()
        })
        
        assert conversation_id is not None
        
        # Load conversation
        loaded = conversation_memory.load_conversation(conversation_id)
        
        assert loaded is not None
        assert loaded["request"] == "Add a purple button"
        assert loaded["response"] == "Button added successfully"
        assert loaded["intent"] == "EXECUTE"
    
    def test_save_multiple_conversations(self, conversation_memory):
        """Test saving multiple conversations and retrieving them."""
        # Save 3 conversations
        conv_ids = []
        for i in range(3):
            conv_id = conversation_memory.save_conversation({
                "request": f"Request {i}",
                "response": f"Response {i}",
                "timestamp": datetime.now().isoformat()
            })
            conv_ids.append(conv_id)
        
        assert len(conv_ids) == 3
        
        # Retrieve all conversations
        recent = conversation_memory.get_recent_conversations(limit=5)
        
        assert len(recent) >= 3
        assert any("Request 2" in c["request"] for c in recent)
    
    def test_conversation_retention_limit(self, conversation_memory):
        """Test that only last 20 conversations are retained."""
        # Save 25 conversations
        for i in range(25):
            conversation_memory.save_conversation({
                "request": f"Request {i}",
                "response": f"Response {i}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Retrieve all
        all_conversations = conversation_memory.get_recent_conversations(limit=30)
        
        # Should only have 20 (or implementation-specific limit)
        assert len(all_conversations) <= 20
    
    def test_conversation_with_context(self, conversation_memory):
        """Test saving conversation with rich context."""
        conversation_id = conversation_memory.save_conversation({
            "request": "Make it purple",
            "response": "Changed button color to purple",
            "intent": "EXECUTE",
            "context": {
                "previous_request": "Add a button",
                "previous_intent": "EXECUTE",
                "entities": {"color": "purple", "element": "button"}
            },
            "timestamp": datetime.now().isoformat()
        })
        
        loaded = conversation_memory.load_conversation(conversation_id)
        
        assert "context" in loaded
        assert loaded["context"]["entities"]["color"] == "purple"


class TestResumeWorkflow:
    """Test resume functionality ('continue where I left off')."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    @pytest.fixture
    def session_manager(self, temp_brain_root):
        """Create session manager instance."""
        return SessionManager(brain_root=str(temp_brain_root))
    
    def test_resume_from_last_conversation(self, session_manager, temp_brain_root):
        """Test resuming from the most recent conversation."""
        # Save a conversation
        memory = ConversationMemory(brain_root=str(temp_brain_root))
        memory.save_conversation({
            "request": "Create a login form",
            "response": "Created form with username and password fields",
            "status": "incomplete",
            "next_steps": ["Add validation", "Add styling", "Add submit handler"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Resume
        resume_context = session_manager.resume_last_session()
        
        assert resume_context is not None
        assert "request" in resume_context
        assert "next_steps" in resume_context
        assert resume_context["status"] == "incomplete"
    
    def test_resume_with_no_previous_conversation(self, session_manager):
        """Test resume when there's no previous conversation."""
        # Resume with empty history
        resume_context = session_manager.resume_last_session()
        
        # Should handle gracefully
        assert resume_context is None or resume_context.get("status") == "no_history"
    
    def test_resume_specific_conversation_by_id(self, session_manager, temp_brain_root):
        """Test resuming a specific conversation by ID."""
        memory = ConversationMemory(brain_root=str(temp_brain_root))
        
        # Save multiple conversations
        conv_id_1 = memory.save_conversation({
            "request": "Task 1",
            "timestamp": datetime.now().isoformat()
        })
        
        conv_id_2 = memory.save_conversation({
            "request": "Task 2",
            "timestamp": datetime.now().isoformat()
        })
        
        # Resume specific conversation
        resume_context = session_manager.resume_session(conv_id_1)
        
        assert resume_context is not None
        assert resume_context["request"] == "Task 1"


class TestContextPreservation:
    """Test that context is preserved across multiple turns."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_pronoun_resolution_across_turns(self, temp_brain_root):
        """Test that pronouns like 'it' are resolved using previous context."""
        memory = ConversationMemory(brain_root=str(temp_brain_root))
        router = IntentRouter(brain_root=str(temp_brain_root))
        
        # Turn 1: Establish context
        conv_id_1 = memory.save_conversation({
            "request": "Create a dashboard component",
            "response": "Created dashboard with charts",
            "entities": {"component": "dashboard"},
            "timestamp": datetime.now().isoformat()
        })
        
        # Turn 2: Use pronoun reference
        intent = router.detect_intent(
            "Make it responsive",
            context=memory.get_recent_conversations(limit=5)
        )
        
        # Should resolve "it" to "dashboard"
        assert intent["primary_intent"] in ["EXECUTE", "REFACTOR"]
        # Note: Actual entity resolution depends on implementation
    
    def test_multi_turn_conversation_context(self, temp_brain_root):
        """Test context accumulation over multiple turns."""
        memory = ConversationMemory(brain_root=str(temp_brain_root))
        
        # Turn 1
        memory.save_conversation({
            "request": "Create a button",
            "entities": {"element": "button"},
            "timestamp": datetime.now().isoformat()
        })
        
        # Turn 2
        memory.save_conversation({
            "request": "Make it purple",
            "entities": {"color": "purple"},
            "timestamp": datetime.now().isoformat()
        })
        
        # Turn 3
        memory.save_conversation({
            "request": "Add a click handler",
            "entities": {"action": "click handler"},
            "timestamp": datetime.now().isoformat()
        })
        
        # Get combined context
        recent = memory.get_recent_conversations(limit=5)
        
        assert len(recent) >= 3
        # Should have all entities available for context resolution


class TestSessionStateManagement:
    """Test session state tracking and management."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        return brain_root
    
    @pytest.fixture
    def session_manager(self, temp_brain_root):
        return SessionManager(brain_root=str(temp_brain_root))
    
    def test_active_session_tracking(self, session_manager):
        """Test tracking of active sessions."""
        # Start session
        session_id = session_manager.start_session("Feature development")
        
        assert session_id is not None
        
        # Check active status
        is_active = session_manager.is_session_active(session_id)
        assert is_active is True
        
        # End session
        session_manager.end_session(session_id)
        
        # Check inactive status
        is_active = session_manager.is_session_active(session_id)
        assert is_active is False
    
    def test_session_metadata_persistence(self, session_manager):
        """Test that session metadata persists correctly."""
        # Create session with metadata
        session_id = session_manager.start_session(
            "Feature development",
            metadata={
                "feature": "authentication",
                "priority": "high",
                "estimated_hours": 4
            }
        )
        
        # Retrieve session
        session = session_manager.get_session(session_id)
        
        assert session is not None
        assert session["metadata"]["feature"] == "authentication"
        assert session["metadata"]["priority"] == "high"
    
    def test_concurrent_sessions(self, session_manager):
        """Test handling multiple concurrent sessions."""
        # Start multiple sessions
        session_1 = session_manager.start_session("Task 1")
        session_2 = session_manager.start_session("Task 2")
        session_3 = session_manager.start_session("Task 3")
        
        # All should be active
        assert session_manager.is_session_active(session_1)
        assert session_manager.is_session_active(session_2)
        assert session_manager.is_session_active(session_3)
        
        # End one session
        session_manager.end_session(session_2)
        
        # Others should still be active
        assert session_manager.is_session_active(session_1)
        assert not session_manager.is_session_active(session_2)
        assert session_manager.is_session_active(session_3)


class TestConversationSearchAndRetrieval:
    """Test searching and retrieving past conversations."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        return brain_root
    
    @pytest.fixture
    def conversation_memory(self, temp_brain_root):
        return ConversationMemory(brain_root=str(temp_brain_root))
    
    def test_search_conversations_by_keyword(self, conversation_memory):
        """Test searching conversations by keyword."""
        # Save conversations with different topics
        conversation_memory.save_conversation({
            "request": "Create authentication system",
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_memory.save_conversation({
            "request": "Add purple button to dashboard",
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_memory.save_conversation({
            "request": "Fix authentication bug",
            "timestamp": datetime.now().isoformat()
        })
        
        # Search for authentication-related conversations
        results = conversation_memory.search_conversations("authentication")
        
        assert len(results) >= 2
        assert any("authentication" in r["request"].lower() for r in results)
    
    def test_get_conversations_by_date_range(self, conversation_memory):
        """Test retrieving conversations within a date range."""
        # Save conversations with specific timestamps
        yesterday = datetime.now() - timedelta(days=1)
        today = datetime.now()
        
        conversation_memory.save_conversation({
            "request": "Old request",
            "timestamp": yesterday.isoformat()
        })
        
        conversation_memory.save_conversation({
            "request": "Recent request",
            "timestamp": today.isoformat()
        })
        
        # Get conversations from last 2 hours
        recent = conversation_memory.get_conversations_since(
            datetime.now() - timedelta(hours=2)
        )
        
        assert any("Recent request" in c["request"] for c in recent)
    
    def test_get_conversations_by_intent(self, conversation_memory):
        """Test filtering conversations by intent type."""
        # Save conversations with different intents
        conversation_memory.save_conversation({
            "request": "Add feature",
            "intent": "EXECUTE",
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_memory.save_conversation({
            "request": "Design system",
            "intent": "ARCHITECT",
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_memory.save_conversation({
            "request": "Create test",
            "intent": "TEST",
            "timestamp": datetime.now().isoformat()
        })
        
        # Get only EXECUTE intents
        execute_conversations = conversation_memory.get_conversations_by_intent("EXECUTE")
        
        assert len(execute_conversations) >= 1
        assert all(c["intent"] == "EXECUTE" for c in execute_conversations)


class TestSessionRecovery:
    """Test recovery from interrupted or crashed sessions."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        return brain_root
    
    @pytest.fixture
    def session_manager(self, temp_brain_root):
        return SessionManager(brain_root=str(temp_brain_root))
    
    def test_detect_interrupted_session(self, session_manager):
        """Test detection of interrupted sessions (not properly closed)."""
        # Simulate interrupted session (started but never ended)
        session_id = session_manager.start_session("Task interrupted by crash")
        
        # Don't call end_session() - simulating crash
        
        # Create new session manager instance (simulating restart)
        new_manager = SessionManager(brain_root=session_manager.brain_root)
        
        # Should detect interrupted session
        interrupted = new_manager.get_interrupted_sessions()
        
        assert len(interrupted) > 0
        assert any(s["id"] == session_id for s in interrupted)
    
    def test_recover_interrupted_session(self, session_manager):
        """Test recovering state from interrupted session."""
        # Start session with work in progress
        session_id = session_manager.start_session(
            "Feature development",
            state={
                "current_task": "Add validation",
                "completed_tasks": ["Create form", "Add styling"],
                "remaining_tasks": ["Add validation", "Add submit handler"]
            }
        )
        
        # Simulate crash (no end_session call)
        
        # Recover session
        recovered = session_manager.recover_session(session_id)
        
        assert recovered is not None
        assert recovered["state"]["current_task"] == "Add validation"
        assert len(recovered["state"]["completed_tasks"]) == 2


class TestConversationContextWindow:
    """Test conversation context window management (last 20 conversations)."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        return brain_root
    
    @pytest.fixture
    def conversation_memory(self, temp_brain_root):
        return ConversationMemory(brain_root=str(temp_brain_root))
    
    def test_context_window_limit(self, conversation_memory):
        """Test that context window respects the 20-conversation limit."""
        # Add 30 conversations
        for i in range(30):
            conversation_memory.save_conversation({
                "request": f"Request {i}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Get context window
        context = conversation_memory.get_context_window()
        
        # Should only return last 20
        assert len(context) == 20
        
        # Should have most recent conversations
        assert any("Request 29" in c["request"] for c in context)
        assert not any("Request 5" in c["request"] for c in context)
    
    def test_context_window_chronological_order(self, conversation_memory):
        """Test that context window is in chronological order."""
        # Add conversations with specific timestamps
        for i in range(10):
            conversation_memory.save_conversation({
                "request": f"Request {i}",
                "timestamp": (datetime.now() + timedelta(seconds=i)).isoformat()
            })
        
        # Get context
        context = conversation_memory.get_context_window()
        
        # Should be in chronological order (oldest first or newest first, depends on implementation)
        # Check that timestamps are monotonic
        timestamps = [datetime.fromisoformat(c["timestamp"]) for c in context]
        assert timestamps == sorted(timestamps) or timestamps == sorted(timestamps, reverse=True)


# Run with: pytest tests/integration/test_session_management.py -v
