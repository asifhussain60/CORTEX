"""
Tests for Vision Rollback Manager - AC-AR-015-03

Comprehensive test coverage for rollback capability:
- Rollback validation and safety checks
- Rollback execution and status management
- Orchestrator update tracking
- Rollback history and statistics
- Persistence and recovery
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

from src.core.vision_rollback_manager import (
    VisionRollbackManager,
    VisionRollbackValidator,
    RollbackEvent,
    RollbackValidation,
    RollbackStatus,
    RollbackReason,
)


class TestRollbackValidation:
    """Test rollback validation logic."""

    def test_valid_rollback_validation(self):
        """Test that valid rollback passes validation."""
        validator = VisionRollbackValidator()
        validation = validator.validate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            affected_orchestrators={"orch-1", "orch-2"},
        )
        
        assert validation.is_safe is True
        assert len(validation.validation_errors) == 0

    def test_empty_snapshot_ids_validation_fails(self):
        """Test that empty snapshot IDs fail validation."""
        validator = VisionRollbackValidator()
        validation = validator.validate_rollback(
            current_snapshot_id="",
            target_snapshot_id="snap-002",
            affected_orchestrators=set(),
        )
        
        assert validation.is_safe is False
        assert "Invalid snapshot IDs" in validation.validation_errors

    def test_same_snapshot_ids_validation_fails(self):
        """Test that same source and target snapshot fails validation."""
        validator = VisionRollbackValidator()
        validation = validator.validate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-001",
            affected_orchestrators=set(),
        )
        
        assert validation.is_safe is False
        assert "Cannot rollback to current snapshot" in validation.validation_errors

    def test_affected_orchestrators_tracked(self):
        """Test that affected orchestrators are properly tracked."""
        validator = VisionRollbackValidator()
        orchestrators = {"orch-1", "orch-2", "orch-3"}
        validation = validator.validate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            affected_orchestrators=orchestrators,
        )
        
        assert validation.affected_orchestrators == orchestrators

    def test_orchestrator_compatibility_check(self):
        """Test orchestrator compatibility validation."""
        validator = VisionRollbackValidator()
        registry = {
            "orchestrators": {
                "orch-1": {"tier": "tier0"},
                "orch-2": {"tier": "tier1"},
            }
        }
        validation = validator.validate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            affected_orchestrators={"orch-1", "orch-2"},
            registry_data=registry,
        )
        
        assert validation.is_safe is True

    def test_unknown_orchestrator_produces_warning(self):
        """Test that unknown orchestrators produce warnings."""
        validator = VisionRollbackValidator()
        registry = {
            "orchestrators": {
                "orch-1": {"tier": "tier0"},
            }
        }
        validation = validator.validate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            affected_orchestrators={"orch-1", "orch-999"},
            registry_data=registry,
        )
        
        assert len(validation.validation_warnings) > 0


class TestRollbackEvent:
    """Test rollback event data structure."""

    def test_rollback_event_creation(self):
        """Test creating a rollback event."""
        event = RollbackEvent(
            rollback_id="RB-00001",
            from_snapshot_id="snap-001",
            to_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            status=RollbackStatus.PENDING,
            notes="Testing rollback capability",
        )
        
        assert event.rollback_id == "RB-00001"
        assert event.from_snapshot_id == "snap-001"
        assert event.to_snapshot_id == "snap-002"
        assert event.reason == RollbackReason.USER_REQUEST

    def test_rollback_event_serialization(self):
        """Test rollback event to_dict conversion."""
        event = RollbackEvent(
            rollback_id="RB-00001",
            from_snapshot_id="snap-001",
            to_snapshot_id="snap-002",
            reason=RollbackReason.SAFETY_ISSUE,
            initiated_by="alice@example.com",
            status=RollbackStatus.APPROVED,
            notes="Safety validation required",
        )
        
        data = event.to_dict()
        
        assert data["rollback_id"] == "RB-00001"
        assert data["reason"] == "safety_issue"
        assert data["status"] == "approved"
        assert data["notes"] == "Safety validation required"

    def test_rollback_event_deserialization(self):
        """Test rollback event from_dict conversion."""
        original = RollbackEvent(
            rollback_id="RB-00001",
            from_snapshot_id="snap-001",
            to_snapshot_id="snap-002",
            reason=RollbackReason.PERFORMANCE_DEGRADATION,
            initiated_by="bob@example.com",
            status=RollbackStatus.COMPLETED,
            notes="Performance restored",
        )
        
        data = original.to_dict()
        restored = RollbackEvent.from_dict(data)
        
        assert restored.rollback_id == original.rollback_id
        assert restored.reason == original.reason
        assert restored.status == original.status


class TestRollbackInitiation:
    """Test rollback initiation."""

    def test_initiate_rollback_success(self):
        """Test successfully initiating a rollback."""
        manager = VisionRollbackManager(storage_path=None)
        success, message, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            affected_orchestrators={"orch-1"},
        )
        
        assert success is True
        assert rbk_id is not None
        assert rbk_id.startswith("RB-")

    def test_initiate_rollback_invalid_snapshots(self):
        """Test rollback initiation with invalid snapshots."""
        manager = VisionRollbackManager(storage_path=None)
        success, message, rbk_id = manager.initiate_rollback(
            current_snapshot_id="",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        assert success is False
        assert rbk_id is not None

    def test_rollback_ids_are_sequential(self):
        """Test that rollback IDs increment sequentially."""
        manager = VisionRollbackManager(storage_path=None)
        
        _, _, rbk_id_1 = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        _, _, rbk_id_2 = manager.initiate_rollback(
            current_snapshot_id="snap-002",
            target_snapshot_id="snap-003",
            reason=RollbackReason.SAFETY_ISSUE,
            initiated_by="bob@example.com",
        )
        
        # Extract numbers from IDs
        id_1_num = int(rbk_id_1.split('-')[1])
        id_2_num = int(rbk_id_2.split('-')[1])
        
        assert id_2_num == id_1_num + 1


class TestRollbackExecution:
    """Test rollback execution."""

    def test_execute_approved_rollback(self):
        """Test executing an approved rollback."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            affected_orchestrators={"orch-1", "orch-2"},
        )
        
        success, message = manager.execute_rollback(
            rollback_id=rbk_id,
            new_vision_content={"version": "2.0"},
        )
        
        assert success is True
        
        event = manager.get_rollback_details(rbk_id)
        assert event.status == RollbackStatus.COMPLETED

    def test_execute_nonexistent_rollback(self):
        """Test executing a rollback that doesn't exist."""
        manager = VisionRollbackManager(storage_path=None)
        success, message = manager.execute_rollback(
            rollback_id="RB-99999",
            new_vision_content={},
        )
        
        assert success is False

    def test_execute_unapproved_rollback_fails(self):
        """Test that executing an unapproved rollback fails."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-001",  # Will fail validation
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        success, message = manager.execute_rollback(
            rollback_id=rbk_id,
            new_vision_content={},
        )
        
        assert success is False

    def test_execute_rollback_updates_orchestrators(self):
        """Test that executing rollback tracks orchestrator updates."""
        manager = VisionRollbackManager(storage_path=None)
        orchestrators = {"orch-1", "orch-2", "orch-3"}
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            affected_orchestrators=orchestrators,
        )
        
        manager.execute_rollback(rbk_id, {})
        
        event = manager.get_rollback_details(rbk_id)
        assert event.orchestrators_updated == orchestrators


class TestRollbackHistory:
    """Test rollback history and retrieval."""

    def test_get_rollback_history_empty(self):
        """Test getting history when no rollbacks exist."""
        manager = VisionRollbackManager(storage_path=None)
        history = manager.get_rollback_history()
        
        assert len(history) == 0

    def test_get_rollback_history_multiple(self):
        """Test getting history with multiple rollbacks."""
        manager = VisionRollbackManager(storage_path=None)
        
        for i in range(3):
            manager.initiate_rollback(
                current_snapshot_id=f"snap-{i:03d}",
                target_snapshot_id=f"snap-{i+1:03d}",
                reason=RollbackReason.USER_REQUEST,
                initiated_by="alice@example.com",
            )
        
        history = manager.get_rollback_history()
        assert len(history) == 3

    def test_get_rollback_history_limited(self):
        """Test limiting rollback history results."""
        manager = VisionRollbackManager(storage_path=None)
        
        for i in range(5):
            manager.initiate_rollback(
                current_snapshot_id=f"snap-{i:03d}",
                target_snapshot_id=f"snap-{i+1:03d}",
                reason=RollbackReason.USER_REQUEST,
                initiated_by="alice@example.com",
            )
        
        history = manager.get_rollback_history(limit=2)
        assert len(history) == 2

    def test_get_rollback_history_filtered_by_status(self):
        """Test filtering rollback history by status."""
        manager = VisionRollbackManager(storage_path=None)
        
        # Create completed rollback
        _, _, rbk_id_1 = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        manager.execute_rollback(rbk_id_1, {})
        
        # Create pending rollback
        manager.initiate_rollback(
            current_snapshot_id="snap-002",
            target_snapshot_id="snap-003",
            reason=RollbackReason.SAFETY_ISSUE,
            initiated_by="bob@example.com",
        )
        
        completed_history = manager.get_rollback_history(status=RollbackStatus.COMPLETED)
        assert len(completed_history) == 1
        assert completed_history[0].status == RollbackStatus.COMPLETED

    def test_get_rollback_details(self):
        """Test getting details of a specific rollback."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.ORCHESTRATOR_INCOMPATIBILITY,
            initiated_by="alice@example.com",
            notes="Testing orchestrator compatibility",
        )
        
        event = manager.get_rollback_details(rbk_id)
        
        assert event is not None
        assert event.rollback_id == rbk_id
        assert event.reason == RollbackReason.ORCHESTRATOR_INCOMPATIBILITY
        assert event.notes == "Testing orchestrator compatibility"

    def test_get_nonexistent_rollback_details(self):
        """Test getting details of nonexistent rollback."""
        manager = VisionRollbackManager(storage_path=None)
        event = manager.get_rollback_details("RB-99999")
        
        assert event is None


class TestRollbackSafety:
    """Test rollback safety checks."""

    def test_can_rollback_to_snapshot_valid(self):
        """Test checking if rollback to snapshot is safe."""
        manager = VisionRollbackManager(storage_path=None)
        is_safe, reason = manager.can_rollback_to_snapshot("snap-001")
        
        assert is_safe is True

    def test_can_rollback_to_empty_snapshot_unsafe(self):
        """Test that rollback to empty snapshot is unsafe."""
        manager = VisionRollbackManager(storage_path=None)
        is_safe, reason = manager.can_rollback_to_snapshot("")
        
        assert is_safe is False
        assert "Invalid" in reason

    def test_dry_run_validation(self):
        """Test dry-run validation without executing rollback."""
        manager = VisionRollbackManager(storage_path=None)
        validation = manager.validate_rollback_dry_run(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            affected_orchestrators={"orch-1", "orch-2"},
        )
        
        assert validation.is_safe is True
        assert len(manager.rollback_events) == 0  # No rollback created


class TestOrchestratorUpdateTracking:
    """Test orchestrator update tracking during rollback."""

    def test_record_orchestrator_update_failure(self):
        """Test recording orchestrator update failure."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            affected_orchestrators={"orch-1", "orch-2"},
        )
        
        success, message = manager.record_orchestrator_update_failure(
            rollback_id=rbk_id,
            orchestrator_id="orch-1",
            error_message="Connection timeout",
        )
        
        assert success is True
        
        event = manager.get_rollback_details(rbk_id)
        assert "orch-1" not in event.orchestrators_updated

    def test_record_multiple_orchestrator_failures(self):
        """Test recording multiple orchestrator failures."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            affected_orchestrators={"orch-1", "orch-2", "orch-3"},
        )
        manager.execute_rollback(rbk_id, {})
        
        manager.record_orchestrator_update_failure(rbk_id, "orch-1", "Timeout")
        manager.record_orchestrator_update_failure(rbk_id, "orch-2", "Invalid state")
        
        event = manager.get_rollback_details(rbk_id)
        assert "orch-1" not in event.orchestrators_updated
        assert "orch-2" not in event.orchestrators_updated
        assert "orch-3" in event.orchestrators_updated


class TestRollbackCompletion:
    """Test rollback completion and status management."""

    def test_mark_rollback_complete_success(self):
        """Test marking rollback as complete and successful."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        success, message = manager.mark_rollback_complete(rbk_id, success=True)
        
        assert success is True
        
        event = manager.get_rollback_details(rbk_id)
        assert event.status == RollbackStatus.COMPLETED

    def test_mark_rollback_complete_failure(self):
        """Test marking rollback as failed."""
        manager = VisionRollbackManager(storage_path=None)
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        success, message = manager.mark_rollback_complete(
            rbk_id,
            success=False,
            error_message="Orchestrator update failed",
        )
        
        assert success is True
        
        event = manager.get_rollback_details(rbk_id)
        assert event.status == RollbackStatus.FAILED
        assert event.error_message == "Orchestrator update failed"


class TestRollbackStatistics:
    """Test rollback statistics and reporting."""

    def test_statistics_empty(self):
        """Test statistics with no rollbacks."""
        manager = VisionRollbackManager(storage_path=None)
        stats = manager.get_rollback_statistics()
        
        assert stats["total_rollbacks"] == 0
        assert stats["success_rate"] == 0.0

    def test_statistics_with_rollbacks(self):
        """Test statistics with multiple rollbacks."""
        manager = VisionRollbackManager(storage_path=None)
        
        # Create successful rollback
        _, _, rbk_id_1 = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        manager.execute_rollback(rbk_id_1, {})
        
        # Create failed rollback
        _, _, rbk_id_2 = manager.initiate_rollback(
            current_snapshot_id="snap-003",
            target_snapshot_id="snap-003",  # Will fail validation
            reason=RollbackReason.SAFETY_ISSUE,
            initiated_by="bob@example.com",
        )
        
        stats = manager.get_rollback_statistics()
        
        assert stats["total_rollbacks"] == 2
        assert "completed" in stats["by_status"] or "failed" in stats["by_status"]

    def test_statistics_by_reason(self):
        """Test statistics broken down by rollback reason."""
        manager = VisionRollbackManager(storage_path=None)
        
        manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        manager.initiate_rollback(
            current_snapshot_id="snap-002",
            target_snapshot_id="snap-003",
            reason=RollbackReason.SAFETY_ISSUE,
            initiated_by="bob@example.com",
        )
        
        stats = manager.get_rollback_statistics()
        
        assert "user_request" in stats["by_reason"]
        assert "safety_issue" in stats["by_reason"]


class TestRollbackExport:
    """Test rollback export functionality."""

    def test_export_rollback_history(self):
        """Test exporting rollback history."""
        manager = VisionRollbackManager(storage_path=None)
        
        manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
        )
        
        export = manager.export_rollback_history()
        
        assert "rollback_events" in export
        assert len(export["rollback_events"]) == 1
        assert export["total_rollbacks"] == 1
        assert "generated_timestamp" in export


class TestRollbackPersistence:
    """Test rollback persistence and recovery."""

    def test_save_and_load_rollback_history(self):
        """Test saving and loading rollback history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "rollbacks_unique.json"
            
            # Create and save rollbacks
            manager1 = VisionRollbackManager(storage_path)
            _, _, rbk_id_1 = manager1.initiate_rollback(
                current_snapshot_id="snap-001",
                target_snapshot_id="snap-002",
                reason=RollbackReason.USER_REQUEST,
                initiated_by="alice@example.com",
                affected_orchestrators={"orch-1"},
            )
            manager1.execute_rollback(rbk_id_1, {})
            
            # Load from storage
            manager2 = VisionRollbackManager(storage_path)
            history = manager2.get_rollback_history()
            
            assert len(history) == 1
            assert history[0].rollback_id == rbk_id_1
            assert history[0].status == RollbackStatus.COMPLETED

    def test_persistence_survives_multiple_operations(self):
        """Test persistence through multiple operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "rollbacks_multi.json"
            
            # First session
            manager1 = VisionRollbackManager(storage_path)
            _, _, rbk_id_1 = manager1.initiate_rollback(
                current_snapshot_id="snap-001",
                target_snapshot_id="snap-002",
                reason=RollbackReason.USER_REQUEST,
                initiated_by="alice@example.com",
            )
            manager1.execute_rollback(rbk_id_1, {})
            
            # Second session
            manager2 = VisionRollbackManager(storage_path)
            _, _, rbk_id_2 = manager2.initiate_rollback(
                current_snapshot_id="snap-002",
                target_snapshot_id="snap-003",
                reason=RollbackReason.SAFETY_ISSUE,
                initiated_by="bob@example.com",
            )
            
            # Third session - verify both exist
            manager3 = VisionRollbackManager(storage_path)
            history = manager3.get_rollback_history()
            
            assert len(history) == 2


class TestComplexRollbackScenarios:
    """Test complex rollback scenarios."""

    def test_cascading_rollback_scenario(self):
        """Test scenario where multiple rollbacks occur."""
        manager = VisionRollbackManager(storage_path=None)
        
        # Initial rollback
        _, _, rbk_id_1 = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.BREAKING_CHANGE,
            initiated_by="alice@example.com",
            affected_orchestrators={"orch-1", "orch-2"},
        )
        manager.execute_rollback(rbk_id_1, {})
        
        # Follow-up rollback
        _, _, rbk_id_2 = manager.initiate_rollback(
            current_snapshot_id="snap-002",
            target_snapshot_id="snap-003",
            reason=RollbackReason.UNINTENDED_CONSEQUENCE,
            initiated_by="bob@example.com",
            affected_orchestrators={"orch-3"},
        )
        manager.execute_rollback(rbk_id_2, {})
        
        history = manager.get_rollback_history()
        assert len(history) == 2
        assert history[0].rollback_id == rbk_id_2  # Most recent first
        assert history[1].rollback_id == rbk_id_1

    def test_partial_orchestrator_failure_scenario(self):
        """Test scenario with partial orchestrator failures."""
        manager = VisionRollbackManager(storage_path=None)
        
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-001",
            target_snapshot_id="snap-002",
            reason=RollbackReason.USER_REQUEST,
            initiated_by="alice@example.com",
            affected_orchestrators={"orch-1", "orch-2", "orch-3"},
        )
        manager.execute_rollback(rbk_id, {})
        
        # Record some failures
        manager.record_orchestrator_update_failure(rbk_id, "orch-1", "Timeout")
        manager.record_orchestrator_update_failure(rbk_id, "orch-2", "Validation error")
        
        # Mark complete
        manager.mark_rollback_complete(rbk_id, success=True)
        
        event = manager.get_rollback_details(rbk_id)
        assert "orch-3" in event.orchestrators_updated
        assert "orch-1" not in event.orchestrators_updated
        assert "orch-2" not in event.orchestrators_updated

    def test_rollback_with_full_audit_trail(self):
        """Test complete rollback with full audit trail."""
        manager = VisionRollbackManager(storage_path=None)
        
        # Initiate
        _, _, rbk_id = manager.initiate_rollback(
            current_snapshot_id="snap-prod",
            target_snapshot_id="snap-stable",
            reason=RollbackReason.SAFETY_ISSUE,
            initiated_by="security@example.com",
            affected_orchestrators={"core", "api", "data"},
            notes="Emergency safety rollback required",
        )
        
        # Validate
        event = manager.get_rollback_details(rbk_id)
        assert event.validation is not None
        assert event.validation.is_safe
        
        # Execute
        manager.execute_rollback(rbk_id, {"version": "stable"})
        
        # Handle failure
        manager.record_orchestrator_update_failure(rbk_id, "api", "Config sync failed")
        
        # Complete
        manager.mark_rollback_complete(rbk_id, success=True)
        
        # Verify trail
        final_event = manager.get_rollback_details(rbk_id)
        assert final_event.status == RollbackStatus.COMPLETED
        assert final_event.completion_timestamp is not None
        assert len(final_event.orchestrators_updated) == 2  # core, data
