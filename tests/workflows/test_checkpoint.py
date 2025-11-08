"""
Unit Tests for CORTEX Workflow Checkpoint System

Tests for CheckpointManager: save, load, delete, list, cleanup, and resume.

Author: CORTEX Development Team
Date: 2025-11-08
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from src.workflows.checkpoint import CheckpointManager
from src.workflows.workflow_engine import WorkflowState, StageStatus


class TestCheckpointManager:
    """Tests for CheckpointManager"""
    
    @pytest.fixture
    def temp_checkpoint_dir(self):
        """Create temporary checkpoint directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def checkpoint_manager(self, temp_checkpoint_dir):
        """Create CheckpointManager instance"""
        return CheckpointManager(temp_checkpoint_dir)
    
    @pytest.fixture
    def sample_state(self):
        """Create sample workflow state"""
        state = WorkflowState(
            workflow_id="wf-test-001",
            conversation_id="conv-123",
            user_request="Implement feature X",
            start_time="2025-11-08T10:00:00"
        )
        state.set_stage_status("stage1", StageStatus.SUCCESS)
        state.set_stage_output("stage1", {"result": "completed"})
        state.set_stage_status("stage2", StageStatus.RUNNING)
        state.current_stage = "stage2"
        return state
    
    def test_create_checkpoint_manager(self, temp_checkpoint_dir):
        """Test creating CheckpointManager creates directory"""
        manager = CheckpointManager(temp_checkpoint_dir)
        
        assert manager.checkpoint_dir.exists()
        assert manager.checkpoint_dir.is_dir()
    
    def test_save_checkpoint(self, checkpoint_manager, sample_state):
        """Test saving a checkpoint"""
        checkpoint_file = checkpoint_manager.save(sample_state)
        
        assert checkpoint_file.exists()
        assert checkpoint_file.name == "wf-test-001.json"
        
        # Verify content
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        
        assert data["workflow_id"] == "wf-test-001"
        assert data["conversation_id"] == "conv-123"
        assert data["current_stage"] == "stage2"
    
    def test_load_checkpoint(self, checkpoint_manager, sample_state):
        """Test loading a checkpoint"""
        checkpoint_manager.save(sample_state)
        
        loaded_state = checkpoint_manager.load("wf-test-001")
        
        assert loaded_state.workflow_id == sample_state.workflow_id
        assert loaded_state.conversation_id == sample_state.conversation_id
        assert loaded_state.user_request == sample_state.user_request
        assert loaded_state.current_stage == "stage2"
        assert loaded_state.stage_statuses["stage1"] == StageStatus.SUCCESS
        assert loaded_state.stage_statuses["stage2"] == StageStatus.RUNNING
    
    def test_load_nonexistent_checkpoint(self, checkpoint_manager):
        """Test loading non-existent checkpoint raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="Checkpoint not found"):
            checkpoint_manager.load("wf-nonexistent")
    
    def test_delete_checkpoint(self, checkpoint_manager, sample_state):
        """Test deleting a checkpoint"""
        checkpoint_manager.save(sample_state)
        
        # Verify it exists
        assert checkpoint_manager.load("wf-test-001") is not None
        
        # Delete it
        result = checkpoint_manager.delete("wf-test-001")
        
        assert result is True
        
        # Verify it's gone
        with pytest.raises(FileNotFoundError):
            checkpoint_manager.load("wf-test-001")
    
    def test_delete_nonexistent_checkpoint(self, checkpoint_manager):
        """Test deleting non-existent checkpoint returns False"""
        result = checkpoint_manager.delete("wf-nonexistent")
        
        assert result is False
    
    def test_list_checkpoints(self, checkpoint_manager):
        """Test listing all checkpoints"""
        # Create multiple checkpoints
        state1 = WorkflowState(
            workflow_id="wf-001",
            conversation_id="conv-1",
            user_request="Task 1",
            start_time="2025-11-08T10:00:00"
        )
        state2 = WorkflowState(
            workflow_id="wf-002",
            conversation_id="conv-2",
            user_request="Task 2",
            start_time="2025-11-08T11:00:00"
        )
        
        checkpoint_manager.save(state1)
        checkpoint_manager.save(state2)
        
        checkpoints = checkpoint_manager.list_checkpoints()
        
        assert len(checkpoints) >= 2
        workflow_ids = [cp["workflow_id"] for cp in checkpoints]
        assert "wf-001" in workflow_ids
        assert "wf-002" in workflow_ids
    
    def test_list_empty_checkpoints(self, checkpoint_manager):
        """Test listing checkpoints when none exist"""
        checkpoints = checkpoint_manager.list_checkpoints()
        
        assert checkpoints == []
    
    def test_get_resumable_checkpoints(self, checkpoint_manager):
        """Test getting resumable (incomplete) checkpoints"""
        # Create incomplete checkpoint
        incomplete_state = WorkflowState(
            workflow_id="wf-incomplete",
            conversation_id="conv-1",
            user_request="Incomplete task",
            start_time="2025-11-08T10:00:00"
        )
        incomplete_state.current_stage = "stage2"
        
        # Create complete checkpoint
        complete_state = WorkflowState(
            workflow_id="wf-complete",
            conversation_id="conv-2",
            user_request="Complete task",
            start_time="2025-11-08T09:00:00",
            end_time="2025-11-08T09:30:00"
        )
        
        checkpoint_manager.save(incomplete_state)
        checkpoint_manager.save(complete_state)
        
        resumable = checkpoint_manager.get_resumable()
        
        resumable_ids = [cp["workflow_id"] for cp in resumable]
        assert "wf-incomplete" in resumable_ids
        assert "wf-complete" not in resumable_ids
    
    def test_cleanup_old_checkpoints(self, checkpoint_manager):
        """Test cleaning up old checkpoints"""
        # Create old checkpoint (simulate by modifying metadata)
        old_state = WorkflowState(
            workflow_id="wf-old",
            conversation_id="conv-1",
            user_request="Old task",
            start_time=(datetime.now() - timedelta(days=40)).isoformat()
        )
        
        # Create recent checkpoint
        recent_state = WorkflowState(
            workflow_id="wf-recent",
            conversation_id="conv-2",
            user_request="Recent task",
            start_time=(datetime.now() - timedelta(days=5)).isoformat()
        )
        
        checkpoint_manager.save(old_state)
        checkpoint_manager.save(recent_state)
        
        # Cleanup checkpoints older than 30 days
        deleted = checkpoint_manager.cleanup_old(days=30)
        
        assert deleted >= 1
        
        # Verify old is gone, recent remains
        with pytest.raises(FileNotFoundError):
            checkpoint_manager.load("wf-old")
        
        assert checkpoint_manager.load("wf-recent") is not None
    
    def test_checkpoint_persistence_across_instances(self, temp_checkpoint_dir, sample_state):
        """Test checkpoints persist across manager instances"""
        # Save with first instance
        manager1 = CheckpointManager(temp_checkpoint_dir)
        manager1.save(sample_state)
        
        # Load with second instance
        manager2 = CheckpointManager(temp_checkpoint_dir)
        loaded_state = manager2.load("wf-test-001")
        
        assert loaded_state.workflow_id == sample_state.workflow_id
        assert loaded_state.current_stage == sample_state.current_stage
