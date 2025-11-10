"""
CORTEX Tier 1: Conversation Manager Tests
Unit tests for ConversationManager class

Tests cover:
- Database initialization and schema creation
- CRUD operations for conversations
- Message management
- Entity tracking
- File modification tracking
- FIFO queue enforcement (20 conversation limit)
- Interactive planning session management (CORTEX 2.1)
- Search and filtering functionality
- Export functionality
"""

import pytest
import sqlite3
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

from src.tier1.conversation_manager import ConversationManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_conversations.db"
    yield db_path
    # Cleanup
    if temp_dir and Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def conversation_manager(temp_db):
    """Create a ConversationManager instance for testing."""
    return ConversationManager(db_path=temp_db)


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "agent_id": "intent_detector",
        "goal": "Test conversation goal",
        "context": {"test": "data", "version": "1.0"}
    }


@pytest.fixture
def sample_planning_session():
    """Sample planning session data for testing."""
    return {
        "session_id": "plan-001",
        "user_request": "Create a new feature",
        "confidence": 0.75,
        "state": "in_progress",
        "started_at": datetime.now().isoformat(),
        "questions": [
            {
                "id": "q1",
                "text": "What should the feature do?",
                "type": "open",
                "priority": 5,
                "context": {}
            }
        ],
        "answers": [
            {
                "question_id": "q1",
                "value": "Add authentication",
                "timestamp": datetime.now().isoformat(),
                "additional_context": {}
            }
        ],
        "metadata": {"version": "2.1"}
    }


# ============================================================================
# Database Initialization Tests
# ============================================================================

class TestDatabaseInitialization:
    """Test database creation and schema setup."""
    
    def test_creates_database_file(self, temp_db):
        """Test that database file is created."""
        manager = ConversationManager(db_path=temp_db)
        assert temp_db.exists()
    
    def test_creates_all_tables(self, conversation_manager):
        """Test that all required tables are created."""
        with conversation_manager._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            
            expected_tables = {
                'conversations',
                'messages',
                'entities',
                'files_modified',
                'planning_sessions',
                'planning_questions',
                'planning_answers'
            }
            
            assert expected_tables.issubset(tables)
    
    def test_creates_indexes(self, conversation_manager):
        """Test that performance indexes are created."""
        with conversation_manager._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all index names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = {row[0] for row in cursor.fetchall()}
            
            expected_indexes = {
                'idx_conv_agent',
                'idx_conv_status',
                'idx_msg_conv',
                'idx_entity_conv',
                'idx_file_conv',
                'idx_planning_session',
                'idx_planning_q_session',
                'idx_planning_a_session'
            }
            
            assert expected_indexes.issubset(indexes)
    
    def test_schema_is_idempotent(self, temp_db):
        """Test that schema creation can be called multiple times safely."""
        manager1 = ConversationManager(db_path=temp_db)
        manager2 = ConversationManager(db_path=temp_db)
        
        # Should not raise an error
        assert temp_db.exists()


# ============================================================================
# Conversation CRUD Tests
# ============================================================================

class TestConversationCRUD:
    """Test conversation create, read, update, delete operations."""
    
    def test_create_conversation(self, conversation_manager, sample_conversation_data):
        """Test creating a new conversation."""
        conv_id = conversation_manager.create_conversation(
            agent_id=sample_conversation_data["agent_id"],
            goal=sample_conversation_data["goal"],
            context=sample_conversation_data["context"]
        )
        
        assert conv_id is not None
        assert conv_id.startswith("conv-")
        assert len(conv_id) > 10  # Has timestamp and random digits
    
    def test_get_conversation(self, conversation_manager, sample_conversation_data):
        """Test retrieving a conversation by ID."""
        conv_id = conversation_manager.create_conversation(
            agent_id=sample_conversation_data["agent_id"],
            goal=sample_conversation_data["goal"]
        )
        
        conv = conversation_manager.get_conversation(conv_id)
        
        assert conv is not None
        assert conv['conversation_id'] == conv_id
        assert conv['agent_id'] == sample_conversation_data["agent_id"]
        assert conv['goal'] == sample_conversation_data["goal"]
        assert conv['status'] == 'active'
        assert 'messages' in conv
        assert 'entities' in conv
        assert 'files' in conv
    
    def test_get_nonexistent_conversation(self, conversation_manager):
        """Test retrieving a conversation that doesn't exist."""
        conv = conversation_manager.get_conversation("nonexistent-id")
        assert conv is None
    
    def test_end_conversation(self, conversation_manager, sample_conversation_data):
        """Test marking a conversation as ended."""
        conv_id = conversation_manager.create_conversation(
            agent_id=sample_conversation_data["agent_id"]
        )
        
        conversation_manager.end_conversation(
            conv_id,
            outcome="Successfully completed test"
        )
        
        conv = conversation_manager.get_conversation(conv_id)
        assert conv['status'] == 'completed'
        assert conv['outcome'] == "Successfully completed test"
        assert conv['end_time'] is not None
    
    def test_get_active_conversation(self, conversation_manager):
        """Test retrieving the active conversation for an agent."""
        agent_id = "test_agent"
        
        # Create first conversation (active)
        conv_id1 = conversation_manager.create_conversation(agent_id=agent_id)
        
        # Get active conversation
        active = conversation_manager.get_active_conversation(agent_id)
        assert active is not None
        assert active['conversation_id'] == conv_id1
        assert active['status'] == 'active'
        
        # End first conversation
        conversation_manager.end_conversation(conv_id1)
        
        # Create second conversation (new active)
        conv_id2 = conversation_manager.create_conversation(agent_id=agent_id)
        
        # Get active should return second conversation
        active = conversation_manager.get_active_conversation(agent_id)
        assert active['conversation_id'] == conv_id2
    
    def test_get_active_conversation_no_active(self, conversation_manager):
        """Test getting active conversation when none exists."""
        active = conversation_manager.get_active_conversation("nonexistent_agent")
        assert active is None
    
    def test_conversation_with_context(self, conversation_manager):
        """Test conversation with JSON context."""
        context = {"key": "value", "nested": {"data": 123}}
        conv_id = conversation_manager.create_conversation(
            agent_id="test_agent",
            context=context
        )
        
        conv = conversation_manager.get_conversation(conv_id)
        assert conv['context'] is not None


# ============================================================================
# Message Management Tests
# ============================================================================

class TestMessageManagement:
    """Test message-related functionality."""
    
    def test_add_message(self, conversation_manager):
        """Test adding a message to a conversation."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        msg_id = conversation_manager.add_message(
            conv_id,
            role="user",
            content="Hello, world!"
        )
        
        assert msg_id is not None
        assert msg_id.startswith("msg-")
    
    def test_get_messages(self, conversation_manager):
        """Test retrieving messages for a conversation."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        # Add multiple messages
        conversation_manager.add_message(conv_id, "user", "First message")
        conversation_manager.add_message(conv_id, "assistant", "Second message")
        conversation_manager.add_message(conv_id, "user", "Third message")
        
        messages = conversation_manager.get_messages(conv_id)
        
        assert len(messages) == 3
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == "First message"
        assert messages[1]['role'] == 'assistant'
        assert messages[2]['role'] == 'user'
    
    def test_message_order(self, conversation_manager):
        """Test that messages are returned in chronological order."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        msg_ids = []
        for i in range(5):
            msg_id = conversation_manager.add_message(
                conv_id, 
                "user", 
                f"Message {i}"
            )
            msg_ids.append(msg_id)
        
        messages = conversation_manager.get_messages(conv_id)
        
        assert len(messages) == 5
        for i, msg in enumerate(messages):
            assert msg['content'] == f"Message {i}"
    
    def test_message_count_update(self, conversation_manager):
        """Test that message_count is updated correctly."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        # Add 3 messages
        for i in range(3):
            conversation_manager.add_message(conv_id, "user", f"Message {i}")
        
        conv = conversation_manager.get_conversation(conv_id)
        assert conv['message_count'] == 3
    
    def test_get_messages_empty_conversation(self, conversation_manager):
        """Test getting messages from a conversation with no messages."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        messages = conversation_manager.get_messages(conv_id)
        assert messages == []


# ============================================================================
# Entity Tracking Tests
# ============================================================================

class TestEntityTracking:
    """Test entity tracking functionality."""
    
    def test_add_entity(self, conversation_manager):
        """Test adding an entity to a conversation."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        conversation_manager.add_entity(
            conv_id,
            entity_type="file",
            entity_value="test.py"
        )
        
        entities = conversation_manager.get_entities(conv_id)
        assert len(entities) == 1
        assert entities[0]['entity_type'] == 'file'
        assert entities[0]['entity_value'] == 'test.py'
    
    def test_add_multiple_entities(self, conversation_manager):
        """Test adding multiple entities."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        conversation_manager.add_entity(conv_id, "file", "test.py")
        conversation_manager.add_entity(conv_id, "intent", "CREATE")
        conversation_manager.add_entity(conv_id, "term", "authentication")
        
        entities = conversation_manager.get_entities(conv_id)
        assert len(entities) == 3
    
    def test_get_entities_by_type(self, conversation_manager):
        """Test filtering entities by type."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        conversation_manager.add_entity(conv_id, "file", "test1.py")
        conversation_manager.add_entity(conv_id, "file", "test2.py")
        conversation_manager.add_entity(conv_id, "intent", "CREATE")
        
        file_entities = conversation_manager.get_entities(conv_id, entity_type="file")
        assert len(file_entities) == 2
        assert all(e['entity_type'] == 'file' for e in file_entities)
        
        intent_entities = conversation_manager.get_entities(conv_id, entity_type="intent")
        assert len(intent_entities) == 1
        assert intent_entities[0]['entity_type'] == 'intent'
    
    def test_get_entities_empty(self, conversation_manager):
        """Test getting entities from conversation with none."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        entities = conversation_manager.get_entities(conv_id)
        assert entities == []
    
    def test_entity_timestamps(self, conversation_manager):
        """Test that entities have timestamps."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        conversation_manager.add_entity(conv_id, "file", "test.py")
        
        entities = conversation_manager.get_entities(conv_id)
        assert entities[0]['timestamp'] is not None
        # Validate timestamp format
        datetime.fromisoformat(entities[0]['timestamp'])


# ============================================================================
# File Tracking Tests
# ============================================================================

class TestFileTracking:
    """Test file modification tracking functionality."""
    
    def test_add_file(self, conversation_manager):
        """Test adding a modified file to a conversation."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        conversation_manager.add_file(
            conv_id,
            file_path="/path/to/test.py",
            operation="modified"
        )
        
        files = conversation_manager.get_files(conv_id)
        assert len(files) == 1
        assert files[0]['file_path'] == '/path/to/test.py'
        assert files[0]['operation'] == 'modified'
    
    def test_add_multiple_files(self, conversation_manager):
        """Test adding multiple files with different operations."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        conversation_manager.add_file(conv_id, "test1.py", "created")
        conversation_manager.add_file(conv_id, "test2.py", "modified")
        conversation_manager.add_file(conv_id, "test3.py", "deleted")
        
        files = conversation_manager.get_files(conv_id)
        assert len(files) == 3
    
    def test_file_operation_types(self, conversation_manager):
        """Test different file operation types."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        operations = ["created", "modified", "deleted"]
        for op in operations:
            conversation_manager.add_file(conv_id, f"file_{op}.py", op)
        
        files = conversation_manager.get_files(conv_id)
        recorded_ops = {f['operation'] for f in files}
        assert recorded_ops == set(operations)
    
    def test_get_files_empty(self, conversation_manager):
        """Test getting files from conversation with none."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        files = conversation_manager.get_files(conv_id)
        assert files == []
    
    def test_file_timestamps(self, conversation_manager):
        """Test that file records have timestamps."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        conversation_manager.add_file(conv_id, "test.py", "modified")
        
        files = conversation_manager.get_files(conv_id)
        assert files[0]['timestamp'] is not None
        datetime.fromisoformat(files[0]['timestamp'])


# ============================================================================
# FIFO Queue Tests
# ============================================================================

class TestFIFOQueue:
    """Test FIFO queue enforcement (20 conversation limit)."""
    
    def test_max_conversations_limit(self, conversation_manager):
        """Test that MAX_CONVERSATIONS constant is set correctly."""
        assert conversation_manager.MAX_CONVERSATIONS == 20
    
    def test_fifo_enforcement(self, conversation_manager):
        """Test that oldest completed conversation is deleted when limit reached."""
        # Create 20 conversations and complete them
        conv_ids = []
        for i in range(20):
            conv_id = conversation_manager.create_conversation(
                agent_id=f"agent_{i}",
                goal=f"Goal {i}"
            )
            conversation_manager.end_conversation(conv_id, f"Outcome {i}")
            conv_ids.append(conv_id)
        
        # Verify all 20 exist
        count = conversation_manager.get_conversation_count()
        assert count == 20
        
        # Create 21st conversation
        new_conv_id = conversation_manager.create_conversation(
            agent_id="agent_new",
            goal="New goal"
        )
        
        # Should still be 20 conversations
        count = conversation_manager.get_conversation_count()
        assert count == 20
        
        # First conversation should be deleted
        first_conv = conversation_manager.get_conversation(conv_ids[0])
        assert first_conv is None
        
        # New conversation should exist
        new_conv = conversation_manager.get_conversation(new_conv_id)
        assert new_conv is not None
    
    def test_fifo_preserves_active_conversations(self, conversation_manager):
        """Test that active conversations are not deleted by FIFO."""
        # Create 20 conversations, keep one active
        active_conv_id = None
        for i in range(20):
            conv_id = conversation_manager.create_conversation(
                agent_id=f"agent_{i}"
            )
            if i == 19:
                active_conv_id = conv_id
            else:
                conversation_manager.end_conversation(conv_id)
        
        # Create 21st conversation
        conversation_manager.create_conversation(agent_id="agent_new")
        
        # Active conversation should still exist
        active_conv = conversation_manager.get_conversation(active_conv_id)
        assert active_conv is not None
        assert active_conv['status'] == 'active'
    
    def test_fifo_deletes_oldest_first(self, conversation_manager):
        """Test that FIFO deletes oldest completed conversation first."""
        # Create and complete 20 conversations
        conv_ids = []
        for i in range(20):
            conv_id = conversation_manager.create_conversation(agent_id=f"agent_{i}")
            conversation_manager.end_conversation(conv_id)
            conv_ids.append(conv_id)
        
        # Create 3 more to trigger deletions
        for i in range(3):
            conversation_manager.create_conversation(agent_id=f"agent_new_{i}")
        
        # First 3 should be deleted
        for i in range(3):
            assert conversation_manager.get_conversation(conv_ids[i]) is None
        
        # 4th onwards should still exist
        assert conversation_manager.get_conversation(conv_ids[3]) is not None


# ============================================================================
# Statistics and Query Tests
# ============================================================================

class TestStatisticsAndQueries:
    """Test statistics and query functionality."""
    
    def test_get_statistics(self, conversation_manager):
        """Test getting conversation statistics."""
        # Create some conversations
        for i in range(5):
            conv_id = conversation_manager.create_conversation(agent_id=f"agent_{i}")
            if i < 3:
                conversation_manager.end_conversation(conv_id)
            # Add messages
            for j in range(i + 1):
                conversation_manager.add_message(conv_id, "user", f"Message {j}")
        
        stats = conversation_manager.get_statistics()
        
        assert stats['total_conversations'] == 5
        assert stats['active_conversations'] == 2
        assert stats['completed_conversations'] == 3
        assert stats['total_messages'] == 15  # 1+2+3+4+5
    
    def test_get_recent_conversations(self, conversation_manager):
        """Test getting recent conversations."""
        # Create conversations
        for i in range(5):
            conversation_manager.create_conversation(
                agent_id=f"agent_{i}",
                goal=f"Goal {i}"
            )
        
        recent = conversation_manager.get_recent_conversations(limit=3)
        assert len(recent) == 3
        # Should be in reverse chronological order
        assert recent[0]['title'] == "Goal 4"
    
    def test_get_conversation_count(self, conversation_manager):
        """Test getting total conversation count."""
        assert conversation_manager.get_conversation_count() == 0
        
        for i in range(5):
            conversation_manager.create_conversation(agent_id=f"agent_{i}")
        
        assert conversation_manager.get_conversation_count() == 5
    
    def test_get_message_count_all(self, conversation_manager):
        """Test getting total message count across all conversations."""
        conv1 = conversation_manager.create_conversation(agent_id="agent_1")
        conv2 = conversation_manager.create_conversation(agent_id="agent_2")
        
        for i in range(3):
            conversation_manager.add_message(conv1, "user", f"Msg {i}")
        for i in range(2):
            conversation_manager.add_message(conv2, "user", f"Msg {i}")
        
        total = conversation_manager.get_message_count()
        assert total == 5
    
    def test_get_message_count_specific(self, conversation_manager):
        """Test getting message count for specific conversation."""
        conv1 = conversation_manager.create_conversation(agent_id="agent_1")
        conv2 = conversation_manager.create_conversation(agent_id="agent_2")
        
        for i in range(3):
            conversation_manager.add_message(conv1, "user", f"Msg {i}")
        for i in range(2):
            conversation_manager.add_message(conv2, "user", f"Msg {i}")
        
        count1 = conversation_manager.get_message_count(conv1)
        count2 = conversation_manager.get_message_count(conv2)
        
        assert count1 == 3
        assert count2 == 2


# ============================================================================
# Search and Filter Tests
# ============================================================================

class TestSearchAndFilter:
    """Test search and filtering functionality."""
    
    def test_search_by_agent_id(self, conversation_manager):
        """Test searching conversations by agent ID."""
        conversation_manager.create_conversation(agent_id="agent_1")
        conversation_manager.create_conversation(agent_id="agent_1")
        conversation_manager.create_conversation(agent_id="agent_2")
        
        results = conversation_manager.search_conversations(agent_id="agent_1")
        assert len(results) == 2
        assert all(c['agent_id'] == "agent_1" for c in results)
    
    def test_search_by_date_range(self, conversation_manager):
        """Test searching conversations by date range."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        conversation_manager.create_conversation(agent_id="test_agent")
        
        # Search within range
        results = conversation_manager.search_conversations(
            start_date=yesterday,
            end_date=tomorrow
        )
        assert len(results) == 1
        
        # Search outside range
        results = conversation_manager.search_conversations(
            start_date=tomorrow,
            end_date=tomorrow + timedelta(days=1)
        )
        assert len(results) == 0
    
    def test_search_by_has_goal(self, conversation_manager):
        """Test searching conversations by goal presence."""
        conversation_manager.create_conversation(agent_id="agent_1", goal="Has goal")
        conversation_manager.create_conversation(agent_id="agent_2")
        conversation_manager.create_conversation(agent_id="agent_3", goal="")
        
        # Search for conversations with goals
        with_goal = conversation_manager.search_conversations(has_goal=True)
        assert len(with_goal) == 1
        
        # Search for conversations without goals
        without_goal = conversation_manager.search_conversations(has_goal=False)
        assert len(without_goal) == 2
    
    def test_search_multiple_criteria(self, conversation_manager):
        """Test searching with multiple criteria."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        conversation_manager.create_conversation(
            agent_id="agent_1", 
            goal="Test goal"
        )
        conversation_manager.create_conversation(
            agent_id="agent_1"
        )
        conversation_manager.create_conversation(
            agent_id="agent_2", 
            goal="Another goal"
        )
        
        results = conversation_manager.search_conversations(
            agent_id="agent_1",
            has_goal=True,
            start_date=yesterday
        )
        assert len(results) == 1
        assert results[0]['agent_id'] == "agent_1"
        assert results[0]['goal'] == "Test goal"


# ============================================================================
# Export Functionality Tests
# ============================================================================

class TestExportFunctionality:
    """Test export functionality."""
    
    def test_export_conversation_jsonl(self, conversation_manager):
        """Test exporting conversation as JSONL string."""
        conv_id = conversation_manager.create_conversation(
            agent_id="test_agent",
            goal="Test goal"
        )
        conversation_manager.add_message(conv_id, "user", "Hello")
        conversation_manager.add_entity(conv_id, "file", "test.py")
        conversation_manager.add_file(conv_id, "test.py", "created")
        
        jsonl = conversation_manager.export_conversation_jsonl(conv_id)
        
        # Parse JSON
        data = json.loads(jsonl)
        assert data['conversation_id'] == conv_id
        assert data['goal'] == "Test goal"
        assert len(data['messages']) == 1
        assert len(data['entities']) == 1
        assert len(data['files']) == 1
    
    def test_export_to_jsonl_file(self, conversation_manager, temp_db):
        """Test exporting conversation to JSONL file."""
        conv_id = conversation_manager.create_conversation(
            agent_id="test_agent",
            goal="Test export"
        )
        
        output_path = temp_db.parent / "export.jsonl"
        conversation_manager.export_to_jsonl(conv_id, output_path)
        
        assert output_path.exists()
        
        # Read and verify
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['conversation_id'] == conv_id
        assert data['goal'] == "Test export"
    
    def test_export_nonexistent_conversation(self, conversation_manager):
        """Test exporting a conversation that doesn't exist."""
        with pytest.raises(ValueError, match="Conversation not found"):
            conversation_manager.export_conversation_jsonl("nonexistent-id")
    
    def test_export_creates_directory(self, conversation_manager, temp_db):
        """Test that export creates parent directory if needed."""
        conv_id = conversation_manager.create_conversation(agent_id="test_agent")
        
        output_path = temp_db.parent / "subdir" / "export.jsonl"
        conversation_manager.export_to_jsonl(conv_id, output_path)
        
        assert output_path.exists()
        assert output_path.parent.exists()


# ============================================================================
# Interactive Planning Session Tests (CORTEX 2.1)
# ============================================================================

class TestInteractivePlanning:
    """Test interactive planning session management."""
    
    def test_save_planning_session(self, conversation_manager, sample_planning_session):
        """Test saving a planning session."""
        result = conversation_manager.save_planning_session(sample_planning_session)
        assert result is True
        
        # Verify saved
        session = conversation_manager.load_planning_session(
            sample_planning_session['session_id']
        )
        assert session is not None
        assert session['session_id'] == sample_planning_session['session_id']
    
    def test_load_planning_session(self, conversation_manager, sample_planning_session):
        """Test loading a planning session."""
        conversation_manager.save_planning_session(sample_planning_session)
        
        session = conversation_manager.load_planning_session(
            sample_planning_session['session_id']
        )
        
        assert session['session_id'] == sample_planning_session['session_id']
        assert session['user_request'] == sample_planning_session['user_request']
        assert session['confidence'] == sample_planning_session['confidence']
        assert session['state'] == sample_planning_session['state']
        assert len(session['questions']) == 1
        assert len(session['answers']) == 1
    
    def test_load_nonexistent_session(self, conversation_manager):
        """Test loading a session that doesn't exist."""
        session = conversation_manager.load_planning_session("nonexistent-id")
        assert session is None
    
    def test_list_planning_sessions(self, conversation_manager):
        """Test listing planning sessions."""
        # Create multiple sessions
        for i in range(3):
            session = {
                "session_id": f"plan-{i}",
                "user_request": f"Request {i}",
                "confidence": 0.8,
                "state": "in_progress" if i < 2 else "completed",
                "started_at": datetime.now().isoformat(),
                "questions": [],
                "answers": []
            }
            conversation_manager.save_planning_session(session)
        
        # List all
        all_sessions = conversation_manager.list_planning_sessions()
        assert len(all_sessions) == 3
        
        # List by state
        in_progress = conversation_manager.list_planning_sessions(state="in_progress")
        assert len(in_progress) == 2
        
        completed = conversation_manager.list_planning_sessions(state="completed")
        assert len(completed) == 1
    
    def test_planning_session_with_final_plan(self, conversation_manager):
        """Test planning session with final plan."""
        session = {
            "session_id": "plan-final",
            "user_request": "Create feature",
            "confidence": 0.9,
            "state": "completed",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "final_plan": {
                "steps": ["Step 1", "Step 2"],
                "estimated_time": "2 hours"
            },
            "questions": [],
            "answers": [],
            "metadata": {"version": "2.1"}
        }
        
        conversation_manager.save_planning_session(session)
        loaded = conversation_manager.load_planning_session("plan-final")
        
        assert loaded['final_plan'] is not None
        assert loaded['final_plan']['steps'] == ["Step 1", "Step 2"]
        assert loaded['metadata']['version'] == "2.1"
    
    def test_planning_session_update(self, conversation_manager, sample_planning_session):
        """Test updating an existing planning session."""
        # Save initial
        conversation_manager.save_planning_session(sample_planning_session)
        
        # Update
        sample_planning_session['state'] = 'completed'
        sample_planning_session['completed_at'] = datetime.now().isoformat()
        conversation_manager.save_planning_session(sample_planning_session)
        
        # Verify update
        session = conversation_manager.load_planning_session(
            sample_planning_session['session_id']
        )
        assert session['state'] == 'completed'
        assert session['completed_at'] is not None
    
    def test_planning_questions_order(self, conversation_manager):
        """Test that planning questions maintain priority order."""
        session = {
            "session_id": "plan-order",
            "user_request": "Test",
            "confidence": 0.8,
            "state": "in_progress",
            "started_at": datetime.now().isoformat(),
            "questions": [
                {"id": "q1", "text": "Low priority", "type": "open", "priority": 1},
                {"id": "q2", "text": "High priority", "type": "open", "priority": 5},
                {"id": "q3", "text": "Medium priority", "type": "open", "priority": 3}
            ],
            "answers": []
        }
        
        conversation_manager.save_planning_session(session)
        loaded = conversation_manager.load_planning_session("plan-order")
        
        # Should be ordered by priority (descending)
        assert loaded['questions'][0]['priority'] == 5
        assert loaded['questions'][1]['priority'] == 3
        assert loaded['questions'][2]['priority'] == 1
    
    def test_planning_answers_chronology(self, conversation_manager):
        """Test that planning answers maintain chronological order."""
        time1 = datetime.now()
        time2 = time1 + timedelta(seconds=1)
        time3 = time2 + timedelta(seconds=1)
        
        session = {
            "session_id": "plan-chrono",
            "user_request": "Test",
            "confidence": 0.8,
            "state": "in_progress",
            "started_at": time1.isoformat(),
            "questions": [
                {"id": "q1", "text": "Q1", "type": "open", "priority": 3}
            ],
            "answers": [
                {"question_id": "q1", "value": "First", "timestamp": time1.isoformat()},
                {"question_id": "q1", "value": "Third", "timestamp": time3.isoformat()},
                {"question_id": "q1", "value": "Second", "timestamp": time2.isoformat()}
            ]
        }
        
        conversation_manager.save_planning_session(session)
        loaded = conversation_manager.load_planning_session("plan-chrono")
        
        # Should be in chronological order
        assert loaded['answers'][0]['value'] == "First"
        assert loaded['answers'][1]['value'] == "Second"
        assert loaded['answers'][2]['value'] == "Third"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test integration of multiple features."""
    
    def test_full_conversation_lifecycle(self, conversation_manager):
        """Test complete conversation lifecycle."""
        # Create conversation
        conv_id = conversation_manager.create_conversation(
            agent_id="integration_test",
            goal="Complete lifecycle test"
        )
        
        # Add messages
        conversation_manager.add_message(conv_id, "user", "Start task")
        conversation_manager.add_message(conv_id, "assistant", "Starting...")
        conversation_manager.add_message(conv_id, "assistant", "Done!")
        
        # Add entities
        conversation_manager.add_entity(conv_id, "intent", "TEST")
        conversation_manager.add_entity(conv_id, "file", "test.py")
        
        # Add files
        conversation_manager.add_file(conv_id, "test.py", "created")
        
        # End conversation
        conversation_manager.end_conversation(conv_id, "Successfully completed")
        
        # Verify everything
        conv = conversation_manager.get_conversation(conv_id)
        assert conv['status'] == 'completed'
        assert conv['outcome'] == "Successfully completed"
        assert len(conv['messages']) == 3
        assert len(conv['entities']) == 2
        assert len(conv['files']) == 1
    
    def test_concurrent_conversations(self, conversation_manager):
        """Test managing multiple concurrent conversations."""
        conv1 = conversation_manager.create_conversation(agent_id="agent_1")
        conv2 = conversation_manager.create_conversation(agent_id="agent_2")
        conv3 = conversation_manager.create_conversation(agent_id="agent_3")
        
        # Add data to different conversations
        conversation_manager.add_message(conv1, "user", "Message 1")
        conversation_manager.add_message(conv2, "user", "Message 2")
        conversation_manager.add_entity(conv1, "file", "file1.py")
        conversation_manager.add_entity(conv2, "file", "file2.py")
        
        # Verify isolation
        msgs1 = conversation_manager.get_messages(conv1)
        msgs2 = conversation_manager.get_messages(conv2)
        msgs3 = conversation_manager.get_messages(conv3)
        
        assert len(msgs1) == 1
        assert len(msgs2) == 1
        assert len(msgs3) == 0
        
        assert msgs1[0]['content'] == "Message 1"
        assert msgs2[0]['content'] == "Message 2"


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_conversation_id(self, conversation_manager):
        """Test operations with invalid conversation ID."""
        # Should not raise error, just return None or empty
        conv = conversation_manager.get_conversation("invalid-id")
        assert conv is None
        
        messages = conversation_manager.get_messages("invalid-id")
        assert messages == []
    
    def test_database_path_creation(self, temp_db):
        """Test that database can be created in existing directory."""
        # SQLite requires parent directory to exist
        nested_dir = temp_db.parent / "nested" / "dir"
        nested_dir.mkdir(parents=True, exist_ok=True)
        nested_path = nested_dir / "test.db"
        
        manager = ConversationManager(db_path=nested_path)
        assert nested_path.exists()
    
    def test_context_manager_exception_handling(self, conversation_manager):
        """Test that context manager handles exceptions properly."""
        # Connection should be closed even if exception occurs
        try:
            with conversation_manager._get_connection() as conn:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Should be able to create new conversation (connection not leaked)
        conv_id = conversation_manager.create_conversation(agent_id="test")
        assert conv_id is not None
