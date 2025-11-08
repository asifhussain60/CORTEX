"""
Unit tests for QueueManager module.
"""

import pytest
import tempfile
from pathlib import Path
from src.tier1.fifo import QueueManager
from src.tier1.conversations import ConversationManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def queue_manager(temp_db):
    """Create a QueueManager instance with temp database."""
    return QueueManager(temp_db)


@pytest.fixture
def conversation_manager(temp_db):
    """Create a ConversationManager for setup."""
    return ConversationManager(temp_db)


class TestEnforceFifoLimit:
    """Tests for FIFO limit enforcement."""
    
    def test_no_eviction_under_limit(self, queue_manager, conversation_manager):
        """Test that no eviction occurs when under limit."""
        # Add 19 conversations (under 20 limit)
        for i in range(19):
            conversation_manager.add_conversation(f"conv-{i}", f"Conv {i}")
        
        queue_manager.enforce_fifo_limit()
        
        status = queue_manager.get_queue_status()
        assert status["total_conversations"] == 19
        assert status["available_slots"] == 1
    
    def test_evicts_oldest_when_at_capacity(self, queue_manager, conversation_manager):
        """Test eviction of oldest when at capacity."""
        # Add exactly 20 conversations
        for i in range(20):
            conversation_manager.add_conversation(f"conv-{i}", f"Conv {i}")
        
        # Enforce limit (should evict oldest)
        queue_manager.enforce_fifo_limit()
        
        # Oldest should be gone
        oldest = conversation_manager.get_conversation("conv-0")
        assert oldest is None
        
        status = queue_manager.get_queue_status()
        assert status["total_conversations"] == 19
    
    def test_never_evicts_active_conversation(self, queue_manager, conversation_manager):
        """Test that active conversations are protected."""
        # Add 20 conversations
        for i in range(20):
            conversation_manager.add_conversation(f"conv-{i}", f"Conv {i}")
        
        # Mark oldest as active
        conversation_manager.set_active_conversation("conv-0")
        
        # Enforce limit
        queue_manager.enforce_fifo_limit()
        
        # Active oldest should still exist
        oldest = conversation_manager.get_conversation("conv-0")
        assert oldest is not None
        assert oldest.is_active
    
    def test_eviction_logs_event(self, queue_manager, conversation_manager):
        """Test that evictions are logged."""
        # Add 20 conversations and trigger eviction
        for i in range(20):
            conversation_manager.add_conversation(f"conv-{i}", f"Conv {i}")
        
        queue_manager.enforce_fifo_limit()
        
        log = queue_manager.get_eviction_log()
        assert len(log) >= 1
        assert log[0]["conversation_id"] == "conv-0"
        assert log[0]["reason"] == "fifo_limit"


class TestGetQueueStatus:
    """Tests for queue status retrieval."""
    
    def test_status_shows_correct_counts(self, queue_manager, conversation_manager):
        """Test that status reflects current state."""
        for i in range(5):
            conversation_manager.add_conversation(f"conv-{i}", f"Conv {i}")
        
        status = queue_manager.get_queue_status()
        assert status["total_conversations"] == 5
        assert status["capacity"] == 20
        assert status["available_slots"] == 15
    
    def test_status_empty_database(self, queue_manager):
        """Test status with no conversations."""
        status = queue_manager.get_queue_status()
        assert status["total_conversations"] == 0
        assert status["available_slots"] == 20


class TestGetEvictionLog:
    """Tests for eviction log retrieval."""
    
    def test_log_empty_initially(self, queue_manager):
        """Test that log is empty with no evictions."""
        log = queue_manager.get_eviction_log()
        assert log == []
