"""
Track A Phase 2: Comprehensive Unit Tests for ConversationalChannelAdapter

Tests Tier 1 integration including:
- Storage and retrieval operations
- Quality filtering
- Statistics calculation
- WorkingMemory integration
- Error handling

Author: CORTEX Team
Date: 2025-11-15
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from src.track_a.integrations.conversational_channel_adapter import ConversationalChannelAdapter
from src.tier1.working_memory import WorkingMemory


class TestAdapterBasics:
    """Test basic ConversationalChannelAdapter functionality."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database directory."""
        db_dir = tmp_path / "cortex_test"
        db_dir.mkdir(parents=True, exist_ok=True)
        yield db_dir
        # Cleanup after test
        shutil.rmtree(db_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db):
        """Create real WorkingMemory instance with temporary database."""
        db_path = temp_db / "working_memory.db"
        return WorkingMemory(db_path=str(db_path))
    
    @pytest.fixture
    def adapter(self, working_memory):
        """Create ConversationalChannelAdapter with real WorkingMemory."""
        return ConversationalChannelAdapter(working_memory=working_memory)
    
    def test_adapter_initialization(self, adapter):
        """Test adapter initializes successfully."""
        assert adapter is not None
        assert hasattr(adapter, 'store')
        assert hasattr(adapter, 'retrieve')
    
    def test_adapter_has_required_methods(self, adapter):
        """Test adapter has all required methods."""
        assert callable(adapter.store)
        assert callable(adapter.retrieve)
        assert hasattr(adapter, 'get_statistics')


class TestStorageOperations:
    """Test conversation storage operations."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database directory."""
        db_dir = tmp_path / "cortex_test"
        db_dir.mkdir(parents=True, exist_ok=True)
        yield db_dir
        # Cleanup after test
        shutil.rmtree(db_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db):
        """Create real WorkingMemory instance with temporary database."""
        db_path = temp_db / "working_memory.db"
        return WorkingMemory(db_path=str(db_path))
    
    @pytest.fixture
    def adapter(self, working_memory):
        return ConversationalChannelAdapter(working_memory=working_memory)
    
    @pytest.fixture
    def sample_conversation(self):
        return {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2025-11-15T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": "Hi there!",
                    "timestamp": "2025-11-15T10:00:05"
                }
            ],
            "metadata": {
                "intents": ["STATUS"],
                "entities": [],
                "quality": 5
            }
        }
    
    def test_store_conversation(self, adapter, sample_conversation):
        """Test storing a conversation."""
        result = adapter.store(sample_conversation, source="copilot_chat")
        
        assert result["success"] is True
        assert "conversation_id" in result
    
    def test_retrieve_conversation(self, adapter, sample_conversation):
        """Test retrieving a conversation by ID."""
        # First store a conversation
        store_result = adapter.store(sample_conversation, source="test")
        conversation_id = store_result["conversation_id"]
        
        # Then retrieve it
        result = adapter.retrieve(conversation_id)
        
        assert result["success"] is True
        assert result["conversation_id"] == conversation_id
        assert "conversation" in result
    
    def test_retrieve_nonexistent_conversation(self, adapter):
        """Test retrieving a conversation that doesn't exist."""
        result = adapter.retrieve("nonexistent_id")
        
        assert result["success"] is False
        assert "error" in result


class TestQualityFiltering:
    """Test quality-based conversation filtering."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database directory."""
        db_dir = tmp_path / "cortex_test"
        db_dir.mkdir(parents=True, exist_ok=True)
        yield db_dir
        # Cleanup after test
        shutil.rmtree(db_dir, ignore_errors=True)
    
    @pytest.fixture
    def working_memory(self, temp_db):
        """Create real WorkingMemory instance with temporary database."""
        db_path = temp_db / "working_memory.db"
        return WorkingMemory(db_path=str(db_path))
    
    @pytest.fixture
    def adapter(self, working_memory):
        return ConversationalChannelAdapter(
            working_memory=working_memory,
            min_quality_threshold=5  # Only accept quality >= 5
        )
    
    def test_accept_high_quality_conversation(self, adapter):
        """Test high-quality conversations are accepted."""
        high_quality = {
            "messages": [{"role": "user", "content": "Detailed question"}],
            "semantic_data": {"quality_score": 8.0}  # Use semantic_data instead of metadata
        }
        
        result = adapter.store(high_quality, source="copilot")
        
        assert result["success"] is True
    
    def test_reject_low_quality_conversation(self, adapter):
        """Test low-quality conversations are rejected."""
        low_quality = {
            "messages": [{"role": "user", "content": "ok"}],
            "semantic_data": {"quality_score": 2.0}  # Use semantic_data instead of metadata
        }
        
        result = adapter.store(low_quality, source="copilot")
        
        # Should be rejected due to low quality (threshold is 5)
        assert result["success"] is False
        assert "quality" in result.get("reason", "").lower()
    
    def test_configurable_quality_threshold(self, working_memory):
        """Test quality threshold is configurable."""
        strict_adapter = ConversationalChannelAdapter(
            working_memory=working_memory,
            min_quality_threshold=8  # Very strict
        )
        
        medium_quality = {
            "messages": [{"role": "user", "content": "Test"}],
            "semantic_data": {"quality_score": 6.0}  # Use semantic_data instead of metadata
        }
        
        # Should fail strict threshold
        result = strict_adapter.store(medium_quality, source="copilot")
        
        # Should be rejected
        assert result["success"] is False
        assert "quality" in result.get("reason", "").lower()


class TestStatistics:
    """Test statistics calculation."""
    
    @pytest.fixture
    def mock_working_memory(self):
        """Create mock with db_path for statistics queries."""
        import tempfile
        import sqlite3
        
        # Create temp database with schema
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = db_file.name
        db_file.close()
        
        # Create schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE conversations (
                conversation_id TEXT PRIMARY KEY,
                conversation_type TEXT DEFAULT 'imported',
                quality_score REAL DEFAULT 0.0,
                message_count INTEGER DEFAULT 0,
                semantic_elements TEXT DEFAULT '{}'
            )
        """)
        # Insert test data
        cursor.execute("""
            INSERT INTO conversations (conversation_id, conversation_type, quality_score, message_count, semantic_elements)
            VALUES ('test1', 'imported', 7.5, 10, '{"entities": [], "intents": []}')
        """)
        conn.commit()
        conn.close()
        
        mock = Mock()
        mock.db_path = db_path
        return mock
    
    @pytest.fixture
    def adapter(self, mock_working_memory):
        return ConversationalChannelAdapter(working_memory=mock_working_memory)
    
    def test_get_conversation_count(self, adapter):
        """Test getting total conversation count."""
        stats = adapter.get_statistics()
        
        assert "total_conversations" in stats
        assert stats["total_conversations"] > 0
    
    def test_get_average_quality(self, adapter):
        """Test getting average quality score."""
        stats = adapter.get_statistics()
        
        assert "average_quality" in stats
        assert 0 <= stats["average_quality"] <= 10
    
    def test_get_statistics_by_source(self, adapter):
        """Test getting statistics grouped by source."""
        stats = adapter.get_statistics()
        
        assert "sources" in stats
        assert isinstance(stats["sources"], dict)
    
    def test_statistics_includes_message_count(self, adapter):
        """Test statistics include total message count."""
        stats = adapter.get_statistics()
        
        assert "total_messages" in stats
        assert stats["total_messages"] >= 0


class TestErrorHandling:
    """Test adapter error handling."""
    
    @pytest.fixture
    def failing_working_memory(self):
        """Create WorkingMemory that raises exceptions."""
        mock = Mock()
        mock.import_conversation.side_effect = Exception("Database error")
        mock.get_conversation.side_effect = Exception("Connection lost")
        return mock
    
    @pytest.fixture
    def adapter(self, failing_working_memory):
        return ConversationalChannelAdapter(working_memory=failing_working_memory)
    
    def test_handle_storage_failure(self, adapter):
        """Test graceful handling of storage failures."""
        conversation = {
            "messages": [{"role": "user", "content": "Test"}],
            "semantic_data": {"quality_score": 5.0}  # Use semantic_data
        }
        
        result = adapter.store(conversation, source="test")
        
        # Should return error response, not crash
        assert result is not None
        assert result["success"] is False
        assert "reason" in result or "error" in result
    
    def test_handle_retrieval_failure(self, adapter):
        """Test graceful handling of retrieval failures."""
        result = adapter.retrieve("some_id")
        
        # Should return error response, not crash
        assert result is not None
        assert "success" in result
        if result["success"] is False:
            assert "error" in result
