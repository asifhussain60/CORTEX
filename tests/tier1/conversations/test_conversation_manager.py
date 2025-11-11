"""
Unit tests for ConversationManager module.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from src.tier1.working_memory import WorkingMemory


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Don't delete - let OS clean up temp files
    # if db_path.exists():
    #     db_path.unlink()


@pytest.fixture
def manager(temp_db):
    """Create a WorkingMemory instance and return its conversation_manager."""
    wm = WorkingMemory(temp_db)
    return wm.conversation_manager


class TestAddConversation:
    """Tests for adding conversations."""
    
    def test_add_conversation_creates_record(self, manager):
        """Test that add_conversation creates a conversation."""
        conv = manager.add_conversation(
            conversation_id="test-123",
            title="Test Conversation",
            tags=["test", "unit"]
        )
        
        assert conv.conversation_id == "test-123"
        assert conv.title == "Test Conversation"
        assert conv.tags == ["test", "unit"]
        assert conv.message_count == 0
        assert not conv.is_active
    
    def test_add_conversation_with_minimal_data(self, manager):
        """Test adding conversation with only required fields."""
        conv = manager.add_conversation(
            conversation_id="minimal-1",
            title="Minimal"
        )
        
        assert conv.conversation_id == "minimal-1"
        assert conv.title == "Minimal"
        assert conv.tags is None
    
    def test_add_conversation_sets_timestamps(self, manager):
        """Test that timestamps are set automatically."""
        conv = manager.add_conversation(
            conversation_id="ts-test",
            title="Timestamp Test"
        )
        
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)
        assert conv.created_at <= conv.updated_at


class TestGetConversation:
    """Tests for retrieving conversations."""
    
    def test_get_existing_conversation(self, manager):
        """Test retrieving an existing conversation."""
        manager.add_conversation("get-1", "Test Get")
        
        conv = manager.get_conversation("get-1")
        assert conv is not None
        assert conv.conversation_id == "get-1"
        assert conv.title == "Test Get"
    
    def test_get_nonexistent_conversation(self, manager):
        """Test that get returns None for nonexistent conversation."""
        conv = manager.get_conversation("does-not-exist")
        assert conv is None
    
    def test_get_conversation_includes_all_fields(self, manager):
        """Test that all fields are populated."""
        manager.add_conversation(
            "full-1",
            "Full Test",
            tags=["a", "b"]
        )
        
        conv = manager.get_conversation("full-1")
        assert conv.conversation_id == "full-1"
        assert conv.title == "Full Test"
        assert conv.tags == ["a", "b"]
        assert conv.message_count == 0
        assert not conv.is_active


class TestGetRecentConversations:
    """Tests for getting recent conversations."""
    
    def test_get_recent_orders_by_created_at(self, manager):
        """Test that conversations are ordered newest first."""
        manager.add_conversation("old", "Old Conversation")
        manager.add_conversation("new", "New Conversation")
        
        recent = manager.get_recent_conversations(limit=10)
        assert len(recent) == 2
        assert recent[0].conversation_id == "new"
        assert recent[1].conversation_id == "old"
    
    def test_get_recent_respects_limit(self, manager):
        """Test that limit parameter works."""
        for i in range(5):
            manager.add_conversation(f"conv-{i}", f"Conversation {i}")
        
        recent = manager.get_recent_conversations(limit=3)
        assert len(recent) == 3
    
    def test_get_recent_empty_database(self, manager):
        """Test with no conversations."""
        recent = manager.get_recent_conversations()
        assert recent == []


class TestSetActiveConversation:
    """Tests for setting active conversation."""
    
    def test_set_active_marks_conversation_active(self, manager):
        """Test that conversation is marked active."""
        manager.add_conversation("active-1", "Active Test")
        manager.set_active_conversation("active-1")
        
        conv = manager.get_conversation("active-1")
        assert conv.is_active
    
    def test_set_active_deactivates_others(self, manager):
        """Test that other conversations are deactivated."""
        manager.add_conversation("first", "First")
        manager.add_conversation("second", "Second")
        
        manager.set_active_conversation("first")
        manager.set_active_conversation("second")
        
        first = manager.get_conversation("first")
        second = manager.get_conversation("second")
        
        assert not first.is_active
        assert second.is_active
    
    def test_set_active_nonexistent_conversation(self, manager):
        """Test setting active on nonexistent conversation."""
        # Should not raise error
        manager.set_active_conversation("does-not-exist")


class TestUpdateConversation:
    """Tests for updating conversations."""
    
    def test_update_title(self, manager):
        """Test updating conversation title."""
        manager.add_conversation("update-1", "Original Title")
        manager.update_conversation("update-1", title="New Title")
        
        conv = manager.get_conversation("update-1")
        assert conv.title == "New Title"
    
    def test_update_summary(self, manager):
        """Test updating summary."""
        manager.add_conversation("update-2", "Test")
        manager.update_conversation("update-2", summary="New Summary")
        
        conv = manager.get_conversation("update-2")
        assert conv.summary == "New Summary"
    
    def test_update_tags(self, manager):
        """Test updating tags."""
        manager.add_conversation("update-3", "Test", tags=["old"])
        manager.update_conversation("update-3", tags=["new", "updated"])
        
        conv = manager.get_conversation("update-3")
        assert conv.tags == ["new", "updated"]
    
    def test_update_message_count(self, manager):
        """Test updating message count."""
        manager.add_conversation("update-4", "Test")
        manager.increment_message_count("update-4", count=5)
        
        conv = manager.get_conversation("update-4")
        assert conv.message_count == 5


class TestDeleteConversation:
    """Tests for deleting conversations."""
    
    def test_delete_removes_conversation(self, manager):
        """Test that conversation is removed."""
        manager.add_conversation("delete-1", "To Delete")
        manager.delete_conversation("delete-1")
        
        conv = manager.get_conversation("delete-1")
        assert conv is None
    
    def test_delete_nonexistent_conversation(self, manager):
        """Test deleting nonexistent conversation."""
        # Should not raise error
        manager.delete_conversation("does-not-exist")
