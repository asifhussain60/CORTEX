#!/usr/bin/env python3
"""
Tests for Tier 1: Working Memory (Conversation Storage & Retrieval)

CORTEX Tier 1 provides short-term conversation memory with FIFO queue,
entity tracking, and fast retrieval (<50ms target).

This test suite validates:
- Conversation storage and retrieval
- FIFO queue behavior (20-conversation limit)
- Entity extraction (files, classes, methods)
- Search functionality
- Performance requirements

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any


# Mock implementation until actual Tier 1 module is available
class WorkingMemory:
    """Mock working memory for testing"""
    
    def __init__(self, max_conversations: int = 20):
        self.max_conversations = max_conversations
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.entities: Dict[str, List[Dict[str, Any]]] = {}
    
    def store_conversation(
        self,
        user_message: str,
        assistant_response: str,
        intent: str = "UNKNOWN",
        context: Dict[str, Any] = None
    ) -> str:
        """Store a conversation and return ID"""
        timestamp = datetime.now()
        conv_id = f"conv_{timestamp.strftime('%Y%m%d_%H%M%S')}_{hash(user_message) % 1000:03d}"
        
        self.conversations[conv_id] = {
            "conversation_id": conv_id,
            "user_message": user_message,
            "assistant_response": assistant_response,
            "intent": intent,
            "context": context or {},
            "timestamp": timestamp
        }
        
        # FIFO queue enforcement
        if len(self.conversations) > self.max_conversations:
            oldest = min(self.conversations.keys(), key=lambda k: self.conversations[k]["timestamp"])
            del self.conversations[oldest]
        
        return conv_id
    
    def get_conversation(self, conv_id: str) -> Dict[str, Any]:
        """Retrieve conversation by ID"""
        return self.conversations.get(conv_id)
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get N most recent conversations"""
        sorted_convs = sorted(
            self.conversations.values(),
            key=lambda x: x["timestamp"],
            reverse=True
        )
        return sorted_convs[:limit]
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        results = []
        query_lower = query.lower()
        
        for conv in self.conversations.values():
            if (query_lower in conv["user_message"].lower() or
                query_lower in conv["assistant_response"].lower()):
                results.append(conv)
        
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def track_entity(
        self,
        conversation_id: str,
        entity_type: str,
        entity_value: str,
        context: str = ""
    ):
        """Track an entity (file, class, method) in conversation"""
        if conversation_id not in self.entities:
            self.entities[conversation_id] = []
        
        self.entities[conversation_id].append({
            "entity_type": entity_type,
            "entity_value": entity_value,
            "context": context
        })
    
    def get_entities(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get entities for a conversation"""
        return self.entities.get(conversation_id, [])
    
    def search_by_entity(self, entity_type: str, entity_value: str) -> List[Dict[str, Any]]:
        """Find conversations mentioning specific entity"""
        results = []
        for conv_id, entities in self.entities.items():
            for entity in entities:
                if (entity["entity_type"] == entity_type and
                    entity["entity_value"] == entity_value):
                    if conv_id in self.conversations:
                        results.append(self.conversations[conv_id])
                    break
        
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)


class TestConversationStorage:
    """Test conversation storage and retrieval"""
    
    @pytest.fixture
    def memory(self):
        """Create clean memory instance"""
        return WorkingMemory()
    
    def test_store_conversation(self, memory):
        """Test basic conversation storage"""
        conv_id = memory.store_conversation(
            user_message="Add a purple button",
            assistant_response="I'll create a purple button component",
            intent="EXECUTE"
        )
        
        assert conv_id is not None
        assert conv_id.startswith("conv_")
        assert len(conv_id) > 10  # Has timestamp and hash
    
    def test_retrieve_conversation(self, memory):
        """Test conversation retrieval"""
        # Store
        conv_id = memory.store_conversation(
            user_message="Test message",
            assistant_response="Test response",
            intent="TEST"
        )
        
        # Retrieve
        conv = memory.get_conversation(conv_id)
        
        assert conv is not None
        assert conv["user_message"] == "Test message"
        assert conv["assistant_response"] == "Test response"
        assert conv["intent"] == "TEST"
        assert conv["conversation_id"] == conv_id
        assert isinstance(conv["timestamp"], datetime)
    
    def test_store_with_context(self, memory):
        """Test conversation storage with context"""
        context = {
            "files_modified": ["AuthService.cs"],
            "intent_confidence": 0.92,
            "agent": "code-executor"
        }
        
        conv_id = memory.store_conversation(
            user_message="Add authentication",
            assistant_response="Creating auth service",
            intent="EXECUTE",
            context=context
        )
        
        conv = memory.get_conversation(conv_id)
        assert conv["context"]["files_modified"] == ["AuthService.cs"]
        assert conv["context"]["intent_confidence"] == 0.92
        assert conv["context"]["agent"] == "code-executor"
    
    def test_nonexistent_conversation(self, memory):
        """Test retrieving non-existent conversation"""
        conv = memory.get_conversation("conv_invalid_12345")
        assert conv is None


class TestFIFOQueue:
    """Test FIFO queue behavior (20-conversation limit)"""
    
    @pytest.fixture
    def memory(self):
        """Create memory with 5-item limit for faster testing"""
        return WorkingMemory(max_conversations=5)
    
    def test_fifo_limit_enforcement(self, memory):
        """Test that oldest conversation is deleted when limit reached"""
        # Store 5 conversations
        conv_ids = []
        for i in range(5):
            conv_id = memory.store_conversation(
                user_message=f"Message {i}",
                assistant_response=f"Response {i}"
            )
            conv_ids.append(conv_id)
            time.sleep(0.01)  # Ensure distinct timestamps
        
        assert len(memory.conversations) == 5
        
        # Add 6th conversation - should trigger FIFO
        new_conv_id = memory.store_conversation(
            user_message="Message 5",
            assistant_response="Response 5"
        )
        
        # Should still have 5 conversations
        assert len(memory.conversations) == 5
        
        # Oldest (conv_ids[0]) should be gone
        assert memory.get_conversation(conv_ids[0]) is None
        
        # Newest should be present
        assert memory.get_conversation(new_conv_id) is not None
    
    def test_fifo_preserves_recent(self, memory):
        """Test that recent conversations are preserved"""
        # Store 10 conversations
        for i in range(10):
            memory.store_conversation(
                user_message=f"Message {i}",
                assistant_response=f"Response {i}"
            )
            time.sleep(0.01)
        
        # Should only have last 5
        assert len(memory.conversations) == 5
        
        # Recent ones should be retrievable
        recent = memory.get_recent_conversations(limit=3)
        assert len(recent) == 3
        assert "Message 9" in recent[0]["user_message"]


class TestRecentConversations:
    """Test recent conversation retrieval"""
    
    @pytest.fixture
    def memory(self):
        """Create memory with sample conversations"""
        mem = WorkingMemory()
        for i in range(10):
            mem.store_conversation(
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                intent="TEST"
            )
            time.sleep(0.01)  # Ensure order
        return mem
    
    def test_get_recent_default(self, memory):
        """Test getting recent conversations (default limit)"""
        recent = memory.get_recent_conversations()
        
        assert len(recent) <= 5
        assert recent[0]["user_message"] == "Message 9"  # Most recent
        assert recent[-1]["user_message"] == "Message 5"
    
    def test_get_recent_custom_limit(self, memory):
        """Test custom limit"""
        recent = memory.get_recent_conversations(limit=3)
        
        assert len(recent) == 3
        assert recent[0]["user_message"] == "Message 9"
        assert recent[2]["user_message"] == "Message 7"
    
    def test_get_recent_empty(self):
        """Test recent conversations on empty memory"""
        memory = WorkingMemory()
        recent = memory.get_recent_conversations()
        
        assert len(recent) == 0


class TestConversationSearch:
    """Test conversation search functionality"""
    
    @pytest.fixture
    def memory(self):
        """Create memory with searchable conversations"""
        mem = WorkingMemory()
        mem.store_conversation(
            user_message="Add purple button to dashboard",
            assistant_response="Creating purple button component"
        )
        mem.store_conversation(
            user_message="Fix authentication bug",
            assistant_response="Fixing auth service"
        )
        mem.store_conversation(
            user_message="Add green button to sidebar",
            assistant_response="Creating green button"
        )
        return mem
    
    def test_search_by_keyword(self, memory):
        """Test searching by keyword"""
        results = memory.search_conversations("button")
        
        assert len(results) == 2
        assert all("button" in r["user_message"].lower() for r in results)
    
    def test_search_case_insensitive(self, memory):
        """Test case-insensitive search"""
        results = memory.search_conversations("BUTTON")
        
        assert len(results) == 2
    
    def test_search_no_results(self, memory):
        """Test search with no matches"""
        results = memory.search_conversations("nonexistent")
        
        assert len(results) == 0
    
    def test_search_in_response(self, memory):
        """Test searching in assistant responses"""
        results = memory.search_conversations("component")
        
        # "component" appears in 2 responses (purple and green button)
        assert len(results) >= 1  # At least one match
        assert any("component" in r["assistant_response"].lower() for r in results)


class TestEntityTracking:
    """Test entity tracking (files, classes, methods)"""
    
    @pytest.fixture
    def memory(self):
        """Create memory for entity tests"""
        return WorkingMemory()
    
    def test_track_file_entity(self, memory):
        """Test tracking file entities"""
        conv_id = memory.store_conversation(
            user_message="Modify AuthService.cs",
            assistant_response="Updating authentication"
        )
        
        memory.track_entity(
            conversation_id=conv_id,
            entity_type="file",
            entity_value="AuthService.cs",
            context="Modified for authentication"
        )
        
        entities = memory.get_entities(conv_id)
        
        assert len(entities) == 1
        assert entities[0]["entity_type"] == "file"
        assert entities[0]["entity_value"] == "AuthService.cs"
    
    def test_track_multiple_entities(self, memory):
        """Test tracking multiple entities in one conversation"""
        conv_id = memory.store_conversation(
            user_message="Refactor LoginController and AuthService",
            assistant_response="Refactoring complete"
        )
        
        memory.track_entity(conv_id, "file", "LoginController.cs")
        memory.track_entity(conv_id, "file", "AuthService.cs")
        memory.track_entity(conv_id, "class", "LoginController")
        memory.track_entity(conv_id, "method", "Login")
        
        entities = memory.get_entities(conv_id)
        
        assert len(entities) == 4
        assert sum(1 for e in entities if e["entity_type"] == "file") == 2
        assert sum(1 for e in entities if e["entity_type"] == "class") == 1
        assert sum(1 for e in entities if e["entity_type"] == "method") == 1
    
    def test_search_by_entity(self, memory):
        """Test finding conversations by entity"""
        # Create conversations with entities
        conv1 = memory.store_conversation(
            user_message="Modify AuthService",
            assistant_response="Done"
        )
        memory.track_entity(conv1, "file", "AuthService.cs")
        
        conv2 = memory.store_conversation(
            user_message="Test AuthService",
            assistant_response="Testing"
        )
        memory.track_entity(conv2, "file", "AuthService.cs")
        
        conv3 = memory.store_conversation(
            user_message="Update LoginController",
            assistant_response="Updated"
        )
        memory.track_entity(conv3, "file", "LoginController.cs")
        
        # Search for AuthService mentions
        results = memory.search_by_entity("file", "AuthService.cs")
        
        assert len(results) == 2
        assert all("AuthService" in r["user_message"] for r in results)


class TestPerformance:
    """Test performance requirements (<50ms)"""
    
    @pytest.fixture
    def memory(self):
        """Create memory with many conversations"""
        mem = WorkingMemory(max_conversations=20)
        for i in range(20):
            mem.store_conversation(
                user_message=f"Message {i}",
                assistant_response=f"Response {i}"
            )
        return mem
    
    def test_storage_performance(self):
        """Test conversation storage speed"""
        memory = WorkingMemory()
        
        start = time.perf_counter()
        memory.store_conversation(
            user_message="Performance test",
            assistant_response="Testing speed"
        )
        duration = (time.perf_counter() - start) * 1000  # Convert to ms
        
        assert duration < 50, f"Storage took {duration:.2f}ms (target: <50ms)"
    
    def test_retrieval_performance(self, memory):
        """Test conversation retrieval speed"""
        # Get a valid conversation ID
        recent = memory.get_recent_conversations(limit=1)
        conv_id = recent[0]["conversation_id"]
        
        start = time.perf_counter()
        conv = memory.get_conversation(conv_id)
        duration = (time.perf_counter() - start) * 1000
        
        assert conv is not None
        assert duration < 50, f"Retrieval took {duration:.2f}ms (target: <50ms)"
    
    def test_search_performance(self, memory):
        """Test search speed"""
        start = time.perf_counter()
        results = memory.search_conversations("message")
        duration = (time.perf_counter() - start) * 1000
        
        assert len(results) > 0
        assert duration < 100, f"Search took {duration:.2f}ms (target: <100ms)"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_message(self):
        """Test storing empty messages"""
        memory = WorkingMemory()
        conv_id = memory.store_conversation(
            user_message="",
            assistant_response=""
        )
        
        assert conv_id is not None
        conv = memory.get_conversation(conv_id)
        assert conv["user_message"] == ""
    
    def test_long_message(self):
        """Test storing very long messages"""
        memory = WorkingMemory()
        long_message = "x" * 10000
        
        conv_id = memory.store_conversation(
            user_message=long_message,
            assistant_response="Response"
        )
        
        conv = memory.get_conversation(conv_id)
        assert len(conv["user_message"]) == 10000
    
    def test_special_characters(self):
        """Test messages with special characters"""
        memory = WorkingMemory()
        special_msg = "Test: <>&\"'`\n\t\r{}"
        
        conv_id = memory.store_conversation(
            user_message=special_msg,
            assistant_response="Response"
        )
        
        conv = memory.get_conversation(conv_id)
        assert conv["user_message"] == special_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
