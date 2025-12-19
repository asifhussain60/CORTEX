"""
CORTEX 4.0 GitCheckpointIntegration Tests

Purpose: Comprehensive unit tests for GitCheckpointManager class
Coverage Target: 85%+
Test Strategy: Mock ALL git subprocess calls (no real git operations)
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19 (Week 8 Day 4)

Test Categories:
- Initialization tests
- Checkpoint creation tests (with/without changes)
- Checkpoint restoration tests
- Workspace validation tests (clean/dirty)
- Stash management tests
- Checkpoint cleanup tests
- Error handling tests
- Git command failure scenarios
"""

import json
import logging
import pytest
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, List
from unittest.mock import Mock, MagicMock, patch, call

from src.orchestrators.planning.git_checkpoint_integration import (
    GitCheckpointManager,
    CheckpointMetadata,
    CheckpointType,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Create temporary workspace root."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def git_checkpoint_manager(workspace_root, mock_logger):
    """Create GitCheckpointManager instance with mocked git checks."""
    with patch.object(GitCheckpointManager, '_is_git_repo', return_value=True):
        return GitCheckpointManager(
            workspace_root=workspace_root,
            checkpoint_prefix="test-checkpoint",
            logger_instance=mock_logger
        )


# ============================================================================
# Initialization Tests
# ============================================================================

def test_git_checkpoint_manager_init(workspace_root, mock_logger):
    """Test GitCheckpointManager initialization with git repo."""
    with patch.object(GitCheckpointManager, '_is_git_repo', return_value=True):
        manager = GitCheckpointManager(
            workspace_root=workspace_root,
            checkpoint_prefix="cortex-test",
            logger_instance=mock_logger
        )
        
        assert manager.workspace_root == Path(workspace_root)
        assert manager.checkpoint_prefix == "cortex-test"
        assert manager.logger == mock_logger
        assert manager.checkpoints == []
        assert manager.checkpoint_file == Path(workspace_root) / ".cortex" / "checkpoints.json"
        assert manager.checkpoint_file.parent.exists()


def test_git_checkpoint_manager_init_not_git_repo(workspace_root, mock_logger):
    """Test GitCheckpointManager initialization when not a git repo."""
    with patch.object(GitCheckpointManager, '_is_git_repo', return_value=False):
        manager = GitCheckpointManager(
            workspace_root=workspace_root,
            logger_instance=mock_logger
        )
        
        # Should log warning but still initialize
        mock_logger.warning.assert_called_once()
        assert "not a git repository" in mock_logger.warning.call_args[0][0]


def test_is_git_repo_success(workspace_root):
    """Test _is_git_repo returns True for valid git repo."""
    manager = GitCheckpointManager(workspace_root=workspace_root)
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        result = manager._is_git_repo()
        
        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "rev-parse", "--git-dir"]
        assert call_args[1]["cwd"] == workspace_root


def test_is_git_repo_failure(workspace_root):
    """Test _is_git_repo returns False for non-git directory."""
    manager = GitCheckpointManager(workspace_root=workspace_root)
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=128)  # Git error code
        
        result = manager._is_git_repo()
        
        assert result is False


def test_is_git_repo_exception(workspace_root):
    """Test _is_git_repo handles subprocess exception."""
    manager = GitCheckpointManager(workspace_root=workspace_root)
    
    with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("git", 5)):
        result = manager._is_git_repo()
        
        assert result is False


# ============================================================================
# Checkpoint Creation Tests
# ============================================================================

def test_create_checkpoint_success_with_changes(git_checkpoint_manager, workspace_root):
    """Test create_checkpoint with uncommitted changes."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_get_current_branch', return_value='main'), \
         patch.object(git_checkpoint_manager, '_count_changed_files', return_value=5), \
         patch.object(git_checkpoint_manager, '_create_commit', return_value='abc123def'), \
         patch.object(git_checkpoint_manager, '_persist_checkpoints'):
        
        checkpoint = git_checkpoint_manager.create_checkpoint(
            checkpoint_type=CheckpointType.PHASE,
            phase_name="DISCOVERY",
            message="After discovery phase"
        )
        
        assert checkpoint is not None
        assert checkpoint.checkpoint_type == CheckpointType.PHASE
        assert checkpoint.phase_name == "DISCOVERY"
        assert checkpoint.commit_sha == 'abc123def'
        assert checkpoint.branch_name == 'main'
        assert checkpoint.files_changed == 5
        assert checkpoint.message == "After discovery phase"
        
        assert len(git_checkpoint_manager.checkpoints) == 1


def test_create_checkpoint_success_no_changes(git_checkpoint_manager):
    """Test create_checkpoint when no changes exist."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_get_current_branch', return_value='feature-branch'), \
         patch.object(git_checkpoint_manager, '_count_changed_files', return_value=0), \
         patch.object(git_checkpoint_manager, '_get_current_commit', return_value='xyz789abc'), \
         patch.object(git_checkpoint_manager, '_persist_checkpoints'):
        
        checkpoint = git_checkpoint_manager.create_checkpoint(
            checkpoint_type=CheckpointType.INITIAL
        )
        
        assert checkpoint is not None
        assert checkpoint.checkpoint_type == CheckpointType.INITIAL
        assert checkpoint.commit_sha == 'xyz789abc'
        assert checkpoint.files_changed == 0


def test_create_checkpoint_with_stash(git_checkpoint_manager):
    """Test create_checkpoint when workspace has uncommitted changes (stashed)."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, 'stash@{0}')), \
         patch.object(git_checkpoint_manager, '_get_current_branch', return_value='main'), \
         patch.object(git_checkpoint_manager, '_count_changed_files', return_value=3), \
         patch.object(git_checkpoint_manager, '_create_commit', return_value='def456ghi'), \
         patch.object(git_checkpoint_manager, '_persist_checkpoints'):
        
        checkpoint = git_checkpoint_manager.create_checkpoint(
            checkpoint_type=CheckpointType.PHASE,
            phase_name="PLANNING"
        )
        
        assert checkpoint is not None
        assert checkpoint.stash_ref == 'stash@{0}'


def test_create_checkpoint_not_git_repo(git_checkpoint_manager, mock_logger):
    """Test create_checkpoint when not a git repo."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=False):
        checkpoint = git_checkpoint_manager.create_checkpoint(CheckpointType.PHASE)
        
        assert checkpoint is None
        mock_logger.warning.assert_called()


def test_create_checkpoint_commit_failure(git_checkpoint_manager, mock_logger):
    """Test create_checkpoint when commit creation fails."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_get_current_branch', return_value='main'), \
         patch.object(git_checkpoint_manager, '_count_changed_files', return_value=5), \
         patch.object(git_checkpoint_manager, '_create_commit', return_value=None):
        
        checkpoint = git_checkpoint_manager.create_checkpoint(CheckpointType.PHASE)
        
        assert checkpoint is None
        mock_logger.error.assert_called()


def test_create_checkpoint_exception_handling(git_checkpoint_manager, mock_logger):
    """Test create_checkpoint exception handling."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', side_effect=RuntimeError("Git error")):
        checkpoint = git_checkpoint_manager.create_checkpoint(CheckpointType.INITIAL)
        
        assert checkpoint is None
        mock_logger.error.assert_called()


# ============================================================================
# Checkpoint Restoration Tests
# ============================================================================

def test_restore_checkpoint_success(git_checkpoint_manager):
    """Test restore_checkpoint for existing checkpoint."""
    # Create checkpoint first
    checkpoint = CheckpointMetadata(
        checkpoint_id="test-checkpoint-001",
        checkpoint_type=CheckpointType.PHASE,
        phase_name="DISCOVERY",
        commit_sha="abc123",
        branch_name="main"
    )
    git_checkpoint_manager.checkpoints.append(checkpoint)
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_reset_to_commit', return_value=True):
        
        result = git_checkpoint_manager.restore_checkpoint("test-checkpoint-001")
        
        assert result is True


def test_restore_checkpoint_with_stash(git_checkpoint_manager):
    """Test restore_checkpoint that includes stash restoration."""
    checkpoint = CheckpointMetadata(
        checkpoint_id="test-checkpoint-002",
        checkpoint_type=CheckpointType.PHASE,
        phase_name="PLANNING",
        commit_sha="def456",
        branch_name="main",
        stash_ref="stash@{0}"
    )
    git_checkpoint_manager.checkpoints.append(checkpoint)
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_reset_to_commit', return_value=True), \
         patch.object(git_checkpoint_manager, '_pop_stash', return_value=True):
        
        result = git_checkpoint_manager.restore_checkpoint("test-checkpoint-002")
        
        assert result is True
        git_checkpoint_manager._pop_stash.assert_called_once_with("stash@{0}")


def test_restore_checkpoint_not_found(git_checkpoint_manager, mock_logger):
    """Test restore_checkpoint for non-existent checkpoint."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True):
        result = git_checkpoint_manager.restore_checkpoint("nonexistent-checkpoint")
    
        assert result is False
        mock_logger.error.assert_called()
        assert "not found" in mock_logger.error.call_args[0][0]


def test_restore_checkpoint_not_git_repo(git_checkpoint_manager, mock_logger):
    """Test restore_checkpoint when not a git repo."""
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=False):
        result = git_checkpoint_manager.restore_checkpoint("test-checkpoint-001")
        
        assert result is False
        mock_logger.warning.assert_called()


def test_restore_checkpoint_reset_failure(git_checkpoint_manager, mock_logger):
    """Test restore_checkpoint when git reset fails."""
    checkpoint = CheckpointMetadata(
        checkpoint_id="test-checkpoint-003",
        checkpoint_type=CheckpointType.PHASE,
        phase_name="IMPLEMENTATION",
        commit_sha="ghi789",
        branch_name="main"
    )
    git_checkpoint_manager.checkpoints.append(checkpoint)
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_reset_to_commit', return_value=False):
        
        result = git_checkpoint_manager.restore_checkpoint("test-checkpoint-003")
        
        assert result is False
        mock_logger.error.assert_called()


def test_restore_checkpoint_stash_pop_failure(git_checkpoint_manager, mock_logger):
    """Test restore_checkpoint when stash pop fails (still returns True)."""
    checkpoint = CheckpointMetadata(
        checkpoint_id="test-checkpoint-004",
        checkpoint_type=CheckpointType.PHASE,
        phase_name="VALIDATION",
        commit_sha="jkl012",
        branch_name="main",
        stash_ref="stash@{1}"
    )
    git_checkpoint_manager.checkpoints.append(checkpoint)
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', return_value=(True, None)), \
         patch.object(git_checkpoint_manager, '_reset_to_commit', return_value=True), \
         patch.object(git_checkpoint_manager, '_pop_stash', return_value=False):
        
        result = git_checkpoint_manager.restore_checkpoint("test-checkpoint-004")
        
        # Should still return True (reset succeeded, only stash failed)
        assert result is True
        mock_logger.warning.assert_called()


def test_restore_checkpoint_exception_handling(git_checkpoint_manager, mock_logger):
    """Test restore_checkpoint exception handling."""
    checkpoint = CheckpointMetadata(
        checkpoint_id="test-checkpoint-005",
        checkpoint_type=CheckpointType.PHASE,
        phase_name="COMPLETION",
        commit_sha="mno345",
        branch_name="main"
    )
    git_checkpoint_manager.checkpoints.append(checkpoint)
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_ensure_clean_workspace', side_effect=RuntimeError("Git error")):
        result = git_checkpoint_manager.restore_checkpoint("test-checkpoint-005")
        
        assert result is False
        mock_logger.error.assert_called()


# ============================================================================
# Checkpoint Cleanup Tests
# ============================================================================

def test_cleanup_checkpoints_keep_final(git_checkpoint_manager):
    """Test cleanup_checkpoints keeping final checkpoint."""
    # Add multiple checkpoints
    git_checkpoint_manager.checkpoints = [
        CheckpointMetadata("cp1", CheckpointType.INITIAL, None, commit_sha="a1"),
        CheckpointMetadata("cp2", CheckpointType.PHASE, "DISCOVERY", commit_sha="a2"),
        CheckpointMetadata("cp3", CheckpointType.PHASE, "PLANNING", commit_sha="a3"),
        CheckpointMetadata("cp4", CheckpointType.FINAL, None, commit_sha="a4"),
    ]
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_persist_checkpoints'):
        count = git_checkpoint_manager.cleanup_checkpoints(keep_final=True)
        
        assert count == 3  # 3 non-final checkpoints cleaned
        assert len(git_checkpoint_manager.checkpoints) == 1
        assert git_checkpoint_manager.checkpoints[0].checkpoint_type == CheckpointType.FINAL


def test_cleanup_checkpoints_remove_all(git_checkpoint_manager):
    """Test cleanup_checkpoints removing all checkpoints."""
    git_checkpoint_manager.checkpoints = [
        CheckpointMetadata("cp1", CheckpointType.INITIAL, None, commit_sha="b1"),
        CheckpointMetadata("cp2", CheckpointType.PHASE, "IMPLEMENTATION", commit_sha="b2"),
        CheckpointMetadata("cp3", CheckpointType.FINAL, None, commit_sha="b3"),
    ]
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=True), \
         patch.object(git_checkpoint_manager, '_persist_checkpoints'):
        count = git_checkpoint_manager.cleanup_checkpoints(keep_final=False)
        
        assert count == 3
        assert len(git_checkpoint_manager.checkpoints) == 0


def test_cleanup_checkpoints_not_git_repo(git_checkpoint_manager):
    """Test cleanup_checkpoints when not a git repo."""
    git_checkpoint_manager.checkpoints = [
        CheckpointMetadata("cp1", CheckpointType.PHASE, None, commit_sha="c1")
    ]
    
    with patch.object(git_checkpoint_manager, '_is_git_repo', return_value=False):
        count = git_checkpoint_manager.cleanup_checkpoints()
        
        assert count == 0
        assert len(git_checkpoint_manager.checkpoints) == 1  # Not modified


# ============================================================================
# Workspace Validation Tests
# ============================================================================

def test_ensure_clean_workspace_already_clean(git_checkpoint_manager, workspace_root):
    """Test _ensure_clean_workspace when workspace is clean."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="")
        
        is_clean, stash_ref = git_checkpoint_manager._ensure_clean_workspace()
        
        assert is_clean is True
        assert stash_ref is None


def test_ensure_clean_workspace_with_changes(git_checkpoint_manager, workspace_root):
    """Test _ensure_clean_workspace with uncommitted changes (stashes them)."""
    with patch('subprocess.run') as mock_run:
        # First call: git status (has changes)
        # Second call: git stash push (success)
        mock_run.side_effect = [
            Mock(returncode=0, stdout=" M file1.py\n M file2.py\n"),
            Mock(returncode=0, stdout=""),
        ]
        
        with patch.object(git_checkpoint_manager, '_get_latest_stash_ref', return_value='stash@{0}'):
            is_clean, stash_ref = git_checkpoint_manager._ensure_clean_workspace()
        
        assert is_clean is True
        assert stash_ref == 'stash@{0}'
        assert mock_run.call_count == 2


def test_ensure_clean_workspace_stash_failure(git_checkpoint_manager, workspace_root, mock_logger):
    """Test _ensure_clean_workspace when stash fails."""
    with patch('subprocess.run') as mock_run:
        # First call: git status (has changes)
        # Second call: git stash push (fails)
        mock_run.side_effect = [
            Mock(returncode=0, stdout=" M file1.py\n"),
            Mock(returncode=1, stderr="Stash error"),
        ]
        
        is_clean, stash_ref = git_checkpoint_manager._ensure_clean_workspace()
        
        assert is_clean is False
        assert stash_ref is None


def test_ensure_clean_workspace_status_failure(git_checkpoint_manager):
    """Test _ensure_clean_workspace when git status fails."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=128, stderr="Not a git repo")
        
        is_clean, stash_ref = git_checkpoint_manager._ensure_clean_workspace()
        
        assert is_clean is False
        assert stash_ref is None


def test_ensure_clean_workspace_exception(git_checkpoint_manager, mock_logger):
    """Test _ensure_clean_workspace exception handling."""
    with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("git", 5)):
        is_clean, stash_ref = git_checkpoint_manager._ensure_clean_workspace()
        
        assert is_clean is False
        assert stash_ref is None


# ============================================================================
# Git Helper Method Tests
# ============================================================================

def test_create_commit_success(git_checkpoint_manager, workspace_root):
    """Test _create_commit creates commit successfully."""
    with patch('subprocess.run') as mock_run:
        # First call: git add -A
        # Second call: git commit -m
        mock_run.side_effect = [
            Mock(returncode=0),
            Mock(returncode=0),
        ]
        
        with patch.object(git_checkpoint_manager, '_get_current_commit', return_value='abc123'):
            commit_sha = git_checkpoint_manager._create_commit("Test commit")
        
        assert commit_sha == 'abc123'
        assert mock_run.call_count == 2


def test_create_commit_failure(git_checkpoint_manager, mock_logger):
    """Test _create_commit when commit fails."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            Mock(returncode=0),  # git add succeeds
            Mock(returncode=1),  # git commit fails
        ]
        
        commit_sha = git_checkpoint_manager._create_commit("Test commit")
        
        assert commit_sha is None


def test_create_commit_exception(git_checkpoint_manager, mock_logger):
    """Test _create_commit exception handling."""
    with patch('subprocess.run', side_effect=RuntimeError("Git error")):
        commit_sha = git_checkpoint_manager._create_commit("Test commit")
        
        assert commit_sha is None


def test_get_current_commit_success(git_checkpoint_manager):
    """Test _get_current_commit returns commit SHA."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="abc123def456\n")
        
        commit_sha = git_checkpoint_manager._get_current_commit()
        
        assert commit_sha == "abc123def456"


def test_get_current_commit_failure(git_checkpoint_manager):
    """Test _get_current_commit when git fails."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=128)
        
        commit_sha = git_checkpoint_manager._get_current_commit()
        
        assert commit_sha is None


def test_get_current_branch_success(git_checkpoint_manager):
    """Test _get_current_branch returns branch name."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="feature-branch\n")
        
        branch_name = git_checkpoint_manager._get_current_branch()
        
        assert branch_name == "feature-branch"


def test_get_current_branch_failure(git_checkpoint_manager):
    """Test _get_current_branch when git fails."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=128)
        
        branch_name = git_checkpoint_manager._get_current_branch()
        
        assert branch_name is None


def test_count_changed_files_success(git_checkpoint_manager):
    """Test _count_changed_files counts changed files."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout=" M file1.py\n M file2.py\n A file3.py\n")
        
        count = git_checkpoint_manager._count_changed_files()
        
        assert count == 3


def test_count_changed_files_no_changes(git_checkpoint_manager):
    """Test _count_changed_files when no changes."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="")
        
        count = git_checkpoint_manager._count_changed_files()
        
        assert count == 0


def test_reset_to_commit_success(git_checkpoint_manager):
    """Test _reset_to_commit resets successfully."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        result = git_checkpoint_manager._reset_to_commit("abc123")
        
        assert result is True


def test_reset_to_commit_failure(git_checkpoint_manager, mock_logger):
    """Test _reset_to_commit when reset fails."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=1)
        
        result = git_checkpoint_manager._reset_to_commit("abc123")
        
        assert result is False


def test_get_latest_stash_ref_success(git_checkpoint_manager):
    """Test _get_latest_stash_ref returns stash reference."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="stash@{0}: WIP on main: abc123 Message\n")
        
        stash_ref = git_checkpoint_manager._get_latest_stash_ref()
        
        assert stash_ref == "stash@{0}"


def test_get_latest_stash_ref_no_stash(git_checkpoint_manager):
    """Test _get_latest_stash_ref when no stash exists."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="")
        
        stash_ref = git_checkpoint_manager._get_latest_stash_ref()
        
        assert stash_ref is None


def test_pop_stash_success(git_checkpoint_manager):
    """Test _pop_stash pops stash successfully."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        result = git_checkpoint_manager._pop_stash("stash@{0}")
        
        assert result is True


def test_pop_stash_failure(git_checkpoint_manager, mock_logger):
    """Test _pop_stash when pop fails."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=1)
        
        result = git_checkpoint_manager._pop_stash("stash@{0}")
        
        assert result is False


# ============================================================================
# Checkpoint Query Tests
# ============================================================================

def test_get_checkpoint_exists(git_checkpoint_manager):
    """Test get_checkpoint for existing checkpoint."""
    checkpoint = CheckpointMetadata("cp1", CheckpointType.PHASE, "DISCOVERY", commit_sha="abc")
    git_checkpoint_manager.checkpoints.append(checkpoint)
    
    result = git_checkpoint_manager.get_checkpoint("cp1")
    
    assert result is not None
    assert result.checkpoint_id == "cp1"


def test_get_checkpoint_not_found(git_checkpoint_manager):
    """Test get_checkpoint for non-existent checkpoint."""
    result = git_checkpoint_manager.get_checkpoint("nonexistent")
    
    assert result is None


def test_get_all_checkpoints(git_checkpoint_manager):
    """Test get_all_checkpoints returns all checkpoints."""
    git_checkpoint_manager.checkpoints = [
        CheckpointMetadata("cp1", CheckpointType.INITIAL, None, commit_sha="a1"),
        CheckpointMetadata("cp2", CheckpointType.PHASE, "DISCOVERY", commit_sha="a2"),
        CheckpointMetadata("cp3", CheckpointType.FINAL, None, commit_sha="a3"),
    ]
    
    result = git_checkpoint_manager.get_all_checkpoints()
    
    assert len(result) == 3
    assert result[0].checkpoint_id == "cp1"
    assert result[1].checkpoint_id == "cp2"
    assert result[2].checkpoint_id == "cp3"


# ============================================================================
# State Persistence Tests
# ============================================================================

def test_persist_checkpoints_json_format(git_checkpoint_manager, workspace_root):
    """Test _persist_checkpoints creates valid JSON."""
    git_checkpoint_manager.checkpoints = [
        CheckpointMetadata(
            checkpoint_id="cp1",
            checkpoint_type=CheckpointType.PHASE,
            phase_name="DISCOVERY",
            commit_sha="abc123",
            branch_name="main",
            message="Test checkpoint",
            files_changed=5
        )
    ]
    
    git_checkpoint_manager._persist_checkpoints()
    
    assert git_checkpoint_manager.checkpoint_file.exists()
    data = json.loads(git_checkpoint_manager.checkpoint_file.read_text())
    
    assert "checkpoints" in data
    assert len(data["checkpoints"]) == 1
    assert data["checkpoints"][0]["checkpoint_id"] == "cp1"
    assert data["checkpoints"][0]["checkpoint_type"] == "phase"


def test_persist_checkpoints_exception_handling(git_checkpoint_manager, mock_logger):
    """Test _persist_checkpoints exception handling."""
    git_checkpoint_manager.checkpoints = [
        CheckpointMetadata("cp1", CheckpointType.PHASE, None, commit_sha="abc")
    ]
    
    # Make write_text raise an exception
    with patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")):
        git_checkpoint_manager._persist_checkpoints()
        
        mock_logger.error.assert_called()


def test_restore_checkpoint_history_success(git_checkpoint_manager, workspace_root):
    """Test restore_checkpoint_history from valid JSON."""
    # Create checkpoint file
    data = {
        "checkpoints": [
            {
                "checkpoint_id": "cp1",
                "checkpoint_type": "phase",
                "phase_name": "DISCOVERY",
                "timestamp": "2025-12-19T10:00:00",
                "commit_sha": "abc123",
                "branch_name": "main",
                "message": "Test checkpoint",
                "files_changed": 5,
                "stash_ref": None
            }
        ]
    }
    git_checkpoint_manager.checkpoint_file.write_text(json.dumps(data))
    
    count = git_checkpoint_manager.restore_checkpoint_history()
    
    assert count == 1
    assert len(git_checkpoint_manager.checkpoints) == 1
    assert git_checkpoint_manager.checkpoints[0].checkpoint_id == "cp1"


def test_restore_checkpoint_history_no_file(git_checkpoint_manager):
    """Test restore_checkpoint_history when no file exists."""
    count = git_checkpoint_manager.restore_checkpoint_history()
    
    assert count == 0
    assert len(git_checkpoint_manager.checkpoints) == 0


def test_restore_checkpoint_history_corrupted_json(git_checkpoint_manager, mock_logger):
    """Test restore_checkpoint_history with corrupted JSON."""
    git_checkpoint_manager.checkpoint_file.write_text("{ invalid json }")
    
    count = git_checkpoint_manager.restore_checkpoint_history()
    
    assert count == 0
    mock_logger.error.assert_called()


# ============================================================================
# Utility Method Tests
# ============================================================================

def test_generate_checkpoint_message_with_phase(git_checkpoint_manager):
    """Test _generate_checkpoint_message with phase name."""
    message = git_checkpoint_manager._generate_checkpoint_message(
        CheckpointType.PHASE,
        "IMPLEMENTATION"
    )
    
    assert "After phase IMPLEMENTATION" in message
    assert git_checkpoint_manager.checkpoint_prefix in message


def test_generate_checkpoint_message_without_phase(git_checkpoint_manager):
    """Test _generate_checkpoint_message without phase name."""
    message = git_checkpoint_manager._generate_checkpoint_message(
        CheckpointType.INITIAL,
        None
    )
    
    assert "initial checkpoint" in message
    assert git_checkpoint_manager.checkpoint_prefix in message


# ============================================================================
# Domain Model Tests
# ============================================================================

def test_checkpoint_metadata_creation():
    """Test CheckpointMetadata dataclass creation."""
    checkpoint = CheckpointMetadata(
        checkpoint_id="test-cp",
        checkpoint_type=CheckpointType.PHASE,
        phase_name="VALIDATION",
        commit_sha="abc123",
        branch_name="feature",
        message="Test message",
        files_changed=10,
        stash_ref="stash@{0}"
    )
    
    assert checkpoint.checkpoint_id == "test-cp"
    assert checkpoint.checkpoint_type == CheckpointType.PHASE
    assert checkpoint.phase_name == "VALIDATION"
    assert checkpoint.commit_sha == "abc123"
    assert checkpoint.timestamp is not None


def test_checkpoint_type_enum():
    """Test CheckpointType enum values."""
    assert CheckpointType.INITIAL.value == "initial"
    assert CheckpointType.PHASE.value == "phase"
    assert CheckpointType.FINAL.value == "final"
    assert CheckpointType.MANUAL.value == "manual"
