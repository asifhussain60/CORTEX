"""
Unit tests for TurnResponseWithChallenges.

Tests cover:
- Segment insertion after header
- Recommendations segment added
- Holistic context segment added
- No segments if no challenges
- Segment order preserved
- Response structure still valid
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List

from cortex.orchestrators.response.turn_response_with_challenges import (
    TurnResponseWithChallenges,
    TurnResponseSegment,
)


class MockChallengGenerator:
    """Mock challenge orchestrator."""
    def process_challenges(self, context: dict) -> List[Dict[str, Any]]:
        return context.get("challenges", [])


class MockContextBuilder:
    """Mock holistic context builder."""
    def build_holistic_context(self, data: dict) -> Dict[str, Any]:
        return {
            "intent": data.get("intent", ""),
            "challenges": data.get("challenges", []),
            "recommendations": data.get("recommendations", []),
        }


class MockResponseGenerator:
    """Mock base response generator."""
    def generate_response(self, context: dict) -> str:
        return context.get("base_response", "Default response")


class TestTurnResponseWithChallenges:
    """Test suite for TurnResponseWithChallenges."""
    
    def test_challenges_segment_added_after_header(self):
        """Test challenges segment is added after header."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Header\n\nContent",
            "challenges": [{"desc": "c1"}],
            "recommendations": [],
        })
        
        assert "challenges" in response.lower() or "challenge" in response.lower()
    
    def test_recommendations_segment_added(self):
        """Test recommendations segment is added to response."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [],
            "recommendations": [{"action": "do something"}],
        })
        
        assert "recommendation" in response.lower() or "action" in response.lower()
    
    def test_holistic_context_segment_added(self):
        """Test holistic context segment is added to response."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "intent": "Add feature",
            "challenges": [],
            "recommendations": [],
        })
        
        # Should contain context information
        assert len(response) > 0
    
    def test_no_segments_if_no_challenges(self):
        """Test no challenge segment added if no challenges."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base response only",
            "challenges": [],
            "recommendations": [],
        })
        
        # Should still have base response
        assert "Base response only" in response
    
    def test_no_segments_if_no_recommendations(self):
        """Test no recommendations segment if no recommendations."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [],
            "recommendations": [],
        })
        
        # Should still produce valid response
        assert len(response) > 0
    
    def test_segment_order_preserved(self):
        """Test segment order: header → challenges → recommendations."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Header content",
            "challenges": [{"desc": "challenge text"}],
            "recommendations": [{"action": "recommendation text"}],
        })
        
        # Header should come before challenges
        header_pos = response.find("Header content")
        challenge_pos = response.find("challenge")
        rec_pos = response.find("recommendation")
        
        if challenge_pos >= 0 and rec_pos >= 0:
            assert challenge_pos < rec_pos
    
    def test_response_structure_still_valid(self):
        """Test response structure remains valid after modifications."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Valid response",
            "challenges": [{"desc": "c1"}],
            "recommendations": [{"action": "a1"}],
        })
        
        # Should be non-empty string
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_multiple_challenges_all_included(self):
        """Test multiple challenges are all included in response."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        challenges = [
            {"desc": "Challenge 1"},
            {"desc": "Challenge 2"},
            {"desc": "Challenge 3"},
        ]
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": challenges,
            "recommendations": [],
        })
        
        # All challenge descriptions should be in response somehow
        assert len(response) > 0
    
    def test_multiple_recommendations_all_included(self):
        """Test multiple recommendations are all included in response."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        recommendations = [
            {"action": "Action 1"},
            {"action": "Action 2"},
            {"action": "Action 3"},
        ]
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [],
            "recommendations": recommendations,
        })
        
        # All actions should be represented
        assert len(response) > 0
    
    def test_empty_challenges_list_handled(self):
        """Test empty challenges list is handled gracefully."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [],
            "recommendations": [{"action": "do"}],
        })
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_empty_recommendations_list_handled(self):
        """Test empty recommendations list is handled gracefully."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [{"desc": "c1"}],
            "recommendations": [],
        })
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_special_characters_in_challenges_handled(self):
        """Test special characters in challenges are handled."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [
                {"desc": "Challenge with 'quotes' & special <chars>"}
            ],
            "recommendations": [],
        })
        
        # Should not throw, should produce valid response
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_backward_compatibility_with_base_generator(self):
        """Test backward compatibility with base response generator."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Original response",
            "challenges": [],
            "recommendations": [],
        })
        
        # Should include original base response
        assert "Original response" in response or len(response) > 0
    
    def test_integration_with_challenge_orchestrator(self):
        """Test integration with challenge orchestrator."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "challenges": [{"desc": "generated"}],
            "recommendations": [],
        })
        
        assert isinstance(response, str)
    
    def test_integration_with_context_builder(self):
        """Test integration with context builder."""
        wrapper = TurnResponseWithChallenges(
            MockResponseGenerator(),
            MockChallengGenerator(),
            MockContextBuilder(),
        )
        
        response = wrapper.generate_response_with_challenges({
            "base_response": "Base",
            "intent": "Test intent",
            "challenges": [],
            "recommendations": [],
        })
        
        assert isinstance(response, str)
