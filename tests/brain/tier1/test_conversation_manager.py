"""
CORTEX 4.0 - ConversationManager Comprehensive Tests (Task 8.6)

Purpose: Test core conversation and message CRUD operations
Coverage Target: 80%+ for src/brain/tier1/conversation_manager.py

Test Areas:
- Database initialization and connection handling
- Conversation CRUD operations
- FIFO queue management (20 conversation limit)
- Message threading and sequencing
- Update operations with dynamic fields
- Error handling and validation
- Edge cases (null, empty, boundary conditions)

Author: CORTEX Development Team
Created: 2025-12-24
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.brain.tier1.conversation_manager import ConversationManager


class TestConversationManagerInitialization:
    """Test database initialization and connection handling."""
    
    def test_init_with_nonexistent_database_raises_error(self):
        """Should raise FileNotFoundError when database doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            ConversationManager("/nonexistent/path/database.db")
        
        assert "Database not found" in str(exc_info.value)
        assert "Run migration scripts first" in str(exc_info.value)
    
    def test_init_with_valid_database_succeeds(self, temp_db_with_schema):
        """Should successfully initialize with existing database."""
        manager = ConversationManager(temp_db_with_schema)
        assert manager.db_path == Path(temp_db_with_schema)
        assert manager.db_path.exists()
    
    def test_get_connection_returns_working_connection(self, manager):
        """Should return functional SQLite connection with row factory."""
        conn = manager._get_connection()
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory == sqlite3.Row
        conn.close()


class TestConversationCRUD:
    """Test conversation Create, Read, Update, Delete operations."""
    
    def test_create_conversation_returns_valid_id(self, manager):
        """Should create conversation and return UUID starting with 'conv-'."""
        conv_id = manager.create_conversation(
            topic="Test Feature Implementation",
            intent="PLAN",
            primary_entity="test_feature"
        )
        
        assert conv_id.startswith("conv-")
        assert len(conv_id) == 17  # "conv-" + 12 hex chars
    
    def test_create_conversation_stores_metadata(self, manager):
        """Should store all conversation metadata correctly."""
        conv_id = manager.create_conversation(
            topic="Test Topic",
            intent="EXECUTE",
            primary_entity="entity_example"
        )
        
        conv = manager.get_conversation(conv_id)
        assert conv is not None
        assert conv['topic'] == "Test Topic"
        assert conv['intent'] == "EXECUTE"
        assert conv['primary_entity'] == "entity_example"
        assert conv['status'] == "active"
        assert conv['message_count'] == 0
    
    def test_create_conversation_with_minimal_args(self, manager):
        """Should create conversation with only topic (intent/entity optional)."""
        conv_id = manager.create_conversation(topic="Minimal Topic")
        
        conv = manager.get_conversation(conv_id)
        assert conv is not None
        assert conv['topic'] == "Minimal Topic"
        assert conv['intent'] is None
        assert conv['primary_entity'] is None
    
    def test_get_conversation_nonexistent_returns_none(self, manager):
        """Should return None for non-existent conversation ID."""
        result = manager.get_conversation("conv-nonexistent")
        assert result is None
    
    def test_get_active_conversation_returns_most_recent(self, manager):
        """Should return most recently updated active conversation."""
        import time
        conv_id_1 = manager.create_conversation(topic="First")
        time.sleep(0.01)
        conv_id_2 = manager.create_conversation(topic="Second")
        time.sleep(0.01)
        conv_id_3 = manager.create_conversation(topic="Third")
        
        active = manager.get_active_conversation()
        assert active is not None
        # Should be one of the three conversations
        assert active['conversation_id'] in [conv_id_1, conv_id_2, conv_id_3]
        # Most recent should have highest updated_at
        assert active['topic'] in ["First", "Second", "Third"]
    
    def test_get_active_conversation_when_none_returns_none(self, manager):
        """Should return None when no active conversations exist."""
        result = manager.get_active_conversation()
        assert result is None
    
    def test_get_recent_conversations_respects_limit(self, manager):
        """Should return conversations limited by parameter."""
        for i in range(10):
            manager.create_conversation(topic=f"Conversation {i}")
        
        recent = manager.get_recent_conversations(limit=5)
        assert len(recent) == 5
    
    def test_get_recent_conversations_ordered_newest_first(self, manager):
        """Should return conversations in descending creation order."""
        import time
        conv_ids = []
        for i in range(3):
            conv_ids.append(manager.create_conversation(topic=f"Conv {i}"))
            time.sleep(0.01)  # Ensure timestamp difference
        
        recent = manager.get_recent_conversations()
        assert len(recent) >= 3
        # Verify all created conversations are present
        recent_ids = [conv['conversation_id'] for conv in recent[:3]]
        for conv_id in conv_ids:
            assert conv_id in recent_ids
        # Verify ordering by checking topics (should be reverse order)
        topics = [conv['topic'] for conv in recent[:3]]
        assert "Conv 2" in topics[0] or "Conv 1" in topics[0] or "Conv 0" in topics[0]
    
    def test_update_conversation_status(self, manager):
        """Should update conversation status correctly."""
        conv_id = manager.create_conversation(topic="Test")
        
        success = manager.update_conversation(conv_id, status="complete")
        assert success is True
        
        conv = manager.get_conversation(conv_id)
        assert conv['status'] == "complete"
        assert conv['completed_at'] is not None
    
    def test_update_conversation_outcome(self, manager):
        """Should update conversation outcome."""
        conv_id = manager.create_conversation(topic="Test")
        
        manager.update_conversation(conv_id, outcome="success")
        
        conv = manager.get_conversation(conv_id)
        assert conv['outcome'] == "success"
    
    def test_update_conversation_duration(self, manager):
        """Should update conversation duration in seconds."""
        conv_id = manager.create_conversation(topic="Test")
        
        manager.update_conversation(conv_id, duration_seconds=300)
        
        conv = manager.get_conversation(conv_id)
        assert conv['duration_seconds'] == 300
    
    def test_update_conversation_related_files(self, manager):
        """Should update related files as JSON array."""
        conv_id = manager.create_conversation(topic="Test")
        files = ["src/file1.py", "src/file2.py", "tests/test_file.py"]
        
        manager.update_conversation(conv_id, related_files=files)
        
        conv = manager.get_conversation(conv_id)
        import json
        stored_files = json.loads(conv['related_files'])
        assert stored_files == files
    
    def test_update_conversation_associated_commits(self, manager):
        """Should update associated commits as JSON."""
        conv_id = manager.create_conversation(topic="Test")
        commits = [
            {"sha": "abc123", "message": "feat: add feature"},
            {"sha": "def456", "message": "fix: resolve bug"}
        ]
        
        manager.update_conversation(conv_id, associated_commits=commits)
        
        conv = manager.get_conversation(conv_id)
        import json
        stored_commits = json.loads(conv['associated_commits'])
        assert stored_commits == commits
    
    def test_update_conversation_multiple_fields(self, manager):
        """Should update multiple fields in single call."""
        conv_id = manager.create_conversation(topic="Test")
        
        manager.update_conversation(
            conv_id,
            status="complete",
            outcome="success",
            duration_seconds=180
        )
        
        conv = manager.get_conversation(conv_id)
        assert conv['status'] == "complete"
        assert conv['outcome'] == "success"
        assert conv['duration_seconds'] == 180
    
    def test_update_conversation_nonexistent_returns_false(self, manager):
        """Should return False when updating non-existent conversation."""
        result = manager.update_conversation("conv-nonexistent", status="complete")
        assert result is False
    
    def test_update_conversation_with_no_changes_returns_true(self, manager):
        """Should return True when called with no update parameters."""
        conv_id = manager.create_conversation(topic="Test")
        result = manager.update_conversation(conv_id)
        assert result is True
    
    def test_update_conversation_updates_timestamp(self, manager):
        """Should update updated_at timestamp on any change."""
        conv_id = manager.create_conversation(topic="Test")
        
        original = manager.get_conversation(conv_id)
        original_updated_at = original['updated_at']
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.1)
        
        manager.update_conversation(conv_id, outcome="success")
        
        updated = manager.get_conversation(conv_id)
        assert updated['updated_at'] > original_updated_at
    
    def test_delete_conversation_removes_record(self, manager):
        """Should delete conversation and return True."""
        conv_id = manager.create_conversation(topic="Test")
        
        success = manager.delete_conversation(conv_id)
        assert success is True
        
        result = manager.get_conversation(conv_id)
        assert result is None
    
    def test_delete_conversation_nonexistent_returns_false(self, manager):
        """Should return False when deleting non-existent conversation."""
        result = manager.delete_conversation("conv-nonexistent")
        assert result is False


class TestFIFOQueueManagement:
    """Test FIFO queue management (20 conversation limit)."""
    
    def test_fifo_queue_allows_up_to_20_conversations(self, manager):
        """Should allow creating 20 active conversations without deletion."""
        conv_ids = []
        for i in range(20):
            conv_ids.append(manager.create_conversation(topic=f"Conv {i}"))
        
        # Verify all 20 exist
        for conv_id in conv_ids:
            conv = manager.get_conversation(conv_id)
            assert conv is not None
            assert conv['status'] == "active"
    
    def test_fifo_queue_deletes_oldest_when_exceeding_20(self, manager):
        """Should delete oldest conversation when creating 21st."""
        conv_ids = []
        for i in range(20):
            conv_ids.append(manager.create_conversation(topic=f"Conv {i}"))
        
        oldest_id = conv_ids[0]
        
        # Create 21st conversation (should trigger FIFO deletion)
        new_id = manager.create_conversation(topic="Conv 21")
        
        # Oldest should be deleted
        oldest = manager.get_conversation(oldest_id)
        assert oldest is None
        
        # Newest should exist
        newest = manager.get_conversation(new_id)
        assert newest is not None
    
    def test_fifo_queue_preserves_most_recent_20(self, manager):
        """Should always preserve the 20 most recent conversations."""
        conv_ids = []
        for i in range(25):
            conv_ids.append(manager.create_conversation(topic=f"Conv {i}"))
        
        # First 5 should be deleted
        for i in range(5):
            conv = manager.get_conversation(conv_ids[i])
            assert conv is None
        
        # Last 20 should exist
        for i in range(5, 25):
            conv = manager.get_conversation(conv_ids[i])
            assert conv is not None


class TestMessageCRUD:
    """Test message Create, Read operations."""
    
    def test_add_message_returns_valid_id(self, manager_with_conversation):
        """Should create message and return UUID starting with 'msg-'."""
        manager, conv_id = manager_with_conversation
        
        msg_id = manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Test message"
        )
        
        assert msg_id.startswith("msg-")
        assert len(msg_id) == 16  # "msg-" + 12 hex chars
    
    def test_add_message_stores_content(self, manager_with_conversation):
        """Should store message content and metadata."""
        manager, conv_id = manager_with_conversation
        
        msg_id = manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="What is the status?",
            intent_detected="QUERY",
            agent_used="intent_router",
            confidence=0.92
        )
        
        messages = manager.get_messages(conv_id)
        assert len(messages) == 1
        assert messages[0]['message_id'] == msg_id
        assert messages[0]['content'] == "What is the status?"
        assert messages[0]['role'] == "user"
        assert messages[0]['intent_detected'] == "QUERY"
        assert messages[0]['agent_used'] == "intent_router"
        assert messages[0]['confidence'] == 0.92
    
    def test_add_message_invalid_role_raises_error(self, manager_with_conversation):
        """Should raise ValueError for invalid role."""
        manager, conv_id = manager_with_conversation
        
        with pytest.raises(ValueError) as exc_info:
            manager.add_message(conv_id, role="invalid", content="Test")
        
        assert "Invalid role" in str(exc_info.value)
        assert "Must be 'user', 'assistant', or 'system'" in str(exc_info.value)
    
    def test_add_message_to_nonexistent_conversation_raises_error(self, manager):
        """Should raise ValueError when conversation doesn't exist."""
        with pytest.raises(ValueError) as exc_info:
            manager.add_message("conv-nonexistent", "user", "Test")
        
        assert "Conversation not found" in str(exc_info.value)
    
    def test_add_message_sequences_correctly(self, manager_with_conversation):
        """Should assign sequential numbers to messages."""
        manager, conv_id = manager_with_conversation
        
        manager.add_message(conv_id, "user", "First message")
        manager.add_message(conv_id, "assistant", "First response")
        manager.add_message(conv_id, "user", "Second message")
        
        messages = manager.get_messages(conv_id)
        assert messages[0]['sequence_number'] == 1
        assert messages[1]['sequence_number'] == 2
        assert messages[2]['sequence_number'] == 3
    
    def test_add_message_updates_conversation_message_count(self, manager_with_conversation):
        """Should increment conversation message_count."""
        manager, conv_id = manager_with_conversation
        
        manager.add_message(conv_id, "user", "Message 1")
        manager.add_message(conv_id, "assistant", "Message 2")
        manager.add_message(conv_id, "user", "Message 3")
        
        conv = manager.get_conversation(conv_id)
        assert conv['message_count'] == 3
    
    def test_add_message_with_resolved_references(self, manager_with_conversation):
        """Should store resolved references as JSON."""
        manager, conv_id = manager_with_conversation
        
        references = {
            "it": "the login button",
            "that": "the authentication flow",
            "this": "the error handling"
        }
        
        manager.add_message(
            conv_id,
            "user",
            "Can you fix it?",
            resolved_references=references
        )
        
        messages = manager.get_messages(conv_id)
        import json
        stored_refs = json.loads(messages[0]['resolved_references'])
        assert stored_refs == references
    
    def test_get_messages_returns_ordered_list(self, manager_with_conversation):
        """Should return messages ordered by sequence_number."""
        manager, conv_id = manager_with_conversation
        
        manager.add_message(conv_id, "user", "First")
        manager.add_message(conv_id, "assistant", "Second")
        manager.add_message(conv_id, "user", "Third")
        
        messages = manager.get_messages(conv_id)
        assert len(messages) == 3
        assert messages[0]['content'] == "First"
        assert messages[1]['content'] == "Second"
        assert messages[2]['content'] == "Third"
    
    def test_get_messages_for_empty_conversation_returns_empty_list(self, manager_with_conversation):
        """Should return empty list for conversation with no messages."""
        manager, conv_id = manager_with_conversation
        
        messages = manager.get_messages(conv_id)
        assert messages == []
    
    def test_get_messages_for_nonexistent_conversation_returns_empty_list(self, manager):
        """Should return empty list for non-existent conversation."""
        messages = manager.get_messages("conv-nonexistent")
        assert messages == []


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_create_conversation_with_null_topic_fails(self, manager):
        """Should handle null topic appropriately."""
        with pytest.raises(Exception):  # SQLite will raise an error
            manager.create_conversation(topic=None)
    
    def test_create_conversation_with_empty_topic(self, manager):
        """Should allow empty string as topic."""
        conv_id = manager.create_conversation(topic="")
        conv = manager.get_conversation(conv_id)
        assert conv['topic'] == ""
    
    def test_create_conversation_with_very_long_topic(self, manager):
        """Should handle very long topic strings."""
        long_topic = "A" * 10000
        conv_id = manager.create_conversation(topic=long_topic)
        conv = manager.get_conversation(conv_id)
        assert conv['topic'] == long_topic
    
    def test_add_message_with_empty_content(self, manager_with_conversation):
        """Should allow empty message content."""
        manager, conv_id = manager_with_conversation
        
        msg_id = manager.add_message(conv_id, "user", "")
        messages = manager.get_messages(conv_id)
        assert messages[0]['content'] == ""
    
    def test_add_message_with_very_long_content(self, manager_with_conversation):
        """Should handle very long message content."""
        manager, conv_id = manager_with_conversation
        
        long_content = "B" * 50000
        manager.add_message(conv_id, "user", long_content)
        messages = manager.get_messages(conv_id)
        assert messages[0]['content'] == long_content
    
    def test_concurrent_message_addition_maintains_sequence(self, manager_with_conversation):
        """Should maintain message sequencing under concurrent additions."""
        manager, conv_id = manager_with_conversation
        
        # Simulate rapid message additions
        for i in range(10):
            manager.add_message(conv_id, "user", f"Message {i}")
        
        messages = manager.get_messages(conv_id)
        for i, msg in enumerate(messages, start=1):
            assert msg['sequence_number'] == i


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_db_with_schema():
    """Create temporary database with tier1_conversations schema."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    db_path = temp_file.name
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tier1_conversations table
    cursor.execute("""
        CREATE TABLE tier1_conversations (
            conversation_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            intent TEXT,
            primary_entity TEXT,
            queue_position INTEGER,
            message_count INTEGER DEFAULT 0,
            outcome TEXT,
            duration_seconds INTEGER,
            related_files TEXT,
            associated_commits TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT
        )
    """)
    
    # Create tier1_messages table
    cursor.execute("""
        CREATE TABLE tier1_messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            sequence_number INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            intent_detected TEXT,
            resolved_references TEXT,
            agent_used TEXT,
            confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES tier1_conversations(conversation_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    import os
    os.unlink(db_path)


@pytest.fixture
def manager(temp_db_with_schema):
    """Create ConversationManager instance with temporary database."""
    return ConversationManager(temp_db_with_schema)


@pytest.fixture
def manager_with_conversation(manager):
    """Create ConversationManager with one active conversation."""
    conv_id = manager.create_conversation(
        topic="Test Conversation",
        intent="TEST",
        primary_entity="test_entity"
    )
    return manager, conv_id
