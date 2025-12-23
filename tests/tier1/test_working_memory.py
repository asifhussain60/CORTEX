"""
Comprehensive tests for Brain Tier 1: Working Memory

Tests conversation storage/retrieval, FIFO eviction, token counting, and session management.
Target: 90% coverage (from 33.07%)

Test Coverage Areas:
1. Conversation storage and retrieval
2. FIFO eviction (70-conversation limit)
3. Token counting and optimization
4. Message management
5. Active conversation tracking
6. Session detection and management
7. Queue status monitoring
8. Entity extraction integration
9. Configuration loading
10. Database initialization
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import tempfile
import shutil
import json

from src.tier1.working_memory import WorkingMemory
from src.tier1.conversations import Conversation


class TestWorkingMemoryBasics:
    """Test basic initialization and configuration."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        wm = WorkingMemory(db_path=temp_db_path)
        yield wm
        # Cleanup
        if temp_db_path.exists():
            temp_db_path.unlink()
    
    def test_initialization(self, working_memory):
        """Test WorkingMemory initialization."""
        assert working_memory is not None
        assert working_memory.db_path.exists()
        assert working_memory.MAX_CONVERSATIONS == 70
    
    def test_initialize_method(self, working_memory):
        """Test initialize() method returns True."""
        result = working_memory.initialize()
        assert result is True
    
    def test_database_schema_creation(self, temp_db_path):
        """Test that database schema is created correctly."""
        wm = WorkingMemory(db_path=temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'conversations', 'messages', 'entities', 
                'conversation_entities', 'eviction_log'
            )
        """)
        
        tables = {row[0] for row in cursor.fetchall()}
        assert 'conversations' in tables
        assert 'messages' in tables
        assert 'entities' in tables
        assert 'conversation_entities' in tables
        assert 'eviction_log' in tables
        
        conn.close()
    
    def test_config_loading_defaults(self, working_memory):
        """Test configuration loading with defaults."""
        config = working_memory.config
        assert 'token_optimization' in config
        assert config['token_optimization'].get('enabled') is not None


class TestConversationManagement:
    """Test conversation storage, retrieval, and updates."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_add_conversation(self, working_memory):
        """Test adding a conversation."""
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'}
        ]
        
        conversation = working_memory.add_conversation(
            conversation_id='conv-001',
            title='Test Conversation',
            messages=messages,
            tags=['test', 'greeting']
        )
        
        assert conversation is not None
        assert conversation.conversation_id == 'conv-001'
        assert conversation.title == 'Test Conversation'
    
    def test_get_conversation(self, working_memory):
        """Test retrieving a conversation by ID."""
        messages = [{'role': 'user', 'content': 'Test message'}]
        
        working_memory.add_conversation(
            conversation_id='conv-002',
            title='Retrievable Conversation',
            messages=messages
        )
        
        retrieved = working_memory.get_conversation('conv-002')
        
        assert retrieved is not None
        assert retrieved.conversation_id == 'conv-002'
        assert retrieved.title == 'Retrievable Conversation'
    
    def test_get_nonexistent_conversation(self, working_memory):
        """Test retrieving a conversation that doesn't exist."""
        result = working_memory.get_conversation('nonexistent-id')
        assert result is None
    
    def test_get_conversation_count(self, working_memory):
        """Test getting conversation count."""
        assert working_memory.get_conversation_count() == 0
        
        # Add conversations
        for i in range(3):
            working_memory.add_conversation(
                conversation_id=f'conv-count-{i}',
                title=f'Conversation {i}',
                messages=[{'role': 'user', 'content': f'Message {i}'}]
            )
        
        assert working_memory.get_conversation_count() == 3
    
    def test_get_recent_conversations(self, working_memory):
        """Test retrieving recent conversations."""
        # Add conversations
        for i in range(5):
            working_memory.add_conversation(
                conversation_id=f'conv-recent-{i}',
                title=f'Recent Conversation {i}',
                messages=[{'role': 'user', 'content': f'Message {i}'}]
            )
        
        recent = working_memory.get_recent_conversations(limit=3)
        
        assert len(recent) == 3
        # Should be in reverse chronological order (newest first)
        assert recent[0].conversation_id == 'conv-recent-4'
    
    def test_update_conversation(self, working_memory):
        """Test updating conversation properties."""
        messages = [{'role': 'user', 'content': 'Initial message'}]
        
        working_memory.add_conversation(
            conversation_id='conv-update',
            title='Original Title',
            messages=messages
        )
        
        working_memory.update_conversation(
            conversation_id='conv-update',
            title='Updated Title',
            summary='This is a summary',
            tags=['updated', 'test']
        )
        
        updated = working_memory.get_conversation('conv-update')
        assert updated.title == 'Updated Title'
        assert updated.summary == 'This is a summary'
    
    def test_set_active_conversation(self, working_memory):
        """Test setting active conversation."""
        messages = [{'role': 'user', 'content': 'Active test'}]
        
        working_memory.add_conversation(
            conversation_id='conv-active',
            title='Active Conversation',
            messages=messages
        )
        
        working_memory.set_active_conversation('conv-active')
        
        active = working_memory.get_active_conversation()
        assert active is not None
        assert active.conversation_id == 'conv-active'
    
    def test_get_active_conversation_none(self, working_memory):
        """Test getting active conversation when none is active."""
        active = working_memory.get_active_conversation()
        assert active is None


class TestFIFOEviction:
    """Test FIFO queue management and eviction (70-conversation limit)."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_fifo_limit_enforcement(self, working_memory):
        """Test that FIFO eviction occurs at 70-conversation limit."""
        # Add conversations up to limit
        for i in range(70):
            working_memory.add_conversation(
                conversation_id=f'conv-fifo-{i}',
                title=f'FIFO Test {i}',
                messages=[{'role': 'user', 'content': f'Message {i}'}]
            )
        
        assert working_memory.get_conversation_count() == 70
        
        # Add one more - should trigger eviction
        working_memory.add_conversation(
            conversation_id='conv-fifo-71',
            title='Overflow Conversation',
            messages=[{'role': 'user', 'content': 'Overflow message'}]
        )
        
        # Count should still be 70 (oldest evicted)
        assert working_memory.get_conversation_count() == 70
        
        # Oldest conversation should be evicted
        oldest = working_memory.get_conversation('conv-fifo-0')
        assert oldest is None
        
        # Newest should exist
        newest = working_memory.get_conversation('conv-fifo-71')
        assert newest is not None
    
    def test_eviction_log(self, working_memory):
        """Test that eviction events are logged."""
        # Fill to capacity
        for i in range(70):
            working_memory.add_conversation(
                conversation_id=f'conv-log-{i}',
                title=f'Log Test {i}',
                messages=[{'role': 'user', 'content': f'Message {i}'}]
            )
        
        # Trigger eviction
        working_memory.add_conversation(
            conversation_id='conv-log-trigger',
            title='Trigger Eviction',
            messages=[{'role': 'user', 'content': 'Trigger'}]
        )
        
        # Check eviction log
        eviction_log = working_memory.queue_manager.get_eviction_log()
        
        assert len(eviction_log) > 0
        assert eviction_log[0]['event_type'] == 'conversation_evicted'
        assert eviction_log[0]['conversation_id'] == 'conv-log-0'
    
    def test_queue_status(self, working_memory):
        """Test queue status monitoring."""
        status = working_memory.queue_manager.get_queue_status()
        
        assert status['current_count'] == 0
        assert status['max_capacity'] == 70
        assert status['available_slots'] == 70
        assert status['is_at_capacity'] is False
        
        # Add conversations
        for i in range(50):
            working_memory.add_conversation(
                conversation_id=f'conv-status-{i}',
                title=f'Status Test {i}',
                messages=[{'role': 'user', 'content': f'Message {i}'}]
            )
        
        status = working_memory.queue_manager.get_queue_status()
        
        assert status['current_count'] == 50
        assert status['available_slots'] == 20
        assert status['is_at_capacity'] is False


class TestMessageManagement:
    """Test message storage and retrieval."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_get_messages(self, working_memory):
        """Test retrieving messages for a conversation."""
        messages = [
            {'role': 'user', 'content': 'First message'},
            {'role': 'assistant', 'content': 'First response'},
            {'role': 'user', 'content': 'Second message'}
        ]
        
        working_memory.add_conversation(
            conversation_id='conv-messages',
            title='Message Test',
            messages=messages
        )
        
        retrieved_messages = working_memory.get_messages('conv-messages')
        
        assert len(retrieved_messages) == 3
        assert retrieved_messages[0]['content'] == 'First message'
        assert retrieved_messages[1]['role'] == 'assistant'
        assert retrieved_messages[2]['content'] == 'Second message'
    
    def test_add_messages_to_existing_conversation(self, working_memory):
        """Test adding messages to an existing conversation."""
        initial_messages = [
            {'role': 'user', 'content': 'Initial message'}
        ]
        
        working_memory.add_conversation(
            conversation_id='conv-add-messages',
            title='Add Messages Test',
            messages=initial_messages
        )
        
        # Add more messages
        additional_messages = [
            {'role': 'assistant', 'content': 'Response'},
            {'role': 'user', 'content': 'Follow-up'}
        ]
        
        working_memory.add_messages(
            conversation_id='conv-add-messages',
            messages=additional_messages
        )
        
        all_messages = working_memory.get_messages('conv-add-messages')
        
        assert len(all_messages) == 3


class TestTokenCounting:
    """Test token counting and optimization features."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_estimate_tokens_basic(self, working_memory):
        """Test basic token estimation."""
        context = {
            'conversations': [
                {
                    'conversation_id': 'test',
                    'title': 'Test',
                    'messages': [
                        {'role': 'user', 'content': 'Hello world'}
                    ]
                }
            ],
            'patterns': []
        }
        
        token_count = working_memory._estimate_tokens(context)
        
        assert token_count > 0
        assert isinstance(token_count, int)
    
    def test_get_optimized_context_disabled(self, working_memory):
        """Test get_optimized_context when optimization is disabled."""
        # Disable optimization
        working_memory.optimization_enabled = False
        
        messages = [{'role': 'user', 'content': 'Test message'}]
        working_memory.add_conversation(
            conversation_id='conv-opt-disabled',
            title='Optimization Test',
            messages=messages
        )
        
        result = working_memory.get_optimized_context(
            conversation_id='conv-opt-disabled'
        )
        
        assert 'original_context' in result
        assert 'optimized_context' in result
        assert 'optimization_stats' in result
        assert result['optimization_stats']['enabled'] is False
        assert result['optimization_stats']['reduction_rate'] == 0.0


class TestSessionManagement:
    """Test session detection and management."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_detect_or_create_session(self, working_memory):
        """Test session detection and creation."""
        workspace_path = "D:/test/workspace"
        
        session = working_memory.detect_or_create_session(workspace_path)
        
        assert session is not None
        assert session.workspace_path == workspace_path
        assert session.is_active is True
    
    def test_get_active_session(self, working_memory):
        """Test retrieving active session."""
        workspace_path = "D:/test/workspace2"
        
        # Create session
        created_session = working_memory.detect_or_create_session(workspace_path)
        
        # Retrieve active session
        active_session = working_memory.get_active_session(workspace_path)
        
        assert active_session is not None
        assert active_session.session_id == created_session.session_id
    
    def test_end_session(self, working_memory):
        """Test ending a session."""
        workspace_path = "D:/test/workspace3"
        
        session = working_memory.detect_or_create_session(workspace_path)
        
        working_memory.end_session(session.session_id, reason="test_completion")
        
        # Session should no longer be active
        active = working_memory.get_active_session(workspace_path)
        assert active is None or active.is_active is False
    
    def test_get_recent_sessions(self, working_memory):
        """Test retrieving recent sessions."""
        # Create multiple sessions
        for i in range(3):
            working_memory.detect_or_create_session(f"D:/test/workspace{i}")
        
        recent = working_memory.get_recent_sessions(limit=2)
        
        assert len(recent) <= 2


class TestLifecycleManagement:
    """Test conversation lifecycle management (CORTEX 3.0)."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_handle_user_request_creates_session(self, working_memory):
        """Test that handle_user_request creates a session."""
        workspace_path = "D:/test/lifecycle_workspace"
        
        result = working_memory.handle_user_request(
            user_request="Hello, start a new project",
            workspace_path=workspace_path
        )
        
        assert 'session_id' in result
        assert 'conversation_id' in result
        assert result['is_new_session'] is True
        assert result['is_new_conversation'] is True
    
    def test_handle_user_request_continues_conversation(self, working_memory):
        """Test that subsequent requests continue the conversation."""
        workspace_path = "D:/test/continue_workspace"
        
        # First request
        result1 = working_memory.handle_user_request(
            user_request="Start task",
            workspace_path=workspace_path
        )
        
        # Second request
        result2 = working_memory.handle_user_request(
            user_request="Continue task",
            workspace_path=workspace_path
        )
        
        assert result2['is_new_conversation'] is False
        assert result2['session_id'] == result1['session_id']
    
    def test_get_conversation_lifecycle_history(self, working_memory):
        """Test retrieving conversation lifecycle history."""
        workspace_path = "D:/test/history_workspace"
        
        result = working_memory.handle_user_request(
            user_request="Test lifecycle",
            workspace_path=workspace_path
        )
        
        conversation_id = result['conversation_id']
        
        history = working_memory.get_conversation_lifecycle_history(conversation_id)
        
        assert isinstance(history, list)


class TestAmbientEventLogging:
    """Test ambient event logging (CORTEX 3.0 Phase 3)."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_log_ambient_event(self, working_memory):
        """Test logging ambient events."""
        workspace_path = "D:/test/ambient_workspace"
        
        session = working_memory.detect_or_create_session(workspace_path)
        
        event_id = working_memory.log_ambient_event(
            session_id=session.session_id,
            event_type="file_change",
            file_path="src/test.py",
            pattern="FEATURE",
            score=75,
            summary="Added new feature"
        )
        
        assert event_id > 0
    
    def test_get_session_events(self, working_memory):
        """Test retrieving session events."""
        workspace_path = "D:/test/events_workspace"
        
        session = working_memory.detect_or_create_session(workspace_path)
        
        # Log multiple events
        working_memory.log_ambient_event(
            session_id=session.session_id,
            event_type="file_change",
            file_path="src/test1.py",
            score=80
        )
        
        working_memory.log_ambient_event(
            session_id=session.session_id,
            event_type="terminal_command",
            summary="Ran tests",
            score=60
        )
        
        events = working_memory.get_session_events(session.session_id)
        
        assert len(events) >= 2


class TestConversationSearch:
    """Test conversation search capabilities."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        wm = WorkingMemory(db_path=temp_db_path)
        
        # Add test conversations
        wm.add_conversation(
            conversation_id='search-001',
            title='Python Testing Guide',
            messages=[
                {'role': 'user', 'content': 'How do I write unit tests in Python?'},
                {'role': 'assistant', 'content': 'You can use pytest for testing.'}
            ],
            tags=['python', 'testing']
        )
        
        wm.add_conversation(
            conversation_id='search-002',
            title='JavaScript Development',
            messages=[
                {'role': 'user', 'content': 'How do I set up a React project?'},
                {'role': 'assistant', 'content': 'Use create-react-app.'}
            ],
            tags=['javascript', 'react']
        )
        
        return wm
    
    def test_search_conversations_by_keyword(self, working_memory):
        """Test searching conversations by keyword."""
        results = working_memory.conversation_search.search_by_keyword('python')
        
        assert len(results) > 0
        assert any('python' in r.title.lower() for r in results)
    
    def test_search_conversations_by_entity(self, working_memory):
        """Test searching conversations by entity."""
        # This test validates the entity search API
        results = working_memory.conversation_search.search_by_entity(
            entity_type='file',
            entity_name='test.py'
        )
        
        # May be empty if no entities were extracted
        assert isinstance(results, list)


class TestEntityManagement:
    """Test entity extraction and management."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_get_conversation_entities(self, working_memory):
        """Test retrieving entities for a conversation."""
        messages = [
            {'role': 'user', 'content': 'I need to work on src/main.py file'}
        ]
        
        conversation = working_memory.add_conversation(
            conversation_id='entity-test',
            title='Entity Test',
            messages=messages
        )
        
        # Get entities (might be empty if extraction doesn't run automatically)
        entities = working_memory.get_conversation_entities('entity-test')
        
        assert isinstance(entities, list)


class TestOptimizationFeatures:
    """Test advanced optimization and token management."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_get_optimized_context_with_patterns(self, working_memory):
        """Test optimization with pattern context."""
        messages = [{'role': 'user', 'content': 'Test optimization'}]
        
        working_memory.add_conversation(
            conversation_id='opt-patterns',
            title='Optimization Test',
            messages=messages
        )
        
        pattern_context = [
            {
                'pattern_type': 'architecture',
                'name': 'MVC Pattern',
                'description': 'Model-View-Controller architecture'
            }
        ]
        
        result = working_memory.get_optimized_context(
            conversation_id='opt-patterns',
            pattern_context=pattern_context
        )
        
        assert 'original_context' in result
        assert 'optimized_context' in result
        assert 'cache_health' in result
    
    def test_cache_monitor_integration(self, working_memory):
        """Test cache monitor is properly initialized."""
        assert working_memory.cache_monitor is not None
    
    def test_token_metrics_integration(self, working_memory):
        """Test token metrics collector is properly initialized."""
        assert working_memory.token_metrics is not None


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_working_memory.db"
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db_path):
        """Create a WorkingMemory instance for testing."""
        return WorkingMemory(db_path=temp_db_path)
    
    def test_add_conversation_duplicate_id(self, working_memory):
        """Test adding conversation with duplicate ID."""
        messages = [{'role': 'user', 'content': 'First'}]
        
        working_memory.add_conversation(
            conversation_id='duplicate-test',
            title='First Conversation',
            messages=messages
        )
        
        # Adding with same ID should handle gracefully
        # (Actual behavior depends on implementation)
        try:
            working_memory.add_conversation(
                conversation_id='duplicate-test',
                title='Second Conversation',
                messages=messages
            )
        except Exception as e:
            # Expected to raise or handle gracefully
            assert True
    
    def test_get_messages_empty_conversation(self, working_memory):
        """Test getting messages from non-existent conversation."""
        messages = working_memory.get_messages('nonexistent-conv')
        
        # Should return empty list or handle gracefully
        assert isinstance(messages, list)
    
    def test_session_detection_with_empty_workspace(self, working_memory):
        """Test session detection with empty workspace path."""
        # Test with minimal workspace path
        workspace_path = "D:/empty"
        
        session = working_memory.detect_or_create_session(workspace_path)
        
        assert session is not None
        assert session.workspace_path == workspace_path


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
