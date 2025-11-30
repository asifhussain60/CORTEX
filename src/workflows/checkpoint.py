"""
CORTEX Workflow Checkpoint System

Provides checkpoint/resume capability for workflow execution,
allowing workflows to be resumed from last successful stage
after interruption or failure.

Author: CORTEX Development Team
Date: 2025-11-08
Version: 2.0.0
"""

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .workflow_engine import WorkflowState, StageStatus


class CheckpointManager:
    """Manages workflow checkpoints for resume capability"""
    
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, state: WorkflowState) -> Path:
        """
        Save workflow state to checkpoint file
        
        Args:
            state: Current workflow state
            
        Returns:
            Path to checkpoint file
        """
        checkpoint_file = self._get_checkpoint_path(state.workflow_id)
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2)
        
        # Also save metadata for quick listing
        self._save_metadata(state)
        
        return checkpoint_file
    
    def load(self, workflow_id: str) -> WorkflowState:
        """
        Load workflow state from checkpoint
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            Restored workflow state
            
        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        checkpoint_file = self._get_checkpoint_path(workflow_id)
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {workflow_id}")
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return WorkflowState.from_dict(data)
    
    def list_checkpoints(self) -> List[dict]:
        """
        List all available checkpoints
        
        Returns:
            List of checkpoint metadata dicts
        """
        metadata_file = self.checkpoint_dir / "checkpoints.json"
        
        if not metadata_file.exists():
            return []
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete(self, workflow_id: str) -> bool:
        """
        Delete a checkpoint
        
        Args:
            workflow_id: Workflow to delete
            
        Returns:
            True if deleted, False if not found
        """
        checkpoint_file = self._get_checkpoint_path(workflow_id)
        
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            self._remove_from_metadata(workflow_id)
            return True
        
        return False
    
    def cleanup_old(self, days: int = 30) -> int:
        """
        Delete checkpoints older than specified days
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of checkpoints deleted
        """
        checkpoints = self.list_checkpoints()
        deleted = 0
        
        for cp in checkpoints:
            age_days = self._get_checkpoint_age_days(cp["start_time"])
            
            if age_days > days:
                if self.delete(cp["workflow_id"]):
                    deleted += 1
        
        return deleted
    
    def get_resumable(self) -> List[dict]:
        """
        Get list of checkpoints that can be resumed
        (workflows that are incomplete)
        
        Returns:
            List of resumable checkpoint metadata
        """
        checkpoints = self.list_checkpoints()
        
        return [
            cp for cp in checkpoints
            if not cp.get("end_time")  # No end_time = incomplete
        ]
    
    def _get_checkpoint_path(self, workflow_id: str) -> Path:
        """Get path to checkpoint file"""
        return self.checkpoint_dir / f"{workflow_id}.json"
    
    def _save_metadata(self, state: WorkflowState) -> None:
        """Save checkpoint metadata for quick listing"""
        metadata_file = self.checkpoint_dir / "checkpoints.json"
        
        # Load existing metadata
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
        else:
            metadata_list = []
        
        # Update or add metadata for this workflow
        metadata = {
            "workflow_id": state.workflow_id,
            "conversation_id": state.conversation_id,
            "user_request": state.user_request[:100],  # Truncate for display
            "current_stage": state.current_stage,
            "start_time": state.start_time,
            "end_time": state.end_time,
            "completed_stages": sum(
                1 for s in state.stage_statuses.values()
                if s == StageStatus.SUCCESS
            ),
            "total_stages": len(state.stage_statuses)
        }
        
        # Remove old entry if exists
        metadata_list = [m for m in metadata_list if m["workflow_id"] != state.workflow_id]
        
        # Add new entry
        metadata_list.append(metadata)
        
        # Save
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=2)
    
    def _remove_from_metadata(self, workflow_id: str) -> None:
        """Remove workflow from metadata list"""
        metadata_file = self.checkpoint_dir / "checkpoints.json"
        
        if not metadata_file.exists():
            return
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)
        
        # Remove entry
        metadata_list = [m for m in metadata_list if m["workflow_id"] != workflow_id]
        
        # Save
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=2)
    
    def _get_checkpoint_age_days(self, start_time: str) -> int:
        """Calculate age of checkpoint in days"""
        start_dt = datetime.fromisoformat(start_time)
        now_dt = datetime.now()
        delta = now_dt - start_dt
        return delta.days


class RollbackManager:
    """Manages workflow rollback operations"""
    
    def __init__(self, checkpoint_manager: CheckpointManager):
        self.checkpoint_manager = checkpoint_manager
    
    def rollback_to_stage(
        self,
        workflow_id: str,
        target_stage: str
    ) -> WorkflowState:
        """
        Rollback workflow to a specific stage
        
        Args:
            workflow_id: Workflow to rollback
            target_stage: Stage to rollback to
            
        Returns:
            Modified workflow state ready to resume from target stage
        """
        # Load current state
        state = self.checkpoint_manager.load(workflow_id)
        
        # Find stages after target
        execution_order = list(state.stage_statuses.keys())
        target_idx = execution_order.index(target_stage)
        
        # Reset stages after target
        for stage_id in execution_order[target_idx:]:
            state.set_stage_status(stage_id, StageStatus.PENDING)
            if stage_id in state.stage_outputs:
                del state.stage_outputs[stage_id]
        
        # Update current stage
        state.current_stage = target_stage
        state.end_time = None
        
        # Save rollback state
        self.checkpoint_manager.save(state)
        
        return state
    
    def clear_failed_stages(self, workflow_id: str) -> WorkflowState:
        """
        Clear failed stages and reset to PENDING for retry
        
        Args:
            workflow_id: Workflow to clear failures from
            
        Returns:
            Modified workflow state
        """
        state = self.checkpoint_manager.load(workflow_id)
        
        # Find all failed stages
        for stage_id, status in state.stage_statuses.items():
            if status == StageStatus.FAILED:
                state.set_stage_status(stage_id, StageStatus.PENDING)
                if stage_id in state.stage_outputs:
                    del state.stage_outputs[stage_id]
        
        # Save updated state
        self.checkpoint_manager.save(state)
        
        return state


__all__ = ["CheckpointManager", "RollbackManager"]
