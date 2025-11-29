"""
Tests for Phase Checkpoint Manager.

This module validates phase checkpoint metadata storage.
"""

import pytest
from pathlib import Path
import json
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager


class TestPhaseCheckpointManager:
    """Test phase checkpoint manager functionality."""
    
    def test_manager_initializes_with_cortex_directory(self, tmp_path):
        """Verify manager creates .cortex directory."""
        manager = PhaseCheckpointManager(cortex_root=tmp_path)
        
        assert (tmp_path / ".cortex").exists()
    
    def test_manager_stores_checkpoint_metadata(self, tmp_path):
        """Verify checkpoint metadata can be stored."""
        manager = PhaseCheckpointManager(cortex_root=tmp_path)
        
        manager.store_checkpoint_metadata(
            session_id="test-session",
            phase="phase-1",
            checkpoint_id="ckpt-123",
            commit_sha="abc123def456"
        )
        
        metadata = manager.get_checkpoint_metadata("test-session", "phase-1")
        
        assert metadata is not None
        assert metadata['checkpoint_id'] == "ckpt-123"
        assert metadata['commit_sha'] == "abc123def456"
    
    def test_manager_lists_all_checkpoints_for_session(self, tmp_path):
        """Verify all checkpoints for session can be listed."""
        manager = PhaseCheckpointManager(cortex_root=tmp_path)
        
        manager.store_checkpoint_metadata("session-1", "phase-1", "ckpt-1", "sha1")
        manager.store_checkpoint_metadata("session-1", "phase-2", "ckpt-2", "sha2")
        manager.store_checkpoint_metadata("session-2", "phase-1", "ckpt-3", "sha3")
        
        checkpoints = manager.list_checkpoints("session-1")
        
        assert len(checkpoints) == 2
        assert any(cp['phase'] == "phase-1" for cp in checkpoints)
        assert any(cp['phase'] == "phase-2" for cp in checkpoints)
    
    def test_manager_returns_none_for_nonexistent_checkpoint(self, tmp_path):
        """Verify None returned for nonexistent checkpoint."""
        manager = PhaseCheckpointManager(cortex_root=tmp_path)
        
        metadata = manager.get_checkpoint_metadata("nonexistent", "phase-1")
        
        assert metadata is None
    
    def test_manager_handles_multiple_sessions(self, tmp_path):
        """Verify multiple sessions handled correctly."""
        manager = PhaseCheckpointManager(cortex_root=tmp_path)
        
        manager.store_checkpoint_metadata("session-1", "phase-1", "ckpt-1", "sha1")
        manager.store_checkpoint_metadata("session-2", "phase-1", "ckpt-2", "sha2")
        
        session1_checkpoints = manager.list_checkpoints("session-1")
        session2_checkpoints = manager.list_checkpoints("session-2")
        
        assert len(session1_checkpoints) == 1
        assert len(session2_checkpoints) == 1
        assert session1_checkpoints[0]['checkpoint_id'] != session2_checkpoints[0]['checkpoint_id']
    
    def test_manager_includes_timestamp_in_metadata(self, tmp_path):
        """Verify timestamp included in checkpoint metadata."""
        manager = PhaseCheckpointManager(cortex_root=tmp_path)
        
        manager.store_checkpoint_metadata("test", "phase-1", "ckpt-1", "sha1")
        
        metadata = manager.get_checkpoint_metadata("test", "phase-1")
        
        assert 'created_at' in metadata
