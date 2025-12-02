"""
CORTEX Phase 7 - Deliverable 7.5: FIFO Conversation Management
TDD Test Suite (RED Phase)

Tests for:
1. 70-conversation limit (increased from 20)
2. Auto-archive to Tier 2 when threshold exceeded
3. Manual override: keep important conversations
4. <100ms query performance validation

Author: Asif Hussain
Created: December 2, 2025
"""

import pytest
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from src.tier1.working_memory import WorkingMemory
from src.tier2.knowledge_graph import KnowledgeGraph


class TestFIFO70ConversationLimit:
    """Test updated 70-conversation FIFO limit"""
    
    @pytest.fixture
    def working_memory(self, tmp_path):
        """Create temporary working memory instance"""
        db_path = tmp_path / "test_fifo.db"
        return WorkingMemory(db_path=db_path)
    
    def test_fifo_limit_is_70_conversations(self, working_memory):
        """Test that FIFO limit is set to 70 conversations"""
        assert working_memory.MAX_CONVERSATIONS == 70, "FIFO limit should be 70 conversations"
    
    def test_queue_manager_has_70_limit(self, working_memory):
        """Test that QueueManager uses 70-conversation limit"""
        assert working_memory.queue_manager.MAX_CONVERSATIONS == 70
    
    def test_no_eviction_below_70_conversations(self, working_memory):
        """Test that no eviction occurs when below 70 conversation limit"""
        # Add 60 conversations (below limit)
        for i in range(60):
            working_memory.store_conversation(
                user_message=f"Test message {i}",
                assistant_response=f"Response {i}",
                intent="test"
            )
        
        # Check queue status
        status = working_memory.queue_manager.get_queue_status()
        
        assert status['current_count'] == 60
        assert status['available_slots'] == 10
        assert not status['is_at_capacity']
    
    def test_eviction_at_71_conversations(self, working_memory):
        """Test that oldest conversation is evicted at 71st conversation"""
        # Add 70 conversations
        conv_ids = []
        for i in range(70):
            conv_id = working_memory.store_conversation(
                user_message=f"Test message {i}",
                assistant_response=f"Response {i}",
                intent="test"
            )
            conv_ids.append(conv_id)
        
        # Mark first conversation as inactive
        working_memory.mark_conversation_inactive(conv_ids[0])
        
        # Add 71st conversation (should trigger eviction)
        working_memory.store_conversation(
            user_message="Message 71",
            assistant_response="Response 71",
            intent="test"
        )
        
        # First conversation should be evicted
        status = working_memory.queue_manager.get_queue_status()
        assert status['current_count'] == 70
        
        # Check eviction log
        log = working_memory.queue_manager.get_eviction_log()
        assert len(log) >= 1
        assert log[0]['event_type'] == 'conversation_evicted'


class TestAutoArchiveToTier2:
    """Test automatic archival of evicted conversations to Tier 2"""
    
    @pytest.fixture
    def working_memory(self, tmp_path):
        """Create working memory instance"""
        db_path = tmp_path / "test_archive_tier1.db"
        return WorkingMemory(db_path=db_path)
    
    @pytest.fixture
    def knowledge_graph(self, tmp_path):
        """Create knowledge graph instance"""
        db_path = tmp_path / "test_archive_tier2.db"
        return KnowledgeGraph(db_path=str(db_path))
    
    def test_archive_conversation_to_tier2_exists(self, working_memory):
        """Test that archive_conversation_to_tier2 method exists"""
        assert hasattr(working_memory, 'archive_conversation_to_tier2')
    
    def test_archive_conversation_to_tier2_preserves_data(self, working_memory, knowledge_graph):
        """Test that archived conversation preserves all data in Tier 2"""
        # Create conversation
        conv_id = working_memory.store_conversation(
            user_message="Important conversation",
            assistant_response="Important response",
            intent="test"
        )
        
        # Get original conversation data
        original_conv = working_memory.get_conversation(conv_id)
        original_messages = working_memory.get_messages(conv_id)
        
        # Archive to Tier 2
        result = working_memory.archive_conversation_to_tier2(
            conversation_id=conv_id,
            knowledge_graph=knowledge_graph
        )
        
        assert result is True, "Archival should succeed"
        
        # Verify data in Tier 2
        archived_pattern = knowledge_graph.get_pattern(f"conv_{conv_id}")
        assert archived_pattern is not None
        assert "conversation" in archived_pattern['content'].lower()
    
    def test_eviction_triggers_automatic_archive(self, working_memory, knowledge_graph, tmp_path):
        """Test that FIFO eviction automatically archives to Tier 2"""
        # Connect Tier 2 to working memory
        working_memory.tier2 = knowledge_graph
        
        # Fill to capacity (70 conversations)
        for i in range(70):
            working_memory.store_conversation(
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                intent="test"
            )
        
        # Mark first 10 as inactive
        convs = working_memory.list_conversations(limit=70)
        for conv in convs[:10]:
            working_memory.mark_conversation_inactive(conv['conversation_id'])
        
        # Add 71st conversation (triggers eviction + archive)
        working_memory.store_conversation(
            user_message="Overflow message",
            assistant_response="Overflow response",
            intent="test"
        )
        
        # Check that archived pattern exists in Tier 2
        # Should have at least 1 archived conversation
        patterns = knowledge_graph.list_patterns(pattern_type='archived_conversation')
        assert len(patterns) >= 1, "Should have archived at least one conversation"
    
    def test_archived_conversation_includes_metadata(self, working_memory, knowledge_graph):
        """Test that archived conversations include metadata"""
        conv_id = working_memory.store_conversation(
            user_message="Test",
            assistant_response="Response",
            intent="test"
        )
        
        working_memory.archive_conversation_to_tier2(
            conversation_id=conv_id,
            knowledge_graph=knowledge_graph
        )
        
        pattern = knowledge_graph.get_pattern(f"conv_{conv_id}")
        assert pattern is not None
        assert 'metadata' in pattern or 'context_json' in pattern


class TestManualOverride:
    """Test manual override to keep important conversations"""
    
    @pytest.fixture
    def working_memory(self, tmp_path):
        """Create working memory instance"""
        db_path = tmp_path / "test_override.db"
        return WorkingMemory(db_path=db_path)
    
    def test_pin_conversation_method_exists(self, working_memory):
        """Test that pin_conversation method exists"""
        assert hasattr(working_memory, 'pin_conversation')
    
    def test_unpin_conversation_method_exists(self, working_memory):
        """Test that unpin_conversation method exists"""
        assert hasattr(working_memory, 'unpin_conversation')
    
    def test_pin_conversation_prevents_eviction(self, working_memory):
        """Test that pinned conversations are not evicted"""
        # Create and pin a conversation
        pinned_conv_id = working_memory.store_conversation(
            user_message="Important pinned conversation",
            assistant_response="Important response",
            intent="test"
        )
        working_memory.pin_conversation(pinned_conv_id)
        
        # Fill to capacity
        for i in range(70):
            working_memory.store_conversation(
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                intent="test"
            )
        
        # Mark all except pinned as inactive
        convs = working_memory.list_conversations(limit=71)
        for conv in convs:
            if conv['conversation_id'] != pinned_conv_id:
                working_memory.mark_conversation_inactive(conv['conversation_id'])
        
        # Add one more conversation (should evict non-pinned, not pinned)
        working_memory.store_conversation(
            user_message="Overflow",
            assistant_response="Response",
            intent="test"
        )
        
        # Verify pinned conversation still exists
        pinned_conv = working_memory.get_conversation(pinned_conv_id)
        assert pinned_conv is not None, "Pinned conversation should not be evicted"
    
    def test_list_pinned_conversations(self, working_memory):
        """Test listing all pinned conversations"""
        # Create and pin multiple conversations
        pinned_ids = []
        for i in range(3):
            conv_id = working_memory.store_conversation(
                user_message=f"Pinned {i}",
                assistant_response=f"Response {i}",
                intent="test"
            )
            working_memory.pin_conversation(conv_id)
            pinned_ids.append(conv_id)
        
        # Get list of pinned conversations
        pinned = working_memory.list_pinned_conversations()
        
        assert len(pinned) == 3
        assert all(p['conversation_id'] in pinned_ids for p in pinned)
    
    def test_unpin_conversation_allows_eviction(self, working_memory):
        """Test that unpinning allows conversation to be evicted"""
        # Create and pin conversation
        conv_id = working_memory.store_conversation(
            user_message="Initially pinned",
            assistant_response="Response",
            intent="test"
        )
        working_memory.pin_conversation(conv_id)
        
        # Verify pinned
        assert working_memory.is_conversation_pinned(conv_id)
        
        # Unpin
        working_memory.unpin_conversation(conv_id)
        
        # Verify unpinned
        assert not working_memory.is_conversation_pinned(conv_id)


class TestPerformanceValidation:
    """Test <100ms query performance with 70 conversations"""
    
    @pytest.fixture
    def working_memory_with_70_convs(self, tmp_path):
        """Create working memory with 70 conversations"""
        db_path = tmp_path / "test_performance.db"
        wm = WorkingMemory(db_path=db_path)
        
        # Add 70 conversations
        for i in range(70):
            wm.store_conversation(
                user_message=f"Performance test message {i}",
                assistant_response=f"Performance response {i}",
                intent="test"
            )
        
        return wm
    
    def test_list_conversations_performance(self, working_memory_with_70_convs):
        """Test that listing conversations takes <100ms with 70 conversations"""
        start_time = time.perf_counter()
        
        conversations = working_memory_with_70_convs.list_conversations(limit=70)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        assert duration_ms < 100, f"list_conversations took {duration_ms:.2f}ms (should be <100ms)"
        assert len(conversations) == 70
    
    def test_get_conversation_performance(self, working_memory_with_70_convs):
        """Test that getting a single conversation takes <50ms"""
        # Get a conversation ID
        convs = working_memory_with_70_convs.list_conversations(limit=1)
        conv_id = convs[0]['conversation_id']
        
        start_time = time.perf_counter()
        
        conversation = working_memory_with_70_convs.get_conversation(conv_id)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        assert duration_ms < 50, f"get_conversation took {duration_ms:.2f}ms (should be <50ms)"
        assert conversation is not None
    
    def test_queue_status_performance(self, working_memory_with_70_convs):
        """Test that queue status check takes <25ms"""
        start_time = time.perf_counter()
        
        status = working_memory_with_70_convs.queue_manager.get_queue_status()
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        assert duration_ms < 25, f"get_queue_status took {duration_ms:.2f}ms (should be <25ms)"
        assert status['current_count'] == 70
    
    def test_eviction_performance(self, working_memory_with_70_convs):
        """Test that FIFO eviction takes <100ms"""
        # Mark all as inactive
        convs = working_memory_with_70_convs.list_conversations(limit=70)
        for conv in convs:
            working_memory_with_70_convs.mark_conversation_inactive(conv['conversation_id'])
        
        start_time = time.perf_counter()
        
        # Trigger eviction by adding 71st conversation
        working_memory_with_70_convs.store_conversation(
            user_message="Eviction trigger",
            assistant_response="Response",
            intent="test"
        )
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # Eviction + store should be <100ms total
        assert duration_ms < 100, f"Eviction took {duration_ms:.2f}ms (should be <100ms)"


class TestFIFOIntegration:
    """Integration tests for complete FIFO system"""
    
    @pytest.fixture
    def full_system(self, tmp_path):
        """Create full system with Tier 1 and Tier 2"""
        tier1_path = tmp_path / "tier1.db"
        tier2_path = tmp_path / "tier2.db"
        
        wm = WorkingMemory(db_path=tier1_path)
        kg = KnowledgeGraph(db_path=str(tier2_path))
        
        wm.tier2 = kg
        
        return {'tier1': wm, 'tier2': kg}
    
    def test_full_fifo_cycle_with_archive(self, full_system):
        """Test complete FIFO cycle: fill → evict → archive → verify"""
        wm = full_system['tier1']
        kg = full_system['tier2']
        
        # Fill to capacity
        first_conv_id = None
        for i in range(70):
            conv_id = wm.store_conversation(
                user_message=f"Cycle message {i}",
                assistant_response=f"Cycle response {i}",
                intent="test"
            )
            if i == 0:
                first_conv_id = conv_id
        
        # Mark first conversation as inactive
        wm.mark_conversation_inactive(first_conv_id)
        
        # Add 71st conversation
        wm.store_conversation(
            user_message="Overflow",
            assistant_response="Response",
            intent="test"
        )
        
        # Verify FIFO maintained 70 limit
        status = wm.queue_manager.get_queue_status()
        assert status['current_count'] == 70
        
        # Verify first conversation archived to Tier 2
        archived = kg.get_pattern(f"conv_{first_conv_id}")
        assert archived is not None or len(kg.list_patterns(pattern_type='archived_conversation')) > 0
