"""
Extended unit tests for RollbackOrchestrator to increase coverage to 90%+.

Tests missing coverage areas:
- format_checkpoint_summary edge cases
- _get_git_status error handling
- check_rollback_safety with various conditions
- execute_rollback with force/dry-run modes

Author: Asif Hussain
Created: 2025-11-28
Increment: 21 (Unit Test Suite)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.orchestrators.rollback_orchestrator import RollbackOrchestrator
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager


class TestRollbackOrchestratorExtended:
    """Extended tests for RollbackOrchestrator to reach 90%+ coverage."""
    
    def test_format_checkpoint_summary_with_none_commit_sha(self):
        """Should handle None commit_sha gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            # Store checkpoint without commit SHA
            session_id = "test-session"
            checkpoint_id = "test-checkpoint"
            
            orchestrator.checkpoint_manager.store_checkpoint_metadata(
                session_id=session_id,
                phase="TestPhase",
                checkpoint_id=checkpoint_id,
                commit_sha=None,  # Explicitly None
                metrics={}
            )
            
            # Format summary
            summary = orchestrator.format_checkpoint_summary(session_id, checkpoint_id)
            
            assert "Commit SHA: unknown" in summary
            assert checkpoint_id in summary
    
    def test_format_checkpoint_summary_with_metrics(self):
        """Should format metrics properly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            session_id = "test-session"
            checkpoint_id = "test-checkpoint"
            metrics = {
                "tests_passing": 15,
                "coverage": 92.5,
                "duration_s": 45.2
            }
            
            orchestrator.checkpoint_manager.store_checkpoint_metadata(
                session_id=session_id,
                phase="TestPhase",
                checkpoint_id=checkpoint_id,
                commit_sha="abc123",
                metrics=metrics
            )
            
            summary = orchestrator.format_checkpoint_summary(session_id, checkpoint_id)
            
            assert "Metrics:" in summary
            assert "tests_passing: 15" in summary
            assert "coverage: 92.5" in summary
            assert "duration_s: 45.2" in summary
    
    def test_format_checkpoint_summary_not_found(self):
        """Should handle checkpoint not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            summary = orchestrator.format_checkpoint_summary("fake-session", "fake-checkpoint")
            
            assert "not found" in summary.lower()
    
    def test_get_git_status_with_uncommitted_changes(self):
        """Should detect uncommitted changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            project_root = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir, project_root=project_root)
            
            # Mock git status output with uncommitted changes
            # Note: git status format is "XY filename" where XY are status codes
            # The code strips from position 3 onwards
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    stdout=" M file1.py\n M file2.py\n",
                    returncode=0
                )
                
                status = orchestrator._get_git_status()
                
                assert status['clean'] is False
                assert len(status['uncommitted_changes']) >= 2
    
    def test_get_git_status_with_merge_in_progress(self):
        """Should detect merge in progress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            project_root = Path(tmpdir)
            
            # Create .git/MERGE_HEAD to simulate merge
            git_dir = project_root / '.git'
            git_dir.mkdir()
            merge_head = git_dir / 'MERGE_HEAD'
            merge_head.write_text("abc123")
            
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir, project_root=project_root)
            
            # Mock git status output (clean)
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="",
                    returncode=0
                )
                
                status = orchestrator._get_git_status()
                
                assert status['merge_in_progress'] is True
                assert status['clean'] is False
    
    def test_get_git_status_clean(self):
        """Should detect clean working tree."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            project_root = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir, project_root=project_root)
            
            # Mock git status output (clean)
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="",
                    returncode=0
                )
                
                status = orchestrator._get_git_status()
                
                assert status['clean'] is True
                assert len(status['uncommitted_changes']) == 0
                assert status['merge_in_progress'] is False
    
    def test_get_git_status_git_command_fails(self):
        """Should handle git command failure gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            project_root = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir, project_root=project_root)
            
            # Mock git command failure
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
                
                status = orchestrator._get_git_status()
                
                # Should assume unsafe when git fails
                assert status['clean'] is False
    
    def test_check_rollback_safety_with_uncommitted_changes(self):
        """Should detect uncommitted changes as safety issue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            # Mock uncommitted changes
            with patch.object(orchestrator, '_get_git_status') as mock_status:
                mock_status.return_value = {
                    'clean': False,
                    'uncommitted_changes': ['file1.py', 'file2.py'],
                    'merge_in_progress': False
                }
                
                result = orchestrator.check_rollback_safety("test-checkpoint")
                
                assert result['safe'] is False
                assert 'Uncommitted changes' in result['warning']
    
    def test_check_rollback_safety_with_merge_in_progress(self):
        """Should detect merge in progress as safety issue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            # Mock merge in progress
            with patch.object(orchestrator, '_get_git_status') as mock_status:
                mock_status.return_value = {
                    'clean': False,
                    'uncommitted_changes': [],
                    'merge_in_progress': True
                }
                
                result = orchestrator.check_rollback_safety("test-checkpoint")
                
                assert result['safe'] is False
                assert 'Merge in progress' in result['warning']
    
    def test_check_rollback_safety_safe(self):
        """Should pass safety check when conditions are met."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            # Mock clean state
            with patch.object(orchestrator, '_get_git_status') as mock_status:
                mock_status.return_value = {
                    'clean': True,
                    'uncommitted_changes': [],
                    'merge_in_progress': False
                }
                
                result = orchestrator.check_rollback_safety("test-checkpoint")
                
                assert result['safe'] is True


class TestRollbackOrchestratorExecutionModes:
    """Tests for different rollback execution modes."""
    
    def test_execute_rollback_dry_run(self):
        """Should execute dry-run without making changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            checkpoint_id = "test-checkpoint"
            
            # Mock _get_git_diff
            with patch.object(orchestrator, '_get_git_diff') as mock_diff:
                mock_diff.return_value = "diff preview"
                
                # Execute dry-run
                result = orchestrator.execute_rollback(
                    checkpoint_id=checkpoint_id,
                    dry_run=True
                )
                
                assert result['executed'] is False
                assert 'dry-run' in result['message'].lower()
    
    def test_execute_rollback_force(self):
        """Should execute forced rollback bypassing safety checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            checkpoint_id = "test-checkpoint"
            
            # Mock _execute_git_reset
            with patch.object(orchestrator, '_execute_git_reset') as mock_reset:
                mock_reset.return_value = {'success': True}
                
                # Execute forced rollback
                result = orchestrator.execute_rollback(
                    checkpoint_id=checkpoint_id,
                    force=True
                )
                
                assert result['executed'] is True
                assert result['forced'] is True
    
    def test_execute_rollback_safety_check_covers_code(self):
        """Test to cover safety check path in execute_rollback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            session_id = "test-session"
            checkpoint_id = "test-checkpoint"
            
            # Store checkpoint so validation passes
            orchestrator.checkpoint_manager.store_checkpoint_metadata(
                session_id=session_id,
                phase="TestPhase",
                checkpoint_id=checkpoint_id,
                commit_sha="abc123",
                metrics={}
            )
            
            # Mock safety check failure
            with patch.object(orchestrator, 'validate_checkpoint') as mock_validate:
                mock_validate.return_value = True
                
                with patch.object(orchestrator, 'check_rollback_safety') as mock_safety:
                    mock_safety.return_value = {
                        'safe': False,
                        'warning': 'Uncommitted changes detected',
                        'details': 'file1.py modified'
                    }
                    
                    # Execute without force (should fail safely)
                    result = orchestrator.execute_rollback(
                        checkpoint_id=checkpoint_id,
                        force=False
                    )
                    
                    assert result['executed'] is False
                    assert 'Uncommitted changes' in result['message']


class TestRollbackOrchestratorEdgeCases:
    """Edge case tests for RollbackOrchestrator."""
    
    def test_validate_nonexistent_checkpoint(self):
        """Should handle nonexistent checkpoint validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir)
            
            is_valid = orchestrator.validate_checkpoint("fake-session", "fake-checkpoint")
            
            assert is_valid is False
    
    def test_auto_detect_cortex_dir(self):
        """Should auto-detect CORTEX directory when not provided."""
        orchestrator = RollbackOrchestrator()
        
        # Should not raise error
        assert orchestrator.cortex_dir is not None
        assert orchestrator.project_root is not None
    
    def test_explicit_project_root(self):
        """Should use explicit project root when provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            orchestrator = RollbackOrchestrator(cortex_dir=cortex_dir, project_root=project_root)
            
            assert orchestrator.project_root == project_root
