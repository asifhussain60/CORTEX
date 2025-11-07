"""
CORTEX Tier 1: Working Memory Tests
Unit tests for short-term memory (STM) with FIFO queue.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil
from CORTEX.src.tier1.working_memory import (
    WorkingMemory,
    Conversation,
    Entity,
    EntityType
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_working_memory.db"
    yield db_path
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def working_memory(temp_db):
    """Create a WorkingMemory instance for testing."""
    return WorkingMemory(db_path=temp_db)


class TestDatabaseInitialization:
    """Test database creation and schema setup."""
    
    def test_creates_database_file(self, temp_db):
        """Test that database file is created."""
        wm = WorkingMemory(db_path=temp_db)
        assert temp_db.exists()
        wm.close()
    
    def test_creates_all_tables(self, working_memory):
        """Test that all required tables are created."""
        conn = sqlite3.connect(working_memory.db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'conversations',
            'entities',
            'conversation_entities',
            'messages'
        }
        
        assert expected_tables.issubset(tables)
        conn.close()
    
    def test_creates_indexes(self, working_memory):
        """Test that performance indexes are created."""
        conn = sqlite3.connect(working_memory.db_path)
        cursor = conn.cursor()
        
        # Get all index names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        expected_indexes = {
            'idx_conversations_created',
            'idx_conversations_active',
            'idx_entities_type',
            'idx_entities_accessed',
            'idx_messages_conversation'
        }
        
        assert expected_indexes.issubset(indexes)
        conn.close()


class TestConversationManagement:
    """Test conversation CRUD operations."""
    
    def test_adds_conversation(self, working_memory):
        """Test adding a new conversation."""
        conversation = working_memory.add_conversation(
            conversation_id="test_conv_001",
            title="Test Conversation",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        )
        
        assert conversation is not None
        assert conversation.conversation_id == "test_conv_001"
        assert conversation.title == "Test Conversation"
        assert conversation.message_count == 2
    
    def test_gets_conversation_by_id(self, working_memory):
        """Test retrieving conversation by ID."""
        # Add conversation
        working_memory.add_conversation(
            conversation_id="test_conv_002",
            title="Another Test",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        # Retrieve it
        conversation = working_memory.get_conversation("test_conv_002")
        
        assert conversation is not None
        assert conversation.conversation_id == "test_conv_002"
        assert conversation.title == "Another Test"
    
    def test_gets_recent_conversations(self, working_memory):
        """Test retrieving recent conversations in order."""
        # Add multiple conversations
        for i in range(5):
            working_memory.add_conversation(
                conversation_id=f"conv_{i}",
                title=f"Conversation {i}",
                messages=[{"role": "user", "content": f"Message {i}"}]
            )
        
        # Get recent 3
        recent = working_memory.get_recent_conversations(limit=3)
        
        assert len(recent) == 3
        # Should be in reverse chronological order (newest first)
        assert recent[0].conversation_id == "conv_4"
        assert recent[1].conversation_id == "conv_3"
        assert recent[2].conversation_id == "conv_2"
    
    def test_marks_conversation_as_active(self, working_memory):
        """Test marking a conversation as active."""
        working_memory.add_conversation(
            conversation_id="active_conv",
            title="Active Test",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        working_memory.set_active_conversation("active_conv")
        
        conversation = working_memory.get_conversation("active_conv")
        assert conversation.is_active is True
    
    def test_updates_conversation(self, working_memory):
        """Test updating conversation properties."""
        working_memory.add_conversation(
            conversation_id="update_conv",
            title="Original Title",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        working_memory.update_conversation(
            conversation_id="update_conv",
            title="Updated Title",
            summary="This is a summary"
        )
        
        conversation = working_memory.get_conversation("update_conv")
        assert conversation.title == "Updated Title"
        assert conversation.summary == "This is a summary"


class TestFIFOQueue:
    """Test FIFO queue management and eviction."""
    
    def test_stores_20_conversations_without_eviction(self, working_memory):
        """Test that 20 conversations can be stored without eviction."""
        # Add 20 conversations
        for i in range(20):
            working_memory.add_conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                messages=[{"role": "user", "content": f"Message {i}"}]
            )
        
        # All 20 should still exist
        count = working_memory.get_conversation_count()
        assert count == 20
    
    def test_evicts_oldest_when_21st_added(self, working_memory):
        """Test that oldest conversation is evicted when 21st is added."""
        # Add 20 conversations
        for i in range(20):
            working_memory.add_conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                messages=[{"role": "user", "content": f"Message {i}"}]
            )
        
        # Add 21st conversation
        working_memory.add_conversation(
            conversation_id="conv_021",
            title="Conversation 21",
            messages=[{"role": "user", "content": "Message 21"}]
        )
        
        # Should still be 20 conversations
        count = working_memory.get_conversation_count()
        assert count == 20
        
        # Oldest (conv_000) should be gone
        oldest = working_memory.get_conversation("conv_000")
        assert oldest is None
        
        # Newest should exist
        newest = working_memory.get_conversation("conv_021")
        assert newest is not None
    
    def test_never_evicts_active_conversation(self, working_memory):
        """Test that active conversation is never evicted."""
        # Add 20 conversations, mark first as active
        for i in range(20):
            working_memory.add_conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                messages=[{"role": "user", "content": f"Message {i}"}]
            )
        
        # Mark oldest as active
        working_memory.set_active_conversation("conv_000")
        
        # Add 21st conversation
        working_memory.add_conversation(
            conversation_id="conv_021",
            title="Conversation 21",
            messages=[{"role": "user", "content": "Message 21"}]
        )
        
        # Active conversation should still exist
        active = working_memory.get_conversation("conv_000")
        assert active is not None
        assert active.is_active is True
        
        # Second oldest (conv_001) should be evicted instead
        second_oldest = working_memory.get_conversation("conv_001")
        assert second_oldest is None
    
    def test_logs_eviction_events(self, working_memory):
        """Test that eviction events are logged."""
        # Add 21 conversations to trigger eviction
        for i in range(21):
            working_memory.add_conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                messages=[{"role": "user", "content": f"Message {i}"}]
            )
        
        # Check eviction log
        events = working_memory.get_eviction_log()
        assert len(events) >= 1
        assert events[0]['conversation_id'] == "conv_000"
        assert events[0]['event_type'] == "conversation_evicted"


class TestEntityExtraction:
    """Test entity extraction from conversations."""
    
    def test_extracts_file_entities(self, working_memory):
        """Test extraction of file path entities."""
        working_memory.add_conversation(
            conversation_id="file_conv",
            title="File Discussion",
            messages=[
                {"role": "user", "content": "Check `governance.yaml` and `working_memory.py`"},
                {"role": "assistant", "content": "Looking at those files now."}
            ]
        )
        
        entities = working_memory.extract_entities("file_conv")
        file_entities = [e for e in entities if e.entity_type == EntityType.FILE]
        
        assert len(file_entities) >= 2
        file_names = {e.entity_name for e in file_entities}
        assert "governance.yaml" in file_names
        assert "working_memory.py" in file_names
    
    def test_extracts_class_entities(self, working_memory):
        """Test extraction of class name entities."""
        working_memory.add_conversation(
            conversation_id="class_conv",
            title="Class Discussion",
            messages=[
                {"role": "user", "content": "The `GovernanceEngine` and `WorkingMemory` classes"},
                {"role": "assistant", "content": "Both are core components."}
            ]
        )
        
        entities = working_memory.extract_entities("class_conv")
        class_entities = [e for e in entities if e.entity_type == EntityType.CLASS]
        
        assert len(class_entities) >= 2
        class_names = {e.entity_name for e in class_entities}
        assert "GovernanceEngine" in class_names
        assert "WorkingMemory" in class_names
    
    def test_extracts_method_entities(self, working_memory):
        """Test extraction of method name entities."""
        working_memory.add_conversation(
            conversation_id="method_conv",
            title="Method Discussion",
            messages=[
                {"role": "user", "content": "Call `add_conversation()` and `extract_entities()`"},
                {"role": "assistant", "content": "Those methods are implemented."}
            ]
        )
        
        entities = working_memory.extract_entities("method_conv")
        method_entities = [e for e in entities if e.entity_type == EntityType.METHOD]
        
        assert len(method_entities) >= 2
        method_names = {e.entity_name for e in method_entities}
        assert "add_conversation" in method_names
        assert "extract_entities" in method_names
    
    def test_links_entities_to_conversations(self, working_memory):
        """Test that entities are linked to conversations."""
        working_memory.add_conversation(
            conversation_id="link_conv",
            title="Link Test",
            messages=[
                {"role": "user", "content": "Discuss `test_file.py` and `TestClass`"}
            ]
        )
        
        working_memory.extract_entities("link_conv")
        
        # Get entities for this conversation
        entities = working_memory.get_conversation_entities("link_conv")
        
        assert len(entities) >= 2


class TestSearchAndQuery:
    """Test search and query operations."""
    
    def test_searches_conversations_by_keyword(self, working_memory):
        """Test searching conversations by keyword."""
        working_memory.add_conversation(
            conversation_id="search_1",
            title="TDD Implementation",
            messages=[
                {"role": "user", "content": "Implement TDD enforcement"}
            ]
        )
        
        working_memory.add_conversation(
            conversation_id="search_2",
            title="Database Setup",
            messages=[
                {"role": "user", "content": "Create SQLite database"}
            ]
        )
        
        # Search for "TDD"
        results = working_memory.search_conversations("TDD")
        
        assert len(results) >= 1
        assert any(r.conversation_id == "search_1" for r in results)
    
    def test_finds_conversations_by_entity(self, working_memory):
        """Test finding conversations that mention a specific entity."""
        working_memory.add_conversation(
            conversation_id="entity_conv_1",
            title="Test 1",
            messages=[
                {"role": "user", "content": "Work on `governance.yaml`"}
            ]
        )
        working_memory.extract_entities("entity_conv_1")
        
        working_memory.add_conversation(
            conversation_id="entity_conv_2",
            title="Test 2",
            messages=[
                {"role": "user", "content": "Check `other_file.py`"}
            ]
        )
        working_memory.extract_entities("entity_conv_2")
        
        # Find conversations with governance.yaml
        results = working_memory.find_conversations_with_entity(
            entity_type=EntityType.FILE,
            entity_name="governance.yaml"
        )
        
        assert len(results) >= 1
        assert any(r.conversation_id == "entity_conv_1" for r in results)
    
    def test_gets_conversations_by_date_range(self, working_memory):
        """Test retrieving conversations within a date range."""
        # Add conversations
        working_memory.add_conversation(
            conversation_id="date_conv",
            title="Recent",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        # Get conversations from last hour
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        results = working_memory.get_conversations_by_date_range(
            start_date=one_hour_ago,
            end_date=now
        )
        
        assert len(results) >= 1
    
    def test_gets_entity_usage_statistics(self, working_memory):
        """Test getting statistics on entity usage."""
        # Add conversations with entities
        for i in range(3):
            working_memory.add_conversation(
                conversation_id=f"stat_conv_{i}",
                title=f"Test {i}",
                messages=[
                    {"role": "user", "content": "Work on `common_file.py`"}
                ]
            )
            working_memory.extract_entities(f"stat_conv_{i}")
        
        # Get entity stats
        stats = working_memory.get_entity_statistics()
        
        # common_file.py should appear 3 times
        common_file_stats = next(
            (s for s in stats if s['entity_name'] == 'common_file.py'),
            None
        )
        
        assert common_file_stats is not None
        assert common_file_stats['conversation_count'] >= 3


class TestMessagesStorage:
    """Test message storage and retrieval."""
    
    def test_stores_all_messages(self, working_memory):
        """Test that all messages are stored with conversation."""
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
            {"role": "assistant", "content": "Second response"}
        ]
        
        working_memory.add_conversation(
            conversation_id="msg_conv",
            title="Message Test",
            messages=messages
        )
        
        # Retrieve messages
        retrieved_messages = working_memory.get_messages("msg_conv")
        
        assert len(retrieved_messages) == 4
        assert retrieved_messages[0]['role'] == 'user'
        assert retrieved_messages[0]['content'] == 'First message'
        assert retrieved_messages[3]['role'] == 'assistant'
    
    def test_appends_new_messages(self, working_memory):
        """Test appending new messages to existing conversation."""
        working_memory.add_conversation(
            conversation_id="append_conv",
            title="Append Test",
            messages=[{"role": "user", "content": "Initial"}]
        )
        
        # Append new messages
        working_memory.add_messages(
            conversation_id="append_conv",
            messages=[
                {"role": "assistant", "content": "Response"},
                {"role": "user", "content": "Follow-up"}
            ]
        )
        
        # Should have 3 messages total
        messages = working_memory.get_messages("append_conv")
        assert len(messages) == 3
        
        # Conversation message count should be updated
        conversation = working_memory.get_conversation("append_conv")
        assert conversation.message_count == 3
