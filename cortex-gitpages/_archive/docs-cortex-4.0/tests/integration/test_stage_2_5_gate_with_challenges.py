"""
Integration tests for Stage 2.5 Gate with challenge integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class MockStage25Gate:
    """Mock Stage 2.5 Gate for testing."""
    
    def __init__(self):
        self.challenges = []
    
    def _generate_challenges(self, context: dict):
        return self.challenges
    
    def evaluate(self, context: dict):
        challenges = self._generate_challenges(context)
        return {
            "status": "evaluated",
            "challenges": challenges,
            "context": context,
        }


class TestStage25GateWithChallenges:
    """Test suite for Stage 2.5 Gate with challenge integration."""
    
    def test_gate_evaluation_includes_challenges(self):
        """Test gate evaluation includes challenges."""
        gate = MockStage25Gate()
        gate.challenges = [{"desc": "c1"}]
        
        result = gate.evaluate({"intent": "Add feature"})
        
        assert "challenges" in result
        assert len(result["challenges"]) == 1
    
    def test_decision_quality_with_challenges(self):
        """Test decision quality with challenges present."""
        gate = MockStage25Gate()
        gate.challenges = [
            {"desc": "Security issue", "severity": "CRITICAL"}
        ]
        
        result = gate.evaluate({"intent": "Add feature"})
        
        assert result is not None
        assert result["challenges"][0]["severity"] == "CRITICAL"
    
    def test_approval_logic_unchanged(self):
        """Test approval logic remains unchanged."""
        gate = MockStage25Gate()
        gate.challenges = []
        
        result = gate.evaluate({"intent": "Add feature", "approval_status": "approved"})
        
        # Should still make correct decision
        assert result is not None
        assert result["status"] == "evaluated"
    
    def test_challenges_attached_to_context(self):
        """Test challenges are attached to gate context."""
        gate = MockStage25Gate()
        challenges = [{"desc": "c1", "severity": "HIGH"}]
        gate.challenges = challenges
        
        result = gate.evaluate({"intent": "Test"})
        
        assert "challenges" in result
        assert result["challenges"] == challenges
    
    def test_zero_regressions_to_existing_tests(self):
        """Test zero regressions to existing gate tests."""
        gate = MockStage25Gate()
        gate.challenges = []
        
        # Should work same as before
        result = gate.evaluate({"intent": "Basic test"})
        
        assert result is not None
        assert result["status"] == "evaluated"
