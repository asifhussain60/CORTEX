"""Unit tests for saga compensation transaction pattern.

Tests compensation logic, forward/backward recovery, crash recovery,
and idempotency guarantees for multi-step distributed operations.
"""

import pytest
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import Mock, patch, call
import time
import tempfile
import json

from cortex.core.recovery.saga_coordinator import (
    SagaCoordinator,
    SagaStep,
    SagaState,
    SagaStatus,
    CompensationError,
    SagaTimeoutError,
)


class TestSagaStep:
    """Test saga step definition and execution."""
    
    def test_step_creation(self) -> None:
        """Test creating saga step with forward and compensation actions."""
        forward = Mock()
        compensate = Mock()
        
        step = SagaStep(
            name="test-step",
            forward_action=forward,
            compensation_action=compensate,
            timeout_seconds=10
        )
        
        assert step.name == "test-step"
        assert step.forward_action == forward
        assert step.compensation_action == compensate
        assert step.timeout_seconds == 10
    
    def test_step_execution(self) -> None:
        """Test forward action execution."""
        action = Mock(return_value="result")
        step = SagaStep(name="test", forward_action=action, compensation_action=Mock())
        
        result = step.execute()
        
        assert result == "result"
        action.assert_called_once()
    
    def test_step_compensation(self) -> None:
        """Test compensation action execution."""
        compensate = Mock()
        step = SagaStep(name="test", forward_action=Mock(), compensation_action=compensate)
        
        step.compensate("previous_result")
        
        compensate.assert_called_once_with("previous_result")
    
    def test_step_idempotency(self) -> None:
        """Test compensation is idempotent (safe to retry)."""
        call_count = 0
        
        def compensate(result: Any) -> None:
            nonlocal call_count
            call_count += 1
        
        step = SagaStep(name="test", forward_action=Mock(), compensation_action=compensate)
        
        step.compensate("result")
        step.compensate("result")
        step.compensate("result")
        
        assert call_count == 3  # All calls succeed


class TestSagaState:
    """Test saga state persistence and restoration."""
    
    def test_state_creation(self) -> None:
        """Test creating new saga state."""
        state = SagaState(saga_id="test-saga", steps=["step1", "step2"])
        
        assert state.saga_id == "test-saga"
        assert state.status == SagaStatus.PENDING
        assert state.completed_steps == []
        assert state.current_step is None
    
    def test_state_progression(self) -> None:
        """Test state updates as saga progresses."""
        state = SagaState(saga_id="test", steps=["s1", "s2", "s3"])
        
        state.start_step("s1")
        assert state.current_step == "s1"
        assert state.status == SagaStatus.IN_PROGRESS
        
        state.complete_step("s1", "result1")
        assert state.completed_steps == ["s1"]
        assert state.step_results["s1"] == "result1"
        assert state.current_step is None
    
    def test_state_persistence(self) -> None:
        """Test saga state can be persisted and restored."""
        state = SagaState(saga_id="test", steps=["s1", "s2"])
        state.start_step("s1")
        state.complete_step("s1", "result")
        
        # Serialize
        data = state.to_dict()
        
        # Restore
        restored = SagaState.from_dict(data)
        
        assert restored.saga_id == state.saga_id
        assert restored.status == state.status
        assert restored.completed_steps == state.completed_steps
        assert restored.step_results == state.step_results
    
    def test_state_compensation_tracking(self) -> None:
        """Test tracking compensation execution."""
        state = SagaState(saga_id="test", steps=["s1", "s2"])
        state.complete_step("s1", "r1")
        state.complete_step("s2", "r2")
        
        state.start_compensation()
        assert state.status == SagaStatus.COMPENSATING
        
        state.compensate_step("s2")
        state.compensate_step("s1")
        
        assert state.compensated_steps == ["s2", "s1"]
        assert state.status == SagaStatus.COMPENSATED


class TestSagaCoordinator:
    """Test saga coordinator orchestration."""
    
    @pytest.fixture
    def storage_dir(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def coordinator(self, storage_dir: Path) -> SagaCoordinator:
        """Create saga coordinator with temporary storage."""
        return SagaCoordinator(storage_path=storage_dir)
    
    def test_successful_saga_execution(self, coordinator: SagaCoordinator) -> None:
        """Test all steps execute successfully."""
        step1 = SagaStep(
            name="step1",
            forward_action=Mock(return_value="result1"),
            compensation_action=Mock()
        )
        step2 = SagaStep(
            name="step2",
            forward_action=Mock(return_value="result2"),
            compensation_action=Mock()
        )
        
        saga_id = coordinator.create_saga([step1, step2])
        result = coordinator.execute_saga(saga_id)
        
        assert result.success is True
        assert result.completed_steps == ["step1", "step2"]
        step1.forward_action.assert_called_once()
        step2.forward_action.assert_called_once()
        step1.compensation_action.assert_not_called()
        step2.compensation_action.assert_not_called()
    
    def test_partial_failure_triggers_compensation(self, coordinator: SagaCoordinator) -> None:
        """Test failure at step 3 compensates steps 1-2."""
        step1 = SagaStep(
            name="step1",
            forward_action=Mock(return_value="r1"),
            compensation_action=Mock()
        )
        step2 = SagaStep(
            name="step2",
            forward_action=Mock(return_value="r2"),
            compensation_action=Mock()
        )
        step3 = SagaStep(
            name="step3",
            forward_action=Mock(side_effect=RuntimeError("step3 failed")),
            compensation_action=Mock()
        )
        
        saga_id = coordinator.create_saga([step1, step2, step3])
        result = coordinator.execute_saga(saga_id)
        
        assert result.success is False
        assert result.completed_steps == ["step1", "step2"]
        assert result.failed_step == "step3"
        
        # Compensation in reverse order
        step2.compensation_action.assert_called_once_with("r2")
        step1.compensation_action.assert_called_once_with("r1")
        step3.compensation_action.assert_not_called()
    
    def test_compensation_failure_retries(self, coordinator: SagaCoordinator) -> None:
        """Test compensation retries with exponential backoff."""
        attempts = [0]
        
        def failing_compensation(result: Any) -> None:
            attempts[0] += 1
            if attempts[0] < 3:
                raise RuntimeError("compensation failed")
        
        step = SagaStep(
            name="step1",
            forward_action=Mock(return_value="result"),
            compensation_action=failing_compensation
        )
        
        saga_id = coordinator.create_saga([step])
        coordinator.execute_saga(saga_id)
        
        # Force compensation
        coordinator._compensate_saga(saga_id)
        
        assert attempts[0] >= 3  # Retried multiple times
    
    def test_saga_timeout_triggers_compensation(self, coordinator: SagaCoordinator) -> None:
        """Test saga timeout triggers compensation."""
        step1 = SagaStep(
            name="step1",
            forward_action=Mock(return_value="r1"),
            compensation_action=Mock(),
            timeout_seconds=0.1
        )
        step2 = SagaStep(
            name="step2",
            forward_action=Mock(side_effect=lambda: time.sleep(1)),
            compensation_action=Mock(),
            timeout_seconds=0.1
        )
        
        saga_id = coordinator.create_saga([step1, step2])
        
        with pytest.raises(SagaTimeoutError):
            coordinator.execute_saga(saga_id)
        
        # Step1 should be compensated
        step1.compensation_action.assert_called_once()
    
    def test_saga_crash_recovery(self, coordinator: SagaCoordinator, storage_dir: Path) -> None:
        """Test saga resumes after coordinator restart."""
        step1 = SagaStep(
            name="step1",
            forward_action=Mock(return_value="r1"),
            compensation_action=Mock()
        )
        step2 = SagaStep(
            name="step2",
            forward_action=Mock(return_value="r2"),
            compensation_action=Mock()
        )
        
        saga_id = coordinator.create_saga([step1, step2])
        
        # Execute first step
        state = coordinator._load_state(saga_id)
        coordinator._execute_step(saga_id, step1, state)
        coordinator._save_state(saga_id, state)
        
        # Simulate crash - create new coordinator
        new_coordinator = SagaCoordinator(storage_path=storage_dir)
        
        # Resume saga
        result = new_coordinator.resume_saga(saga_id, [step1, step2])
        
        assert result.success is True
        assert result.completed_steps == ["step1", "step2"]
        # step1 not re-executed, only step2
        step2.forward_action.assert_called_once()
    
    def test_non_compensatable_step_alerts(self, coordinator: SagaCoordinator) -> None:
        """Test non-compensatable step marks saga as stuck."""
        step1 = SagaStep(
            name="step1",
            forward_action=Mock(return_value="r1"),
            compensation_action=Mock(side_effect=CompensationError("cannot compensate"))
        )
        
        saga_id = coordinator.create_saga([step1])
        coordinator.execute_saga(saga_id)
        
        # Try to compensate
        with pytest.raises(CompensationError):
            coordinator._compensate_saga(saga_id)
        
        state = coordinator._load_state(saga_id)
        assert state.status == SagaStatus.STUCK
    
    def test_saga_state_auditable(self, coordinator: SagaCoordinator) -> None:
        """Test saga execution creates complete audit trail."""
        step = SagaStep(
            name="test-step",
            forward_action=Mock(return_value="result"),
            compensation_action=Mock()
        )
        
        saga_id = coordinator.create_saga([step])
        coordinator.execute_saga(saga_id)
        
        audit = coordinator.get_audit_trail(saga_id)
        
        assert len(audit) >= 2  # Start and complete events
        assert any(e["event"] == "saga_started" for e in audit)
        assert any(e["event"] == "saga_completed" for e in audit)
        assert all("timestamp" in e for e in audit)
    
    def test_partial_compensation_checkpoint(self, coordinator: SagaCoordinator) -> None:
        """Test partial compensation tracks progress and resumes."""
        compensations = [0]
        
        def slow_compensation(result: Any) -> None:
            compensations[0] += 1
            if compensations[0] == 2:
                raise RuntimeError("crash during compensation")
        
        steps = [
            SagaStep(name=f"step{i}", forward_action=Mock(return_value=f"r{i}"),
                    compensation_action=slow_compensation)
            for i in range(3)
        ]
        
        saga_id = coordinator.create_saga(steps)
        coordinator.execute_saga(saga_id)
        
        # Compensate with crash
        try:
            coordinator._compensate_saga(saga_id)
        except RuntimeError:
            pass
        
        # Resume compensation
        coordinator._compensate_saga(saga_id)
        
        state = coordinator._load_state(saga_id)
        assert len(state.compensated_steps) == 3


class TestSagaIntegration:
    """Integration tests for saga patterns in realistic scenarios."""
    
    def test_distributed_transaction_pattern(self) -> None:
        """Test saga for distributed transaction across services."""
        # Mock external service calls
        payment_service = Mock()
        payment_service.charge.return_value = {"tx_id": "pay-123"}
        payment_service.refund = Mock()
        
        inventory_service = Mock()
        inventory_service.reserve.return_value = {"reservation_id": "inv-456"}
        inventory_service.release = Mock()
        
        shipping_service = Mock()
        shipping_service.schedule.side_effect = RuntimeError("shipping unavailable")
        shipping_service.cancel = Mock()
        
        # Define saga steps
        charge_step = SagaStep(
            name="charge-payment",
            forward_action=lambda: payment_service.charge(100),
            compensation_action=lambda result: payment_service.refund(result["tx_id"])
        )
        
        reserve_step = SagaStep(
            name="reserve-inventory",
            forward_action=lambda: inventory_service.reserve("item-1", qty=1),
            compensation_action=lambda result: inventory_service.release(result["reservation_id"])
        )
        
        schedule_step = SagaStep(
            name="schedule-shipping",
            forward_action=lambda: shipping_service.schedule("order-1"),
            compensation_action=lambda result: shipping_service.cancel(result)
        )
        
        coordinator = SagaCoordinator()
        saga_id = coordinator.create_saga([charge_step, reserve_step, schedule_step])
        result = coordinator.execute_saga(saga_id)
        
        # Shipping failed, so payment and inventory should be compensated
        assert result.success is False
        assert result.failed_step == "schedule-shipping"
        payment_service.refund.assert_called_once_with("pay-123")
        inventory_service.release.assert_called_once_with("inv-456")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
