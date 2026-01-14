"""
Tests for RollbackManager - OE-007 Enforcement
TDD Cycle: RED phase (tests written before implementation)
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json


class TestRollbackManager:
    """Test suite for RollbackManager state snapshot and restore."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def rollback_manager(self, temp_workspace):
        """Create RollbackManager instance."""
        from src.infrastructure.rollback_manager import RollbackManager
        return RollbackManager(workspace_root=temp_workspace)
    
    def test_create_snapshot_basic(self, rollback_manager, temp_workspace):
        """Test creating a basic state snapshot."""
        # RED: This will fail - RollbackManager doesn't exist yet
        state = {
            "phase": "P1",
            "tasks_completed": 3,
            "context": {"feature": "test"}
        }
        
        snapshot_id = rollback_manager.create_snapshot(
            orchestrator="planning_v5",
            state=state,
            description="Test snapshot"
        )
        
        assert snapshot_id is not None
        assert len(snapshot_id) == 36  # UUID format
        
    def test_create_snapshot_with_files(self, rollback_manager, temp_workspace):
        """Test creating snapshot with file tracking."""
        # Create test files
        test_file = temp_workspace / "test.txt"
        test_file.write_text("original content")
        
        state = {"phase": "P1"}
        files_to_track = [str(test_file)]
        
        snapshot_id = rollback_manager.create_snapshot(
            orchestrator="planning_v5",
            state=state,
            files=files_to_track
        )
        
        # Modify file
        test_file.write_text("modified content")
        
        # Verify snapshot preserved original
        snapshot = rollback_manager.get_snapshot(snapshot_id)
        assert snapshot is not None
        assert "test.txt" in snapshot["files"]
        
    def test_restore_snapshot(self, rollback_manager, temp_workspace):
        """Test restoring state from snapshot."""
        original_state = {
            "phase": "P2",
            "tasks_completed": 5,
            "metrics": {"duration": 120}
        }
        
        snapshot_id = rollback_manager.create_snapshot(
            orchestrator="planning_v5",
            state=original_state
        )
        
        # Restore snapshot
        restored_state = rollback_manager.restore_snapshot(snapshot_id)
        
        assert restored_state == original_state
        
    def test_restore_snapshot_with_files(self, rollback_manager, temp_workspace):
        """Test restoring files from snapshot."""
        test_file = temp_workspace / "test.txt"
        test_file.write_text("original content")
        
        snapshot_id = rollback_manager.create_snapshot(
            orchestrator="planning_v5",
            state={"phase": "P1"},
            files=[str(test_file)]
        )
        
        # Modify file
        test_file.write_text("corrupted content")
        
        # Restore
        rollback_manager.restore_snapshot(snapshot_id, restore_files=True)
        
        assert test_file.read_text() == "original content"
        
    def test_list_snapshots(self, rollback_manager):
        """Test listing snapshots for an orchestrator."""
        rollback_manager.create_snapshot("planner", {"phase": "P1"}, description="First")
        rollback_manager.create_snapshot("planner", {"phase": "P2"}, description="Second")
        rollback_manager.create_snapshot("ado", {"phase": "P1"}, description="Other")
        
        snapshots = rollback_manager.list_snapshots(orchestrator="planner")
        
        assert len(snapshots) == 2
        assert all(s["orchestrator"] == "planner" for s in snapshots)
        
    def test_delete_snapshot(self, rollback_manager):
        """Test deleting a snapshot."""
        snapshot_id = rollback_manager.create_snapshot("planner", {"phase": "P1"})
        
        assert rollback_manager.get_snapshot(snapshot_id) is not None
        
        rollback_manager.delete_snapshot(snapshot_id)
        
        assert rollback_manager.get_snapshot(snapshot_id) is None
        
    def test_snapshot_metadata(self, rollback_manager):
        """Test snapshot contains proper metadata."""
        snapshot_id = rollback_manager.create_snapshot(
            orchestrator="planning_v5",
            state={"phase": "P1"},
            description="Test metadata"
        )
        
        snapshot = rollback_manager.get_snapshot(snapshot_id)
        
        assert snapshot["id"] == snapshot_id
        assert snapshot["orchestrator"] == "planning_v5"
        assert snapshot["description"] == "Test metadata"
        assert "created_at" in snapshot
        assert "state" in snapshot
        
    def test_restore_nonexistent_snapshot(self, rollback_manager):
        """Test restoring nonexistent snapshot raises error."""
        with pytest.raises(ValueError, match="Snapshot .* not found"):
            rollback_manager.restore_snapshot("nonexistent-id")
            
    def test_snapshot_isolation(self, rollback_manager):
        """Test snapshots are isolated from each other."""
        state1 = {"phase": "P1", "value": 100}
        state2 = {"phase": "P2", "value": 200}
        
        id1 = rollback_manager.create_snapshot("orch1", state1)
        id2 = rollback_manager.create_snapshot("orch2", state2)
        
        restored1 = rollback_manager.restore_snapshot(id1)
        restored2 = rollback_manager.restore_snapshot(id2)
        
        assert restored1["value"] == 100
        assert restored2["value"] == 200
        
    def test_snapshot_with_binary_files(self, rollback_manager, temp_workspace):
        """Test snapshot handles binary files correctly."""
        binary_file = temp_workspace / "test.bin"
        binary_data = b'\x00\x01\x02\xff\xfe\xfd'
        binary_file.write_bytes(binary_data)
        
        snapshot_id = rollback_manager.create_snapshot(
            orchestrator="test",
            state={"phase": "P1"},
            files=[str(binary_file)]
        )
        
        # Corrupt file
        binary_file.write_bytes(b'\x00' * 10)
        
        # Restore
        rollback_manager.restore_snapshot(snapshot_id, restore_files=True)
        
        assert binary_file.read_bytes() == binary_data
