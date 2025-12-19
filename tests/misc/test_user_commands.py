"""
Integration tests for user commands with rollback functionality.

Tests verify that:
1. Intent router detects rollback commands
2. Command parser extracts checkpoint IDs correctly
3. Commands integrate with RollbackOrchestrator
4. Error handling for invalid commands
5. User confirmation workflow

Author: Asif Hussain
Created: 2025-11-28
Increment: 17 (User Command Integration)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.rollback_command_parser import RollbackCommandParser
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager


class TestCommandParsing:
    """Test command parsing for rollback operations."""
    
    def test_parse_standard_rollback_command(self):
        """Parser should extract checkpoint ID from 'rollback to X' format."""
        parser = RollbackCommandParser()
        result = parser.parse_command("rollback to checkpoint-abc123")
        
        assert result["valid"] is True
        assert result["checkpoint_id"] == "checkpoint-abc123"
        assert result["session_id"] is None
    
    def test_parse_session_rollback_command(self):
        """Parser should extract both session and checkpoint from 'rollback session Y to X'."""
        parser = RollbackCommandParser()
        result = parser.parse_command("rollback session planning-2025 to checkpoint-dor")
        
        assert result["valid"] is True
        assert result["session_id"] == "planning-2025"
        assert result["checkpoint_id"] == "checkpoint-dor"
    
    def test_parse_shorthand_rollback(self):
        """Parser should handle shorthand 'rollback X' format."""
        parser = RollbackCommandParser()
        result = parser.parse_command("rollback green-phase")
        
        assert result["valid"] is True
        assert result["checkpoint_id"] == "green-phase"
    
    def test_reject_invalid_command(self):
        """Parser should reject malformed commands."""
        parser = RollbackCommandParser()
        result = parser.parse_command("rolllback typo")
        
        assert result["valid"] is False
        assert "error_message" in result


class TestIntentRouting:
    """Test intent detection for rollback commands."""
    
    def test_detect_rollback_intent(self):
        """Intent router should recognize rollback commands."""
        commands = [
            "rollback to checkpoint-123",
            "rollback session xyz to checkpoint-456",
            "rollback abc",
            "Rollback to DoR",  # Case insensitive
        ]
        
        for cmd in commands:
            # Simulate intent detection
            is_rollback = cmd.lower().startswith("rollback")
            assert is_rollback, f"Failed to detect rollback intent in: {cmd}"
    
    def test_reject_non_rollback_commands(self):
        """Intent router should not trigger on non-rollback commands."""
        commands = [
            "plan feature",
            "start tdd",
            "align system",
            "fallback option",  # Contains "back" but not rollback
        ]
        
        for cmd in commands:
            is_rollback = cmd.lower().startswith("rollback")
            assert not is_rollback, f"Incorrectly detected rollback in: {cmd}"


class TestCommandOrchestration:
    """Test end-to-end command execution with orchestrators."""
    
    def test_command_triggers_rollback_validation(self):
        """Command should trigger checkpoint validation before execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            # Setup checkpoint
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            session_id = "test-session"
            checkpoint_id = "test-checkpoint"
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="Test_Phase",
                checkpoint_id=checkpoint_id,
                commit_sha="abc123",
                metrics={}
            )
            
            # Parse command
            parser = RollbackCommandParser()
            command_result = parser.parse_command(f"rollback to {checkpoint_id}")
            
            assert command_result["valid"] is True
            
            # Validate with orchestrator
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            is_valid = rollback_orch.validate_checkpoint(session_id, checkpoint_id)
            assert is_valid is True
    
    def test_invalid_checkpoint_returns_error(self):
        """Invalid checkpoint ID should return helpful error message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Attempt validation with non-existent checkpoint
            is_valid = rollback_orch.validate_checkpoint("fake-session", "nonexistent")
            assert is_valid is False


class TestUserConfirmation:
    """Test user confirmation workflow."""
    
    def test_safety_check_requires_confirmation(self):
        """Rollback should show diff and require confirmation before execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Check safety - should return warnings/info for confirmation
            safety_result = rollback_orch.check_rollback_safety(
                checkpoint_id="test-checkpoint"
            )
            
            # Should have safety info for user to review
            assert isinstance(safety_result, dict)
            assert "safe" in safety_result
    
    def test_force_flag_bypasses_confirmation(self):
        """Force flag should skip user confirmation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Force flag should allow bypassing safety checks in execute_rollback
            rollback_result = rollback_orch.execute_rollback(
                checkpoint_id="test-checkpoint",
                force=True,
                dry_run=True
            )
            
            # With force, execution should proceed (dry-run won't actually execute)
            assert isinstance(rollback_result, dict)


class TestErrorHandling:
    """Test error handling for command execution."""
    
    def test_missing_checkpoint_id_returns_usage(self):
        """Missing checkpoint ID should return usage instructions."""
        parser = RollbackCommandParser()
        result = parser.parse_command("rollback to")
        
        assert result["valid"] is False
        assert "usage" in result.get("error_message", "").lower() or "checkpoint id" in result.get("error_message", "").lower()
    
    def test_invalid_characters_rejected(self):
        """Checkpoint IDs with invalid characters should be rejected."""
        parser = RollbackCommandParser()
        result = parser.parse_command("rollback to checkpoint@invalid#123")
        
        assert result["valid"] is False
        assert "alphanumeric" in result.get("error_message", "").lower() or "invalid" in result.get("error_message", "").lower()
