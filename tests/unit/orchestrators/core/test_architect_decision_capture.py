"""
Tests for DecisionJournal integration with InteractionOrchestrator.

Tests AC-PHASE24-009: DecisionJournal captures architectural decisions
during challenge and DoR approval phases.
"""
import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path
from datetime import datetime

from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
from cortex.orchestrators.support.decision_journal import DecisionJournal


class TestArchitectDecisionCapture:
    """Test DecisionJournal integration with InteractionOrchestrator."""
    
    @pytest.fixture
    def mock_decision_journal(self):
        """Mock DecisionJournal for testing."""
        return Mock(spec=DecisionJournal)
    
    @pytest.fixture
    def orchestrator_with_journal(self, mock_decision_journal):
        """Create InteractionOrchestrator with DecisionJournal."""
        from cortex.brain.core.orchestrator.conversation_protocol import ConversationProtocol
        
        conversation_protocol = ConversationProtocol(
            orchestrator=None,
            max_turns=10,
            token_limit=20000
        )
        orchestrator = InteractionOrchestrator(conversation_protocol=conversation_protocol)
        orchestrator.decision_journal = mock_decision_journal
        return orchestrator
    
    def test_decision_captured_on_challenge_verdict(self, orchestrator_with_journal, mock_decision_journal):
        """Test decision captured when challenge generates verdict."""
        # Simulate challenge with PROCEED verdict
        challenge_result = {
            "verdict": "PROCEED",
            "weaknesses": ["No input validation", "Missing error handling"],
            "counter_proposal": "Add validation layer before processing"
        }
        
        # Call the method that should capture decision
        orchestrator_with_journal._capture_challenge_decision(
            request="Implement user authentication",
            challenge_result=challenge_result
        )
        
        # Verify decision was recorded
        mock_decision_journal.record_decision.assert_called_once()
        call_args = mock_decision_journal.record_decision.call_args[1]
        
        assert call_args["decision_type"] == "challenge_verdict"
        assert call_args["decision"] == "PROCEED"
        assert "No input validation" in call_args["rationale"]
        assert "Add validation layer" in call_args["alternatives_considered"]
    
    def test_decision_captured_on_dor_approval(self, orchestrator_with_journal, mock_decision_journal):
        """Test decision captured when user approves DoR."""
        dor_data = {
            "intent": "IMPLEMENT",
            "scope": "Authentication module",
            "confidence": 0.95
        }
        
        # Call the method that should capture DoR approval
        orchestrator_with_journal._capture_dor_approval(
            dor_data=dor_data,
            user_response="proceed"
        )
        
        # Verify decision was recorded
        mock_decision_journal.record_decision.assert_called_once()
        call_args = mock_decision_journal.record_decision.call_args[1]
        
        assert call_args["decision_type"] == "dor_approval"
        assert call_args["decision"] == "APPROVED"
        assert "Authentication module" in call_args["context"]
    
    def test_decision_not_captured_when_journal_disabled(self, mock_decision_journal):
        """Test decision capture skipped when journal not initialized."""
        from cortex.brain.core.orchestrator.conversation_protocol import ConversationProtocol
        
        conversation_protocol = ConversationProtocol(
            orchestrator=None,
            max_turns=10,
            token_limit=20000
        )
        orchestrator = InteractionOrchestrator(conversation_protocol=conversation_protocol)
        # No decision_journal attribute set
        
        challenge_result = {"verdict": "PROCEED"}
        
        # Should not raise error when journal is None
        try:
            orchestrator._capture_challenge_decision(
                request="Test request",
                challenge_result=challenge_result
            )
        except AttributeError:
            pytest.fail("Should handle missing decision_journal gracefully")
    
    def test_decision_capture_handles_errors_gracefully(self, orchestrator_with_journal, mock_decision_journal):
        """Test decision capture doesn't break flow on journal errors."""
        # Make journal raise error
        mock_decision_journal.record_decision.side_effect = IOError("Disk full")
        
        challenge_result = {"verdict": "PROCEED", "weaknesses": []}
        
        # Should log error but not crash
        try:
            orchestrator_with_journal._capture_challenge_decision(
                request="Test request",
                challenge_result=challenge_result
            )
        except IOError:
            pytest.fail("Should handle journal errors gracefully")
    
    def test_decision_includes_execution_outcome(self, orchestrator_with_journal, mock_decision_journal):
        """Test decision updated with execution outcome."""
        # Record initial decision
        decision_id = "decision-20260205-143022.yaml"
        mock_decision_journal.record_decision.return_value = decision_id
        
        orchestrator_with_journal._capture_challenge_decision(
            request="Test request",
            challenge_result={"verdict": "PROCEED", "weaknesses": []}
        )
        
        # Now update with execution outcome
        execution_outcome = {
            "success": True,
            "tests_passing": True,
            "files_modified": ["auth.py", "test_auth.py"]
        }
        
        orchestrator_with_journal._update_decision_with_outcome(
            decision_id=decision_id,
            outcome=execution_outcome
        )
        
        # Verify update was called
        mock_decision_journal.update_decision.assert_called_once_with(
            decision_id=decision_id,
            outcome=execution_outcome
        )
    
    def test_decision_capture_integration_flow(self, orchestrator_with_journal, mock_decision_journal):
        """Test full decision capture flow: challenge → DoR → execution."""
        # Step 1: Challenge verdict
        mock_decision_journal.record_decision.return_value = "decision-001.yaml"
        
        orchestrator_with_journal._capture_challenge_decision(
            request="Implement feature X",
            challenge_result={"verdict": "PROCEED", "weaknesses": ["gap1"]}
        )
        
        # Step 2: DoR approval
        orchestrator_with_journal._capture_dor_approval(
            dor_data={"intent": "IMPLEMENT"},
            user_response="proceed"
        )
        
        # Step 3: Execution outcome
        orchestrator_with_journal._update_decision_with_outcome(
            decision_id="decision-001.yaml",
            outcome={"success": True}
        )
        
        # Verify all three calls happened
        assert mock_decision_journal.record_decision.call_count == 2  # challenge + dor
        assert mock_decision_journal.update_decision.call_count == 1
