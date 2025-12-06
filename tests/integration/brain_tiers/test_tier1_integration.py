"""
Integration tests for Tier 1 (Working Memory).

Tests conversation storage, retrieval, and cross-tier integration.
"""

import pytest


def test_tier1_initialization(temp_brain):
    """Test Tier 1 working memory initialization."""
    from src.tier1.working_memory import WorkingMemory
    
    memory = WorkingMemory(brain_path=temp_brain)
    
    assert memory is not None
    assert memory.is_initialized()


def test_tier1_conversation_storage(temp_brain):
    """Test conversation storage and retrieval."""
    from src.tier1.working_memory import WorkingMemory
    
    memory = WorkingMemory(brain_path=temp_brain)
    
    # Store conversation
    memory.store_conversation(
        session_id="test-session-001",
        user_message="What is CORTEX?",
        assistant_response="CORTEX is an AI assistant enhancement system.",
        intent="general_query"
    )
    
    # Retrieve conversations
    conversations = memory.get_recent_conversations(limit=5)
    
    assert len(conversations) > 0
    assert conversations[0]["session_id"] == "test-session-001"
    assert conversations[0]["user_message"] == "What is CORTEX?"


def test_tier1_fifo_limit(temp_brain):
    """Test FIFO limit (70 conversations)."""
    from src.tier1.working_memory import WorkingMemory
    
    memory = WorkingMemory(brain_path=temp_brain)
    
    # Store 75 conversations
    for i in range(75):
        memory.store_conversation(
            session_id=f"test-{i}",
            user_message=f"Message {i}",
            assistant_response=f"Response {i}",
            intent="test"
        )
    
    # Verify only 70 remain
    conversations = memory.get_all_conversations()
    
    assert len(conversations) <= 70
    # Oldest should be removed
    session_ids = [c["session_id"] for c in conversations]
    assert "test-0" not in session_ids  # First should be removed
    assert "test-74" in session_ids  # Last should remain


def test_tier1_tier2_integration(temp_brain):
    """Test Tier 1 integration with Tier 2 for pattern learning."""
    from src.tier1.working_memory import WorkingMemory
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    memory = WorkingMemory(brain_path=temp_brain)
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Store conversation
    memory.store_conversation(
        session_id="learning-001",
        user_message="How do I implement TDD?",
        assistant_response="Follow RED-GREEN-REFACTOR cycle",
        intent="tdd_query"
    )
    
    # Tier 2 should be able to query Tier 1 data for patterns
    conversations = memory.get_conversations_by_intent("tdd_query")
    
    assert len(conversations) > 0
    
    # Store pattern learned from conversation
    pattern_id = kg.store_pattern(
        pattern_type="tdd_question",
        description=f"TDD query from session learning-001",
        confidence=0.8
    )
    
    assert pattern_id is not None
