"""
CORTEX 6.0 StateManager Unit Tests
==================================
TDD Phase: RED - These tests MUST fail initially

Tests for SQLite-based StateManager with:
- CRUD operations
- WAL mode
- Optimistic locking
- Checkpoint/resume functionality

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
"""

import pytest
import json
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import threading
import time


class TestStateManagerCRUD:
    """Tests for basic Create, Read, Update, Delete operations."""
    
    def test_create_state(self, state_manager):
        """Test creating a new state entry."""
        # Arrange
        key = "test_key_1"
        value = {"name": "test", "count": 42}
        
        # Act
        result = state_manager.create_state(key, value)
        
        # Assert
        assert result is not None
        assert result["key"] == key
        assert result["value"] == value
        assert result["version"] == 1
        assert "created_at" in result
        
    def test_create_state_duplicate_key_raises(self, state_manager):
        """Test that creating duplicate key raises exception."""
        # Arrange
        key = "duplicate_key"
        value = {"data": "original"}
        state_manager.create_state(key, value)
        
        # Act & Assert
        with pytest.raises(state_manager.DuplicateKeyError):
            state_manager.create_state(key, {"data": "duplicate"})
            
    def test_read_state(self, state_manager):
        """Test reading an existing state entry."""
        # Arrange
        key = "read_test_key"
        value = {"message": "hello world"}
        state_manager.create_state(key, value)
        
        # Act
        result = state_manager.read_state(key)
        
        # Assert
        assert result is not None
        assert result["key"] == key
        assert result["value"] == value
        assert result["version"] == 1
        
    def test_read_state_not_found(self, state_manager):
        """Test reading non-existent key returns None."""
        # Act
        result = state_manager.read_state("nonexistent_key")
        
        # Assert
        assert result is None
        
    def test_update_state(self, state_manager):
        """Test updating an existing state entry."""
        # Arrange
        key = "update_test_key"
        original_value = {"count": 1}
        state_manager.create_state(key, original_value)
        
        # Act
        new_value = {"count": 2}
        result = state_manager.update_state(key, new_value, expected_version=1)
        
        # Assert
        assert result is not None
        assert result["value"] == new_value
        assert result["version"] == 2
        
    def test_update_state_not_found_raises(self, state_manager):
        """Test updating non-existent key raises exception."""
        # Act & Assert
        with pytest.raises(state_manager.KeyNotFoundError):
            state_manager.update_state("nonexistent", {"data": "value"}, expected_version=1)
            
    def test_delete_state(self, state_manager):
        """Test deleting an existing state entry."""
        # Arrange
        key = "delete_test_key"
        state_manager.create_state(key, {"to_delete": True})
        
        # Act
        result = state_manager.delete_state(key)
        
        # Assert
        assert result is True
        assert state_manager.read_state(key) is None
        
    def test_delete_state_not_found(self, state_manager):
        """Test deleting non-existent key returns False."""
        # Act
        result = state_manager.delete_state("nonexistent_key")
        
        # Assert
        assert result is False


class TestOptimisticLocking:
    """Tests for optimistic locking with version conflicts."""
    
    def test_optimistic_locking_success(self, state_manager):
        """Test successful update with correct version."""
        # Arrange
        key = "lock_test_key"
        state_manager.create_state(key, {"v": 1})
        
        # Act - Update with correct version
        result = state_manager.update_state(key, {"v": 2}, expected_version=1)
        
        # Assert
        assert result["version"] == 2
        assert result["value"]["v"] == 2
        
    def test_version_conflict_raises(self, state_manager):
        """Test update with wrong version raises VersionConflictError."""
        # Arrange
        key = "conflict_test_key"
        state_manager.create_state(key, {"v": 1})
        state_manager.update_state(key, {"v": 2}, expected_version=1)  # Version now 2
        
        # Act & Assert - Try to update with old version
        with pytest.raises(state_manager.VersionConflictError) as exc_info:
            state_manager.update_state(key, {"v": 3}, expected_version=1)
            
        assert exc_info.value.expected_version == 1
        assert exc_info.value.actual_version == 2
        
    def test_concurrent_updates_detect_conflict(self, state_manager):
        """Test that concurrent updates properly detect conflicts."""
        # Arrange
        key = "concurrent_key"
        state_manager.create_state(key, {"counter": 0})
        
        # Simulate concurrent access - both read version 1
        state1 = state_manager.read_state(key)
        state2 = state_manager.read_state(key)
        
        # First update succeeds
        state_manager.update_state(key, {"counter": 1}, expected_version=state1["version"])
        
        # Second update should fail - version mismatch
        with pytest.raises(state_manager.VersionConflictError):
            state_manager.update_state(key, {"counter": 2}, expected_version=state2["version"])
            
    def test_version_increment_on_update(self, state_manager):
        """Test that version increments correctly on each update."""
        # Arrange
        key = "version_increment_key"
        state_manager.create_state(key, {"data": "v1"})
        
        # Act - Multiple updates
        for i in range(2, 6):
            state_manager.update_state(key, {"data": f"v{i}"}, expected_version=i-1)
            
        # Assert
        final = state_manager.read_state(key)
        assert final["version"] == 5
        assert final["value"]["data"] == "v5"


class TestWALMode:
    """Tests for SQLite WAL (Write-Ahead Logging) mode."""
    
    def test_wal_mode_enabled(self, state_manager):
        """Test that WAL mode is enabled on database."""
        # Act
        journal_mode = state_manager.get_journal_mode()
        
        # Assert
        assert journal_mode.lower() == "wal"
        
    def test_wal_checkpoint(self, state_manager):
        """Test WAL checkpoint operation."""
        # Arrange - Create some data to generate WAL entries
        for i in range(10):
            state_manager.create_state(f"wal_test_{i}", {"index": i})
            
        # Act
        result = state_manager.checkpoint()
        
        # Assert
        assert result is True
        
    def test_synchronous_mode(self, state_manager):
        """Test that synchronous mode is set correctly (NORMAL for WAL)."""
        # Act
        sync_mode = state_manager.get_synchronous_mode()
        
        # Assert - NORMAL (1) or FULL (2) are acceptable for WAL
        assert sync_mode in [1, 2]  # 1=NORMAL, 2=FULL


class TestCheckpointResume:
    """Tests for checkpoint and resume functionality."""
    
    def test_create_checkpoint(self, state_manager):
        """Test creating a checkpoint."""
        # Arrange
        state_manager.create_state("cp_key_1", {"data": "value1"})
        state_manager.create_state("cp_key_2", {"data": "value2"})
        
        # Act
        checkpoint = state_manager.create_checkpoint(
            name="test_checkpoint",
            description="Test checkpoint for testing"
        )
        
        # Assert
        assert checkpoint is not None
        assert "checkpoint_id" in checkpoint
        assert checkpoint["name"] == "test_checkpoint"
        assert "created_at" in checkpoint
        
    def test_list_checkpoints(self, state_manager):
        """Test listing checkpoints."""
        # Arrange
        state_manager.create_state("list_cp_key", {"data": "value"})
        state_manager.create_checkpoint(name="checkpoint_1")
        state_manager.create_checkpoint(name="checkpoint_2")
        
        # Act
        checkpoints = state_manager.list_checkpoints()
        
        # Assert
        assert len(checkpoints) >= 2
        names = [cp["name"] for cp in checkpoints]
        assert "checkpoint_1" in names
        assert "checkpoint_2" in names
        
    def test_restore_checkpoint(self, state_manager):
        """Test restoring from a checkpoint."""
        # Arrange - Create initial state
        state_manager.create_state("restore_key", {"stage": "before"})
        checkpoint = state_manager.create_checkpoint(name="before_change")
        
        # Modify state after checkpoint
        state_manager.update_state("restore_key", {"stage": "after"}, expected_version=1)
        state_manager.create_state("new_key", {"added": "after_checkpoint"})
        
        # Verify state changed
        assert state_manager.read_state("restore_key")["value"]["stage"] == "after"
        assert state_manager.read_state("new_key") is not None
        
        # Act - Restore checkpoint
        result = state_manager.restore_checkpoint(checkpoint["checkpoint_id"])
        
        # Assert - State should be restored
        assert result is True
        restored_state = state_manager.read_state("restore_key")
        assert restored_state["value"]["stage"] == "before"
        
    def test_resume_from_checkpoint(self, state_manager):
        """Test resuming execution from checkpoint."""
        # Arrange
        state_manager.create_state("resume_key", {"step": 1})
        checkpoint = state_manager.create_checkpoint(
            name="resume_point",
            checkpoint_type="PHASE_COMPLETE"
        )
        
        # Simulate some work after checkpoint
        state_manager.update_state("resume_key", {"step": 2}, expected_version=1)
        
        # Act - Resume from checkpoint (should restore to step 1)
        resume_state = state_manager.resume_from_checkpoint(checkpoint["checkpoint_id"])
        
        # Assert
        assert resume_state is not None
        assert resume_state["resume_key"]["value"]["step"] == 1
        
    def test_checkpoint_with_todo_items(self, state_manager):
        """Test checkpoint includes TODO items state."""
        # Arrange
        state_manager.create_todo_item(
            item_id="task-1",
            feature_id="feat01",
            phase_id=1,
            name="Test Task",
            status="IN_PROGRESS"
        )
        
        checkpoint = state_manager.create_checkpoint(name="todo_checkpoint")
        
        # Modify TODO item
        state_manager.update_todo_item("task-1", status="COMPLETED")
        
        # Act - Restore
        state_manager.restore_checkpoint(checkpoint["checkpoint_id"])
        
        # Assert
        todo = state_manager.get_todo_item("task-1")
        assert todo["status"] == "IN_PROGRESS"


class TestTodoItemsManagement:
    """Tests for TODO items CRUD operations."""
    
    def test_create_todo_item(self, state_manager):
        """Test creating a TODO item."""
        # Act
        result = state_manager.create_todo_item(
            item_id="task-2.1",
            feature_id="feat01-foundation",
            phase_id=2,
            name="Design SQLite schema",
            description="Create schema.sql with tables",
            priority="P0_CRITICAL",
            tdd_phase="RED"
        )
        
        # Assert
        assert result is not None
        assert result["item_id"] == "task-2.1"
        assert result["status"] == "NOT_STARTED"
        assert result["version"] == 1
        
    def test_get_todo_item(self, state_manager):
        """Test retrieving a TODO item."""
        # Arrange
        state_manager.create_todo_item(
            item_id="task-get-test",
            feature_id="feat01",
            phase_id=1,
            name="Get Test"
        )
        
        # Act
        result = state_manager.get_todo_item("task-get-test")
        
        # Assert
        assert result is not None
        assert result["item_id"] == "task-get-test"
        assert result["name"] == "Get Test"
        
    def test_update_todo_item(self, state_manager):
        """Test updating a TODO item."""
        # Arrange
        state_manager.create_todo_item(
            item_id="task-update-test",
            feature_id="feat01",
            phase_id=1,
            name="Update Test"
        )
        
        # Act
        result = state_manager.update_todo_item(
            "task-update-test",
            status="IN_PROGRESS",
            started_at=datetime.utcnow().isoformat()
        )
        
        # Assert
        assert result["status"] == "IN_PROGRESS"
        assert result["version"] == 2
        
    def test_list_todo_items_by_status(self, state_manager):
        """Test listing TODO items filtered by status."""
        # Arrange
        state_manager.create_todo_item(item_id="t1", feature_id="f1", phase_id=1, name="Task 1")
        state_manager.create_todo_item(item_id="t2", feature_id="f1", phase_id=1, name="Task 2")
        state_manager.update_todo_item("t1", status="COMPLETED")
        
        # Act
        not_started = state_manager.list_todo_items(status="NOT_STARTED")
        completed = state_manager.list_todo_items(status="COMPLETED")
        
        # Assert
        assert len([t for t in not_started if t["item_id"] == "t2"]) == 1
        assert len([t for t in completed if t["item_id"] == "t1"]) == 1


class TestExecutionState:
    """Tests for execution state tracking."""
    
    def test_create_execution(self, state_manager):
        """Test creating execution state."""
        # Act
        result = state_manager.create_execution(
            execution_id="exec-001",
            orchestrator="planning",
            workflow_type="feature_build"
        )
        
        # Assert
        assert result is not None
        assert result["execution_id"] == "exec-001"
        assert result["status"] == "PENDING"
        
    def test_update_execution_progress(self, state_manager):
        """Test updating execution progress."""
        # Arrange
        state_manager.create_execution(
            execution_id="exec-progress",
            orchestrator="tdd"
        )
        
        # Act
        result = state_manager.update_execution(
            "exec-progress",
            status="RUNNING",
            phase="RED",
            step=1
        )
        
        # Assert
        assert result["status"] == "RUNNING"
        assert result["phase"] == "RED"
        assert result["step"] == 1
        
    def test_complete_execution(self, state_manager):
        """Test completing execution."""
        # Arrange
        state_manager.create_execution(execution_id="exec-complete", orchestrator="debug")
        
        # Act
        result = state_manager.complete_execution(
            "exec-complete",
            status="COMPLETED",
            result={"tests_passed": 10, "issues_fixed": 2}
        )
        
        # Assert
        assert result["status"] == "COMPLETED"
        assert result["result"]["tests_passed"] == 10
        assert result["completed_at"] is not None


class TestContextManager:
    """Tests for StateManager context manager support."""
    
    def test_context_manager_commits_on_success(self, temp_db):
        """Test that context manager commits on successful exit."""
        from src.database.state_manager import StateManager
        
        with StateManager(temp_db) as sm:
            sm.create_state("context_test", {"data": "value"})
            
        # Verify committed by opening new connection
        with StateManager(temp_db) as sm2:
            result = sm2.read_state("context_test")
            assert result is not None
            
    def test_context_manager_rollback_on_exception(self, temp_db):
        """Test that context manager rolls back on exception."""
        from src.database.state_manager import StateManager
        
        try:
            with StateManager(temp_db) as sm:
                sm.create_state("rollback_test", {"data": "value"})
                raise ValueError("Simulated error")
        except ValueError:
            pass
            
        # Verify rolled back
        with StateManager(temp_db) as sm2:
            result = sm2.read_state("rollback_test")
            assert result is None


class TestStateHistory:
    """Tests for state change history tracking."""
    
    def test_history_recorded_on_create(self, state_manager):
        """Test that create operations are recorded in history."""
        # Act
        state_manager.create_state("history_create_key", {"initial": True})
        
        # Assert
        history = state_manager.get_state_history("state", "history_create_key")
        assert len(history) >= 1
        assert history[0]["operation"] == "INSERT"
        
    def test_history_recorded_on_update(self, state_manager):
        """Test that update operations are recorded in history."""
        # Arrange
        state_manager.create_state("history_update_key", {"v": 1})
        
        # Act
        state_manager.update_state("history_update_key", {"v": 2}, expected_version=1)
        
        # Assert
        history = state_manager.get_state_history("state", "history_update_key")
        updates = [h for h in history if h["operation"] == "UPDATE"]
        assert len(updates) >= 1
        
    def test_history_includes_version_tracking(self, state_manager):
        """Test that history includes version information."""
        # Arrange
        state_manager.create_state("version_history_key", {"data": "v1"})
        state_manager.update_state("version_history_key", {"data": "v2"}, expected_version=1)
        
        # Act
        history = state_manager.get_state_history("state", "version_history_key")
        
        # Assert
        update_record = [h for h in history if h["operation"] == "UPDATE"][0]
        assert update_record["version_before"] == 1
        assert update_record["version_after"] == 2


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database file."""
    db_path = tmp_path / "test_state.db"
    yield str(db_path)
    # Cleanup handled by tmp_path fixture


@pytest.fixture
def state_manager(temp_db):
    """Create a StateManager instance for testing."""
    from src.database.state_manager import StateManager
    
    sm = StateManager(temp_db)
    sm.initialize()
    yield sm
    sm.close()
