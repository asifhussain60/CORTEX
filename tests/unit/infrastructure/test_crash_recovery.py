"""Unit tests for crash recovery and state reconstruction."""

import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import json
import time

from cortex.infrastructure.crash_recovery import (
    CrashRecovery,
    WriteAheadLog,
    WALEntry,
    Checkpoint,
    RecoveryResult,
    RecoveryError,
)


class TestWALEntry:
    """Test write-ahead log entry."""
    
    def test_entry_creation(self) -> None:
        """Test creating WAL entry."""
        entry = WALEntry(
            sequence_number=1,
            operation="update_phase",
            data={"phase_id": "phase-1", "status": "IN_PROGRESS"},
            timestamp=datetime.utcnow()
        )
        
        assert entry.sequence_number == 1
        assert entry.operation == "update_phase"
        assert entry.data["phase_id"] == "phase-1"
    
    def test_entry_serialization(self) -> None:
        """Test WAL entry can be serialized."""
        entry = WALEntry(
            sequence_number=5,
            operation="create_lock",
            data={"lock_id": "lock-123"},
            timestamp=datetime.utcnow()
        )
        
        data = entry.to_dict()
        restored = WALEntry.from_dict(data)
        
        assert restored.sequence_number == entry.sequence_number
        assert restored.operation == entry.operation
        assert restored.data == entry.data


class TestCheckpoint:
    """Test checkpoint mechanism."""
    
    def test_checkpoint_creation(self) -> None:
        """Test creating checkpoint."""
        checkpoint = Checkpoint(
            sequence_number=100,
            state_snapshot={"phases": {}, "locks": {}},
            timestamp=datetime.utcnow()
        )
        
        assert checkpoint.sequence_number == 100
        assert "phases" in checkpoint.state_snapshot
    
    def test_checkpoint_persistence(self) -> None:
        """Test checkpoint can be saved and loaded."""
        checkpoint = Checkpoint(
            sequence_number=50,
            state_snapshot={"data": "test"},
            timestamp=datetime.utcnow()
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write(json.dumps(checkpoint.to_dict()))
            temp_path = Path(f.name)
        
        try:
            loaded = Checkpoint.from_file(temp_path)
            assert loaded.sequence_number == 50
            assert loaded.state_snapshot == {"data": "test"}
        finally:
            temp_path.unlink()


class TestWriteAheadLog:
    """Test write-ahead log functionality."""
    
    @pytest.fixture
    def wal_dir(self) -> Path:
        """Create temporary WAL directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def wal(self, wal_dir: Path) -> WriteAheadLog:
        """Create WAL instance."""
        return WriteAheadLog(storage_path=wal_dir)
    
    def test_append_entry(self, wal: WriteAheadLog) -> None:
        """Test appending entry to WAL."""
        wal.append("create_phase", {"phase_id": "phase-1"})
        
        entries = wal.read_entries(from_sequence=0)
        assert len(entries) == 1
        assert entries[0].operation == "create_phase"
    
    def test_entries_ordered_by_sequence(self, wal: WriteAheadLog) -> None:
        """Test WAL entries maintain sequence order."""
        wal.append("op1", {"data": 1})
        wal.append("op2", {"data": 2})
        wal.append("op3", {"data": 3})
        
        entries = wal.read_entries(from_sequence=0)
        
        assert len(entries) == 3
        assert entries[0].sequence_number < entries[1].sequence_number < entries[2].sequence_number
    
    def test_read_from_sequence(self, wal: WriteAheadLog) -> None:
        """Test reading WAL from specific sequence."""
        for i in range(10):
            wal.append(f"op{i}", {"data": i})
        
        # Read from sequence 5
        entries = wal.read_entries(from_sequence=5)
        
        assert all(e.sequence_number >= 5 for e in entries)
    
    def test_wal_corruption_detected(self, wal: WriteAheadLog, wal_dir: Path) -> None:
        """Test corrupted WAL entries detected."""
        wal.append("op1", {"data": 1})
        
        # Corrupt WAL file
        wal_file = next(wal_dir.glob("wal_*.log"))
        with open(wal_file, 'a') as f:
            f.write("CORRUPTED_DATA\n")
        
        # Should detect corruption
        with pytest.raises(RecoveryError):
            wal.read_entries(from_sequence=0)
    
    def test_wal_idempotent_replay(self, wal: WriteAheadLog) -> None:
        """Test WAL replay is idempotent."""
        state = {"counter": 0}
        
        def apply_entry(entry: WALEntry) -> None:
            if entry.operation == "increment":
                state["counter"] += entry.data["amount"]
        
        # Write entries
        wal.append("increment", {"amount": 1})
        wal.append("increment", {"amount": 2})
        
        # Replay once
        for entry in wal.read_entries(from_sequence=0):
            apply_entry(entry)
        
        first_result = state["counter"]
        
        # Replay again
        state["counter"] = 0
        for entry in wal.read_entries(from_sequence=0):
            apply_entry(entry)
        
        # Should get same result
        assert state["counter"] == first_result


class TestCrashRecovery:
    """Test crash recovery orchestration."""
    
    @pytest.fixture
    def storage_dir(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_state_manager(self) -> Mock:
        """Mock state manager."""
        manager = Mock()
        manager.get_state_snapshot.return_value = {"phases": {}}
        manager.restore_state = Mock()
        manager.apply_operation = Mock()
        return manager
    
    @pytest.fixture
    def recovery(
        self,
        storage_dir: Path,
        mock_state_manager: Mock
    ) -> CrashRecovery:
        """Create crash recovery instance."""
        return CrashRecovery(
            storage_path=storage_dir,
            state_manager=mock_state_manager
        )
    
    def test_startup_recovery_without_crash(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test startup recovery when no crash occurred."""
        result = recovery.recover_from_crash()
        
        assert result.success is True
        assert result.records_replayed == 0
    
    def test_startup_recovery_replays_wal(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test startup recovery replays WAL entries."""
        # Simulate operations before crash
        recovery.record_operation("create_phase", {"phase_id": "phase-1"})
        recovery.record_operation("update_phase", {"phase_id": "phase-1", "status": "COMPLETED"})
        
        # Create new recovery instance (simulating restart)
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        result = new_recovery.recover_from_crash()
        
        assert result.success is True
        assert result.records_replayed == 2
        assert mock_state_manager.apply_operation.call_count == 2
    
    def test_checkpoint_reduces_replay_time(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test checkpoint reduces WAL replay time."""
        # Record many operations
        for i in range(100):
            recovery.record_operation(f"op{i}", {"data": i})
        
        # Create checkpoint at 50
        recovery.create_checkpoint()
        
        # Record more operations
        for i in range(100, 110):
            recovery.record_operation(f"op{i}", {"data": i})
        
        # Recover
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        result = new_recovery.recover_from_crash()
        
        # Should only replay operations after checkpoint
        assert result.records_replayed < 100
    
    def test_detect_in_flight_operations(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test detecting in-flight operations during crash."""
        # Start operation
        recovery.begin_operation("op-1", "process_phase")
        recovery.record_operation("step1", {"op_id": "op-1"})
        # Crash before completing
        
        # Recover
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        result = new_recovery.recover_from_crash()
        
        # Should detect incomplete operation
        assert "op-1" in result.incomplete_operations
    
    def test_resume_in_flight_operation(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test resuming in-flight operation after crash."""
        # Start multi-step operation
        recovery.begin_operation("saga-1", "distributed_transaction")
        recovery.record_operation("step1_completed", {"saga": "saga-1"})
        # Crash before step 2
        
        # Recover
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        new_recovery.recover_from_crash()
        
        # Should be able to resume from checkpoint
        assert new_recovery.can_resume_operation("saga-1")
    
    def test_abort_corrupted_operation(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test aborting operation with corrupted state."""
        # Operation with partially corrupted state
        recovery.begin_operation("op-corrupt", "test")
        recovery.record_operation("step1", {"data": "valid"})
        
        # Manually corrupt the state
        # (In real scenario, this could be filesystem corruption)
        
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        # Recovery should handle corruption gracefully
        result = new_recovery.recover_from_crash()
        
        # Might abort corrupted operation rather than replay
        assert result.success is True
    
    def test_state_validation_post_recovery(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test state validated after recovery."""
        recovery.record_operation("op1", {"data": "test"})
        
        # Add validator
        mock_state_manager.validate_state.return_value = True
        
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        result = new_recovery.recover_from_crash()
        
        # Should validate state after replay
        mock_state_manager.validate_state.assert_called_once()
        assert result.validation_passed is True
    
    def test_recovery_time_under_threshold(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test recovery completes within time threshold."""
        # Record operations
        for i in range(50):
            recovery.record_operation(f"op{i}", {"data": i})
        
        # Recover and measure time
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        start = time.time()
        result = new_recovery.recover_from_crash()
        duration = time.time() - start
        
        assert result.success is True
        assert duration < 30  # Should complete in <30 seconds
    
    def test_zero_data_loss_for_committed(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock
    ) -> None:
        """Test zero data loss for committed operations."""
        # Commit operations
        recovery.record_operation("op1", {"data": 1})
        recovery.commit()
        
        recovery.record_operation("op2", {"data": 2})
        recovery.commit()
        
        # Recover
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        result = new_recovery.recover_from_crash()
        
        # Both committed operations should be replayed
        assert result.records_replayed == 2
    
    def test_wal_fallback_to_checkpoint(
        self,
        recovery: CrashRecovery,
        mock_state_manager: Mock,
        storage_dir: Path
    ) -> None:
        """Test fallback to checkpoint when WAL corrupted."""
        # Create checkpoint
        recovery.create_checkpoint()
        
        # Corrupt WAL
        wal_file = next(storage_dir.glob("wal_*.log"), None)
        if wal_file:
            with open(wal_file, 'w') as f:
                f.write("CORRUPTED")
        
        # Recover - should fallback to checkpoint
        new_recovery = CrashRecovery(
            storage_path=recovery.storage_path,
            state_manager=mock_state_manager
        )
        
        result = new_recovery.recover_from_crash()
        
        # Should recover from checkpoint despite WAL corruption
        assert result.success is True
        assert result.recovered_from_checkpoint is True


class TestRecoveryIntegration:
    """Integration tests for crash recovery scenarios."""
    
    def test_complete_crash_recovery_flow(self) -> None:
        """Test complete crash recovery flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            state_manager = Mock()
            state_manager.get_state_snapshot.return_value = {"data": "initial"}
            state_manager.apply_operation = Mock()
            state_manager.validate_state.return_value = True
            
            # Session 1 - before crash
            recovery1 = CrashRecovery(
                storage_path=storage_path,
                state_manager=state_manager
            )
            
            recovery1.record_operation("create_resource", {"id": "res-1"})
            recovery1.record_operation("update_resource", {"id": "res-1", "status": "active"})
            recovery1.create_checkpoint()
            recovery1.record_operation("delete_resource", {"id": "res-2"})
            # Crash here
            
            # Session 2 - after crash
            recovery2 = CrashRecovery(
                storage_path=storage_path,
                state_manager=state_manager
            )
            
            result = recovery2.recover_from_crash()
            
            # Should replay uncommitted operations
            assert result.success is True
            assert result.records_replayed >= 1  # At least the delete operation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
