"""
CORTEX Tier 1: Unit Tests
Comprehensive test suite for Tier 1 Working Memory

Task 1.7: Unit Testing
Duration: 1.5 hours
Target: 15 tests, 95% coverage
"""

import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from tempfile import TemporaryDirectory

from CORTEX.src.tier1.conversation_manager import ConversationManager
from CORTEX.src.tier1.entity_extractor import EntityExtractor
from CORTEX.src.tier1.file_tracker import FileTracker
from CORTEX.src.tier1.request_logger import RequestLogger
from CORTEX.src.tier1.tier1_api import Tier1API


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def db_path(temp_dir):
    """Create temporary database path"""
    return temp_dir / "test_tier1.db"


@pytest.fixture
def log_path(temp_dir):
    """Create temporary log path"""
    return temp_dir / "test_requests.jsonl"


@pytest.fixture
def conversation_manager(db_path):
    """Create ConversationManager instance"""
    return ConversationManager(db_path)


@pytest.fixture
def entity_extractor():
    """Create EntityExtractor instance"""
    return EntityExtractor()


@pytest.fixture
def file_tracker():
    """Create FileTracker instance"""
    return FileTracker()


@pytest.fixture
def request_logger(log_path):
    """Create RequestLogger instance"""
    return RequestLogger(log_path)


@pytest.fixture
def tier1_api(db_path, log_path):
    """Create Tier1API instance"""
    return Tier1API(db_path, log_path)


# ============================================================================
# CONVERSATION MANAGER TESTS (5 tests)
# ============================================================================

def test_create_conversation(conversation_manager):
    """Test creating a conversation"""
    conv_id = conversation_manager.create_conversation(
        agent_id="test-agent",
        goal="Test conversation"
    )
    
    assert conv_id is not None
    assert conv_id.startswith("conv-")
    
    # Verify in database
    conversation = conversation_manager.get_conversation(conv_id)
    assert conversation is not None
    assert conversation['agent_id'] == "test-agent"
    assert conversation['goal'] == "Test conversation"
    assert conversation['status'] == "active"


def test_add_message(conversation_manager):
    """Test adding messages to conversation"""
    conv_id = conversation_manager.create_conversation(agent_id="test-agent")
    
    # Add user message
    msg_id1 = conversation_manager.add_message(
        conversation_id=conv_id,
        role="user",
        content="Test message 1"
    )
    assert msg_id1 is not None
    
    # Add assistant message
    msg_id2 = conversation_manager.add_message(
        conversation_id=conv_id,
        role="assistant",
        content="Test response"
    )
    assert msg_id2 is not None
    
    # Verify messages
    messages = conversation_manager.get_messages(conv_id)
    assert len(messages) == 2
    assert messages[0]['role'] == "user"
    assert messages[1]['role'] == "assistant"


def test_fifo_enforcement(conversation_manager):
    """Test FIFO queue enforcement (20 conversation limit)"""
    # Create 25 conversations, marking first 10 as completed
    conv_ids = []
    for i in range(25):
        conv_id = conversation_manager.create_conversation(
            agent_id=f"agent-{i}",
            goal=f"Conversation {i}"
        )
        conv_ids.append(conv_id)
        
        # Mark first 10 as completed so they can be deleted
        if i < 10:
            conversation_manager.end_conversation(conv_id, "completed")
    
    # First 5 completed should be deleted (to make room for new ones)
    for i in range(5):
        conversation = conversation_manager.get_conversation(conv_ids[i])
        assert conversation is None
    
    # Conversations 5-9 should still exist (completed but not deleted yet)
    for i in range(5, 10):
        conversation = conversation_manager.get_conversation(conv_ids[i])
        assert conversation is not None
    
    # Last 15 should exist (active)
    for i in range(10, 25):
        conversation = conversation_manager.get_conversation(conv_ids[i])
        assert conversation is not None


def test_entity_tracking(conversation_manager):
    """Test entity extraction and tracking"""
    conv_id = conversation_manager.create_conversation(agent_id="test-agent")
    
    # Add entities
    conversation_manager.add_entity(conv_id, "file", "src/main.py")
    conversation_manager.add_entity(conv_id, "intent", "debug")
    conversation_manager.add_entity(conv_id, "file", "src/utils.py")
    
    # Get all entities
    entities = conversation_manager.get_entities(conv_id)
    assert len(entities) == 3
    
    # Get file entities only
    file_entities = conversation_manager.get_entities(conv_id, entity_type="file")
    assert len(file_entities) == 2


def test_file_tracking(conversation_manager):
    """Test file modification tracking"""
    conv_id = conversation_manager.create_conversation(agent_id="test-agent")
    
    # Add file modifications
    conversation_manager.add_file(conv_id, "src/main.py", "created")
    conversation_manager.add_file(conv_id, "src/main.py", "modified")
    conversation_manager.add_file(conv_id, "tests/test_main.py", "created")
    
    # Get files
    files = conversation_manager.get_files(conv_id)
    assert len(files) == 3
    
    # Verify operations
    operations = [f['operation'] for f in files]
    assert "created" in operations
    assert "modified" in operations


# ============================================================================
# ENTITY EXTRACTOR TESTS (3 tests)
# ============================================================================

def test_extract_file_paths(entity_extractor):
    """Test file path extraction"""
    text = "Modified src/main.py and tests/test_main.py files"
    
    files = entity_extractor.extract_files(text)
    assert len(files) == 2
    assert "src/main.py" in files
    assert "tests/test_main.py" in files


def test_extract_intents(entity_extractor):
    """Test intent extraction"""
    text = "DEBUG the error in the implementation and TEST the fix"
    
    intents = entity_extractor.extract_intents(text)
    assert len(intents) > 0
    # Should find DEBUG or TEST
    assert any(intent in ['DEBUG', 'TEST'] for intent in intents)


def test_extract_technical_terms(entity_extractor):
    """Test technical term extraction"""
    text = "Implement REST API with SQLite database and pytest tests"
    
    terms = entity_extractor.extract_technical_terms(text)
    assert len(terms) > 0
    
    # Should extract compound terms (returned as dict with 'term' and 'count')
    term_names = [t['term'] for t in terms]
    # Check for known technical terms
    assert any('api' in t or 'database' in t or 'test' in t for t in term_names)


# ============================================================================
# FILE TRACKER TESTS (2 tests)
# ============================================================================

def test_file_pattern_detection(file_tracker):
    """Test file pattern grouping"""
    files = [
        "src/tier1/conversation.py",
        "src/tier1/entity.py",
        "src/tier2/knowledge.py",
        "tests/test_tier1.py"
    ]
    
    patterns = file_tracker.get_file_patterns(files)
    assert len(patterns) > 0
    
    # Should group by directory
    assert any('tier1' in p for p in patterns)
    assert any('tier2' in p for p in patterns)


def test_file_statistics(file_tracker):
    """Test file statistics generation"""
    files = [
        "src/tier1/conversation.py",
        "src/tier1/entity.py",
        "src/tier2/knowledge.py"
    ]
    
    stats = file_tracker.get_file_statistics(files)
    assert stats['total_files'] == 3
    assert stats['total_directories'] > 0
    assert 'by_extension' in stats
    assert stats['by_extension'].get('.py', 0) == 3


# ============================================================================
# REQUEST LOGGER TESTS (2 tests)
# ============================================================================

def test_log_request_response(request_logger):
    """Test logging requests and responses"""
    # Log request
    request_id = request_logger.log_request(
        request_text="Test request",
        conversation_id="conv-123",
        intent="test"
    )
    assert request_id is not None
    assert request_id.startswith("req-")
    
    # Log response
    request_logger.log_response(
        request_id=request_id,
        response_text="Test response",
        conversation_id="conv-123",
        status="success"
    )
    
    # Get pair
    pair = request_logger.get_request_response_pair(request_id)
    assert pair['request'] is not None
    assert pair['response'] is not None
    assert pair['request']['text'] == "Test request"
    assert pair['response']['text'] == "Test response"


def test_request_statistics(request_logger):
    """Test request logging statistics"""
    # Log multiple requests
    for i in range(5):
        request_id = request_logger.log_request(
            request_text=f"Request {i}",
            intent="test"
        )
        request_logger.log_response(
            request_id=request_id,
            response_text=f"Response {i}",
            status="success"
        )
    
    # Get statistics
    stats = request_logger.get_statistics()
    assert stats['total_requests'] == 5
    assert stats['total_responses'] == 5
    assert stats['by_intent'].get('test', 0) == 5


# ============================================================================
# TIER1 API TESTS (3 tests)
# ============================================================================

def test_api_start_conversation(tier1_api):
    """Test starting conversation via API"""
    conv_id = tier1_api.start_conversation(
        agent_id="test-agent",
        goal="Test goal"
    )
    
    assert conv_id is not None
    conversation = tier1_api.get_active_conversation("test-agent")
    assert conversation is not None
    assert conversation['goal'] == "Test goal"


def test_api_process_message(tier1_api):
    """Test processing message with automatic extraction"""
    conv_id = tier1_api.start_conversation(agent_id="test-agent")
    
    # Process user message
    result = tier1_api.process_message(
        conversation_id=conv_id,
        role="user",
        content="Debug the error in src/main.py"
    )
    
    assert result['message_id'] is not None
    assert result['request_id'] is not None
    assert len(result['files']) > 0
    assert len(result['entities']) > 0


def test_api_conversation_history(tier1_api):
    """Test getting conversation history"""
    conv_id = tier1_api.start_conversation(agent_id="test-agent")
    
    # Add messages
    tier1_api.process_message(conv_id, "user", "Test message 1")
    tier1_api.process_message(conv_id, "assistant", "Test response 1")
    tier1_api.process_message(conv_id, "user", "Test message 2")
    
    # Get history
    history = tier1_api.get_conversation_history(conv_id)
    assert history['conversation'] is not None
    assert len(history['messages']) == 3
    assert 'entities' in history
    assert 'files' in history


# ============================================================================
# INTEGRATION TESTS (bonus)
# ============================================================================

def test_full_conversation_workflow(tier1_api):
    """Test complete conversation workflow"""
    # Start conversation
    conv_id = tier1_api.start_conversation(
        agent_id="integration-test",
        goal="Full workflow test"
    )
    
    # Process multiple messages
    result1 = tier1_api.process_message(
        conv_id,
        "user",
        "Create src/main.py with REST API implementation"
    )
    
    result2 = tier1_api.process_message(
        conv_id,
        "assistant",
        "I'll create the file with FastAPI implementation"
    )
    
    # Track file modification
    tier1_api.track_file_modification(
        conv_id,
        "src/main.py",
        "created"
    )
    
    # Log response
    tier1_api.log_response(
        result1['request_id'],
        "File created successfully"
    )
    
    # End conversation
    summary = tier1_api.end_conversation(conv_id, "completed")
    
    # Verify
    assert summary['message_count'] == 2
    assert summary['outcome'] == "completed"
    
    # Get full history
    history = tier1_api.get_conversation_history(conv_id)
    assert len(history['files']) > 0
    assert len(history['entities']) > 0
    
    # Get statistics
    stats = tier1_api.get_tier1_statistics()
    assert stats['conversations']['total_conversations'] >= 1
    assert stats['requests']['total_requests'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=CORTEX.src.tier1", "--cov-report=term-missing"])
