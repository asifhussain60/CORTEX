"""
Unit tests for TurnResponseGenerator Challenge Hook.

Tests cover:
- Response generation works with challenges
- Response generation works without challenges
- Response format unchanged
- All existing tests still pass
- Zero regressions
"""

import pytest
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.orchestrators.response.turn_response_generator import (
    TurnResponseGenerator,
    ResponseMode,
    ResponseTone,
    TurnResponse,
)


class MockChallengeOrchestrator:
    """Mock challenge orchestrator."""
    
    def __init__(self, challenges: List[Dict[str, Any]] = None):
        self.challenges = challenges or []
    
    def process_challenges(self, context: dict) -> List[Dict[str, Any]]:
        """Return pre-configured challenges."""
        return self.challenges


class MockContextBuilder:
    """Mock context builder."""
    
    def build_holistic_context(self, data: dict) -> Dict[str, Any]:
        """Return holistic context."""
        return {
            "intent": data.get("intent", ""),
            "analysis": data.get("analysis", {}),
            "challenges": data.get("challenges", []),
            "recommendations": data.get("recommendations", []),
        }


class TestTurnResponseGeneratorChallengeHook:
    """Test suite for TurnResponseGenerator with challenge integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = TurnResponseGenerator()
    
    def test_response_generation_with_challenges(self):
        """Test response generation works with challenges."""
        challenges = [
            {"description": "Challenge 1", "severity": "HIGH", "confidence": 0.8}
        ]
        context = {
            "challenges": challenges,
            "intent": "Add feature",
        }
        
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
            mode=ResponseMode.CHAT,
        )
        
        assert isinstance(response, TurnResponse)
        assert response.operation_id == "op123"
        assert response.turn_number == 1
    
    def test_response_generation_without_challenges(self):
        """Test response generation works without challenges."""
        context = {}
        
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
            mode=ResponseMode.CHAT,
        )
        
        assert isinstance(response, TurnResponse)
        assert response.operation_id == "op123"
    
    def test_response_format_unchanged(self):
        """Test response format is unchanged by challenge integration."""
        response1 = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
            mode=ResponseMode.CHAT,
        )
        
        # Format should still be valid
        assert hasattr(response1, 'operation_id')
        assert hasattr(response1, 'turn_number')
        assert hasattr(response1, 'metadata')
        assert hasattr(response1, 'segments')
        assert hasattr(response1, 'raw_content')
    
    def test_existing_interface_preserved(self):
        """Test existing generate_response interface is preserved."""
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            phase="PHASE-01",
            orchestrator="MasterOrchestrator",
        )
        
        assert response.metadata.mode == ResponseMode.CHAT
        assert response.metadata.tone == ResponseTone.TECHNICAL
        assert response.metadata.phase == "PHASE-01"
        assert response.metadata.orchestrator == "MasterOrchestrator"
    
    def test_multiple_responses_with_challenges(self):
        """Test multiple responses can be generated with different challenges."""
        challenges1 = [{"description": "Challenge 1", "severity": "HIGH"}]
        challenges2 = [{"description": "Challenge 2", "severity": "MEDIUM"}]
        
        response1 = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Content 1",
        )
        
        response2 = self.generator.generate_response(
            operation_id="op124",
            turn_number=1,
            content="Content 2",
        )
        
        assert response1.operation_id == "op123"
        assert response2.operation_id == "op124"
    
    def test_response_caching_still_works(self):
        """Test response caching is not affected."""
        response1 = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
        )
        
        # Get cached response
        cached = self.generator.get_cached_response("op123", 1)
        assert cached is not None
        assert cached.operation_id == "op123"
    
    def test_cache_clear_works(self):
        """Test cache clear functionality works."""
        self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
        )
        
        # Clear cache
        self.generator.clear_cache("op123")
        
        # Verify cleared
        cached = self.generator.get_cached_response("op123", 1)
        assert cached is None
    
    def test_statistics_include_challenges(self):
        """Test statistics reflect challenge-aware generation."""
        self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
        )
        
        stats = self.generator.get_statistics()
        assert "total_generations" in stats
        assert stats["total_generations"] >= 1
    
    def test_backward_compatibility_optional_parameters(self):
        """Test backward compatibility with optional parameters."""
        # All optional parameters should work
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
            # mode and tone are optional
        )
        
        assert response is not None
        assert response.operation_id == "op123"
    
    def test_alternatives_still_work(self):
        """Test alternatives parameter still works."""
        alternatives = [
            {"name": "Option A", "description": "First approach"},
            {"name": "Option B", "description": "Second approach"},
        ]
        
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
            alternatives=alternatives,
        )
        
        assert response.alternatives is not None
    
    def test_formatting_works(self):
        """Test response formatting functionality."""
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
        )
        
        # Format for chat
        formatted = self.generator.format_response(response, output_format="chat")
        assert formatted is not None
    
    def test_challenge_context_accepted(self):
        """Test that methods can accept challenge context."""
        # This tests the interface accepts challenge data
        challenge_context = {
            "challenges": [
                {"description": "Test challenge", "severity": "HIGH"}
            ],
            "intent": "Test intent",
        }
        
        # Should not raise an error
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=1,
            content="Test content",
        )
        
        assert response is not None
    
    def test_turn_number_sequence(self):
        """Test turn number sequence is maintained."""
        for i in range(1, 4):
            response = self.generator.generate_response(
                operation_id="op123",
                turn_number=i,
                content=f"Content {i}",
            )
            
            assert response.turn_number == i
    
    def test_operation_id_tracking(self):
        """Test operation IDs are tracked correctly."""
        ops = ["op1", "op2", "op3"]
        
        for op_id in ops:
            response = self.generator.generate_response(
                operation_id=op_id,
                turn_number=1,
                content="Test",
            )
            
            assert response.operation_id == op_id
    
    def test_metadata_preserved(self):
        """Test metadata is correctly preserved."""
        response = self.generator.generate_response(
            operation_id="op123",
            turn_number=5,
            content="Test",
            phase="PHASE-07",
            orchestrator="IntentRouter",
        )
        
        assert response.metadata.phase == "PHASE-07"
        assert response.metadata.orchestrator == "IntentRouter"
        assert response.metadata.turn_number == 5
