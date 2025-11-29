"""
Unit tests for GitCheckpointOrchestrator

Tests git checkpoint creation, phase commits, rollback, and SKULL Rule #8 validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
import subprocess
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@cortex.ai"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "CORTEX Test"], cwd=repo_path, check=True, capture_output=True)
    
    # Create initial commit
    (repo_path / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)
    
    yield repo_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def orchestrator(temp_git_repo):
    """Create GitCheckpointOrchestrator instance."""
    return GitCheckpointOrchestrator(temp_git_repo)


class TestGitCheckpointOrchestrator:
    """Test suite for GitCheckpointOrchestrator."""
    
    def test_init_creates_checkpoints_file(self, orchestrator):
        """Test that initialization creates checkpoints tracking file."""
        assert orchestrator.checkpoints_file.exists()
        data = json.loads(orchestrator.checkpoints_file.read_text())
        assert "checkpoints" in data
        assert isinstance(data["checkpoints"], list)
    
    def test_get_current_branch(self, orchestrator):
        """Test getting current branch name."""
        branch = orchestrator._get_current_branch()
        assert branch is not None
        assert isinstance(branch, str)
        # Default branch is usually 'master' or 'main'
        assert branch in ["master", "main"]
    
    def test_get_current_commit_sha(self, orchestrator):
        """Test getting current commit SHA."""
        sha = orchestrator._get_current_commit_sha()
        assert sha is not None
        assert isinstance(sha, str)
        assert len(sha) == 40  # Git SHA is 40 characters
    
    def test_has_uncommitted_changes_false(self, orchestrator):
        """Test detecting no uncommitted changes."""
        assert not orchestrator._has_uncommitted_changes()
    
    def test_has_uncommitted_changes_true(self, orchestrator, temp_git_repo):
        """Test detecting uncommitted changes."""
        # Create new file
        (temp_git_repo / "test.txt").write_text("test")
        assert orchestrator._has_uncommitted_changes()
    
    def test_create_checkpoint_clean_state(self, orchestrator):
        """Test creating checkpoint with clean working tree."""
        session_id = "test-session-001"
        phase = "RED"
        
        checkpoint_id = orchestrator.create_checkpoint(session_id, phase, "Test checkpoint")
        
        assert checkpoint_id is not None
        assert len(checkpoint_id) == 40  # Git SHA
        
        # Verify checkpoint saved
        checkpoints = orchestrator.list_checkpoints(session_id)
        assert len(checkpoints) == 1
        assert checkpoints[0]["session_id"] == session_id
        assert checkpoints[0]["phase"] == phase
        assert checkpoints[0]["checkpoint_id"] == checkpoint_id
    
    def test_create_checkpoint_with_uncommitted_changes(self, orchestrator, temp_git_repo):
        """Test creating checkpoint stashes uncommitted changes."""
        # Create uncommitted change
        (temp_git_repo / "test.txt").write_text("test")
        
        session_id = "test-session-002"
        checkpoint_id = orchestrator.create_checkpoint(session_id, "GREEN")
        
        assert checkpoint_id is not None
        # Changes should be stashed
        assert not orchestrator._has_uncommitted_changes()
    
    def test_commit_phase_completion_no_changes(self, orchestrator):
        """Test committing phase with no changes."""
        session_id = "test-session-003"
        
        commit_sha = orchestrator.commit_phase_completion(session_id, "REFACTOR")
        
        # Should return current SHA since nothing to commit
        assert commit_sha is not None
        assert len(commit_sha) == 40
    
    def test_commit_phase_completion_with_changes(self, orchestrator, temp_git_repo):
        """Test committing phase with changes."""
        # Create changes
        (temp_git_repo / "test.txt").write_text("test content")
        
        session_id = "test-session-004"
        phase = "GREEN"
        metrics = {"duration_seconds": 120, "lines_added": 10}
        
        commit_sha = orchestrator.commit_phase_completion(session_id, phase, metrics)
        
        assert commit_sha is not None
        assert len(commit_sha) == 40
        
        # Verify commit message
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )
        commit_msg = result.stdout.strip()
        
        assert "CORTEX TDD: GREEN phase complete" in commit_msg
        assert f"Session: {session_id}" in commit_msg
        assert f"Phase: {phase}" in commit_msg
        assert "duration_seconds: 120" in commit_msg
        assert "lines_added: 10" in commit_msg
    
    def test_list_checkpoints_empty(self, orchestrator):
        """Test listing checkpoints when none exist."""
        checkpoints = orchestrator.list_checkpoints()
        assert checkpoints == []
    
    def test_list_checkpoints_filtered_by_session(self, orchestrator):
        """Test listing checkpoints filtered by session ID."""
        # Create checkpoints for different sessions
        orchestrator.create_checkpoint("session-1", "RED")
        orchestrator.create_checkpoint("session-2", "GREEN")
        orchestrator.create_checkpoint("session-1", "REFACTOR")
        
        # Filter by session-1
        session1_checkpoints = orchestrator.list_checkpoints("session-1")
        assert len(session1_checkpoints) == 2
        assert all(cp["session_id"] == "session-1" for cp in session1_checkpoints)
        
        # Filter by session-2
        session2_checkpoints = orchestrator.list_checkpoints("session-2")
        assert len(session2_checkpoints) == 1
        assert session2_checkpoints[0]["session_id"] == "session-2"
    
    def test_rollback_to_checkpoint(self, orchestrator, temp_git_repo):
        """Test rolling back to a checkpoint."""
        # Create initial checkpoint
        session_id = "test-session-005"
        checkpoint_id = orchestrator.create_checkpoint(session_id, "RED")
        
        # Make changes and commit
        (temp_git_repo / "test.txt").write_text("new content")
        orchestrator.commit_phase_completion(session_id, "GREEN")
        
        # Verify file exists
        assert (temp_git_repo / "test.txt").exists()
        
        # Rollback to checkpoint
        success = orchestrator.rollback_to_checkpoint(session_id, checkpoint_id)
        
        assert success
        # File should not exist after rollback
        assert not (temp_git_repo / "test.txt").exists()
    
    def test_rollback_to_last_checkpoint(self, orchestrator, temp_git_repo):
        """Test rolling back to last checkpoint when not specified."""
        session_id = "test-session-006"
        
        # Create first checkpoint
        checkpoint1 = orchestrator.create_checkpoint(session_id, "RED")
        (temp_git_repo / "file1.txt").write_text("file1")
        orchestrator.commit_phase_completion(session_id, "GREEN")
        
        # Create second checkpoint
        checkpoint2 = orchestrator.create_checkpoint(session_id, "GREEN")
        (temp_git_repo / "file2.txt").write_text("file2")
        orchestrator.commit_phase_completion(session_id, "REFACTOR")
        
        # Rollback without specifying checkpoint (should use last one)
        success = orchestrator.rollback_to_checkpoint(session_id)
        
        assert success
        # file1 should exist (from first checkpoint), file2 should not
        assert (temp_git_repo / "file1.txt").exists()
        assert not (temp_git_repo / "file2.txt").exists()
    
    def test_rollback_nonexistent_checkpoint(self, orchestrator):
        """Test rollback fails for nonexistent checkpoint."""
        success = orchestrator.rollback_to_checkpoint("nonexistent-session")
        assert not success
    
    def test_validate_skull_rule_8_pass(self, orchestrator):
        """Test SKULL Rule #8 validation passes when checkpoint exists."""
        session_id = "test-session-007"
        orchestrator.create_checkpoint(session_id, "RED")
        
        is_valid = orchestrator.validate_skull_rule_8(session_id)
        assert is_valid
    
    def test_validate_skull_rule_8_fail(self, orchestrator):
        """Test SKULL Rule #8 validation fails when no checkpoint."""
        is_valid = orchestrator.validate_skull_rule_8("nonexistent-session")
        assert not is_valid
    
    def test_checkpoint_metadata_complete(self, orchestrator):
        """Test checkpoint contains all required metadata."""
        session_id = "test-session-008"
        phase = "RED"
        message = "Custom checkpoint message"
        
        checkpoint_id = orchestrator.create_checkpoint(session_id, phase, message)
        checkpoints = orchestrator.list_checkpoints(session_id)
        
        assert len(checkpoints) == 1
        checkpoint = checkpoints[0]
        
        # Verify all metadata fields
        assert checkpoint["checkpoint_id"] == checkpoint_id
        assert checkpoint["session_id"] == session_id
        assert checkpoint["phase"] == phase
        assert checkpoint["message"] == message
        assert "branch" in checkpoint
        assert "timestamp" in checkpoint
        
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(checkpoint["timestamp"])
    
    def test_multiple_sessions_isolated(self, orchestrator):
        """Test that checkpoints for different sessions are isolated."""
        # Create checkpoints for multiple sessions
        session1_cp1 = orchestrator.create_checkpoint("session-1", "RED")
        session2_cp1 = orchestrator.create_checkpoint("session-2", "RED")
        session1_cp2 = orchestrator.create_checkpoint("session-1", "GREEN")
        
        # Verify isolation
        session1_checkpoints = orchestrator.list_checkpoints("session-1")
        session2_checkpoints = orchestrator.list_checkpoints("session-2")
        
        assert len(session1_checkpoints) == 2
        assert len(session2_checkpoints) == 1
        
        # Verify checkpoint IDs are different
        assert session1_cp1 == session1_cp2  # Same commit initially
        assert session1_cp1 == session2_cp1  # All pointing to same initial commit


class TestGitCheckpointOrchestratorErrorHandling:
    """Test error handling in GitCheckpointOrchestrator."""
    
    def test_create_checkpoint_git_failure(self, orchestrator):
        """Test handling of git command failure."""
        with patch.object(orchestrator, '_run_git_command', return_value=(False, "Git error")):
            checkpoint_id = orchestrator.create_checkpoint("session-1", "RED")
            assert checkpoint_id is None
    
    def test_commit_phase_git_failure(self, orchestrator):
        """Test handling of commit failure."""
        with patch.object(orchestrator, '_has_uncommitted_changes', return_value=True), \
             patch.object(orchestrator, '_run_git_command', return_value=(False, "Commit failed")):
            commit_sha = orchestrator.commit_phase_completion("session-1", "GREEN")
            assert commit_sha is None
    
    def test_rollback_git_failure(self, orchestrator):
        """Test handling of rollback failure."""
        # Create checkpoint first
        orchestrator.create_checkpoint("session-1", "RED")
        
        with patch.object(orchestrator, '_run_git_command', return_value=(False, "Reset failed")):
            success = orchestrator.rollback_to_checkpoint("session-1")
            assert not success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
