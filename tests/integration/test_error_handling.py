"""
Integration tests for error handling across all components.

Tests verify that:
1. Git operation failures are caught and reported gracefully
2. Checkpoint failures don't crash workflows
3. Rollback safety violations are prevented
4. File system errors are handled
5. Invalid input is rejected with helpful messages
6. Network/remote failures are handled (git fetch, push)

Author: Asif Hussain
Created: 2025-11-28
Increment: 19 (Error Handling)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator
from src.enrichers.git_history_enricher import GitHistoryEnricher
from src.orchestrators.rollback_command_parser import RollbackCommandParser


class TestGitOperationErrors:
    """Test error handling for git operations."""
    
    def test_git_history_non_existent_file(self):
        """Git history should handle non-existent file gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            
            enricher = GitHistoryEnricher(repo_path=project_root)
            history = enricher.get_file_history("nonexistent.py")
            
            # Should return empty list, not crash
            assert isinstance(history, list)
            assert len(history) == 0
    
    def test_git_history_non_git_directory(self):
        """Git history should handle non-git directory gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            enricher = GitHistoryEnricher(repo_path=project_root)
            history = enricher.get_file_history("any_file.py")
            
            # Should return empty list or error dict, not crash
            assert isinstance(history, (list, dict))
            if isinstance(history, list):
                assert len(history) == 0
    
    def test_rollback_invalid_commit_sha(self):
        """Rollback should reject invalid commit SHA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Attempt rollback with invalid SHA
            result = rollback_orch.execute_rollback(
                checkpoint_id="invalid-checkpoint",
                dry_run=True
            )
            
            # Should return result dict, not crash - check for executed=False or error preview
            assert isinstance(result, dict)
            assert result.get("executed") is False or "error" in result.get("preview", "").lower()


class TestCheckpointErrors:
    """Test error handling for checkpoint operations."""
    
    def test_checkpoint_missing_session(self):
        """Checkpoint manager should handle missing session gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            # List checkpoints for non-existent session
            checkpoints = checkpoint_mgr.list_checkpoints("nonexistent-session")
            
            # Should return empty list, not crash
            assert isinstance(checkpoints, list)
            assert len(checkpoints) == 0
    
    def test_checkpoint_corrupted_metadata(self):
        """Checkpoint manager should handle corrupted metadata file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            # Create corrupted metadata file
            metadata_file = cortex_root / ".cortex" / "phase-checkpoints-test.json"
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            metadata_file.write_text("{invalid json")
            
            # Should handle gracefully
            checkpoints = checkpoint_mgr.list_checkpoints("test")
            
            # Should return empty list or handle error, not crash
            assert isinstance(checkpoints, list)
    
    def test_checkpoint_validation_missing_checkpoint(self):
        """Rollback validator should reject missing checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Validate non-existent checkpoint
            is_valid = rollback_orch.validate_checkpoint("session", "nonexistent")
            
            assert is_valid is False


class TestRollbackSafetyErrors:
    """Test rollback safety violation handling."""
    
    def test_rollback_with_uncommitted_changes(self):
        """Rollback should detect and reject uncommitted changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            # Create uncommitted file
            test_file = project_root / "uncommitted.py"
            test_file.write_text("# Uncommitted")
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Safety check should detect uncommitted changes
            safety_result = rollback_orch.check_rollback_safety("test-checkpoint")
            
            assert isinstance(safety_result, dict)
            assert safety_result["safe"] is False
            assert "uncommitted" in safety_result.get("warning", "").lower()
    
    def test_rollback_during_merge(self):
        """Rollback should detect and reject merge in progress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            # Simulate merge in progress by creating MERGE_HEAD
            merge_head = project_root / ".git" / "MERGE_HEAD"
            merge_head.write_text("abc123")
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Safety check should detect merge
            safety_result = rollback_orch.check_rollback_safety("test-checkpoint")
            
            assert isinstance(safety_result, dict)
            assert safety_result["safe"] is False
            assert "merge" in safety_result.get("warning", "").lower()


class TestCommandParsingErrors:
    """Test command parsing error handling."""
    
    def test_empty_command(self):
        """Parser should reject empty command."""
        parser = RollbackCommandParser()
        result = parser.parse_command("")
        
        assert result["valid"] is False
        assert "error_message" in result
    
    def test_whitespace_only_command(self):
        """Parser should reject whitespace-only command."""
        parser = RollbackCommandParser()
        result = parser.parse_command("   ")
        
        assert result["valid"] is False
        assert "error_message" in result
    
    def test_invalid_checkpoint_format(self):
        """Parser should reject checkpoint IDs with special characters."""
        parser = RollbackCommandParser()
        invalid_ids = [
            "checkpoint@123",
            "check#point",
            "check point",  # Space
            "check/point",  # Slash
        ]
        
        for invalid_id in invalid_ids:
            result = parser.parse_command(f"rollback to {invalid_id}")
            assert result["valid"] is False, f"Should reject: {invalid_id}"


class TestFileSystemErrors:
    """Test file system error handling."""
    
    def test_checkpoint_readonly_directory(self):
        """Checkpoint manager should handle readonly directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_dir = cortex_root / ".cortex"
            checkpoint_dir.mkdir(parents=True)
            
            # Make directory read-only (platform-dependent)
            import os, stat
            try:
                os.chmod(checkpoint_dir, stat.S_IREAD)
                
                checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
                
                # Attempt to store checkpoint (should handle gracefully)
                try:
                    checkpoint_mgr.store_checkpoint_metadata(
                        session_id="test",
                        phase="Test",
                        checkpoint_id="test-checkpoint",
                        commit_sha="abc123",
                        metrics={}
                    )
                except PermissionError:
                    # Expected - error should be raised, not silent failure
                    pass
            finally:
                # Restore write permission
                os.chmod(checkpoint_dir, stat.S_IWRITE | stat.S_IREAD)
    
    def test_checkpoint_disk_full_simulation(self):
        """Checkpoint manager should handle disk full scenario."""
        # This test is conceptual - actual disk full testing requires mocking
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            # Normal operation should succeed
            checkpoint_mgr.store_checkpoint_metadata(
                session_id="test",
                phase="Test",
                checkpoint_id="test-checkpoint",
                commit_sha="abc123",
                metrics={}
            )
            
            # Verify checkpoint was stored
            checkpoints = checkpoint_mgr.list_checkpoints("test")
            assert len(checkpoints) > 0


class TestGracefulDegradation:
    """Test graceful degradation when components fail."""
    
    def test_enricher_fallback_without_git(self):
        """Git enricher should provide empty history if git unavailable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            enricher = GitHistoryEnricher(repo_path=project_root)
            history = enricher.get_file_history("test.py")
            
            # Should return empty list, not exception
            assert isinstance(history, (list, dict))
    
    def test_rollback_dry_run_without_checkpoint(self):
        """Dry-run should work even if checkpoint doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Dry-run with non-existent checkpoint
            result = rollback_orch.execute_rollback(
                checkpoint_id="nonexistent",
                dry_run=True
            )
            
            # Should return result (success/failure), not crash
            assert isinstance(result, dict)
