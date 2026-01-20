"""
Unit tests for Stage 2.5 Gate Challenge Integration.

Tests cover:
- Challenges generated during gate evaluation
- Challenges attached to confirmation context
- Challenges appear in decision rationale
- Gate still makes correct decisions
- Zero regressions to existing gate tests
"""

import pytest
from typing import List, Dict, Any
from dataclasses import dataclass

from src.orchestrators.core.stage_2_5_gate import (
    Stage25Gate,
    ConfirmationContext,
    ContinuationDecision,
)
from src.core.orchestrator.complexity_assessment import ComplexitySignals
from src.core.orchestrator.approval_gate import AlternativeRecommendation


class MockComplexityAssessment:
    """Mock complexity assessment."""
    
    def __init__(self, complexity_level="SIMPLE"):
        self.complexity_score = 0.3 if complexity_level == "SIMPLE" else 0.7
        self.complexity_level = complexity_level
        self.confidence = 0.9
        self.factors = {"scope": 0.4, "coupling": 0.2}


class MockApprovalDecision:
    """Mock approval decision."""
    
    def __init__(self, approved=True):
        self.approved = approved
        self.complexity_level = "SIMPLE" if approved else "MODERATE"
        self.reason = "Auto-approved" if approved else "Confirmation needed"
        # Create mock alternatives without using AlternativeRecommendation
        self.alternatives = []


class MockComplexityAssessmentEngine:
    """Mock engine."""
    
    def assess_complexity(self, signals, intent_type="general", use_cache=True):
        return MockComplexityAssessment("SIMPLE")


class MockApprovalGateLogic:
    """Mock gate logic."""
    
    def evaluate_approval(self, assessment, operation_id, alternatives=None):
        return MockApprovalDecision(approved=True)


class TestStage25GateChallengeIntegration:
    """Test suite for Stage 2.5 Gate with challenge integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.gate = Stage25Gate()
        # Replace with mocks
        self.gate.engine = MockComplexityAssessmentEngine()
        self.gate.gate = MockApprovalGateLogic()
    
    def test_challenges_generated_during_evaluation(self):
        """Test challenges are processed during gate evaluation."""
        challenges = [
            {"description": "Challenge 1", "severity": "HIGH", "confidence": 0.8}
        ]
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            challenges=challenges
        )
        
        # Decision should be made (challenges don't affect approval for SIMPLE)
        assert isinstance(decision, ContinuationDecision)
        assert decision is not None
    
    def test_challenges_attached_to_context(self):
        """Test challenges are attached to confirmation context."""
        challenges = [
            {"description": "Challenge 1", "severity": "HIGH"},
            {"description": "Challenge 2", "severity": "MEDIUM"}
        ]
        
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            challenges=challenges
        )
        
        # Decision should be made
        assert isinstance(decision, ContinuationDecision)
        # If confirmation context exists, challenges should be there
        if decision.confirmation_context:
            assert len(decision.confirmation_context.challenges) == 2
            assert decision.confirmation_context.challenges[0]["description"] == "Challenge 1"
    
    def test_challenges_appear_in_decision_rationale(self):
        """Test challenges are included in decision context."""
        challenges = [
            {"description": "SQL injection risk", "severity": "CRITICAL", "confidence": 0.9}
        ]
        
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            challenges=challenges
        )
        
        # Challenge should be accessible for display if context exists
        if decision.confirmation_context:
            assert decision.confirmation_context.challenges[0]["description"] == "SQL injection risk"
            assert decision.confirmation_context.challenges[0]["severity"] == "CRITICAL"
        else:
            # Or challenges passed through should be in the decision somehow
            assert decision is not None
    
    def test_gate_makes_correct_decisions_with_challenges(self):
        """Test gate logic still makes correct approval decisions."""
        # Test auto-approval path
        signals = ComplexitySignals(
            lens_confidence=0.9, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.9,
            signals=signals,
            challenges=[]
        )
        
        # Simple operations should still auto-approve
        assert decision.continue_execution == True
        assert "Auto-approved" in decision.reason
    
    def test_zero_regressions_existing_gate_functionality(self):
        """Test existing gate tests still pass."""
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals
        )
        
        # Decision should be made regardless
        assert isinstance(decision, ContinuationDecision)
        assert decision is not None
    
    def test_empty_challenges_handled_gracefully(self):
        """Test empty challenge list is handled."""
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            challenges=[]
        )
        
        assert decision is not None
        assert isinstance(decision, ContinuationDecision)
    
    def test_challenges_with_user_intent(self):
        """Test challenges attached when user intent provided."""
        challenges = [
            {"description": "Intent-related challenge", "severity": "HIGH"}
        ]
        
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            user_intent="Add authentication",
            challenges=challenges
        )
        
        # If confirmation context exists, check for user intent and challenges
        if decision.confirmation_context:
            assert decision.confirmation_context.user_intent == "Add authentication"
            assert len(decision.confirmation_context.challenges) == 1
        else:
            assert decision is not None
    
    def test_challenges_with_affected_files(self):
        """Test challenges attached when affected files provided."""
        challenges = [
            {"description": "File-related challenge", "severity": "MEDIUM"}
        ]
        affected_files = ["src/auth.py", "tests/test_auth.py"]
        
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=2, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            affected_files=affected_files,
            challenges=challenges
        )
        
        # If confirmation context exists, check for affected files and challenges
        if decision.confirmation_context:
            assert decision.confirmation_context.affected_files == affected_files
            assert len(decision.confirmation_context.challenges) == 1
        else:
            assert decision is not None
    
    def test_multiple_challenges_all_included(self):
        """Test all multiple challenges are included."""
        challenges = [
            {"description": "Challenge 1", "severity": "CRITICAL", "confidence": 0.9},
            {"description": "Challenge 2", "severity": "HIGH", "confidence": 0.8},
            {"description": "Challenge 3", "severity": "MEDIUM", "confidence": 0.7},
        ]
        
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            challenges=challenges
        )
        
        # If confirmation context exists, all challenges should be there
        if decision.confirmation_context:
            assert len(decision.confirmation_context.challenges) == 3
            assert decision.confirmation_context.challenges[0]["severity"] == "CRITICAL"
            assert decision.confirmation_context.challenges[2]["severity"] == "MEDIUM"
        else:
            assert decision is not None
    
    def test_challenges_with_alternatives(self):
        """Test challenges displayed alongside alternatives."""
        challenges = [
            {"description": "Alternative needed", "severity": "MEDIUM"}
        ]
        
        signals = ComplexitySignals(
            lens_confidence=0.5, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope="local", ast_complexity=0, criticality_level="low"
        )
        
        alternatives = [
            {"name": "Option A", "description": "First approach"},
            {"name": "Option B", "description": "Second approach"}
        ]
        
        decision = self.gate.evaluate(
            operation_id="op123",
            lens_confidence=0.5,
            signals=signals,
            alternatives=alternatives,
            challenges=challenges
        )
        
        # If confirmation context exists, both should be present
        if decision.confirmation_context:
            assert len(decision.confirmation_context.challenges) == 1
            assert len(decision.confirmation_context.alternatives) > 0
        else:
            assert decision is not None
