"""
Git Checkpoint Module Tests

Tests for git checkpoint creation, validation, and rollback functionality.
Implements tests for GIT_CHECKPOINT_ENFORCEMENT Tier 0 instinct.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import subprocess
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.operations.modules.git_checkpoint_module import (
    GitCheckpointModule,
    CheckpointType,
    CheckpointViolation
)


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_path, check=True, capture_output=True)
    
    # Create initial commit
    test_file = temp_path / "README.md"
    test_file.write_text("# Test Repository")
    subprocess.run(['git', 'add', '.'], cwd=temp_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_path, check=True, capture_output=True)
    
    # Store original directory
    original_dir = Path.cwd()
    
    # Change to temp directory for tests
    import os
    os.chdir(temp_path)
    
    yield temp_path
    
    # Cleanup
    os.chdir(original_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestGitCheckpointModule:
    """Test suite for GitCheckpointModule."""
    
    def test_module_initialization(self, temp_git_repo):
        """Test module initializes correctly in git repo."""
        module = GitCheckpointModule()
        
        metadata = module.get_metadata()
        assert metadata.module_id == "git_checkpoint"
        assert metadata.version == "1.0.0"
        assert module.repo_path is not None
        assert module.repo_path.exists()
    
    def test_module_initialization_no_git_repo(self, tmp_path, monkeypatch):
        """Test module handles non-git directory gracefully."""
        monkeypatch.chdir(tmp_path)
        module = GitCheckpointModule()
        
        assert module.repo_path is None
    
    def test_create_commit_checkpoint_with_changes(self, temp_git_repo):
        """Test creating commit checkpoint with uncommitted changes."""
        # Create some changes
        test_file = temp_git_repo / "feature.py"
        test_file.write_text("def new_feature(): pass")
        
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'before authentication feature',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        assert result.success
        assert 'checkpoint' in result.message.lower()
        assert result.data['checkpoint_type'] == 'commit'
        assert 'commit_hash' in result.data
        assert len(result.data['commit_hash']) == 40  # Full SHA-1 hash
        assert result.data['commit_message'] == 'checkpoint: before authentication feature'
    
    def test_create_empty_checkpoint_no_changes(self, temp_git_repo):
        """Test creating empty checkpoint when no changes exist."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'before refactor',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        assert result.success
        assert 'empty checkpoint' in result.message.lower() or 'checkpoint' in result.message.lower()
        assert result.data['checkpoint_type'] == 'commit'
        assert 'commit_hash' in result.data
    
    def test_create_tag_checkpoint(self, temp_git_repo):
        """Test creating tag checkpoint."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'before major refactor',
            'checkpoint_type': CheckpointType.TAG
        })
        
        assert result.success
        assert 'tag' in result.message.lower()
        assert result.data['checkpoint_type'] == 'tag'
        assert 'tag_name' in result.data
        assert result.data['tag_name'].startswith('checkpoint-')
        assert 'timestamp' in result.data
    
    def test_create_stash_checkpoint_with_changes(self, temp_git_repo):
        """Test creating stash checkpoint with uncommitted changes."""
        # Create some changes
        test_file = temp_git_repo / "wip.py"
        test_file.write_text("# Work in progress")
        
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'experimental changes',
            'checkpoint_type': CheckpointType.STASH
        })
        
        assert result.success
        assert 'stash' in result.message.lower()
        assert result.data['checkpoint_type'] == 'stash'
        assert 'stash_message' in result.data
    
    def test_create_stash_checkpoint_no_changes_fails(self, temp_git_repo):
        """Test stash checkpoint fails when no changes exist."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'nothing to stash',
            'checkpoint_type': CheckpointType.STASH
        })
        
        assert not result.success
        assert 'no changes' in result.message.lower()
    
    def test_validate_checkpoint_clean_working_tree(self, temp_git_repo):
        """Test validation passes with clean working tree."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'validate',
            'required_for': 'authentication feature'
        })
        
        assert result.success
        assert 'validation passed' in result.message.lower()
        assert result.data['valid'] is True
        assert result.data['clean_working_tree'] is True
    
    def test_validate_checkpoint_fails_with_uncommitted_changes(self, temp_git_repo):
        """Test validation fails when uncommitted changes exist."""
        # Create uncommitted changes
        test_file = temp_git_repo / "uncommitted.py"
        test_file.write_text("# Uncommitted work")
        
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'validate',
            'required_for': 'payment integration'
        })
        
        assert not result.success
        assert 'uncommitted changes' in result.message.lower()
        assert 'violation' in result.data
        assert result.data['violation'] is True
    
    def test_list_checkpoints_commit(self, temp_git_repo):
        """Test listing commit checkpoints."""
        # Create a checkpoint commit
        module = GitCheckpointModule()
        module.execute({
            'operation': 'create',
            'message': 'first checkpoint',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        # List checkpoints
        result = module.execute({
            'operation': 'list',
            'limit': 10
        })
        
        assert result.success
        assert 'commit_checkpoints' in result.data
        assert len(result.data['commit_checkpoints']) >= 1
        assert result.data['commit_checkpoints'][0]['type'] == 'commit'
        assert 'checkpoint' in result.data['commit_checkpoints'][0]['message'].lower()
    
    def test_list_checkpoints_tag(self, temp_git_repo):
        """Test listing tag checkpoints."""
        # Create a tag checkpoint
        module = GitCheckpointModule()
        module.execute({
            'operation': 'create',
            'message': 'tag checkpoint',
            'checkpoint_type': CheckpointType.TAG
        })
        
        # List checkpoints
        result = module.execute({
            'operation': 'list'
        })
        
        assert result.success
        assert 'tag_checkpoints' in result.data
        assert len(result.data['tag_checkpoints']) >= 1
        assert result.data['tag_checkpoints'][0]['type'] == 'tag'
        assert 'checkpoint-' in result.data['tag_checkpoints'][0]['name']
    
    def test_rollback_to_checkpoint(self, temp_git_repo):
        """Test rolling back to a checkpoint."""
        # Create initial state
        test_file = temp_git_repo / "version1.py"
        test_file.write_text("version = 1")
        
        module = GitCheckpointModule()
        checkpoint_result = module.execute({
            'operation': 'create',
            'message': 'version 1',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        checkpoint_hash = checkpoint_result.data['commit_hash']
        
        # Make more changes
        test_file.write_text("version = 2")
        module.execute({
            'operation': 'create',
            'message': 'version 2',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        # Rollback to checkpoint
        rollback_result = module.execute({
            'operation': 'rollback',
            'checkpoint_id': checkpoint_hash
        })
        
        assert rollback_result.success
        assert 'rolled back' in rollback_result.message.lower()
        assert rollback_result.data['checkpoint_id'] == checkpoint_hash
        assert 'safety_tag' in rollback_result.data
        assert 'recovery_command' in rollback_result.data
        
        # Verify rollback worked
        content = test_file.read_text()
        assert content == "version = 1"
    
    def test_rollback_nonexistent_checkpoint_fails(self, temp_git_repo):
        """Test rollback fails for nonexistent checkpoint."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'rollback',
            'checkpoint_id': 'nonexistent123'
        })
        
        assert not result.success
        assert 'failed' in result.message.lower()
    
    def test_rollback_without_checkpoint_id_fails(self, temp_git_repo):
        """Test rollback fails when checkpoint_id is missing."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'rollback'
        })
        
        assert not result.success
        assert 'required' in result.message.lower()
    
    def test_git_status_check(self, temp_git_repo):
        """Test internal git status checking."""
        # Create changes
        test_file = temp_git_repo / "new_file.py"
        test_file.write_text("# New file")
        
        module = GitCheckpointModule()
        status = module._check_git_status()
        
        assert status['has_changes'] is True
        assert len(status['untracked']) >= 1
        assert 'new_file.py' in status['untracked'][0]
    
    def test_invalid_operation(self, temp_git_repo):
        """Test invalid operation returns error."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'invalid_op'
        })
        
        assert not result.success
        assert 'unknown operation' in result.message.lower()
        assert 'valid_operations' in result.data
    
    def test_invalid_checkpoint_type(self, temp_git_repo):
        """Test invalid checkpoint type returns error."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'test',
            'checkpoint_type': 'invalid_type'
        })
        
        assert not result.success
        assert 'unknown checkpoint type' in result.message.lower()
        assert 'valid_types' in result.data
    
    def test_checkpoint_message_formatting(self, temp_git_repo):
        """Test checkpoint messages are properly formatted."""
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'create',
            'message': 'user authentication implementation',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        assert result.success
        assert result.data['commit_message'] == 'checkpoint: user authentication implementation'
    
    def test_not_in_git_repo_error(self, tmp_path, monkeypatch):
        """Test error when not in a git repository."""
        monkeypatch.chdir(tmp_path)
        module = GitCheckpointModule()
        
        result = module.execute({
            'operation': 'create',
            'message': 'test'
        })
        
        assert not result.success
        assert 'not in a git repository' in result.message.lower()


class TestCheckpointEnforcement:
    """Test suite for checkpoint enforcement in development workflows."""
    
    def test_checkpoint_required_before_feature_implementation(self, temp_git_repo):
        """Test that checkpoint is required before implementing features."""
        # Simulate uncommitted changes
        test_file = temp_git_repo / "old_work.py"
        test_file.write_text("# Old work")
        
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'validate',
            'required_for': 'new feature implementation'
        })
        
        assert not result.success
        assert 'uncommitted changes' in result.message.lower()
    
    def test_checkpoint_enforcement_with_alternatives(self, temp_git_repo):
        """Test that alternatives are provided when checkpoint is missing."""
        test_file = temp_git_repo / "work.py"
        test_file.write_text("# Work")
        
        module = GitCheckpointModule()
        result = module.execute({
            'operation': 'validate',
            'required_for': 'refactoring'
        })
        
        assert not result.success
        assert 'alternatives' in result.data
        assert len(result.data['alternatives']) > 0
    
    def test_checkpoint_workflow_create_then_validate(self, temp_git_repo):
        """Test complete workflow: create checkpoint then validate."""
        # Create changes
        test_file = temp_git_repo / "feature.py"
        test_file.write_text("def feature(): pass")
        
        module = GitCheckpointModule()
        
        # Create checkpoint
        create_result = module.execute({
            'operation': 'create',
            'message': 'before new feature',
            'checkpoint_type': CheckpointType.COMMIT
        })
        assert create_result.success
        
        # Now validation should pass
        validate_result = module.execute({
            'operation': 'validate',
            'required_for': 'new feature'
        })
        assert validate_result.success


class TestCheckpointIntegration:
    """Integration tests for checkpoint system."""
    
    def test_multiple_checkpoints_sequence(self, temp_git_repo):
        """Test creating multiple checkpoints in sequence."""
        module = GitCheckpointModule()
        
        # Checkpoint 1
        file1 = temp_git_repo / "step1.py"
        file1.write_text("step = 1")
        result1 = module.execute({
            'operation': 'create',
            'message': 'step 1 complete',
            'checkpoint_type': CheckpointType.COMMIT
        })
        assert result1.success
        
        # Checkpoint 2
        file2 = temp_git_repo / "step2.py"
        file2.write_text("step = 2")
        result2 = module.execute({
            'operation': 'create',
            'message': 'step 2 complete',
            'checkpoint_type': CheckpointType.COMMIT
        })
        assert result2.success
        
        # List should show both
        list_result = module.execute({'operation': 'list', 'limit': 10})
        assert list_result.success
        assert list_result.data['total'] >= 2
    
    def test_checkpoint_safety_tag_on_rollback(self, temp_git_repo):
        """Test that safety tag is created before rollback."""
        module = GitCheckpointModule()
        
        # Create checkpoint
        test_file = temp_git_repo / "work.py"
        test_file.write_text("work = 1")
        checkpoint_result = module.execute({
            'operation': 'create',
            'message': 'safe point',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        checkpoint_hash = checkpoint_result.data['commit_hash']
        
        # Make more changes
        test_file.write_text("work = 2")
        module.execute({
            'operation': 'create',
            'message': 'more work',
            'checkpoint_type': CheckpointType.COMMIT
        })
        
        # Rollback
        rollback_result = module.execute({
            'operation': 'rollback',
            'checkpoint_id': checkpoint_hash
        })
        
        assert rollback_result.success
        assert 'before-rollback-' in rollback_result.data['safety_tag']
        
        # Verify safety tag exists
        tag_check = subprocess.run(
            ['git', 'tag', '-l', rollback_result.data['safety_tag']],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )
        assert rollback_result.data['safety_tag'] in tag_check.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
