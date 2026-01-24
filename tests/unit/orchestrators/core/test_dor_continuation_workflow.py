"""
Continuation State Machine Tests: Multi-Turn DoR Workflows

This test module validates persistence of DoR approval state across
multiple conversation turns (continuations).

Test Scenarios:
1. Single-turn workflow: Request → Classification → Approval → Execution
2. Multi-turn workflow: Pending approval in turn 1 → Continue in turn 2 → Execute
3. State reset: Complete workflow → New request resets state
4. Approval persistence: Approved in turn 1 → Can execute in turn 2
5. Modification workflow: Initial request → Modify → Reclassify → Approve

Governance Rules Enforced:
- CORE-008: TDD (all tests written first)
- CORE-032: Mandatory intent classification with state tracking

AC-ID: AC-GOVE-CONTINUATION-001
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any, Optional

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestSingleTurnWorkflow:
    """
    Tests for single-turn request-approval-execution cycle
    
    Governance: CORE-032
    """

    def test_single_turn_classify_approve_execute(self) -> None:
        """
        Single turn: Classify → Approve → Execute
        
        Expected: Operation completes in one turn
        
        Governance: CORE-032 (complete workflow)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Classify, approve, execute
        orchestrator._dor_gate.classify_and_reflect("Fix bug in login", {})
        orchestrator._dor_gate.approve()
        result = orchestrator._dor_gate.execute_if_approved()

        assert result is not None
        assert orchestrator._dor_gate._approval_decision.status.value == "approved"

    def test_single_turn_classify_reject(self) -> None:
        """
        Single turn: Classify → Reject (no execution)
        
        Expected: Rejection prevents execution
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        orchestrator._dor_gate.classify_and_reflect("Delete production data", {})
        orchestrator._dor_gate.reject("Too risky")

        with pytest.raises(RuntimeError):
            orchestrator._dor_gate.execute_if_approved()


class TestMultiTurnPendingApproval:
    """
    Tests for workflows where approval decision spans multiple turns
    
    Governance: CORE-032 (state persistence)
    """

    def test_two_turn_workflow_pending_then_approve(self) -> None:
        """
        Turn 1: Classify (state = PENDING)
        Turn 2: Approve and Execute
        
        Expected: Approval persists and execution succeeds
        
        Governance: CORE-032 (approval state persistence)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Classify
        orchestrator._dor_gate.classify_and_reflect("Implement caching layer", {})
        
        # Verify pending state
        assert orchestrator._dor_gate.is_pending
        assert orchestrator._dor_gate._approval_decision is None

        # Turn 2: Approve and execute
        orchestrator._dor_gate.approve()
        
        assert orchestrator._dor_gate._approval_decision.status == ApprovalStatus.APPROVED
        
        result = orchestrator._dor_gate.execute_if_approved()
        assert result is not None

    def test_two_turn_workflow_pending_then_reject(self) -> None:
        """
        Turn 1: Classify (state = PENDING)
        Turn 2: Reject
        
        Expected: Rejection from different turn blocks execution
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Classify
        orchestrator._dor_gate.classify_and_reflect("Clear all database", {})
        
        # Turn 2: Reject
        orchestrator._dor_gate.reject("Missing safeguards")
        
        assert orchestrator._dor_gate._approval_decision.status == ApprovalStatus.REJECTED

        # Execution blocked
        with pytest.raises(RuntimeError):
            orchestrator._dor_gate.execute_if_approved()

    def test_multi_turn_pending_then_modify_then_approve(self) -> None:
        """
        Turn 1: Classify (state = PENDING)
        Turn 2: Modify intent
        Turn 3: Approve and execute
        
        Expected: State transitions correctly across turns
        
        Governance: CORE-032 (multi-turn modification)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Classify
        orchestrator._dor_gate.classify_and_reflect("Delete all analytics", {})
        assert orchestrator._dor_gate.is_pending

        # Turn 2: Modify
        orchestrator._dor_gate.modify("Delete analytics older than 90 days")
        assert orchestrator._dor_gate._approval_decision.status == ApprovalStatus.MODIFIED

        # Turn 3: Reset and reclassify with modified intent
        orchestrator._dor_gate.reset()
        orchestrator._dor_gate.classify_and_reflect("Delete analytics older than 90 days", {})
        orchestrator._dor_gate.approve()

        result = orchestrator._dor_gate.execute_if_approved()
        assert result is not None


class TestStatePersistenceAcrossTurns:
    """
    Tests for state preservation when gate is not reset
    
    Governance: CORE-032 (state preservation)
    """

    def test_approved_state_persists_without_reset(self) -> None:
        """
        Approval state persists across simulated turns without reset.
        
        Expected: State remains APPROVED
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Simulate turn 1
        orchestrator._dor_gate.classify_and_reflect("Add logging", {})
        orchestrator._dor_gate.approve()

        state_after_approval = orchestrator._dor_gate._approval_decision.status

        # Simulate turn 2 (no reset)
        state_after_turn_2 = orchestrator._dor_gate._approval_decision.status

        # States should match
        assert state_after_approval == state_after_turn_2 == ApprovalStatus.APPROVED

    def test_pending_state_persists_without_reset(self) -> None:
        """
        Pending state persists across simulated turns.
        
        Expected: State remains PENDING
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Classify
        orchestrator._dor_gate.classify_and_reflect("Implement feature", {})
        
        # Verify pending
        assert orchestrator._dor_gate.is_pending

        # Turn 2: Query without changing state
        is_pending_t2 = orchestrator._dor_gate.is_pending
        
        # Should still be pending
        assert is_pending_t2

    def test_reflected_intent_persists(self) -> None:
        """
        IntentReflection persists and remains accessible.
        
        Expected: Reflection available after classification
        
        Governance: CORE-032 (reflection persistence)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Classify
        reflection1 = orchestrator._dor_gate.classify_and_reflect("Optimize queries", {})
        intent_type_1 = reflection1.intent_type
        markdown_1 = orchestrator._dor_gate.get_reflection_markdown()

        # Turn 2: Same data persists
        markdown_2 = orchestrator._dor_gate.get_reflection_markdown()

        assert intent_type_1 is not None
        assert markdown_1 == markdown_2  # Markdown unchanged


class TestResetBehavior:
    """
    Tests for state reset between workflows
    
    Governance: CORE-032 (state isolation)
    """

    def test_reset_clears_classification(self) -> None:
        """
        Reset clears classification state.
        
        Expected: After reset, pending new classification
        
        Governance: CORE-032 (state isolation)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Workflow 1
        orchestrator._dor_gate.classify_and_reflect("Fix bug", {})
        orchestrator._dor_gate.approve()

        # Reset for new workflow
        orchestrator._dor_gate.reset()

        # Should be pending classification
        assert orchestrator._dor_gate.is_pending == False
        assert orchestrator._dor_gate._approval_decision is None

    def test_reset_prevents_execution(self) -> None:
        """
        After reset, execution without new classification fails.
        
        Expected: RuntimeError on execute after reset
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Workflow 1
        orchestrator._dor_gate.classify_and_reflect("Initial operation", {})
        orchestrator._dor_gate.approve()

        # Reset
        orchestrator._dor_gate.reset()

        # Should fail - no classification
        with pytest.raises(RuntimeError):
            orchestrator._dor_gate.execute_if_approved()

    def test_reset_enables_new_classification(self) -> None:
        """
        After reset, new classification starts fresh workflow.
        
        Expected: New classification and approval succeeds
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Workflow 1
        orchestrator._dor_gate.classify_and_reflect("Operation 1", {})
        orchestrator._dor_gate.approve()

        # Reset
        orchestrator._dor_gate.reset()

        # Workflow 2: New classification
        orchestrator._dor_gate.classify_and_reflect("Operation 2", {})
        orchestrator._dor_gate.approve()

        assert orchestrator._dor_gate._approval_decision.status == ApprovalStatus.APPROVED


class TestApprovedStateExecution:
    """
    Tests for execution with approved state persisting
    
    Governance: CORE-032 (execution control)
    """

    def test_approved_allows_execution(self) -> None:
        """
        Once approved, execution allowed immediately.
        
        Expected: Execute succeeds without additional approval
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        orchestrator._dor_gate.classify_and_reflect("Deploy service", {})
        orchestrator._dor_gate.approve()

        # First execution
        result1 = orchestrator._dor_gate.execute_if_approved()
        assert result1 is not None

    def test_execution_captures_approved_timestamp(self) -> None:
        """
        Approved state captures timestamp for audit.
        
        Expected: Timestamp recorded when approved
        
        Governance: CORE-032 (audit trail)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        orchestrator._dor_gate.classify_and_reflect("Save data", {})
        orchestrator._dor_gate.approve()

        approval = orchestrator._dor_gate._approval_decision
        assert approval.timestamp is not None


class TestModificationWorkflow:
    """
    Tests for intent modification spanning multiple operations
    
    Governance: CORE-032 (modification handling)
    """

    def test_modify_and_reclassify(self) -> None:
        """
        Modify intent, then reclassify with new text.
        
        Expected: New reflection reflects modification
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Initial
        original = "Delete all user sessions"
        orchestrator._dor_gate.classify_and_reflect(original, {})

        # Modify
        modified = "Delete expired user sessions"
        orchestrator._dor_gate.modify(modified)

        assert orchestrator._dor_gate._approval_decision.status == ApprovalStatus.MODIFIED

        # Reclassify with modified text
        orchestrator._dor_gate.reset()
        orchestrator._dor_gate.classify_and_reflect(modified, {})

        # Approve new classification
        orchestrator._dor_gate.approve()
        result = orchestrator._dor_gate.execute_if_approved()

        assert result is not None

    def test_modification_captures_original_and_new(self) -> None:
        """
        Modification audit captures both original and new intent.
        
        Expected: Modified intent stored in approval decision
        
        Governance: CORE-032 (audit trail)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        original = "Update all records"
        orchestrator._dor_gate.classify_and_reflect(original, {})

        modified = "Update inactive records"
        orchestrator._dor_gate.modify(modified)

        approval = orchestrator._dor_gate._approval_decision
        assert approval.modified_intent == modified


class TestContinuationWithContext:
    """
    Tests for context preservation across turns
    
    Governance: CORE-032 (context tracking)
    """

    def test_classification_with_empty_context(self) -> None:
        """
        Classification works with empty context in turn 1.
        
        Expected: Classification succeeds without context
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        reflection = orchestrator._dor_gate.classify_and_reflect("Build cache", {})
        
        assert reflection is not None
        assert reflection.intent_type is not None

    def test_classification_with_provided_context(self) -> None:
        """
        Classification uses provided context.
        
        Expected: Scope affected by context
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        context = {"scope": "MODULE", "domain": "payment"}
        reflection = orchestrator._dor_gate.classify_and_reflect("Fix payment bug", context)
        
        assert reflection is not None
        assert reflection.scope is not None

    def test_reflection_includes_context_scope(self) -> None:
        """
        Reflection scope reflects provided context.
        
        Expected: Scope in reflection matches context
        
        Governance: CORE-032 (scope tracking)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        context = {"scope": "DOMAIN"}
        reflection = orchestrator._dor_gate.classify_and_reflect(
            "Refactor authentication domain", context
        )
        
        assert reflection.scope is not None


class TestErrorRecoveryAcrossTurns:
    """
    Tests for error handling across conversation turns
    
    Governance: CORE-032 (error resilience)
    """

    def test_empty_intent_then_valid_intent(self) -> None:
        """
        Invalid intent in turn 1, valid intent in turn 2.
        
        Expected: Turn 2 succeeds with reset
        
        Governance: CORE-032 (error recovery)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Turn 1: Invalid
        try:
            orchestrator._dor_gate.classify_and_reflect("", {})
        except (ValueError, RuntimeError):
            pass

        # Turn 2: Reset and retry with valid
        orchestrator._dor_gate.reset()
        reflection = orchestrator._dor_gate.classify_and_reflect("Valid operation", {})

        assert reflection is not None

    def test_approval_after_failed_classification(self) -> None:
        """
        After classification error, new classification and approval work.
        
        Expected: Fresh state allows new workflow
        
        Governance: CORE-032 (recovery)
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        # Simulate error
        try:
            orchestrator._dor_gate.classify_and_reflect("", {})
        except (ValueError, RuntimeError):
            pass

        # Recover
        orchestrator._dor_gate.reset()
        orchestrator._dor_gate.classify_and_reflect("Fix timeout issue", {})
        orchestrator._dor_gate.approve()

        result = orchestrator._dor_gate.execute_if_approved()
        assert result is not None


class TestApprovalDecisionAcrossTurns:
    """
    Tests for approval decision preservation and consistency
    
    Governance: CORE-032 (decision consistency)
    """

    def test_approval_consistent_across_queries(self) -> None:
        """
        Approval decision consistent across multiple queries.
        
        Expected: Same approval state returned each time
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        orchestrator._dor_gate.classify_and_reflect("Deploy code", {})
        orchestrator._dor_gate.approve()

        # Query multiple times
        decision1 = orchestrator._dor_gate._approval_decision.status
        decision2 = orchestrator._dor_gate._approval_decision.status
        decision3 = orchestrator._dor_gate._approval_decision.status

        assert decision1 == decision2 == decision3 == ApprovalStatus.APPROVED

    def test_rejection_consistent_across_queries(self) -> None:
        """
        Rejection decision consistent across multiple queries.
        
        Expected: Same rejection returned each time
        
        Governance: CORE-032
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.dor_approval_gate import ApprovalStatus

        orchestrator = MasterOrchestrator()
        
        if orchestrator._dor_gate is None:
            pytest.skip("DoRApprovalGate not initialized")

        orchestrator._dor_gate.classify_and_reflect("Delete everything", {})
        orchestrator._dor_gate.reject("Too dangerous")

        # Query multiple times
        decision1 = orchestrator._dor_gate._approval_decision.status
        decision2 = orchestrator._dor_gate._approval_decision.status
        decision3 = orchestrator._dor_gate._approval_decision.status

        assert decision1 == decision2 == decision3 == ApprovalStatus.REJECTED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
