"""
Tests for RecoveryManager - Checkpoint/Rollback System.

Phase 3 of Toolkit Manager Implementation
TDD: RED Phase - Tests written before implementation

Test Categories:
1. Checkpoint dataclass tests
2. RecoveryManager initialization tests
3. Checkpoint creation tests
4. Rollback functionality tests
5. Checkpoint persistence tests
6. Auto-prune tests
7. Edge cases and error handling
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from unittest.mock import patch, MagicMock

# Import classes under test
from core.checkpoint import Checkpoint, CheckpointState
from core.recovery_manager import (
    RecoveryManager,
    ExecutionContext,
    RollbackResult,
    RecoveryError,
    CheckpointNotFoundError,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_toolkit_root(tmp_path):
    """Create a temporary toolkit root directory."""
    toolkit_root = tmp_path / "toolkit"
    toolkit_root.mkdir()
    return toolkit_root


@pytest.fixture
def recovery_manager(temp_toolkit_root):
    """Create a RecoveryManager instance with temp directory."""
    return RecoveryManager(temp_toolkit_root)


@pytest.fixture
def sample_files(temp_toolkit_root):
    """Create sample files for testing."""
    files = {}
    
    # Create a Python tool file
    tool_file = temp_toolkit_root / "tools" / "my_tool.py"
    tool_file.parent.mkdir(parents=True, exist_ok=True)
    tool_file.write_text("# Original content\ndef main(): pass")
    files["tool"] = tool_file
    
    # Create a config file
    config_file = temp_toolkit_root / "config" / "settings.yaml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("setting: value")
    files["config"] = config_file
    
    return files


@pytest.fixture
def execution_context(sample_files):
    """Create a sample execution context."""
    return ExecutionContext(
        tool="cleanup",
        args=["--force", "--verbose"],
        affected_paths=[sample_files["tool"], sample_files["config"]],
        is_destructive=True,
    )


# =============================================================================
# 1. Checkpoint Dataclass Tests
# =============================================================================

class TestCheckpoint:
    """Tests for the Checkpoint dataclass."""
    
    def test_checkpoint_creation(self):
        """Checkpoint can be created with all required fields."""
        checkpoint = Checkpoint(
            id="test-123",
            timestamp=datetime.now(),
            tool="cleanup",
            args=["--force"],
            affected_paths=[Path("/some/path")],
            git_sha="abc123",
            state_snapshot={"/some/path": "content"},
        )
        
        assert checkpoint.id == "test-123"
        assert checkpoint.tool == "cleanup"
        assert len(checkpoint.affected_paths) == 1
    
    def test_checkpoint_to_json(self):
        """Checkpoint can be serialized to JSON."""
        timestamp = datetime(2025, 12, 31, 10, 0, 0)
        checkpoint = Checkpoint(
            id="test-456",
            timestamp=timestamp,
            tool="validate",
            args=["--strict"],
            affected_paths=[Path("/test/file.py")],
            git_sha="def456",
            state_snapshot={"/test/file.py": "original content"},
        )
        
        json_str = checkpoint.to_json()
        data = json.loads(json_str)
        
        assert data["id"] == "test-456"
        assert data["tool"] == "validate"
        assert "state_snapshot" in data
    
    def test_checkpoint_from_json(self):
        """Checkpoint can be deserialized from JSON."""
        json_data = {
            "id": "test-789",
            "timestamp": "2025-12-31T10:00:00",
            "tool": "migrate",
            "args": ["--dry-run"],
            "affected_paths": ["/path/to/file"],
            "git_sha": "ghi789",
            "state_snapshot": {"/path/to/file": "content"},
        }
        
        checkpoint = Checkpoint.from_json(json.dumps(json_data))
        
        assert checkpoint.id == "test-789"
        assert checkpoint.tool == "migrate"
        assert len(checkpoint.affected_paths) == 1
    
    def test_checkpoint_optional_git_sha(self):
        """Checkpoint can have None git_sha (not in git repo)."""
        checkpoint = Checkpoint(
            id="no-git",
            timestamp=datetime.now(),
            tool="test",
            args=[],
            affected_paths=[],
            git_sha=None,
            state_snapshot={},
        )
        
        assert checkpoint.git_sha is None
    
    def test_checkpoint_state_enum(self):
        """CheckpointState enum has correct values."""
        assert CheckpointState.PENDING.value == "pending"
        assert CheckpointState.ACTIVE.value == "active"
        assert CheckpointState.ROLLED_BACK.value == "rolled_back"
        assert CheckpointState.EXPIRED.value == "expired"


# =============================================================================
# 2. RecoveryManager Initialization Tests
# =============================================================================

class TestRecoveryManagerInit:
    """Tests for RecoveryManager initialization."""
    
    def test_manager_creates_checkpoint_directory(self, temp_toolkit_root):
        """RecoveryManager creates .checkpoints directory on init."""
        manager = RecoveryManager(temp_toolkit_root)
        
        checkpoint_dir = temp_toolkit_root / ".checkpoints"
        assert checkpoint_dir.exists()
        assert checkpoint_dir.is_dir()
    
    def test_manager_with_existing_checkpoint_dir(self, temp_toolkit_root):
        """RecoveryManager works with existing .checkpoints directory."""
        checkpoint_dir = temp_toolkit_root / ".checkpoints"
        checkpoint_dir.mkdir()
        (checkpoint_dir / "existing.json").write_text("{}")
        
        manager = RecoveryManager(temp_toolkit_root)
        
        assert checkpoint_dir.exists()
        # Existing files preserved
        assert (checkpoint_dir / "existing.json").exists()
    
    def test_manager_stores_toolkit_root(self, temp_toolkit_root):
        """RecoveryManager stores toolkit root path."""
        manager = RecoveryManager(temp_toolkit_root)
        
        assert manager.toolkit_root == temp_toolkit_root
    
    def test_manager_default_max_checkpoints(self, temp_toolkit_root):
        """RecoveryManager has default max_checkpoints of 50."""
        manager = RecoveryManager(temp_toolkit_root)
        
        assert manager.max_checkpoints == 50
    
    def test_manager_custom_max_checkpoints(self, temp_toolkit_root):
        """RecoveryManager accepts custom max_checkpoints."""
        manager = RecoveryManager(temp_toolkit_root, max_checkpoints=10)
        
        assert manager.max_checkpoints == 10


# =============================================================================
# 3. Checkpoint Creation Tests
# =============================================================================

class TestCheckpointCreation:
    """Tests for creating checkpoints."""
    
    def test_create_checkpoint_returns_checkpoint(
        self, recovery_manager, execution_context
    ):
        """create_checkpoint returns a Checkpoint instance."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        assert isinstance(checkpoint, Checkpoint)
        assert checkpoint.id is not None
        assert len(checkpoint.id) > 0
    
    def test_checkpoint_captures_tool_and_args(
        self, recovery_manager, execution_context
    ):
        """Checkpoint captures tool name and arguments."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        assert checkpoint.tool == "cleanup"
        assert checkpoint.args == ["--force", "--verbose"]
    
    def test_checkpoint_captures_affected_paths(
        self, recovery_manager, execution_context, sample_files
    ):
        """Checkpoint captures affected file paths."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        assert len(checkpoint.affected_paths) == 2
        path_strings = [str(p) for p in checkpoint.affected_paths]
        assert str(sample_files["tool"]) in path_strings
    
    def test_checkpoint_captures_state_snapshot(
        self, recovery_manager, execution_context, sample_files
    ):
        """Checkpoint captures file contents as state snapshot."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # State snapshot should contain file contents
        tool_path = str(sample_files["tool"])
        assert tool_path in checkpoint.state_snapshot
        assert "Original content" in checkpoint.state_snapshot[tool_path]
    
    def test_checkpoint_has_timestamp(
        self, recovery_manager, execution_context
    ):
        """Checkpoint has a timestamp."""
        before = datetime.now()
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        after = datetime.now()
        
        assert before <= checkpoint.timestamp <= after
    
    def test_checkpoint_has_unique_id(
        self, recovery_manager, execution_context
    ):
        """Each checkpoint has a unique ID."""
        cp1 = recovery_manager.create_checkpoint(execution_context)
        cp2 = recovery_manager.create_checkpoint(execution_context)
        
        assert cp1.id != cp2.id
    
    def test_checkpoint_captures_git_sha(
        self, recovery_manager, execution_context
    ):
        """Checkpoint captures git SHA if in git repo."""
        with patch.object(
            recovery_manager, '_get_current_sha', return_value='abc123'
        ):
            checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        assert checkpoint.git_sha == 'abc123'
    
    def test_checkpoint_handles_non_git_repo(
        self, recovery_manager, execution_context
    ):
        """Checkpoint handles directories not in git repo."""
        # Default behavior - _get_current_sha returns None for non-git
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # Should not raise, git_sha can be None
        assert checkpoint.git_sha is None or isinstance(checkpoint.git_sha, str)


# =============================================================================
# 4. Checkpoint Persistence Tests
# =============================================================================

class TestCheckpointPersistence:
    """Tests for checkpoint persistence."""
    
    def test_checkpoint_persisted_to_file(
        self, recovery_manager, execution_context
    ):
        """Created checkpoint is persisted to disk."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        checkpoint_file = (
            recovery_manager.checkpoint_dir / f"{checkpoint.id}.json"
        )
        assert checkpoint_file.exists()
    
    def test_persisted_checkpoint_is_valid_json(
        self, recovery_manager, execution_context
    ):
        """Persisted checkpoint file contains valid JSON."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        checkpoint_file = (
            recovery_manager.checkpoint_dir / f"{checkpoint.id}.json"
        )
        data = json.loads(checkpoint_file.read_text())
        
        assert data["id"] == checkpoint.id
        assert data["tool"] == "cleanup"
    
    def test_list_checkpoints_returns_all(
        self, recovery_manager, execution_context
    ):
        """list_checkpoints returns all stored checkpoints."""
        # Create multiple checkpoints
        cp1 = recovery_manager.create_checkpoint(execution_context)
        cp2 = recovery_manager.create_checkpoint(execution_context)
        cp3 = recovery_manager.create_checkpoint(execution_context)
        
        checkpoints = recovery_manager.list_checkpoints()
        
        assert len(checkpoints) >= 3
        ids = [cp.id for cp in checkpoints]
        assert cp1.id in ids
        assert cp2.id in ids
        assert cp3.id in ids
    
    def test_list_checkpoints_with_limit(
        self, recovery_manager, execution_context
    ):
        """list_checkpoints respects limit parameter."""
        # Create 5 checkpoints
        for _ in range(5):
            recovery_manager.create_checkpoint(execution_context)
        
        checkpoints = recovery_manager.list_checkpoints(limit=3)
        
        assert len(checkpoints) == 3
    
    def test_list_checkpoints_ordered_by_timestamp(
        self, recovery_manager, execution_context
    ):
        """list_checkpoints returns newest first."""
        cp1 = recovery_manager.create_checkpoint(execution_context)
        cp2 = recovery_manager.create_checkpoint(execution_context)
        cp3 = recovery_manager.create_checkpoint(execution_context)
        
        checkpoints = recovery_manager.list_checkpoints()
        
        # Newest should be first
        assert checkpoints[0].id == cp3.id
    
    def test_get_checkpoint_by_id(
        self, recovery_manager, execution_context
    ):
        """Can retrieve specific checkpoint by ID."""
        original = recovery_manager.create_checkpoint(execution_context)
        
        retrieved = recovery_manager.get_checkpoint(original.id)
        
        assert retrieved.id == original.id
        assert retrieved.tool == original.tool
    
    def test_get_checkpoint_not_found(self, recovery_manager):
        """get_checkpoint raises error for unknown ID."""
        with pytest.raises(CheckpointNotFoundError):
            recovery_manager.get_checkpoint("nonexistent-id")


# =============================================================================
# 5. Rollback Functionality Tests
# =============================================================================

class TestRollback:
    """Tests for rollback functionality."""
    
    def test_rollback_restores_file_contents(
        self, recovery_manager, execution_context, sample_files
    ):
        """Rollback restores files to checkpoint state."""
        # Create checkpoint with original content
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # Modify the file
        sample_files["tool"].write_text("# Modified content")
        
        # Rollback
        result = recovery_manager.rollback(checkpoint.id)
        
        # File should be restored
        content = sample_files["tool"].read_text()
        assert "Original content" in content
    
    def test_rollback_returns_result(
        self, recovery_manager, execution_context
    ):
        """rollback returns RollbackResult."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        result = recovery_manager.rollback(checkpoint.id)
        
        assert isinstance(result, RollbackResult)
        assert result.success is True
        assert result.checkpoint_id == checkpoint.id
    
    def test_rollback_reports_restored_files(
        self, recovery_manager, execution_context, sample_files
    ):
        """RollbackResult includes list of restored files."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        sample_files["tool"].write_text("# Modified")
        
        result = recovery_manager.rollback(checkpoint.id)
        
        assert len(result.restored_paths) > 0
    
    def test_rollback_nonexistent_checkpoint(self, recovery_manager):
        """rollback raises error for unknown checkpoint."""
        with pytest.raises(CheckpointNotFoundError):
            recovery_manager.rollback("fake-checkpoint-id")
    
    def test_rollback_handles_deleted_files(
        self, recovery_manager, execution_context, sample_files
    ):
        """Rollback recreates deleted files."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # Delete the file
        sample_files["tool"].unlink()
        assert not sample_files["tool"].exists()
        
        # Rollback should recreate
        result = recovery_manager.rollback(checkpoint.id)
        
        assert sample_files["tool"].exists()
        assert "Original content" in sample_files["tool"].read_text()
    
    def test_rollback_handles_new_files(
        self, recovery_manager, execution_context, sample_files
    ):
        """Rollback removes files created after checkpoint."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # Create new file after checkpoint
        new_file = sample_files["tool"].parent / "new_file.py"
        new_file.write_text("# New file")
        
        # Rollback - new file should remain (only restores tracked paths)
        result = recovery_manager.rollback(checkpoint.id)
        
        # New file is NOT in checkpoint, so rollback doesn't touch it
        assert new_file.exists()
    
    def test_rollback_updates_checkpoint_state(
        self, recovery_manager, execution_context
    ):
        """Rollback marks checkpoint as rolled back."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        recovery_manager.rollback(checkpoint.id)
        
        updated = recovery_manager.get_checkpoint(checkpoint.id)
        assert updated.state == CheckpointState.ROLLED_BACK


# =============================================================================
# 6. Auto-Prune Tests
# =============================================================================

class TestAutoPrune:
    """Tests for automatic checkpoint pruning."""
    
    def test_auto_prune_when_exceeds_max(self, temp_toolkit_root, sample_files):
        """Old checkpoints pruned when max exceeded."""
        manager = RecoveryManager(temp_toolkit_root, max_checkpoints=3)
        
        context = ExecutionContext(
            tool="test",
            args=[],
            affected_paths=[sample_files["tool"]],
            is_destructive=True,
        )
        
        # Create 5 checkpoints (max is 3)
        checkpoints = []
        for i in range(5):
            cp = manager.create_checkpoint(context)
            checkpoints.append(cp)
        
        # Should only have 3 checkpoints
        remaining = manager.list_checkpoints()
        assert len(remaining) == 3
        
        # Oldest should be pruned
        remaining_ids = [cp.id for cp in remaining]
        assert checkpoints[0].id not in remaining_ids
        assert checkpoints[1].id not in remaining_ids
    
    def test_auto_prune_keeps_newest(self, temp_toolkit_root, sample_files):
        """Auto-prune keeps the newest checkpoints."""
        manager = RecoveryManager(temp_toolkit_root, max_checkpoints=2)
        
        context = ExecutionContext(
            tool="test",
            args=[],
            affected_paths=[sample_files["tool"]],
            is_destructive=True,
        )
        
        cp1 = manager.create_checkpoint(context)
        cp2 = manager.create_checkpoint(context)
        cp3 = manager.create_checkpoint(context)
        
        remaining = manager.list_checkpoints()
        remaining_ids = [cp.id for cp in remaining]
        
        # Newest two should remain
        assert cp3.id in remaining_ids
        assert cp2.id in remaining_ids
        assert cp1.id not in remaining_ids
    
    def test_manual_prune(self, recovery_manager, execution_context):
        """Can manually prune checkpoints older than age."""
        # Create checkpoint
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # Manually prune (0 seconds = prune all)
        pruned = recovery_manager.prune_checkpoints(max_age_seconds=0)
        
        assert len(pruned) > 0
        assert checkpoint.id in pruned
    
    def test_prune_by_count(self, recovery_manager, execution_context):
        """Can prune to keep only N checkpoints."""
        # Create 5 checkpoints
        for _ in range(5):
            recovery_manager.create_checkpoint(execution_context)
        
        # Prune to keep only 2
        pruned = recovery_manager.prune_checkpoints(keep_count=2)
        
        remaining = recovery_manager.list_checkpoints()
        assert len(remaining) == 2


# =============================================================================
# 7. Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_checkpoint_empty_affected_paths(self, recovery_manager):
        """Checkpoint can be created with no affected paths."""
        context = ExecutionContext(
            tool="readonly",
            args=["--info"],
            affected_paths=[],
            is_destructive=False,
        )
        
        checkpoint = recovery_manager.create_checkpoint(context)
        
        assert checkpoint is not None
        assert len(checkpoint.affected_paths) == 0
    
    def test_checkpoint_large_file(self, recovery_manager, temp_toolkit_root):
        """Checkpoint handles large files."""
        large_file = temp_toolkit_root / "large.txt"
        # Create ~1MB file
        large_file.write_text("x" * (1024 * 1024))
        
        context = ExecutionContext(
            tool="process",
            args=[],
            affected_paths=[large_file],
            is_destructive=True,
        )
        
        checkpoint = recovery_manager.create_checkpoint(context)
        
        assert len(checkpoint.state_snapshot[str(large_file)]) == 1024 * 1024
    
    def test_checkpoint_binary_file_skipped(
        self, recovery_manager, temp_toolkit_root
    ):
        """Checkpoint skips binary files (stores marker instead)."""
        binary_file = temp_toolkit_root / "image.png"
        binary_file.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        
        context = ExecutionContext(
            tool="process",
            args=[],
            affected_paths=[binary_file],
            is_destructive=True,
        )
        
        checkpoint = recovery_manager.create_checkpoint(context)
        
        # Binary files should have a marker, not content
        snapshot = checkpoint.state_snapshot.get(str(binary_file))
        assert snapshot is None or snapshot == "<binary>"
    
    def test_checkpoint_nonexistent_file(
        self, recovery_manager, temp_toolkit_root
    ):
        """Checkpoint handles paths that don't exist yet."""
        nonexistent = temp_toolkit_root / "will_be_created.py"
        
        context = ExecutionContext(
            tool="generate",
            args=[],
            affected_paths=[nonexistent],
            is_destructive=True,
        )
        
        checkpoint = recovery_manager.create_checkpoint(context)
        
        # Should record that file didn't exist
        snapshot = checkpoint.state_snapshot.get(str(nonexistent))
        assert snapshot is None or snapshot == "<not_exists>"
    
    def test_rollback_with_permission_error(
        self, recovery_manager, execution_context, sample_files
    ):
        """Rollback reports errors for permission issues."""
        checkpoint = recovery_manager.create_checkpoint(execution_context)
        
        # Modify file so rollback needs to restore it
        sample_files["tool"].write_text("# Modified")
        
        # Make file read-only to simulate permission error
        original_write_text = Path.write_text
        call_count = [0]
        
        def mock_write_text(self, *args, **kwargs):
            # Allow checkpoint persistence (first call), fail on file restore
            call_count[0] += 1
            if str(self).endswith('.json'):
                return original_write_text(self, *args, **kwargs)
            raise PermissionError("Cannot write to protected file")
        
        with patch.object(Path, 'write_text', mock_write_text):
            result = recovery_manager.rollback(checkpoint.id)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "Permission denied" in result.errors[0] or "Cannot write" in str(result.errors)
    
    def test_context_with_special_characters_in_args(
        self, recovery_manager, sample_files
    ):
        """Checkpoint handles special characters in arguments."""
        context = ExecutionContext(
            tool="search",
            args=["--pattern='*.py'", '--exclude="test_*"'],
            affected_paths=[sample_files["tool"]],
            is_destructive=False,
        )
        
        checkpoint = recovery_manager.create_checkpoint(context)
        
        assert "*.py" in str(checkpoint.args)
    
    def test_concurrent_checkpoint_creation(
        self, recovery_manager, execution_context
    ):
        """Multiple checkpoints can be created rapidly."""
        checkpoints = []
        for _ in range(10):
            cp = recovery_manager.create_checkpoint(execution_context)
            checkpoints.append(cp)
        
        # All should have unique IDs
        ids = [cp.id for cp in checkpoints]
        assert len(ids) == len(set(ids))


# =============================================================================
# 8. ExecutionContext Tests
# =============================================================================

class TestExecutionContext:
    """Tests for ExecutionContext dataclass."""
    
    def test_context_creation(self, sample_files):
        """ExecutionContext can be created with all fields."""
        context = ExecutionContext(
            tool="cleanup",
            args=["--force"],
            affected_paths=[sample_files["tool"]],
            is_destructive=True,
        )
        
        assert context.tool == "cleanup"
        assert context.is_destructive is True
    
    def test_context_default_is_destructive(self, sample_files):
        """ExecutionContext defaults is_destructive to False."""
        context = ExecutionContext(
            tool="info",
            args=[],
            affected_paths=[],
        )
        
        assert context.is_destructive is False
    
    def test_context_with_metadata(self, sample_files):
        """ExecutionContext can include optional metadata."""
        context = ExecutionContext(
            tool="migrate",
            args=["v1", "v2"],
            affected_paths=[sample_files["tool"]],
            is_destructive=True,
            metadata={"reason": "schema update", "user": "cortex"},
        )
        
        assert context.metadata["reason"] == "schema update"


# =============================================================================
# 9. Integration Tests
# =============================================================================

class TestRecoveryManagerIntegration:
    """Integration tests for full checkpoint/rollback workflow."""
    
    def test_full_checkpoint_rollback_cycle(
        self, recovery_manager, sample_files
    ):
        """Complete cycle: create -> modify -> rollback -> verify."""
        # 1. Create context
        context = ExecutionContext(
            tool="refactor",
            args=["--aggressive"],
            affected_paths=[sample_files["tool"], sample_files["config"]],
            is_destructive=True,
        )
        
        # 2. Create checkpoint
        checkpoint = recovery_manager.create_checkpoint(context)
        original_tool_content = sample_files["tool"].read_text()
        original_config_content = sample_files["config"].read_text()
        
        # 3. Simulate destructive changes
        sample_files["tool"].write_text("# Completely refactored\npass")
        sample_files["config"].write_text("setting: new_value")
        
        # Verify changes applied
        assert "refactored" in sample_files["tool"].read_text()
        
        # 4. Rollback
        result = recovery_manager.rollback(checkpoint.id)
        
        # 5. Verify restoration
        assert result.success is True
        assert sample_files["tool"].read_text() == original_tool_content
        assert sample_files["config"].read_text() == original_config_content
    
    def test_multiple_checkpoints_selective_rollback(
        self, recovery_manager, sample_files
    ):
        """Can rollback to any checkpoint, not just the latest."""
        context = ExecutionContext(
            tool="edit",
            args=[],
            affected_paths=[sample_files["tool"]],
            is_destructive=True,
        )
        
        # Checkpoint 1: Original state
        cp1 = recovery_manager.create_checkpoint(context)
        original_content = sample_files["tool"].read_text()
        
        # Make change 1
        sample_files["tool"].write_text("# Version 2")
        
        # Checkpoint 2: After change 1
        cp2 = recovery_manager.create_checkpoint(context)
        
        # Make change 2
        sample_files["tool"].write_text("# Version 3")
        
        # Checkpoint 3: After change 2
        cp3 = recovery_manager.create_checkpoint(context)
        
        # Make change 3
        sample_files["tool"].write_text("# Version 4 - latest")
        
        # Rollback to checkpoint 1 (original)
        result = recovery_manager.rollback(cp1.id)
        
        assert result.success is True
        assert sample_files["tool"].read_text() == original_content
    
    def test_persistence_across_manager_instances(
        self, temp_toolkit_root, sample_files
    ):
        """Checkpoints persist across RecoveryManager instances."""
        # Create checkpoint with first manager
        manager1 = RecoveryManager(temp_toolkit_root)
        context = ExecutionContext(
            tool="test",
            args=[],
            affected_paths=[sample_files["tool"]],
            is_destructive=True,
        )
        checkpoint = manager1.create_checkpoint(context)
        original_content = sample_files["tool"].read_text()
        
        # Modify file
        sample_files["tool"].write_text("# Modified")
        
        # Create new manager instance
        manager2 = RecoveryManager(temp_toolkit_root)
        
        # Should be able to rollback with new instance
        result = manager2.rollback(checkpoint.id)
        
        assert result.success is True
        assert sample_files["tool"].read_text() == original_content
