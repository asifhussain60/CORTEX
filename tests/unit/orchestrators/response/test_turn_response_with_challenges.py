"""
Unit tests for TurnResponseWithChallenges.

Tests cover:
- Challenges segment added after header
- Recommendations segment added
- Holistic context segment added
- No segments if no challenges/recommendations
- Segment order preserved
- Response structure validity
"""

import pytest
from typing import List, Dict, Any

from cortex.orchestrators.response.turn_response_with_challenges import (
    TurnResponseWithChallenges,
    TurnResponseSegment,
)


class MockBaseResponseGenerator:
    """Mock base response generator."""
    
    def generate_response(self, context: dict) -> str:
        """Generate basic response."""
        return "## Base Response\nHello, this is the base response."


class MockChallengeOrchestrator:
    """Mock challenge orchestrator."""
    
    def __init__(self, challenges: List[Dict[str, Any]] = None):
        self.challenges = challenges or []
    
    def process_challenges(self, context: dict) -> List[Dict[str, Any]]:
        """Return pre-configured challenges."""
        return self.challenges


class MockContextBuilder:
    """Mock holistic context builder."""
    
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
    
    def build_holistic_context(self, data: dict) -> Dict[str, Any]:
        """Return pre-configured context."""
        return self.context


class TestTurnResponseWithChallenges:
    """Test suite for TurnResponseWithChallenges."""
    
    def test_challenges_segment_added_after_header(self):
        """Test challenges segment is added after header."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "SQL injection risk", "severity": "HIGH", "confidence": 0.8}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "## Challenges Identified" in response
        assert "SQL injection risk" in response
        assert response.index("## Base Response") < response.index("## Challenges Identified")
    
    def test_recommendations_segment_added(self):
        """Test recommendations segment is added."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": [
                {"action": "Add tests", "priority": 1}
            ]
        }
        response = wrapper.generate_response_with_challenges(context)
        
        assert "## Recommendations" in response
        assert "Add tests" in response
    
    def test_holistic_context_segment_added(self):
        """Test holistic context segment is added."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_data = {
            "intent": "Add feature",
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": {}
        }
        context_builder = MockContextBuilder(context=context_data)
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        # Holistic context should be included
        assert len(response) > 0
        assert "Base Response" in response
    
    def test_no_segments_if_no_challenges(self):
        """Test no challenge segment if no challenges."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "## Challenges Identified" not in response
    
    def test_no_segments_if_no_recommendations(self):
        """Test no recommendations segment if none provided."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "## Recommendations" not in response
    
    def test_segment_order_preserved(self):
        """Test segments appear in correct order."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "Issue 1", "severity": "HIGH", "confidence": 0.8}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": [
                {"action": "Action 1", "priority": 1}
            ]
        }
        response = wrapper.generate_response_with_challenges(context)
        
        base_pos = response.index("## Base Response")
        challenges_pos = response.index("## Challenges Identified")
        recommendations_pos = response.index("## Recommendations")
        
        assert base_pos < challenges_pos < recommendations_pos
    
    def test_response_structure_remains_valid(self):
        """Test response structure is valid after injection."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "Issue", "severity": "HIGH", "confidence": 0.8}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        # Check structure validity
        assert isinstance(response, str)
        assert len(response) > 0
        assert "## Base Response" in response
        assert "Hello, this is the base response." in response
    
    def test_challenge_with_severity_formatting(self):
        """Test challenge severity is formatted correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "Test issue", "severity": "CRITICAL", "confidence": 0.9}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "Severity: CRITICAL" in response
    
    def test_challenge_with_confidence_formatting(self):
        """Test challenge confidence is formatted correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "Test issue", "severity": "HIGH", "confidence": 0.75}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "Confidence: 75%" in response
    
    def test_challenge_with_mitigation_formatting(self):
        """Test challenge mitigation is formatted correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {
                "description": "Test issue",
                "severity": "HIGH",
                "confidence": 0.8,
                "mitigation": "Use safe functions"
            }
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "Mitigation: Use safe functions" in response
    
    def test_recommendation_with_priority_formatting(self):
        """Test recommendation priority is formatted correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": [
                {"action": "Add tests", "priority": 1}
            ]
        }
        response = wrapper.generate_response_with_challenges(context)
        
        assert "Priority: 1" in response
    
    def test_recommendation_with_rationale_formatting(self):
        """Test recommendation rationale is formatted correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": [
                {"action": "Add tests", "rationale": "Improve coverage"}
            ]
        }
        response = wrapper.generate_response_with_challenges(context)
        
        assert "Rationale: Improve coverage" in response
    
    def test_multiple_challenges_formatted_as_list(self):
        """Test multiple challenges are numbered correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "Issue 1", "severity": "HIGH", "confidence": 0.8},
            {"description": "Issue 2", "severity": "MEDIUM", "confidence": 0.7},
            {"description": "Issue 3", "severity": "LOW", "confidence": 0.6}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        response = wrapper.generate_response_with_challenges({"dummy": "context"})
        
        assert "1. Issue 1" in response
        assert "2. Issue 2" in response
        assert "3. Issue 3" in response
    
    def test_multiple_recommendations_formatted_as_list(self):
        """Test multiple recommendations are numbered correctly."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": [
                {"action": "Action 1", "priority": 1},
                {"action": "Action 2", "priority": 2},
                {"action": "Action 3", "priority": 3}
            ]
        }
        response = wrapper.generate_response_with_challenges(context)
        
        assert "1. Action 1" in response
        assert "2. Action 2" in response
        assert "3. Action 3" in response
    
    def test_empty_recommendation_list_handled(self):
        """Test empty recommendation list is handled gracefully."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator()
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": []
        }
        response = wrapper.generate_response_with_challenges(context)
        
        assert "## Recommendations" not in response
    
    def test_all_segments_combined_when_all_present(self):
        """Test all segments are combined when all data present."""
        base_gen = MockBaseResponseGenerator()
        challenge_orch = MockChallengeOrchestrator(challenges=[
            {"description": "Challenge 1", "severity": "HIGH", "confidence": 0.8}
        ])
        context_builder = MockContextBuilder()
        
        wrapper = TurnResponseWithChallenges(base_gen, challenge_orch, context_builder)
        context = {
            "dummy": "context",
            "recommendations": [
                {"action": "Recommendation 1", "priority": 1}
            ]
        }
        response = wrapper.generate_response_with_challenges(context)
        
        # All segments should be present
        assert "## Base Response" in response
        assert "## Challenges Identified" in response
        assert "## Recommendations" in response
        assert "Base Response" in response  # Content from base gen
        assert "Challenge 1" in response
        assert "Recommendation 1" in response
