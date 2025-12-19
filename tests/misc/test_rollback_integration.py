"""
Integration tests for complete rollback workflow.

Tests the end-to-end rollback process combining:
- Command parsing (INCREMENT 12)
- Orchestrator foundation (INCREMENT 11)
- Safety checks (INCREMENT 13)

Tests workflow: command parse → safety check → user confirm → git restore

Version: 1.0
Status: RED phase (tests should fail initially)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator with temporary git repository."""
    # Create temporary CORTEX and project directories
    cortex_dir = tmp_path / "CORTEX"
    cortex_dir.mkdir()
    project_root = tmp_path
    
    return RollbackOrchestrator(
        cortex_dir=cortex_dir,
        project_root=project_root
    )


def test_complete_rollback_workflow_with_clean_repo(orchestrator):
    """Test complete rollback workflow when repository is clean."""
    checkpoint_id = "pre-work-20251128-100000"
    
    # Mock git operations
    with patch.object(orchestrator, '_get_git_status') as mock_status, \
         patch.object(orchestrator, 'validate_checkpoint') as mock_validate, \
         patch.object(orchestrator, '_get_git_diff') as mock_diff, \
         patch('builtins.input', return_value='yes') as mock_input, \
         patch.object(orchestrator, '_execute_git_reset') as mock_reset:
        
        # Setup: Clean repo, valid checkpoint
        mock_status.return_value = {
            'clean': True,
            'uncommitted_changes': [],
            'merge_in_progress': False
        }
        mock_validate.return_value = True
        mock_diff.return_value = "diff --git a/file.py b/file.py\n-old line\n+new line"
        mock_reset.return_value = {'success': True}
        
        # Execute complete workflow
        result = orchestrator.execute_rollback(checkpoint_id)
        
        # Verify workflow steps executed
        assert result['executed'] is True
        assert result['message'] == f'Rollback to {checkpoint_id} completed successfully'
        mock_status.assert_called_once()
        mock_validate.assert_called_once_with(checkpoint_id)
        mock_input.assert_called_once()
        mock_reset.assert_called_once_with(checkpoint_id)


def test_complete_rollback_workflow_blocks_on_uncommitted_changes(orchestrator):
    """Test workflow blocks rollback when uncommitted changes detected."""
    checkpoint_id = "pre-work-20251128-100000"
    
    with patch.object(orchestrator, '_get_git_status') as mock_status, \
         patch.object(orchestrator, 'validate_checkpoint') as mock_validate:
        
        # Setup: Uncommitted changes present
        mock_status.return_value = {
            'clean': False,
            'uncommitted_changes': [' M src/file.py', 'A  tests/new_test.py'],
            'merge_in_progress': False
        }
        mock_validate.return_value = True
        
        # Execute workflow
        result = orchestrator.execute_rollback(checkpoint_id)
        
        # Verify rollback blocked
        assert result['executed'] is False
        assert 'uncommitted changes' in result['message'].lower()


def test_complete_rollback_workflow_blocks_on_merge_conflict(orchestrator):
    """Test workflow blocks rollback during merge conflict."""
    checkpoint_id = "pre-work-20251128-100000"
    
    with patch.object(orchestrator, '_get_git_status') as mock_status, \
         patch.object(orchestrator, 'validate_checkpoint') as mock_validate:
        
        # Setup: Merge in progress
        mock_status.return_value = {
            'clean': False,
            'uncommitted_changes': [],
            'merge_in_progress': True
        }
        mock_validate.return_value = True
        
        # Execute workflow
        result = orchestrator.execute_rollback(checkpoint_id)
        
        # Verify rollback blocked
        assert result['executed'] is False
        assert 'merge' in result['message'].lower()
        assert 'resolve conflicts' in result['message'].lower()


def test_complete_rollback_workflow_handles_user_cancellation(orchestrator):
    """Test workflow respects user cancellation."""
    checkpoint_id = "pre-work-20251128-100000"
    
    with patch.object(orchestrator, '_get_git_status') as mock_status, \
         patch.object(orchestrator, 'validate_checkpoint') as mock_validate, \
         patch.object(orchestrator, '_get_git_diff') as mock_diff, \
         patch('builtins.input', return_value='no') as mock_input, \
         patch.object(orchestrator, '_execute_git_reset') as mock_reset:
        
        # Setup: Clean repo but user cancels
        mock_status.return_value = {
            'clean': True,
            'uncommitted_changes': [],
            'merge_in_progress': False
        }
        mock_validate.return_value = True
        mock_diff.return_value = "diff --git a/file.py b/file.py\n-old line\n+new line"
        
        # Execute workflow
        result = orchestrator.execute_rollback(checkpoint_id)
        
        # Verify cancellation respected
        assert result['executed'] is False
        assert 'cancelled' in result['message'].lower()
        mock_reset.assert_not_called()


def test_complete_rollback_workflow_with_dry_run_mode(orchestrator):
    """Test workflow in dry-run mode shows preview without execution."""
    checkpoint_id = "pre-work-20251128-100000"
    
    with patch.object(orchestrator, '_get_git_diff') as mock_diff:
        
        # Setup: Diff preview available
        mock_diff.return_value = "diff --git a/file.py b/file.py\n-old line\n+new line"
        
        # Execute workflow in dry-run mode
        result = orchestrator.execute_rollback(checkpoint_id, dry_run=True)
        
        # Verify dry-run behavior
        assert result['executed'] is False
        assert 'preview' in result
        assert 'dry-run' in result['message'].lower()


def test_complete_rollback_workflow_with_force_flag(orchestrator):
    """Test workflow bypasses safety checks with force flag."""
    checkpoint_id = "pre-work-20251128-100000"
    
    with patch.object(orchestrator, '_get_git_status') as mock_status, \
         patch.object(orchestrator, 'validate_checkpoint') as mock_validate, \
         patch.object(orchestrator, '_execute_git_reset') as mock_reset:
        
        # Setup: Uncommitted changes but force=True
        mock_status.return_value = {
            'clean': False,
            'uncommitted_changes': [' M src/file.py'],
            'merge_in_progress': False
        }
        mock_validate.return_value = True
        mock_reset.return_value = {'success': True}
        
        # Execute workflow with force flag
        result = orchestrator.execute_rollback(checkpoint_id, force=True)
        
        # Verify force execution
        assert result['forced'] is True
        assert 'forced' in result['message'].lower()
        mock_reset.assert_called_once_with(checkpoint_id)


def test_complete_rollback_workflow_handles_invalid_checkpoint(orchestrator):
    """Test workflow handles invalid checkpoint ID gracefully."""
    checkpoint_id = "invalid-checkpoint-id"
    
    with patch.object(orchestrator, 'validate_checkpoint') as mock_validate:
        
        # Setup: Invalid checkpoint
        mock_validate.return_value = False
        
        # Execute workflow
        result = orchestrator.execute_rollback(checkpoint_id)
        
        # Verify validation failure handled
        assert result['executed'] is False
        assert 'invalid' in result['message'].lower() or 'not found' in result['message'].lower()


def test_complete_rollback_workflow_integration_with_command_parser(orchestrator):
    """Test integration between command parser and rollback execution."""
    user_input = "rollback to pre-work-20251128-100000"
    
    with patch.object(orchestrator, '_get_git_status') as mock_status, \
         patch.object(orchestrator, 'validate_checkpoint') as mock_validate, \
         patch.object(orchestrator, '_get_git_diff') as mock_diff, \
         patch('builtins.input', return_value='yes'), \
         patch.object(orchestrator, '_execute_git_reset') as mock_reset:
        
        # Setup: Clean repo, valid checkpoint
        mock_status.return_value = {
            'clean': True,
            'uncommitted_changes': [],
            'merge_in_progress': False
        }
        mock_validate.return_value = True
        mock_diff.return_value = "diff output"
        mock_reset.return_value = {'success': True}
        
        # Parse command (using orchestrator's parsing logic)
        parsed = orchestrator.parse_rollback_command(user_input)
        
        # Execute rollback with parsed checkpoint
        result = orchestrator.execute_rollback(parsed['checkpoint_id'])
        
        # Verify end-to-end integration
        assert parsed['checkpoint_id'] == 'pre-work-20251128-100000'
        assert result['executed'] is True
