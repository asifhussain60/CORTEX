"""
Resumption Handler Tests - TDD for AC-FR-006

Tests for:
- AC-FR-006-02: Operations resumable after interruption
- AC-FR-006-03: Partial completion preserved in resumption

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.core.checkpoint_manager import CheckpointManager, CheckpointStatus
from cortex.core.resumption_handler import (
    ResumptionHandler,
    RecoveryStrategy,
    ResumptionStatus,
    RecoveryContext,
)


@pytest.mark.ac("FR-006-02")
class TestResumptionInitiation:
    """Test AC-FR-006-02: Operations resumable after interruption"""
    
    def test_initiate_resumption(self):
        """Should initiate resumption from checkpoint."""
        # Setup: Create checkpoint first
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-001",
            operation_type="phase_transition",
            state_snapshot={"phase": "PHASE-01"},
            recovery_instructions="Resume phase transition",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Initiate resumption
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        res_result = handler.initiate_resumption(
            checkpoint_id=checkpoint_id,
            strategy=RecoveryStrategy.FROM_CHECKPOINT,
        )
        
        assert res_result.is_ok()
        record = res_result.unwrap()
        assert record.resumption_id.startswith("RES-")
        assert record.status == ResumptionStatus.INITIATED
    
    def test_validate_checkpoint(self):
        """Should validate checkpoint integrity."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-002",
            operation_type="test",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Validate
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        validation = handler.validate_checkpoint(checkpoint_id)
        
        assert validation.is_ok()
        assert validation.unwrap() is True
    
    def test_validate_nonexistent_checkpoint(self):
        """Should fail validation for missing checkpoint."""
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        validation = handler.validate_checkpoint("NONEXISTENT")
        
        assert validation.is_err()
    
    def test_validate_inactive_checkpoint(self):
        """Should fail validation for non-active checkpoint."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-003",
            operation_type="test",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Commit checkpoint (make it inactive)
        cp_manager.commit_checkpoint(checkpoint_id)
        
        # Try to validate
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        validation = handler.validate_checkpoint(checkpoint_id)
        
        assert validation.is_err()


@pytest.mark.ac("FR-006-03")
class TestStateReconstruction:
    """Test AC-FR-006-03: Partial completion preserved"""
    
    def test_reconstruct_full_state(self):
        """Should reconstruct complete state from checkpoint."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        state = {"phase": "PHASE-01", "acs": 10, "completed": 3}
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-004",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Reconstruct
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        recon_result = handler.reconstruct_state(checkpoint_id)
        
        assert recon_result.is_ok()
        recovered = recon_result.unwrap()
        assert recovered["phase"] == "PHASE-01"
        assert recovered["acs"] == 10
        assert recovered["completed"] == 3
    
    def test_reconstruct_partial_state(self):
        """Should reconstruct partial state by paths."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        state = {
            "phase": {
                "id": "PHASE-01",
                "status": "executing",
                "progress": {
                    "completed": 5,
                    "total": 10,
                },
            },
        }
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-005",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Reconstruct partial
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        paths = ["phase.id", "phase.progress.completed"]
        recon_result = handler.reconstruct_state(checkpoint_id, partial_paths=paths)
        
        assert recon_result.is_ok()
        recovered = recon_result.unwrap()
        assert "phase.id" in recovered
        assert "phase.progress.completed" in recovered


class TestOperationHandlers:
    """Test operation handler registration and execution"""
    
    def test_register_operation_handler(self):
        """Should register handler for operation type."""
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        def dummy_handler(context: RecoveryContext):
            from cortex.core.result import Ok
            return Ok({"recovered": True})
        
        reg_result = handler.register_operation_handler("phase_transition", dummy_handler)
        
        assert reg_result.is_ok()
        assert handler.is_operation_idempotent("phase_transition") is True
    
    def test_is_operation_idempotent(self):
        """Should check if operation is registered."""
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        def dummy_handler(context: RecoveryContext):
            from cortex.core.result import Ok
            return Ok({"result": "ok"})
        
        handler.register_operation_handler("test_op", dummy_handler)
        
        assert handler.is_operation_idempotent("test_op") is True
        assert handler.is_operation_idempotent("unknown_op") is False


class TestRecoveryExecution:
    """Test recovery workflow execution"""
    
    def test_execute_recovery_success(self):
        """Should successfully execute recovery."""
        # Setup checkpoint
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        state = {"value": "recovered"}
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-006",
            operation_type="test_recovery",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Setup handler
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        def recovery_handler(context: RecoveryContext):
            from cortex.core.result import Ok
            return Ok({"recovered_value": context.recovered_state["value"]})
        
        handler.register_operation_handler("test_recovery", recovery_handler)
        
        # Initiate and execute
        res_result = handler.initiate_resumption(checkpoint_id)
        resumption_id = res_result.unwrap().resumption_id
        
        exec_result = handler.execute_recovery(
            resumption_id=resumption_id,
            checkpoint_id=checkpoint_id,
            operation_type="test_recovery",
        )
        
        assert exec_result.is_ok()
        outcome = exec_result.unwrap()
        assert outcome["recovered_value"] == "recovered"
    
    def test_execute_recovery_handler_failure(self):
        """Should handle recovery handler failure."""
        # Setup checkpoint
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-007",
            operation_type="failing_op",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Setup failing handler
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        def failing_handler(context: RecoveryContext):
            from cortex.core.result import Err
            return Err("Recovery failed")
        
        handler.register_operation_handler("failing_op", failing_handler)
        
        # Execute
        res_result = handler.initiate_resumption(checkpoint_id)
        resumption_id = res_result.unwrap().resumption_id
        
        exec_result = handler.execute_recovery(
            resumption_id=resumption_id,
            checkpoint_id=checkpoint_id,
            operation_type="failing_op",
        )
        
        assert exec_result.is_err()
        
        # Verify record marked as failed
        rec_result = handler.get_resumption_record(resumption_id)
        record = rec_result.unwrap()
        assert record.status == ResumptionStatus.FAILED
    
    def test_execute_recovery_no_handler(self):
        """Should fail if no handler registered."""
        # Setup checkpoint
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-008",
            operation_type="unknown_type",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Execute without registering handler
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        res_result = handler.initiate_resumption(checkpoint_id)
        resumption_id = res_result.unwrap().resumption_id
        
        exec_result = handler.execute_recovery(
            resumption_id=resumption_id,
            checkpoint_id=checkpoint_id,
            operation_type="unknown_type",
        )
        
        assert exec_result.is_err()


class TestResumptionRecords:
    """Test resumption record management"""
    
    def test_get_resumption_record(self):
        """Should retrieve resumption record."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-009",
            operation_type="test",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Create resumption
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        res_result = handler.initiate_resumption(checkpoint_id)
        resumption_id = res_result.unwrap().resumption_id
        
        # Retrieve
        get_result = handler.get_resumption_record(resumption_id)
        
        assert get_result.is_ok()
        record = get_result.unwrap()
        assert record.resumption_id == resumption_id
    
    def test_list_resumptions_for_checkpoint(self):
        """Should list all resumptions for checkpoint."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-010",
            operation_type="test",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Create multiple resumptions
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        for _ in range(3):
            handler.initiate_resumption(checkpoint_id)
        
        # List
        list_result = handler.list_resumptions_for_checkpoint(checkpoint_id)
        
        assert list_result.is_ok()
        resumptions = list_result.unwrap()
        assert len(resumptions) == 3
    
    def test_mark_resumption_complete(self):
        """Should mark resumption as complete."""
        # Setup
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-011",
            operation_type="test",
            state_snapshot={"data": "value"},
            recovery_instructions="test",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Create resumption
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        res_result = handler.initiate_resumption(checkpoint_id)
        resumption_id = res_result.unwrap().resumption_id
        
        # Mark complete
        complete_result = handler.mark_resumption_complete(resumption_id)
        
        assert complete_result.is_ok()
        
        # Verify
        rec_result = handler.get_resumption_record(resumption_id)
        record = rec_result.unwrap()
        assert record.status == ResumptionStatus.COMPLETED


class TestResumptionStatistics:
    """Test resumption statistics"""
    
    def test_successful_resumption_count(self):
        """Should count successful resumptions."""
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        count_result = handler.get_successful_resumption_count("test_op")
        
        assert count_result.is_ok()
        assert count_result.unwrap() == 0
    
    def test_failed_resumption_count(self):
        """Should count failed resumptions."""
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        count_result = handler.get_failed_resumption_count()
        
        assert count_result.is_ok()
        assert count_result.unwrap() == 0


class TestResumptionIntegration:
    """Integration tests for resumption"""
    
    def test_complete_recovery_workflow(self):
        """Should handle complete recovery workflow."""
        # Setup checkpoint
        cp_manager = CheckpointManager()
        cp_manager.reset_instance()
        cp_manager = CheckpointManager.instance()
        
        state = {"step": 1, "data": "initial"}
        
        cp_result = cp_manager.create_checkpoint(
            operation_id="OP-012",
            operation_type="workflow",
            state_snapshot=state,
            recovery_instructions="Resume workflow",
        )
        
        checkpoint = cp_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Mark partial completion
        cp_manager.mark_partial_completion(
            checkpoint_id,
            completion_percentage=50.0,
            current_state={"step": 2, "data": "partial"},
        )
        
        # Setup handler
        handler = ResumptionHandler()
        handler.reset_instance()
        handler = ResumptionHandler.instance()
        
        def workflow_handler(context: RecoveryContext):
            from cortex.core.result import Ok
            return Ok({"completed": True})
        
        handler.register_operation_handler("workflow", workflow_handler)
        
        # Initiate resumption
        res_result = handler.initiate_resumption(checkpoint_id)
        resumption_id = res_result.unwrap().resumption_id
        
        # Execute recovery
        exec_result = handler.execute_recovery(
            resumption_id=resumption_id,
            checkpoint_id=checkpoint_id,
            operation_type="workflow",
        )
        
        assert exec_result.is_ok()
        
        # Verify resumption completed
        rec_result = handler.get_resumption_record(resumption_id)
        record = rec_result.unwrap()
        assert record.status == ResumptionStatus.COMPLETED
    
    def test_singleton_consistency(self):
        """Should maintain singleton consistency."""
        handler1 = ResumptionHandler.instance()
        handler2 = ResumptionHandler.instance()
        
        assert handler1 is handler2
