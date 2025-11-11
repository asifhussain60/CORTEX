"""
Unit tests for MessageStore module.
"""

import pytest
from src.tier1.messages import MessageStore


@pytest.fixture
def store(tmp_path):
    """Create a MessageStore instance with temp database."""
    db_path = tmp_path / "test.db"
    return MessageStore(db_path)


class TestAddMessages:
    """Tests for adding messages."""
    
    def test_add_single_message(self, store):
        """Test adding a single message."""
        messages = [{"role": "user", "content": "Hello"}]
        store.add_messages("conv-1", messages)
        
        retrieved = store.get_messages("conv-1")
        assert len(retrieved) == 1
        assert retrieved[0]["role"] == "user"
        assert retrieved[0]["content"] == "Hello"
    
    def test_add_multiple_messages(self, store):
        """Test adding multiple messages at once."""
        messages = [
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Answer"}
        ]
        store.add_messages("conv-2", messages)
        
        retrieved = store.get_messages("conv-2")
        assert len(retrieved) == 2
    
    def test_add_messages_to_different_conversations(self, store):
        """Test that messages are isolated by conversation."""
        store.add_messages("conv-a", [{"role": "user", "content": "A"}])
        store.add_messages("conv-b", [{"role": "user", "content": "B"}])
        
        messages_a = store.get_messages("conv-a")
        messages_b = store.get_messages("conv-b")
        
        assert len(messages_a) == 1
        assert len(messages_b) == 1
        assert messages_a[0]["content"] == "A"
        assert messages_b[0]["content"] == "B"


class TestGetMessages:
    """Tests for retrieving messages."""
    
    def test_get_messages_preserves_order(self, store):
        """Test that messages are returned in insertion order."""
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Second"},
            {"role": "user", "content": "Third"}
        ]
        store.add_messages("conv-1", messages)
        
        retrieved = store.get_messages("conv-1")
        assert retrieved[0]["content"] == "First"
        assert retrieved[1]["content"] == "Second"
        assert retrieved[2]["content"] == "Third"
    
    def test_get_messages_empty_conversation(self, store):
        """Test getting messages from nonexistent conversation."""
        messages = store.get_messages("nonexistent")
        assert messages == []
    
    def test_get_messages_includes_all_fields(self, store):
        """Test that all message fields are preserved."""
        messages = [{
            "role": "system",
            "content": "You are helpful",
            "name": "system-prompt"
        }]
        store.add_messages("conv-1", messages)
        
        retrieved = store.get_messages("conv-1")
        assert retrieved[0]["role"] == "system"
        assert retrieved[0]["content"] == "You are helpful"
        assert retrieved[0]["name"] == "system-prompt"


class TestGetMessageCount:
    """Tests for getting message counts."""
    
    def test_count_after_adding_messages(self, store):
        """Test that count reflects added messages."""
        store.add_messages("conv-1", [
            {"role": "user", "content": "1"},
            {"role": "assistant", "content": "2"}
        ])
        
        count = store.get_message_count("conv-1")
        assert count == 2
    
    def test_count_empty_conversation(self, store):
        """Test count for nonexistent conversation."""
        count = store.get_message_count("nonexistent")
        assert count == 0
    
    def test_count_after_multiple_adds(self, store):
        """Test count accumulates across multiple adds."""
        store.add_messages("conv-1", [{"role": "user", "content": "1"}])
        store.add_messages("conv-1", [{"role": "assistant", "content": "2"}])
        
        count = store.get_message_count("conv-1")
        assert count == 2


class TestDeleteMessages:
    """Tests for deleting messages."""
    
    def test_delete_removes_all_messages(self, store):
        """Test that delete removes all conversation messages."""
        store.add_messages("conv-1", [
            {"role": "user", "content": "Test 1"},
            {"role": "assistant", "content": "Test 2"}
        ])
        
        store.delete_messages("conv-1")
        
        messages = store.get_messages("conv-1")
        count = store.get_message_count("conv-1")
        
        assert messages == []
        assert count == 0
    
    def test_delete_nonexistent_conversation(self, store):
        """Test deleting from nonexistent conversation."""
        # Should not raise error
        store.delete_messages("nonexistent")
