"""
Tests for Brain Ingestion Agent

Tests conversation capture and brain storage functionality.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.agents.brain_ingestion_agent import BrainIngestionAgent


@pytest.fixture
def temp_brain_storage(tmp_path):
    """Create temporary brain storage directory."""
    brain_dir = tmp_path / "cortex-brain" / "tier1"
    brain_dir.mkdir(parents=True)
    return brain_dir


@pytest.fixture
def agent(temp_brain_storage):
    """Create brain ingestion agent instance."""
    return BrainIngestionAgent(storage_path=str(temp_brain_storage))


class TestBrainIngestionAgent:
    """Test suite for Brain Ingestion Agent."""
    
    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.storage_path is not None
    
    def test_can_handle_conversation_capture_request(self, agent):
        """Test agent detects conversation capture requests."""
        assert agent.can_handle("capture this conversation") is True
        assert agent.can_handle("import conversation") is True
        assert agent.can_handle("save conversation") is True
        assert agent.can_handle("unrelated request") is False
    
    def test_ingest_conversation_creates_storage(self, agent, temp_brain_storage):
        """Test conversation ingestion creates storage."""
        conversation_data = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"}
            ],
            "timestamp": datetime.now().isoformat(),
            "topic": "greeting"
        }
        
        result = agent.ingest_conversation(conversation_data)
        
        assert result.success is True
        assert result.conversation_id is not None
    
    def test_retrieve_conversation_by_id(self, agent):
        """Test retrieving stored conversation by ID."""
        # First ingest
        conversation_data = {
            "messages": [
                {"role": "user", "content": "Test"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        ingest_result = agent.ingest_conversation(conversation_data)
        conversation_id = ingest_result.conversation_id
        
        # Then retrieve
        retrieved = agent.retrieve_conversation(conversation_id)
        
        assert retrieved is not None
        assert retrieved["messages"][0]["content"] == "Test"
    
    def test_search_conversations_by_topic(self, agent):
        """Test searching conversations by topic."""
        # Ingest multiple conversations
        agent.ingest_conversation({
            "messages": [{"role": "user", "content": "Python programming"}],
            "timestamp": datetime.now().isoformat(),
            "topic": "programming"
        })
        
        agent.ingest_conversation({
            "messages": [{"role": "user", "content": "Database design"}],
            "timestamp": datetime.now().isoformat(),
            "topic": "database"
        })
        
        # Search
        results = agent.search_conversations(topic="programming")
        
        assert len(results) > 0
        assert any("Python" in str(r) for r in results)
    
    def test_delete_conversation(self, agent):
        """Test deleting stored conversation."""
        conversation_data = {
            "messages": [{"role": "user", "content": "To be deleted"}],
            "timestamp": datetime.now().isoformat()
        }
        
        ingest_result = agent.ingest_conversation(conversation_data)
        conversation_id = ingest_result.conversation_id
        
        # Delete
        delete_result = agent.delete_conversation(conversation_id)
        
        assert delete_result.success is True
        
        # Verify deletion
        retrieved = agent.retrieve_conversation(conversation_id)
        assert retrieved is None
    
    def test_execute_with_conversation_data(self, agent):
        """Test agent execution with conversation data."""
        context = {
            "user_request": "capture this conversation",
            "conversation_data": {
                "messages": [
                    {"role": "user", "content": "Test message"}
                ],
                "timestamp": datetime.now().isoformat()
            }
        }
        
        result = agent.execute(context)
        
        assert result.success is True
        assert "conversation_id" in result.data
    
    def test_auto_topic_extraction(self, agent):
        """Test automatic topic extraction from conversation."""
        conversation_data = {
            "messages": [
                {"role": "user", "content": "How do I implement TDD workflow?"},
                {"role": "assistant", "content": "TDD workflow involves..."}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        result = agent.ingest_conversation(conversation_data)
        
        # Retrieve and check topic was auto-extracted
        retrieved = agent.retrieve_conversation(result.conversation_id)
        assert "topic" in retrieved
        assert len(retrieved["topic"]) > 0
    
    def test_conversation_scoring_relevance(self, agent):
        """Test conversation relevance scoring."""
        # Ingest conversation
        conversation_data = {
            "messages": [
                {"role": "user", "content": "Explain system alignment"},
                {"role": "assistant", "content": "System alignment validates..."}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        agent.ingest_conversation(conversation_data)
        
        # Score against query
        query = "How does system alignment work?"
        scored_conversations = agent.score_conversations(query)
        
        assert len(scored_conversations) > 0
        assert all(0 <= score <= 1.0 for _, score in scored_conversations)
    
    def test_conversation_privacy_protection(self, agent):
        """Test sensitive data redaction in stored conversations."""
        conversation_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "My API key is sk-abc123xyz and email is user@example.com"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        result = agent.ingest_conversation(conversation_data)
        retrieved = agent.retrieve_conversation(result.conversation_id)
        
        # Check sensitive data was redacted
        content = retrieved["messages"][0]["content"]
        assert "sk-abc123xyz" not in content
        assert "user@example.com" not in content
        assert "[REDACTED_API_KEY]" in content or "[REDACTED]" in content
    
    def test_storage_size_management(self, agent):
        """Test storage management when approaching limits."""
        # Ingest many conversations
        for i in range(100):
            agent.ingest_conversation({
                "messages": [{"role": "user", "content": f"Message {i}"}],
                "timestamp": datetime.now().isoformat()
            })
        
        # Check storage size
        storage_info = agent.get_storage_info()
        
        assert storage_info["conversation_count"] == 100
        assert storage_info["total_size_bytes"] > 0
    
    def test_batch_import_conversations(self, agent):
        """Test importing multiple conversations in batch."""
        conversations = [
            {
                "messages": [{"role": "user", "content": f"Test {i}"}],
                "timestamp": datetime.now().isoformat()
            }
            for i in range(10)
        ]
        
        result = agent.batch_import(conversations)
        
        assert result.success is True
        assert result.imported_count == 10
        assert len(result.conversation_ids) == 10


@pytest.mark.integration
class TestBrainIngestionIntegration:
    """Integration tests for brain ingestion with real storage."""
    
    def test_end_to_end_capture_and_retrieve(self, temp_brain_storage):
        """Test complete capture and retrieval flow."""
        agent = BrainIngestionAgent(storage_path=str(temp_brain_storage))
        
        # Capture conversation
        conversation = {
            "messages": [
                {"role": "user", "content": "Setup CORTEX"},
                {"role": "assistant", "content": "To setup CORTEX..."}
            ],
            "timestamp": datetime.now().isoformat(),
            "topic": "setup"
        }
        
        capture_result = agent.ingest_conversation(conversation)
        assert capture_result.success
        
        # Retrieve
        retrieved = agent.retrieve_conversation(capture_result.conversation_id)
        assert retrieved["messages"][0]["content"] == "Setup CORTEX"
        
        # Search
        search_results = agent.search_conversations(topic="setup")
        assert len(search_results) > 0
