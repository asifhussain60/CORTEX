"""
Test Dual-Channel Memory Integration (Step 5)
==============================================

Tests the integration of ConversationalChannelAdapter with dual_channel_memory.py
and validates the fusion layer for unified narrative generation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json

from src.cortex_3_0.dual_channel_memory import (
    DualChannelMemory,
    ConversationalChannel,
    TraditionalChannel,
    IntelligentFusion
)
from src.tier1.working_memory import WorkingMemory


@pytest.fixture
def temp_cortex_brain():
    """Create temporary CORTEX brain directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_path = Path(tmpdir) / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        yield brain_path


@pytest.fixture
def dual_channel_memory(temp_cortex_brain):
    """Create DualChannelMemory instance for testing"""
    return DualChannelMemory(temp_cortex_brain)


class TestConversationalChannelIntegration:
    """Test ConversationalChannel with ConversationalChannelAdapter"""
    
    def test_store_conversation_via_adapter(self, dual_channel_memory):
        """Test storing conversation through adapter integration"""
        # Store conversation
        conv_id = dual_channel_memory.store_conversation(
            user_message="How do I implement feature X?",
            assistant_response="To implement feature X, you should: 1. Define the interface, 2. Create implementation, 3. Add tests.",
            intent="IMPLEMENT_FEATURE"
        )
        
        assert conv_id is not None
        # WorkingMemory.import_conversation generates IDs with "imported-conv-" prefix
        assert conv_id.startswith("imported-conv-")
    
    def test_retrieve_conversation_with_semantic_data(self, dual_channel_memory):
        """Test retrieving conversation includes semantic metadata"""
        # Store conversation with entities
        conv_id = dual_channel_memory.store_conversation(
            user_message="Update the User class in models.py",
            assistant_response="I'll update the User class with the new fields.",
            intent="UPDATE_CODE",
            entities=["User", "models.py"],
            context_references=["the class", "it"]
        )
        
        # Retrieve
        context = dual_channel_memory.conversational_channel.get_conversation_context(conv_id)
        
        assert context is not None
        assert context["success"] is True
        assert "conversation" in context
        assert "semantic_data" in context["conversation"]
        assert context["conversation"]["semantic_data"]["intent"] == "UPDATE_CODE"
        assert "User" in context["conversation"]["semantic_data"]["entities"]
    
    def test_quality_assessment(self, dual_channel_memory):
        """Test quality assessment in stored conversations"""
        # Store detailed conversation (should have high quality)
        conv_id = dual_channel_memory.store_conversation(
            user_message="Can you help me refactor the authentication module to use JWT tokens instead of session-based auth? I need it to support refresh tokens and proper expiration handling.",
            assistant_response="""To refactor authentication to JWT:

```python
class JWTAuthenticator:
    def generate_token(self, user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

This provides secure token-based authentication with proper expiration.""",
            intent="REFACTOR_CODE"
        )
        
        # Retrieve and check quality
        context = dual_channel_memory.conversational_channel.get_conversation_context(conv_id)
        
        assert context is not None
        quality = context["quality_score"]
        
        # Detailed message + code blocks = high quality (should be 7+)
        assert quality >= 7.0, f"Expected quality >= 7.0, got {quality}"
    
    def test_statistics_via_adapter(self, dual_channel_memory):
        """Test statistics retrieval through adapter"""
        # Store multiple conversations
        for i in range(3):
            dual_channel_memory.store_conversation(
                user_message=f"Question {i}",
                assistant_response=f"Answer {i}",
                intent="TEST"
            )
        
        # Get statistics
        stats = dual_channel_memory.conversational_channel.get_statistics()
        
        assert stats["total_conversations"] >= 3
        assert stats["total_messages"] >= 6  # 2 messages per conversation


class TestTraditionalChannelIntegration:
    """Test TraditionalChannel storage and retrieval"""
    
    def test_store_execution(self, dual_channel_memory):
        """Test storing traditional execution events"""
        event_id = dual_channel_memory.store_execution(
            operation="document_cortex",
            parameters={"module": "tier1", "format": "markdown"},
            result={"success": True, "files_generated": 3},
            execution_time_ms=1500,
            success=True
        )
        
        assert event_id is not None
        assert event_id.startswith("trad_")
    
    def test_retrieve_recent_executions(self, dual_channel_memory):
        """Test retrieving recent execution events"""
        # Store executions
        for i in range(5):
            dual_channel_memory.store_execution(
                operation=f"test_operation_{i}",
                parameters={"index": i},
                result={"completed": True},
                execution_time_ms=100,
                success=True
            )
        
        # Retrieve recent
        recent = dual_channel_memory.traditional_channel.get_recent_executions(3)
        
        assert len(recent) == 3
        assert all("operation" in event for event in recent)


class TestIntelligentFusion:
    """Test fusion layer correlation and unified narrative generation"""
    
    def test_correlate_channels_time_window(self, dual_channel_memory):
        """Test correlating events across channels within time window"""
        # Store related conversation and execution
        conv_id = dual_channel_memory.store_conversation(
            user_message="Run the optimize command",
            assistant_response="I'll run the optimize command for you.",
            intent="EXECUTE_COMMAND"
        )
        
        exec_id = dual_channel_memory.store_execution(
            operation="optimize_cortex",
            parameters={"phase": "all"},
            result={"success": True, "optimizations": 5},
            execution_time_ms=2000,
            success=True
        )
        
        # Get unified narratives
        narratives = dual_channel_memory.get_unified_narrative(time_window_minutes=30)
        
        # Should have at least one narrative correlating the conversation and execution
        assert len(narratives) > 0
        
        # Check narrative structure
        narrative = narratives[0]
        assert "type" in narrative
        assert narrative["type"] == "unified_narrative"
        assert "conversation_id" in narrative
        assert "executions" in narrative
        assert "timeline" in narrative
        assert "outcome" in narrative
    
    def test_unified_narrative_structure(self, dual_channel_memory):
        """Test complete unified narrative structure"""
        # Store conversation
        conv_id = dual_channel_memory.store_conversation(
            user_message="Implement feature X",
            assistant_response="Implementing feature X with tests.",
            intent="IMPLEMENT"
        )
        
        # Store related executions
        dual_channel_memory.store_execution(
            operation="create_feature",
            parameters={"name": "X"},
            result={"success": True},
            execution_time_ms=1000,
            success=True
        )
        
        dual_channel_memory.store_execution(
            operation="run_tests",
            parameters={"feature": "X"},
            result={"passed": 10, "failed": 0},
            execution_time_ms=500,
            success=True
        )
        
        # Get narratives
        narratives = dual_channel_memory.get_unified_narrative()
        
        assert len(narratives) > 0
        
        narrative = narratives[0]
        
        # Verify complete structure
        assert narrative["user_request"] == "Implement feature X"
        assert narrative["intent"] == "IMPLEMENT"
        assert len(narrative["executions"]) == 2
        assert len(narrative["timeline"]) == 3  # 1 conversation + 2 executions
        assert narrative["outcome"] == "successful"
        assert narrative["learning_value"] in ["high", "medium", "low"]
    
    def test_outcome_determination(self, dual_channel_memory):
        """Test outcome determination for narratives"""
        # Test successful outcome
        conv_id = dual_channel_memory.store_conversation(
            user_message="Fix bug",
            assistant_response="Fixed the bug",
            intent="FIX"
        )
        
        dual_channel_memory.store_execution(
            operation="fix_bug",
            parameters={},
            result={"fixed": True},
            execution_time_ms=500,
            success=True
        )
        
        narratives = dual_channel_memory.get_unified_narrative()
        assert len(narratives) > 0
        assert narratives[0]["outcome"] == "successful"
    
    def test_learning_value_assessment(self, dual_channel_memory):
        """Test learning value assessment for Tier 2"""
        # High-value: Detailed conversation + successful execution
        conv_id = dual_channel_memory.store_conversation(
            user_message="How do I implement a complex feature with multiple components and proper error handling?",
            assistant_response="Here's a comprehensive implementation with error handling and tests.",
            intent="IMPLEMENT"
        )
        
        dual_channel_memory.store_execution(
            operation="implement_feature",
            parameters={"complexity": "high"},
            result={"success": True, "files": 5},
            execution_time_ms=3000,
            success=True
        )
        
        narratives = dual_channel_memory.get_unified_narrative()
        
        assert len(narratives) > 0
        # Complex conversation (>10 words) + successful execution = high learning value
        assert narratives[0]["learning_value"] in ["high", "medium"]


class TestDualChannelMemoryIntegration:
    """End-to-end integration tests for dual-channel memory"""
    
    def test_complete_workflow(self, dual_channel_memory):
        """Test complete workflow: store, correlate, retrieve"""
        # 1. Store conversation
        conv_id = dual_channel_memory.store_conversation(
            user_message="Optimize the database",
            assistant_response="Running optimization",
            intent="OPTIMIZE"
        )
        
        # 2. Store execution
        exec_id = dual_channel_memory.store_execution(
            operation="optimize_database",
            parameters={"tables": ["users", "posts"]},
            result={"optimized": 2, "time_saved_ms": 500},
            execution_time_ms=2000,
            success=True
        )
        
        # 3. Get unified narrative
        narratives = dual_channel_memory.get_unified_narrative()
        
        assert len(narratives) > 0
        assert narratives[0]["conversation_id"] == conv_id
        assert len(narratives[0]["executions"]) >= 1
        
        # 4. Get development context
        context = dual_channel_memory.get_development_context(conv_id)
        
        assert "unified_narratives" in context
        assert "recent_conversations" in context
        assert "recent_executions" in context
        assert "current_conversation" in context
    
    def test_search_across_channels(self, dual_channel_memory):
        """Test searching across both channels"""
        # Store in both channels
        dual_channel_memory.store_conversation(
            user_message="Implement authentication",
            assistant_response="Adding JWT authentication",
            intent="IMPLEMENT"
        )
        
        dual_channel_memory.store_execution(
            operation="add_authentication",
            parameters={"type": "JWT"},
            result={"success": True},
            execution_time_ms=1000,
            success=True
        )
        
        # Search across channels
        results = dual_channel_memory.search_memory("authentication")
        
        # Should find results from both channels
        assert len(results) >= 2
        channels = [r.get("channel") for r in results]
        assert "conversational" in channels
        assert "traditional" in channels
    
    def test_session_persistence(self, dual_channel_memory):
        """Test that data persists across dual-channel memory lifecycle"""
        # Store data
        conv_id = dual_channel_memory.store_conversation(
            user_message="Test persistence",
            assistant_response="Testing",
            intent="TEST"
        )
        
        exec_id = dual_channel_memory.store_execution(
            operation="test_operation",
            parameters={},
            result={"success": True},
            execution_time_ms=100,
            success=True
        )
        
        # Create new instance (simulates new session)
        new_instance = DualChannelMemory(dual_channel_memory.cortex_brain_path)
        
        # Retrieve data
        context = new_instance.conversational_channel.get_conversation_context(conv_id)
        executions = new_instance.traditional_channel.get_recent_executions(5)
        
        assert context is not None
        assert context["success"] is True
        assert len(executions) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
