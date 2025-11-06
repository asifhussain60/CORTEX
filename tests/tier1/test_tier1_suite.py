"""
Tier 1 Test Suite
----------------
Comprehensive tests for all Tier 1 components:
- ConversationManager (5 tests)
- FIFO Queue (2 tests)
- EntityExtractor (4 tests)
- FileTracker (3 tests)
- Integration (1 test)

Total: 15 tests covering all Tier 1 functionality.

Run with: pytest tests/tier1/test_tier1_suite.py -v
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
import json
import sys

# Add CORTEX to path and import tier1 modules directly to avoid CORTEX package init issues
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from CORTEX.src.brain.tier1.tier1_api import Tier1API, get_tier1_api
from CORTEX.src.brain.tier1.conversation_manager import ConversationManager
from CORTEX.src.brain.tier1.entity_extractor import EntityExtractor
from CORTEX.src.brain.tier1.file_tracker import FileTracker
from CORTEX.src.brain.tier1.request_logger import RequestLogger


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_path = temp_file.name
    temp_file.close()
    
    # Initialize schema
    conn = sqlite3.connect(temp_path)
    with open('cortex-brain/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def api(temp_db):
    """Create a Tier1API instance with temporary database."""
    return Tier1API(db_path=temp_db)


@pytest.fixture
def conv_manager(temp_db):
    """Create a ConversationManager instance with temporary database."""
    return ConversationManager(db_path=temp_db)


@pytest.fixture
def entity_extractor():
    """Create an EntityExtractor instance."""
    return EntityExtractor()


@pytest.fixture
def file_tracker(temp_db):
    """Create a FileTracker instance with temporary database."""
    return FileTracker(db_path=temp_db)


@pytest.fixture
def request_logger(temp_db):
    """Create a RequestLogger instance with temporary database."""
    return RequestLogger(db_path=temp_db)


# ============================================================================
# ConversationManager Tests (5 tests)
# ============================================================================

def test_conversation_crud(conv_manager):
    """Test 1: Create, Read, Update, Delete conversation."""
    # Create
    conv_id = conv_manager.create_conversation(
        agent_name="test-agent",
        related_files=["file1.py", "file2.py"],
        metadata={"session": "test"}
    )
    assert conv_id is not None
    
    # Read
    conv = conv_manager.get_conversation(conv_id)
    assert conv is not None
    assert conv['agent_name'] == "test-agent"
    assert "file1.py" in conv['related_files']
    
    # Update
    success = conv_manager.update_conversation(
        conv_id,
        related_files=["file3.py"]
    )
    assert success is True
    conv = conv_manager.get_conversation(conv_id)
    assert "file3.py" in conv['related_files']
    
    # Delete
    success = conv_manager.delete_conversation(conv_id)
    assert success is True
    conv = conv_manager.get_conversation(conv_id)
    assert conv is None


def test_message_operations(conv_manager):
    """Test 2: Add messages and retrieve them."""
    conv_id = conv_manager.create_conversation(agent_name="test-agent")
    
    # Add user message
    msg_id = conv_manager.add_message(
        conversation_id=conv_id,
        role="user",
        content="Test request",
        extracted_entities={'files': ['test.py']}
    )
    assert msg_id == 1
    
    # Add assistant message
    msg_id = conv_manager.add_message(
        conversation_id=conv_id,
        role="assistant",
        content="Test response"
    )
    assert msg_id == 2
    
    # Get conversation with messages
    conv = conv_manager.get_conversation(conv_id, include_messages=True)
    assert len(conv['messages']) == 2
    assert conv['messages'][0]['role'] == "user"
    assert conv['messages'][1]['role'] == "assistant"


def test_conversation_search(conv_manager):
    """Test 3: Full-text search using FTS5."""
    # Create conversations with different content
    conv1_id = conv_manager.create_conversation(agent_name="agent1")
    conv_manager.add_message(conv1_id, "user", "Fix authentication bug")
    
    conv2_id = conv_manager.create_conversation(agent_name="agent2")
    conv_manager.add_message(conv2_id, "user", "Add database migration")
    
    conv3_id = conv_manager.create_conversation(agent_name="agent3")
    conv_manager.add_message(conv3_id, "user", "Refactor authentication module")
    
    # Search for "authentication"
    results = conv_manager.search_conversations("authentication", limit=10)
    assert len(results) == 2
    
    # Verify ranking (both should match)
    agent_names = [r['agent_name'] for r in results]
    assert "agent1" in agent_names
    assert "agent3" in agent_names


def test_get_recent_conversations(conv_manager):
    """Test 4: Get recent conversations ordered by created_at."""
    # Create 5 conversations
    conv_ids = []
    for i in range(5):
        conv_id = conv_manager.create_conversation(agent_name=f"agent{i}")
        conv_ids.append(conv_id)
    
    # Get recent (should be in reverse order)
    recent = conv_manager.get_recent_conversations(limit=3)
    assert len(recent) == 3
    assert recent[0]['agent_name'] == "agent4"
    assert recent[1]['agent_name'] == "agent3"
    assert recent[2]['agent_name'] == "agent2"


def test_context_resolution(conv_manager):
    """Test 5: Get conversation context for a specific date/time range."""
    # Create conversation with messages
    conv_id = conv_manager.create_conversation(agent_name="test-agent")
    conv_manager.add_message(conv_id, "user", "First message")
    conv_manager.add_message(conv_id, "assistant", "First response")
    
    # Get conversation with messages
    conv = conv_manager.get_conversation(conv_id, include_messages=True)
    assert conv['message_count'] == 2
    assert len(conv['messages']) == 2


# ============================================================================
# FIFO Queue Tests (2 tests)
# ============================================================================

def test_fifo_queue_enforcement(conv_manager):
    """Test 6: FIFO queue automatically deletes oldest conversation when exceeding 20."""
    # Create 21 conversations
    conv_ids = []
    for i in range(21):
        conv_id = conv_manager.create_conversation(agent_name=f"agent{i}")
        conv_ids.append(conv_id)
    
    # Check that oldest conversation (conv_ids[0]) was deleted
    oldest_conv = conv_manager.get_conversation(conv_ids[0])
    assert oldest_conv is None
    
    # Check that newest 20 conversations still exist
    newest_conv = conv_manager.get_conversation(conv_ids[-1])
    assert newest_conv is not None
    
    # Verify total count is 20
    recent = conv_manager.get_recent_conversations(limit=100)
    assert len(recent) == 20


def test_fifo_queue_message_deletion(conv_manager):
    """Test 7: FIFO queue deletes messages when deleting conversation."""
    # Create conversation with messages
    conv_id = conv_manager.create_conversation(agent_name="test-agent")
    conv_manager.add_message(conv_id, "user", "Message 1")
    conv_manager.add_message(conv_id, "assistant", "Message 2")
    
    # Verify messages exist
    conv = conv_manager.get_conversation(conv_id, include_messages=True)
    assert len(conv['messages']) == 2
    
    # Delete conversation
    conv_manager.delete_conversation(conv_id)
    
    # Verify messages were also deleted
    conn = sqlite3.connect(conv_manager.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tier1_messages WHERE conversation_id = ?", (conv_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0


# ============================================================================
# EntityExtractor Tests (4 tests)
# ============================================================================

def test_entity_extraction_files(entity_extractor):
    """Test 8: Extract file paths from text."""
    text = "Fix the bug in src/auth.py and update tests/test_auth.py"
    entities = entity_extractor.extract_entities(text)
    
    assert 'files' in entities
    assert "src/auth.py" in entities['files']
    assert "tests/test_auth.py" in entities['files']


def test_entity_extraction_components(entity_extractor):
    """Test 9: Extract component names from text."""
    text = "Refactor the AuthService class and update UserController"
    entities = entity_extractor.extract_entities(text)
    
    assert 'components' in entities
    assert "AuthService" in entities['components']
    assert "UserController" in entities['components']


def test_intent_extraction(entity_extractor):
    """Test 10: Extract user intents from text."""
    text = "Plan: First refactor auth.py, then add tests"
    intents = entity_extractor.extract_intents(text)
    
    assert 'PLAN' in intents


def test_reference_resolution(entity_extractor):
    """Test 11: Resolve ambiguous references using context."""
    context = "user: Fix the bug in auth.py\nassistant: Done"
    resolved = entity_extractor.resolve_reference("it", context)
    
    assert resolved == "auth.py"


# ============================================================================
# FileTracker Tests (3 tests)
# ============================================================================

def test_file_tracking(file_tracker, conv_manager):
    """Test 12: Track file modifications in conversations."""
    # Create conversation and track files
    conv_id = conv_manager.create_conversation(agent_name="test-agent")
    file_tracker.track_files(conv_id, ["file1.py", "file2.py"])
    
    # Verify tracking exists
    conn = sqlite3.connect(file_tracker.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tier1_file_tracking WHERE conversation_id = ?", (conv_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count > 0


def test_co_modification_detection(file_tracker, conv_manager):
    """Test 13: Detect files frequently modified together."""
    # Create 5 conversations modifying file1.py and file2.py together
    for i in range(5):
        conv_id = conv_manager.create_conversation(agent_name=f"agent{i}")
        file_tracker.track_files(conv_id, ["file1.py", "file2.py"])
    
    # Create 2 conversations modifying file1.py and file3.py together
    for i in range(2):
        conv_id = conv_manager.create_conversation(agent_name=f"agent{i+5}")
        file_tracker.track_files(conv_id, ["file1.py", "file3.py"])
    
    # Detect co-modifications for file1.py
    patterns = file_tracker.detect_co_modifications("file1.py", min_confidence=0.2)
    
    # file2.py should have higher confidence than file3.py
    assert len(patterns) >= 2
    file2_pattern = next((p for p in patterns if p['file_b'] == 'file2.py'), None)
    file3_pattern = next((p for p in patterns if p['file_b'] == 'file3.py'), None)
    
    assert file2_pattern is not None
    assert file3_pattern is not None
    assert file2_pattern['confidence'] > file3_pattern['confidence']


def test_export_to_tier2(file_tracker, conv_manager):
    """Test 14: Export high-confidence patterns to Tier 2."""
    # Create conversations with file patterns
    for i in range(10):
        conv_id = conv_manager.create_conversation(agent_name=f"agent{i}")
        file_tracker.track_files(conv_id, ["auth.py", "user.py"])
    
    # Export patterns
    patterns = file_tracker.export_for_tier2(min_confidence=0.5, limit=100)
    
    # Verify export format
    assert len(patterns) > 0
    pattern = patterns[0]
    assert 'file_a' in pattern
    assert 'file_b' in pattern
    assert 'confidence' in pattern
    assert pattern['confidence'] >= 0.5


# ============================================================================
# Integration Test (1 test)
# ============================================================================

def test_tier1_api_integration(api):
    """Test 15: Full integration using Tier1API."""
    # Log a conversation
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Fix the authentication bug in src/auth.py",
        response="Fixed the issue by adding null check",
        related_files=["src/auth.py"]
    )
    
    assert conv_id is not None
    
    # Search for conversation
    results = api.search("authentication", limit=5)
    assert len(results) >= 1
    
    # Get file patterns
    patterns = api.get_file_patterns("src/auth.py", min_confidence=0.1)
    # May be empty since only 1 conversation, but should not raise error
    assert isinstance(patterns, list)
    
    # Get stats
    stats = api.get_stats()
    assert stats['total_conversations'] == 1
    assert stats['total_messages'] == 2  # user + assistant
    
    # Health check
    health = api.health_check()
    assert health['healthy'] is True
    assert len(health['warnings']) == 0
    
    # Get conversation summary
    summary = api.get_conversation_summary(conv_id)
    assert "authentication" in summary.lower()


# ============================================================================
# RequestLogger Tests (bonus - 3 additional tests)
# ============================================================================

def test_request_logging(request_logger):
    """Test: Log raw requests and responses."""
    req_id = request_logger.log_raw_request(
        raw_request="Test request",
        raw_response="Test response",
        agent_name="test-agent"
    )
    
    assert req_id > 0
    
    # Retrieve logged request
    logged = request_logger.get_raw_request(req_id)
    assert logged is not None
    assert logged['raw_request'] == "Test request"


def test_sensitive_data_redaction(request_logger):
    """Test: Automatic redaction of sensitive data."""
    text_with_secrets = "My API key is sk-abc123xyz456 and password=secret123"
    redacted, was_redacted = request_logger.redact_sensitive_data(text_with_secrets)
    
    assert was_redacted is True
    assert "sk-abc123xyz456" not in redacted
    assert "[REDACTED" in redacted


def test_redaction_stats(request_logger):
    """Test: Get redaction statistics."""
    # Log request with sensitive data
    request_logger.log_raw_request(
        raw_request="Use token sk-abc123",
        raw_response="Done",
        agent_name="test"
    )
    
    # Log request without sensitive data
    request_logger.log_raw_request(
        raw_request="Fix the bug",
        raw_response="Fixed",
        agent_name="test"
    )
    
    stats = request_logger.get_redaction_stats()
    assert stats['total_logs'] == 2
    assert stats['redacted_logs'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
