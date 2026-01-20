"""Unit tests for automatic state repair mechanisms."""

import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile

from cortex.core.recovery.state_repair import (
    StateRepair,
    InconsistencyType,
    InconsistencyRecord,
    RepairStrategy,
    RepairResult,
    RepairMode,
    RepairError,
)


class TestInconsistencyRecord:
    """Test inconsistency detection and recording."""
    
    def test_record_creation(self) -> None:
        """Test creating inconsistency record."""
        record = InconsistencyRecord(
            inconsistency_id="inc-123",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash mismatch at block 5",
            affected_resources=["block-5", "block-6"],
            metadata={"expected": "abc", "actual": "def"}
        )
        
        assert record.inconsistency_type == InconsistencyType.HASH_CHAIN_BREAK
        assert record.severity == "HIGH"
        assert len(record.affected_resources) == 2
    
    def test_severity_ordering(self) -> None:
        """Test inconsistencies ordered by severity."""
        critical = InconsistencyRecord(
            inconsistency_id="c1",
            inconsistency_type=InconsistencyType.DATA_CORRUPTION,
            severity="CRITICAL",
            detected_at=datetime.utcnow(),
            description="",
            affected_resources=[]
        )
        high = InconsistencyRecord(
            inconsistency_id="h1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="",
            affected_resources=[]
        )
        
        assert critical.priority() > high.priority()


class TestRepairStrategy:
    """Test repair strategy selection."""
    
    def test_hash_chain_repair_strategy(self) -> None:
        """Test hash chain break repair strategy."""
        strategy = RepairStrategy.for_inconsistency(InconsistencyType.HASH_CHAIN_BREAK)
        
        assert strategy.action == "rebuild_hash_chain"
        assert "Rebuild hash chain" in strategy.description
    
    def test_referential_integrity_repair(self) -> None:
        """Test referential integrity repair strategy."""
        strategy = RepairStrategy.for_inconsistency(InconsistencyType.REFERENTIAL_INTEGRITY)
        
        assert strategy.action == "fix_references"
        assert "Fix broken references" in strategy.description
    
    def test_version_mismatch_repair(self) -> None:
        """Test version mismatch repair strategy."""
        strategy = RepairStrategy.for_inconsistency(InconsistencyType.VERSION_MISMATCH)
        
        assert strategy.action == "reconcile_versions"


class TestStateRepair:
    """Test state repair orchestration."""
    
    @pytest.fixture
    def storage_dir(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_hash_chain(self) -> Mock:
        """Mock hash chain manager."""
        manager = Mock()
        manager.verify_integrity.return_value = True
        manager.rebuild_chain = Mock()
        return manager
    
    @pytest.fixture
    def repair_engine(
        self,
        storage_dir: Path,
        mock_hash_chain: Mock
    ) -> StateRepair:
        """Create repair engine with mocked dependencies."""
        return StateRepair(
            storage_path=storage_dir,
            hash_chain_manager=mock_hash_chain,
            enable_auto_repair=False
        )
    
    def test_detect_hash_chain_break(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test detecting hash chain break."""
        mock_hash_chain.verify_integrity.return_value = False
        mock_hash_chain.get_break_location.return_value = ("block-5", "hash mismatch")
        
        inconsistencies = repair_engine.detect_inconsistencies()
        
        assert len(inconsistencies) > 0
        hash_breaks = [i for i in inconsistencies if i.inconsistency_type == InconsistencyType.HASH_CHAIN_BREAK]
        assert len(hash_breaks) > 0
        assert "block-5" in hash_breaks[0].affected_resources
    
    def test_dry_run_mode(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test dry-run detects without modifying."""
        mock_hash_chain.verify_integrity.return_value = False
        mock_hash_chain.get_break_location.return_value = ("block-5", "mismatch")
        
        inconsistencies = repair_engine.detect_inconsistencies()
        
        # Run in dry-run mode
        results = repair_engine.repair_inconsistencies(
            inconsistencies,
            mode=RepairMode.DRY_RUN
        )
        
        assert len(results) > 0
        assert all(r.dry_run for r in results)
        # No actual repair called
        mock_hash_chain.rebuild_chain.assert_not_called()
    
    def test_actual_repair_modifies_state(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test actual repair modifies state."""
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash break at block-5",
            affected_resources=["block-5"],
            metadata={}
        )
        
        results = repair_engine.repair_inconsistencies(
            [inconsistency],
            mode=RepairMode.EXECUTE
        )
        
        assert len(results) == 1
        assert results[0].success is True
        assert not results[0].dry_run
        mock_hash_chain.rebuild_chain.assert_called_once()
    
    def test_repair_audit_trail(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test repair creates audit trail with before/after state."""
        mock_hash_chain.get_state_snapshot.side_effect = [
            {"hash": "before"},
            {"hash": "after"}
        ]
        
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash break",
            affected_resources=["block-5"],
            metadata={}
        )
        
        results = repair_engine.repair_inconsistencies([inconsistency])
        
        assert len(results) == 1
        assert results[0].before_state is not None
        assert results[0].after_state is not None
        assert results[0].before_state != results[0].after_state
    
    def test_repair_validation(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test repair validates result doesn't introduce new issues."""
        # First repair succeeds, but validation shows new issue
        mock_hash_chain.rebuild_chain.return_value = None
        mock_hash_chain.verify_integrity.side_effect = [
            False,  # Initial detection
            False   # Post-repair validation (still broken)
        ]
        
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash break",
            affected_resources=["block-5"],
            metadata={}
        )
        
        results = repair_engine.repair_inconsistencies([inconsistency])
        
        # Repair should be marked as failed validation
        assert len(results) == 1
        assert results[0].success is False
        assert "validation failed" in results[0].message.lower()
    
    def test_rollback_on_failed_validation(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test repair rolled back if validation fails."""
        backup_state = {"hash": "backup"}
        mock_hash_chain.create_backup.return_value = backup_state
        mock_hash_chain.rebuild_chain.return_value = None
        mock_hash_chain.verify_integrity.side_effect = [False, False]  # Still broken after repair
        
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash break",
            affected_resources=["block-5"],
            metadata={}
        )
        
        results = repair_engine.repair_inconsistencies([inconsistency])
        
        # Should have restored backup
        mock_hash_chain.restore_backup.assert_called_once_with(backup_state)
    
    def test_multiple_inconsistencies_prioritized(
        self,
        repair_engine: StateRepair
    ) -> None:
        """Test multiple inconsistencies repaired in priority order."""
        critical = InconsistencyRecord(
            inconsistency_id="c1",
            inconsistency_type=InconsistencyType.DATA_CORRUPTION,
            severity="CRITICAL",
            detected_at=datetime.utcnow(),
            description="Data corruption",
            affected_resources=[],
            metadata={}
        )
        low = InconsistencyRecord(
            inconsistency_id="l1",
            inconsistency_type=InconsistencyType.VERSION_MISMATCH,
            severity="LOW",
            detected_at=datetime.utcnow(),
            description="Version mismatch",
            affected_resources=[],
            metadata={}
        )
        
        # Submit in wrong order
        results = repair_engine.repair_inconsistencies([low, critical])
        
        # Should repair critical first
        assert results[0].inconsistency_id == "c1"
        assert results[1].inconsistency_id == "l1"
    
    def test_repair_conflicts_with_active_operations(
        self,
        repair_engine: StateRepair
    ) -> None:
        """Test repair deferred if conflicts with active operations."""
        # Set active operation on same resource
        repair_engine._active_operations.add("block-5")
        
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash break",
            affected_resources=["block-5"],
            metadata={}
        )
        
        results = repair_engine.repair_inconsistencies([inconsistency])
        
        # Should defer repair
        assert len(results) == 1
        assert results[0].success is False
        assert "deferred" in results[0].message.lower() or "conflict" in results[0].message.lower()
    
    def test_irreparable_corruption_quarantined(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test irreparable corruption is quarantined."""
        mock_hash_chain.rebuild_chain.side_effect = RepairError("Cannot repair: data lost")
        
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.DATA_CORRUPTION,
            severity="CRITICAL",
            detected_at=datetime.utcnow(),
            description="Corruption",
            affected_resources=["block-5"],
            metadata={}
        )
        
        results = repair_engine.repair_inconsistencies([inconsistency])
        
        # Should quarantine
        assert repair_engine.is_quarantined("block-5")
        
        # Alert should be sent
        assert repair_engine.get_alerts()  # Should have alert
    
    def test_partial_repair_checkpoint(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test partial repair checkpoints progress."""
        inconsistencies = [
            InconsistencyRecord(
                inconsistency_id=f"inc-{i}",
                inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
                severity="HIGH",
                detected_at=datetime.utcnow(),
                description=f"Break {i}",
                affected_resources=[f"block-{i}"],
                metadata={}
            )
            for i in range(3)
        ]
        
        # Second repair fails
        mock_hash_chain.rebuild_chain.side_effect = [
            None,  # First succeeds
            RuntimeError("crash"),  # Second crashes
            None   # Third would succeed
        ]
        
        try:
            repair_engine.repair_inconsistencies(inconsistencies)
        except RuntimeError:
            pass
        
        # Should have checkpoint of first repair
        progress = repair_engine.get_repair_progress()
        assert progress["completed"] >= 1
        
        # Resume from checkpoint
        results = repair_engine.resume_repair()
        
        # Should complete remaining repairs
        assert len(results) >= 2
    
    def test_scheduled_repair_trigger(self, repair_engine: StateRepair) -> None:
        """Test repair can be scheduled to run automatically."""
        with patch.object(repair_engine, 'detect_inconsistencies', return_value=[]) as mock_detect:
            repair_engine.schedule_repair(interval_hours=24)
            
            # Trigger should be set
            assert repair_engine._scheduled_repair_active
    
    def test_on_demand_repair(
        self,
        repair_engine: StateRepair,
        mock_hash_chain: Mock
    ) -> None:
        """Test operator can trigger repair on demand."""
        mock_hash_chain.verify_integrity.return_value = False
        mock_hash_chain.get_break_location.return_value = ("block-5", "mismatch")
        
        # On-demand repair
        results = repair_engine.repair_on_demand()
        
        assert len(results) > 0
        # Should have detected and repaired
        mock_hash_chain.rebuild_chain.assert_called()
    
    def test_repair_metrics(self, repair_engine: StateRepair) -> None:
        """Test repair metrics collected."""
        inconsistency = InconsistencyRecord(
            inconsistency_id="inc-1",
            inconsistency_type=InconsistencyType.HASH_CHAIN_BREAK,
            severity="HIGH",
            detected_at=datetime.utcnow(),
            description="Hash break",
            affected_resources=["block-5"],
            metadata={}
        )
        
        repair_engine.repair_inconsistencies([inconsistency])
        
        metrics = repair_engine.get_metrics()
        
        assert "repairs_attempted" in metrics
        assert "repairs_succeeded" in metrics
        assert "repair_duration_seconds" in metrics


class TestRepairIntegration:
    """Integration tests for state repair scenarios."""
    
    def test_end_to_end_hash_chain_repair(self) -> None:
        """Test complete hash chain repair flow."""
        hash_chain = Mock()
        hash_chain.verify_integrity.side_effect = [False, True]  # Broken then fixed
        hash_chain.get_break_location.return_value = ("block-10", "hash mismatch")
        hash_chain.create_backup.return_value = {"backup": "data"}
        hash_chain.get_state_snapshot.side_effect = [
            {"broken": True},
            {"broken": False}
        ]
        
        repair = StateRepair(hash_chain_manager=hash_chain)
        
        # Detect
        inconsistencies = repair.detect_inconsistencies()
        assert len(inconsistencies) > 0
        
        # Repair
        results = repair.repair_inconsistencies(inconsistencies)
        assert len(results) > 0
        assert results[0].success is True
        
        # Verify hash chain rebuilt
        hash_chain.rebuild_chain.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
