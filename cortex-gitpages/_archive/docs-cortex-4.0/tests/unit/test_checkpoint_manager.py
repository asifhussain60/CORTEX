"""
Checkpoint Manager Tests - TDD for AC-FR-006

Tests for:
- AC-FR-006-01: State checkpointed before long operations
- AC-FR-006-03: Partial completion preserved

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.core.checkpoint_manager import (
    CheckpointManager,
    Checkpoint,
    CheckpointStatus,
    OperationState,
)


@pytest.mark.ac("FR-006-01")
class TestCheckpointCreation:
    """Test AC-FR-006-01: State checkpoint before long operations"""
    
    def test_create_checkpoint(self):
        """Should create checkpoint with operation state."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"phase_id": "PHASE-01", "ac_count": 10, "completed": 3}
        
        result = manager.create_checkpoint(
            operation_id="OP-001",
            operation_type="phase_transition",
            state_snapshot=state,
            recovery_instructions="Resume from phase start",
            ac_id="AC-TEST-001",
            phase_id="PHASE-01",
        )
        
        assert result.is_ok()
        checkpoint = result.unwrap()
        assert checkpoint.checkpoint_id.startswith("CKP-")
        assert checkpoint.metadata.operation_id == "OP-001"
        assert checkpoint.metadata.status == CheckpointStatus.ACTIVE
        assert checkpoint.metadata.operation_state == OperationState.INITIATED
    
    def test_checkpoint_integrity_verification(self):
        """Should verify checkpoint data integrity."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"value": "test_data"}
        
        result = manager.create_checkpoint(
            operation_id="OP-002",
            operation_type="state_update",
            state_snapshot=state,
            recovery_instructions="Resume state update",
        )
        
        checkpoint = result.unwrap()
        assert checkpoint.verify_integrity() is True
    
    def test_checkpoint_with_metadata(self):
        """Should store additional metadata."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"data": "value"}
        metadata_json = {"priority": "HIGH", "retry_count": 2}
        
        result = manager.create_checkpoint(
            operation_id="OP-003",
            operation_type="governance_enforcement",
            state_snapshot=state,
            recovery_instructions="Re-enforce governance",
            metadata_json=metadata_json,
        )
        
        checkpoint = result.unwrap()
        assert checkpoint.metadata.metadata_json["priority"] == "HIGH"
        assert checkpoint.metadata.metadata_json["retry_count"] == 2
    
    def test_multiple_checkpoints_unique_ids(self):
        """Should generate unique checkpoint IDs."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"value": "data"}
        
        result1 = manager.create_checkpoint(
            operation_id="OP-001",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        result2 = manager.create_checkpoint(
            operation_id="OP-002",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        cp1 = result1.unwrap()
        cp2 = result2.unwrap()
        assert cp1.checkpoint_id != cp2.checkpoint_id


@pytest.mark.ac("FR-006-03")
class TestPartialCompletion:
    """Test AC-FR-006-03: Partial completion preserved"""
    
    def test_mark_partial_completion(self):
        """Should track partial completion percentage."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        initial_state = {"phase": "PHASE-01", "acs_completed": 3}
        
        result = manager.create_checkpoint(
            operation_id="OP-004",
            operation_type="phase_execution",
            state_snapshot=initial_state,
            recovery_instructions="Resume phase execution",
        )
        
        checkpoint = result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Mark 50% completion
        updated_state = {"phase": "PHASE-01", "acs_completed": 5}
        
        update_result = manager.mark_partial_completion(
            checkpoint_id,
            completion_percentage=50.0,
            current_state=updated_state,
        )
        
        assert update_result.is_ok()
        updated_checkpoint = update_result.unwrap()
        assert updated_checkpoint.metadata.partial_completion_percentage == 50.0
    
    def test_partial_completion_updates_state(self):
        """Should update state snapshot on partial completion."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        initial_state = {"progress": 0}
        
        create_result = manager.create_checkpoint(
            operation_id="OP-005",
            operation_type="test",
            state_snapshot=initial_state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Update with progress
        updated_state = {"progress": 75}
        
        update_result = manager.mark_partial_completion(
            checkpoint_id,
            completion_percentage=75.0,
            current_state=updated_state,
        )
        
        assert update_result.is_ok()
        updated = update_result.unwrap()
        assert updated.state_snapshot["progress"] == 75
    
    def test_partial_state_extraction(self):
        """Should extract partial state by path."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {
            "phase": {
                "id": "PHASE-01",
                "progress": {
                    "completed": 5,
                    "total": 10,
                },
            },
        }
        
        create_result = manager.create_checkpoint(
            operation_id="OP-006",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        
        # Extract nested path
        progress = checkpoint.get_partial_state("phase.progress.completed")
        assert progress == 5
    
    def test_partial_state_not_found(self):
        """Should return None for missing paths."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"data": "value"}
        
        create_result = manager.create_checkpoint(
            operation_id="OP-007",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        
        # Try to extract non-existent path
        result = checkpoint.get_partial_state("nonexistent.path")
        assert result is None


class TestCheckpointRetrieval:
    """Test checkpoint retrieval and queries"""
    
    def test_get_checkpoint(self):
        """Should retrieve checkpoint by ID."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"test": "data"}
        
        create_result = manager.create_checkpoint(
            operation_id="OP-008",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Retrieve it
        get_result = manager.get_checkpoint(checkpoint_id)
        
        assert get_result.is_ok()
        retrieved = get_result.unwrap()
        assert retrieved.checkpoint_id == checkpoint_id
    
    def test_get_checkpoint_not_found(self):
        """Should return error for missing checkpoint."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        result = manager.get_checkpoint("NONEXISTENT")
        
        assert result.is_err()
    
    def test_get_active_checkpoints(self):
        """Should retrieve all active checkpoints for operation."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"value": "data"}
        
        # Create multiple checkpoints for same operation
        result1 = manager.create_checkpoint(
            operation_id="OP-009",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        result2 = manager.create_checkpoint(
            operation_id="OP-009",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        # List active checkpoints
        list_result = manager.get_active_checkpoints("OP-009")
        
        assert list_result.is_ok()
        checkpoints = list_result.unwrap()
        assert len(checkpoints) == 2


class TestCheckpointCommitment:
    """Test checkpoint lifecycle transitions"""
    
    def test_commit_checkpoint(self):
        """Should mark checkpoint as committed."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"value": "data"}
        
        create_result = manager.create_checkpoint(
            operation_id="OP-010",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Commit it
        commit_result = manager.commit_checkpoint(checkpoint_id)
        
        assert commit_result.is_ok()
        
        # Verify status changed
        get_result = manager.get_checkpoint(checkpoint_id)
        updated = get_result.unwrap()
        assert updated.metadata.status == CheckpointStatus.COMMITTED
        assert updated.metadata.operation_state == OperationState.COMPLETED
    
    def test_rollback_checkpoint(self):
        """Should mark checkpoint as rolled back."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"value": "data"}
        
        create_result = manager.create_checkpoint(
            operation_id="OP-011",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Rollback with reason
        rollback_result = manager.rollback_checkpoint(
            checkpoint_id,
            reason="Operation failed",
        )
        
        assert rollback_result.is_ok()
        
        # Verify status changed
        get_result = manager.get_checkpoint(checkpoint_id)
        updated = get_result.unwrap()
        assert updated.metadata.status == CheckpointStatus.ROLLED_BACK
        assert updated.metadata.metadata_json["rollback_reason"] == "Operation failed"


class TestRecoveryTimeEstimate:
    """Test recovery time estimation"""
    
    def test_set_recovery_time_estimate(self):
        """Should set estimated recovery time."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        state = {"value": "data"}
        
        create_result = manager.create_checkpoint(
            operation_id="OP-012",
            operation_type="test",
            state_snapshot=state,
            recovery_instructions="test",
        )
        
        checkpoint = create_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Set estimate
        estimate_result = manager.set_recovery_time_estimate(
            checkpoint_id,
            estimated_seconds=45.5,
        )
        
        assert estimate_result.is_ok()
        
        # Verify stored
        get_result = manager.get_checkpoint(checkpoint_id)
        updated = get_result.unwrap()
        assert updated.metadata.estimated_recovery_time_seconds == 45.5


class TestCheckpointIntegration:
    """Integration tests for checkpoint manager"""
    
    def test_complete_checkpoint_lifecycle(self):
        """Should handle complete checkpoint lifecycle."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        # Create
        state = {"step": 1, "data": "initial"}
        create_result = manager.create_checkpoint(
            operation_id="OP-013",
            operation_type="multi_step",
            state_snapshot=state,
            recovery_instructions="Resume multi-step operation",
            ac_id="AC-TEST-001",
            phase_id="PHASE-01",
        )
        
        assert create_result.is_ok()
        checkpoint = create_result.unwrap()
        checkpoint_id = checkpoint.checkpoint_id
        
        # Mark partial
        partial_state = {"step": 2, "data": "updated"}
        partial_result = manager.mark_partial_completion(
            checkpoint_id,
            completion_percentage=33.33,
            current_state=partial_state,
        )
        
        assert partial_result.is_ok()
        
        # Estimate recovery time
        estimate_result = manager.set_recovery_time_estimate(checkpoint_id, 30.0)
        assert estimate_result.is_ok()
        
        # Commit
        commit_result = manager.commit_checkpoint(checkpoint_id)
        assert commit_result.is_ok()
        
        # Verify final state
        get_result = manager.get_checkpoint(checkpoint_id)
        final = get_result.unwrap()
        assert final.metadata.status == CheckpointStatus.COMMITTED
        assert final.metadata.partial_completion_percentage == 33.33
        assert final.metadata.estimated_recovery_time_seconds == 30.0
    
    def test_singleton_consistency(self):
        """Should maintain singleton consistency."""
        manager1 = CheckpointManager.instance()
        manager2 = CheckpointManager.instance()
        
        assert manager1 is manager2
    
    def test_concurrent_checkpoints(self):
        """Should handle multiple concurrent checkpoints."""
        manager = CheckpointManager()
        manager.reset_instance()
        manager = CheckpointManager.instance()
        
        # Create multiple operations
        for i in range(5):
            state = {"operation": i, "status": "running"}
            result = manager.create_checkpoint(
                operation_id=f"OP-{i:03d}",
                operation_type="test",
                state_snapshot=state,
                recovery_instructions=f"Resume operation {i}",
            )
            assert result.is_ok()
        
        # Verify all stored
        for i in range(5):
            active_result = manager.get_active_checkpoints(f"OP-{i:03d}")
            assert active_result.is_ok()
            checkpoints = active_result.unwrap()
            assert len(checkpoints) == 1
