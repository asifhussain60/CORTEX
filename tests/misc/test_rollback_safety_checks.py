"""
Tests for RollbackOrchestrator safety checks and user confirmation.

Tests verify:
- Uncommitted changes detection
- Merge conflict detection
- User confirmation prompt flow
- Dry-run preview mode
- Safety check bypass (forced rollback)
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator


class TestRollbackSafetyChecks:
    """Test suite for rollback safety validation."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temporary git repo."""
        return RollbackOrchestrator(project_root=tmp_path)
    
    def test_safety_check_detects_uncommitted_changes(self, orchestrator):
        """Safety check should detect uncommitted changes in working tree."""
        # Mock git status to show modified files
        with patch.object(orchestrator, '_get_git_status') as mock_status:
            mock_status.return_value = {
                'clean': False,
                'uncommitted_changes': ['file1.py', 'file2.py'],
                'merge_in_progress': False
            }
            
            result = orchestrator.check_rollback_safety('checkpoint-123')
            
            assert result['safe'] is False
            assert 'uncommitted changes' in result['warning'].lower()
            assert 'file1.py' in result['details']
            assert 'file2.py' in result['details']
    
    def test_safety_check_detects_merge_in_progress(self, orchestrator):
        """Safety check should detect merge conflicts."""
        with patch.object(orchestrator, '_get_git_status') as mock_status:
            mock_status.return_value = {
                'clean': True,
                'uncommitted_changes': [],
                'merge_in_progress': True
            }
            
            result = orchestrator.check_rollback_safety('checkpoint-123')
            
            assert result['safe'] is False
            assert 'merge' in result['warning'].lower()
            assert 'resolve conflicts' in result['warning'].lower()
    
    def test_safety_check_passes_for_clean_repo(self, orchestrator):
        """Safety check should pass when repo is clean."""
        with patch.object(orchestrator, '_get_git_status') as mock_status:
            mock_status.return_value = {
                'clean': True,
                'uncommitted_changes': [],
                'merge_in_progress': False
            }
            
            result = orchestrator.check_rollback_safety('checkpoint-123')
            
            assert result['safe'] is True
            assert result['warning'] is None
    
    def test_user_confirmation_shows_change_preview(self, orchestrator):
        """Confirmation prompt should show git diff preview."""
        with patch.object(orchestrator, '_get_git_diff') as mock_diff:
            mock_diff.return_value = "diff --git a/file.py\n-old line\n+new line"
            
            with patch('builtins.input', return_value='yes'):
                result = orchestrator.confirm_rollback(
                    checkpoint_id='checkpoint-123',
                    show_diff=True
                )
                
                assert result['confirmed'] is True
                mock_diff.assert_called_once_with('checkpoint-123')
    
    def test_user_can_cancel_rollback(self, orchestrator):
        """User can cancel rollback at confirmation prompt."""
        with patch('builtins.input', return_value='no'):
            result = orchestrator.confirm_rollback(
                checkpoint_id='checkpoint-123',
                show_diff=False
            )
            
            assert result['confirmed'] is False
            assert 'cancelled' in result['message'].lower()
    
    def test_dry_run_mode_shows_preview_without_execution(self, orchestrator):
        """Dry-run should show what would change without executing rollback."""
        with patch.object(orchestrator, '_get_git_diff') as mock_diff:
            mock_diff.return_value = "diff preview"
            
            result = orchestrator.execute_rollback(
                checkpoint_id='checkpoint-123',
                dry_run=True
            )
            
            assert result['executed'] is False
            assert result['preview'] is not None
            assert 'would rollback' in result['message'].lower()
    
    def test_forced_rollback_bypasses_safety_checks(self, orchestrator):
        """Forced rollback should skip safety checks and confirmation."""
        with patch.object(orchestrator, '_execute_git_reset') as mock_reset:
            mock_reset.return_value = {'success': True}
            
            result = orchestrator.execute_rollback(
                checkpoint_id='checkpoint-123',
                force=True
            )
            
            assert result['executed'] is True
            assert result['forced'] is True
            mock_reset.assert_called_once()
