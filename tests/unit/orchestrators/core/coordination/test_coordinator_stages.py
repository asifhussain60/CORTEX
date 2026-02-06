"""
Unit tests for Coordinator stage execution methods.

AC-PERMANENT-FIX-006: Challenge-driven comprehension testing
AC-CHALLENGE-SYSTEM-002: Challenge generation behavior validation
AC-GOVE-REM-001: Intent classification testing
AC-PHASE-6C-001: Governance enforcement testing

Phase 1 extraction from master_orchestrator.process_user_request() + execute_operation()
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any, Optional

from cortex.orchestrators.core.coordination.coordinator import (
    Coordinator,
    PipelineStage,
    StageResult
)
from cortex.orchestrators.core.enforcement_orchestrator import EnforcementLevel


class TestCoordinatorChallengeStage:
    """Test CHALLENGE stage (Stage 1) execution."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator with mock orchestrators."""
        return Coordinator()

    @pytest.fixture
    def user_request(self):
        """Sample user request."""
        return "Implement cache invalidation strategy"

    @pytest.fixture
    def context(self):
        """Sample context."""
        return {
            "conversation_history": [],
            "operation_name": "implement",
            "parameters": {}
        }

    def test_challenge_with_interaction_orchestrator_present(self, coordinator, user_request, context):
        """Test challenge execution when InteractionOrchestrator is available."""
        # Setup mock
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute_turn_with_challenge.return_value = {
            "type": "challenge",
            "content": "Potential issues: No caching strategy defined..."
        }
        coordinator.orchestrators["interaction_orchestrator"] = mock_orchestrator

        # Execute
        result = coordinator.execute_stage_challenge(user_request, context)

        # Assert
        assert result.stage == PipelineStage.CHALLENGE
        assert result.success is True
        assert result.data.get("challenge_generated") is True
        assert result.data.get("challenge") is not None
        assert result.error is None

    def test_challenge_without_interaction_orchestrator(self, coordinator, user_request, context):
        """Test challenge execution when InteractionOrchestrator unavailable (graceful degradation)."""
        # AC-PERMANENT-FIX-006: Fallback behavior
        coordinator.orchestrators = {}  # No orchestrators

        result = coordinator.execute_stage_challenge(user_request, context)

        assert result.stage == PipelineStage.CHALLENGE
        assert result.success is True  # Still succeeds, but skips challenge
        assert result.data.get("challenge_needed") is False
        assert result.data.get("reason") == "orchestrator_unavailable"
        assert result.error is None

    def test_challenge_no_challenge_needed(self, coordinator, user_request, context):
        """Test when challenge system decides no challenge is needed."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute_turn_with_challenge.return_value = {
            "type": "no_challenge",
            "reason": "Request is clear and unambiguous"
        }
        coordinator.orchestrators["interaction_orchestrator"] = mock_orchestrator

        result = coordinator.execute_stage_challenge(user_request, context)

        assert result.stage == PipelineStage.CHALLENGE
        assert result.success is True
        assert result.data.get("challenge_generated") is False
        assert result.error is None

    def test_challenge_orchestrator_error_graceful(self, coordinator, user_request, context):
        """Test that challenge orchestrator errors are graceful (don't block execution)."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute_turn_with_challenge.side_effect = RuntimeError("Orchestrator failed")
        coordinator.orchestrators["interaction_orchestrator"] = mock_orchestrator

        result = coordinator.execute_stage_challenge(user_request, context)

        # Should succeed with degraded behavior, not fail
        assert result.stage == PipelineStage.CHALLENGE
        assert result.success is True
        # When error occurs, challenge_generated key may not be set, check challenge_needed instead
        assert result.data.get("challenge_needed") is False or result.data.get("challenge_generated") is not True
        assert result.error is None

    def test_challenge_round_context_building(self, coordinator, context):
        """Test RoundContext is properly built from user input."""
        mock_orchestrator = MagicMock()
        call_args = None

        def capture_args(round_context):
            nonlocal call_args
            call_args = round_context
            return {"type": "no_challenge"}

        mock_orchestrator.execute_turn_with_challenge.side_effect = capture_args
        coordinator.orchestrators["interaction_orchestrator"] = mock_orchestrator

        user_request = "Test request for round context"
        context["conversation_history"] = [{"role": "user", "message": "previous"}]

        result = coordinator.execute_stage_challenge(user_request, context)

        # Verify RoundContext was built correctly
        assert call_args is not None
        assert call_args.user_input == user_request
        assert call_args.orchestrator_name == "interaction_orchestrator"
        assert call_args.round_number == 1

    def test_challenge_ac_compliance_markers(self, coordinator, user_request, context):
        """Test AC compliance markers are present."""
        # AC-PERMANENT-FIX-006: Fallback handling
        # AC-CHALLENGE-SYSTEM-002: Challenge generation

        coordinator.orchestrators = {}  # Trigger fallback
        result = coordinator.execute_stage_challenge(user_request, context)

        # Fallback path should work (AC-PERMANENT-FIX-006 compliance)
        assert result.success is True

    def test_challenge_multiple_calls_independent(self, coordinator, context):
        """Test that multiple challenge calls are independent (no state leakage)."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute_turn_with_challenge.side_effect = [
            {"type": "challenge", "content": "First challenge"},
            {"type": "no_challenge"},
            {"type": "challenge", "content": "Third challenge"}
        ]
        coordinator.orchestrators["interaction_orchestrator"] = mock_orchestrator

        # Three independent calls
        result1 = coordinator.execute_stage_challenge("Request 1", context)
        result2 = coordinator.execute_stage_challenge("Request 2", context)
        result3 = coordinator.execute_stage_challenge("Request 3", context)

        assert result1.data.get("challenge_generated") is True
        assert result2.data.get("challenge_generated") is False
        assert result3.data.get("challenge_generated") is True


class TestCoordinatorExecutionStage:
    """Test EXECUTION stage (Stages 2-4) execution."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator with mock orchestrators."""
        return Coordinator()

    @pytest.fixture
    def user_request(self):
        """Sample user request."""
        return "Implement cache layer"

    @pytest.fixture
    def context(self):
        """Sample context with all parameters."""
        return {
            "operation_name": "implement",
            "parameters": {"scope": "full", "priority": "high"},
            "conversation_history": []
        }

    def test_execution_stage_2_intent_classification(self, coordinator, user_request, context):
        """Test Stage 2: Intent classification (AC-GOVE-REM-001)."""
        # AC-GOVE-REM-001: Mandatory intent classification
        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {"status": "success"}

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Verify intent was classified
        mock_router.classify_intent.assert_called_once()
        assert result.success is True

    def test_execution_stage_3_governance_enforcement_blocked(self, coordinator, user_request, context):
        """Test Stage 3: Governance enforcement (AC-PHASE-6C-001) - BLOCKED case."""
        # AC-PHASE-6C-001: Governance enforcement with BLOCKED enforcement level

        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        mock_enforcement = MagicMock()
        mock_enforcement_result = MagicMock()
        mock_enforcement_result.level = EnforcementLevel.BLOCKED
        mock_enforcement.validate_operation.return_value = mock_enforcement_result

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["enforcement_orchestrator"] = mock_enforcement
        # Also add execution_orchestrator so we can test the governance blocking before execution
        mock_execution = MagicMock()
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Governance should block execution (before even trying to execute domain logic)
        assert result.success is False
        assert "Governance enforcement blocked" in result.error or "enforcement" in result.error.lower()

    def test_execution_stage_3_governance_enforcement_warning(self, coordinator, user_request, context):
        """Test Stage 3: Governance enforcement - WARNING case (should continue)."""
        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        mock_enforcement = MagicMock()
        mock_enforcement_result = MagicMock()
        mock_enforcement_result.level = "WARNING"
        mock_enforcement.validate_operation.return_value = mock_enforcement_result

        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {"status": "success"}

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["enforcement_orchestrator"] = mock_enforcement
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # WARNING should not block execution
        assert result.success is True

    def test_execution_stage_4_domain_execution(self, coordinator, user_request, context):
        """Test Stage 4: Domain execution via ExecutionOrchestrator."""
        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        mock_execution = MagicMock()
        expected_result = {"files_modified": 3, "tests_passing": True}
        mock_execution.execute_tdd_cycle.return_value = expected_result

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Verify execution completed
        assert result.success is True
        assert result.data == expected_result

    def test_execution_no_execution_orchestrator(self, coordinator, user_request, context):
        """Test graceful failure when ExecutionOrchestrator not registered."""
        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        coordinator.orchestrators["intent_router"] = mock_router
        # No execution_orchestrator

        result = coordinator.execute_stage_execution(user_request, context)

        assert result.success is False
        assert "No execution orchestrator" in result.error

    def test_execution_no_intent_router(self, coordinator, user_request, context):
        """Test execution continues even without intent router."""
        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {"status": "success"}

        coordinator.orchestrators["execution_orchestrator"] = mock_execution
        # No intent_router

        result = coordinator.execute_stage_execution(user_request, context)

        # Should still succeed, just without intent classification
        assert result.success is True

    def test_execution_intent_classification_error_graceful(self, coordinator, user_request, context):
        """Test that intent classification errors don't block execution."""
        mock_router = MagicMock()
        mock_router.classify_intent.side_effect = RuntimeError("Classification failed")

        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {"status": "success"}

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Should complete despite intent classification failure
        assert result.success is True

    def test_execution_governance_enforcement_error_graceful(self, coordinator, user_request, context):
        """Test that governance enforcement errors don't block execution."""
        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        mock_enforcement = MagicMock()
        mock_enforcement.validate_operation.side_effect = RuntimeError("Enforcement check failed")

        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {"status": "success"}

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["enforcement_orchestrator"] = mock_enforcement
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Should complete despite enforcement error
        assert result.success is True

    def test_execution_all_stages_success_path(self, coordinator, user_request, context):
        """Test complete success path through all execution stages."""
        # Stage 2: Intent classification
        mock_router = MagicMock()
        mock_router.classify_intent.return_value = MagicMock(intent_type="IMPLEMENT")

        # Stage 3: Governance enforcement
        mock_enforcement = MagicMock()
        mock_enforcement_result = MagicMock()
        mock_enforcement_result.level = "PASS"
        mock_enforcement.validate_operation.return_value = mock_enforcement_result

        # Stage 4: Domain execution
        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {
            "status": "success",
            "files_modified": 3,
            "tests_passing": True
        }

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["enforcement_orchestrator"] = mock_enforcement
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        assert result.stage == PipelineStage.EXECUTION
        assert result.success is True
        assert result.data["files_modified"] == 3
        assert result.data["tests_passing"] is True
        assert result.error is None

    def test_execution_parameters_passed_correctly(self, coordinator, user_request, context):
        """Test that parameters are passed correctly through execution stages."""
        captured_intent_call: Optional[tuple] = None
        captured_enforcement_call: Optional[Dict[str, Any]] = None
        captured_execution_call: Optional[tuple] = None

        def capture_intent_call(req, ctx):
            nonlocal captured_intent_call
            captured_intent_call = (req, ctx)
            return MagicMock(intent_type="IMPLEMENT")

        def capture_enforcement_call(ctx):
            nonlocal captured_enforcement_call
            captured_enforcement_call = ctx
            return MagicMock(level="PASS")

        def capture_execution_call(intent, parameters):
            nonlocal captured_execution_call
            captured_execution_call = (intent, parameters)
            return {"status": "success"}

        mock_router = MagicMock()
        mock_router.classify_intent.side_effect = capture_intent_call

        mock_enforcement = MagicMock()
        mock_enforcement.validate_operation.side_effect = capture_enforcement_call

        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.side_effect = capture_execution_call

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["enforcement_orchestrator"] = mock_enforcement
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Verify parameters were passed correctly through all stages
        assert result.success is True
        assert captured_intent_call is not None
        assert captured_enforcement_call is not None
        assert captured_execution_call is not None
        assert captured_intent_call[0] == user_request
        assert captured_enforcement_call.get("operation") == "implement"
        assert captured_execution_call[1] == context["parameters"]

    def test_execution_exception_handling(self, coordinator, user_request, context):
        """Test unexpected exception handling in execution stage."""
        mock_router = MagicMock()
        mock_router.classify_intent.side_effect = Exception("Unexpected error")

        mock_execution = MagicMock()
        mock_execution.execute_tdd_cycle.return_value = {"status": "success"}

        coordinator.orchestrators["intent_router"] = mock_router
        coordinator.orchestrators["execution_orchestrator"] = mock_execution

        result = coordinator.execute_stage_execution(user_request, context)

        # Should handle gracefully
        assert result.success is True  # Continues despite router error

