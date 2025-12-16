"""
OrchestrationCheckpointManager - Feature 11 Implementation

Purpose: Save/restore/rollback orchestrator workflow state for failure recovery

Key Features:
- JSON-based checkpoint storage in cortex-brain/checkpoints/
- save_checkpoint(): Create checkpoint with state serialization
- restore_checkpoint(): Restore state from checkpoint
- rollback(): Restore state and remove later checkpoints
- cleanup_old_checkpoints(): 30-day retention policy with auto-cleanup
- Thread-safe operations for parallel orchestrators
- Performance: <50ms save/restore operations

Storage Structure:
    cortex-brain/checkpoints/
    ├── planning_orchestrator/
    │   ├── checkpoint-2024-12-13T10-30-00-abc123.json
    │   └── checkpoint-2024-12-13T11-15-00-def456.json
    ├── tdd_orchestrator/
    │   └── checkpoint-2024-12-13T09-45-00-ghi789.json
    └── system_maintenance_orchestrator/
        └── checkpoint-2024-12-13T08-00-00-jkl012.json

Checkpoint Schema:
{
    "checkpoint_id": "checkpoint-2024-12-13T10-30-00-abc123",
    "orchestrator_name": "planning_orchestrator",
    "timestamp": "2024-12-13T10:30:00.123456",
    "phase": "Phase 2: Implementation",
    "state": {
        "phase": 2,
        "current_task": "task_2.1",
        "completed_tasks": ["task_1.1", "task_1.2"],
        "variables": {"feature_name": "Feature 11"}
    }
}

Author: Asif Hussain
Created: December 13, 2024
Phase: 11.2 (GREEN)
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import logging
from src.utils.resource_resolver import get_root_path

logger = logging.getLogger(__name__)


class CheckpointNotFoundError(Exception):
    """Raised when attempting to restore a non-existent checkpoint."""
    pass


class CheckpointCorruptedError(Exception):
    """Raised when a checkpoint file is corrupted or invalid JSON."""
    pass


class OrchestrationCheckpointManager:
    """
    Manages checkpoint save/restore/rollback for orchestrator workflows.
    
    Provides recovery capability for long-running orchestrator executions,
    allowing workflows to resume from checkpoints after failures.
    
    Thread-safe for concurrent orchestrator operations.
    """
    
    def __init__(self, checkpoint_root: Optional[str] = None):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_root: Root directory for checkpoints.
                            Defaults to cortex-brain/checkpoints/
        """
        if checkpoint_root:
            self.checkpoint_root = Path(checkpoint_root)
        else:
            # Default to cortex-brain/checkpoints/
            cortex_root = get_root_path().parent
            self.checkpoint_root = cortex_root / "cortex-brain" / "checkpoints"
        
        self.checkpoint_root.mkdir(parents=True, exist_ok=True)
        
        # Thread lock for atomic file operations
        self._lock = threading.Lock()
        
        logger.info(f"✅ OrchestrationCheckpointManager initialized: {self.checkpoint_root}")
    
    def save_checkpoint(
        self,
        orchestrator_name: str,
        state: Dict[str, Any],
        phase: Optional[str] = None
    ) -> str:
        """
        Save a checkpoint with the current orchestrator state.
        
        Args:
            orchestrator_name: Name of the orchestrator (e.g., 'planning_orchestrator')
            state: Dictionary containing orchestrator state to save
            phase: Optional phase name (e.g., 'Phase 2: Implementation')
        
        Returns:
            str: Unique checkpoint ID for later restoration
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> state = {'phase': 2, 'tasks': ['task_1', 'task_2']}
            >>> checkpoint_id = manager.save_checkpoint('planning_orchestrator', state, 'Phase 2')
            >>> print(checkpoint_id)
            'checkpoint-2024-12-13T10-30-00-abc123'
        """
        timestamp = datetime.now()
        
        # Generate unique checkpoint ID with timestamp and random suffix
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H-%M-%S")
        random_suffix = str(uuid.uuid4())[:6]
        checkpoint_id = f"checkpoint-{timestamp_str}-{random_suffix}"
        
        # Create checkpoint data
        checkpoint_data = {
            'checkpoint_id': checkpoint_id,
            'orchestrator_name': orchestrator_name,
            'timestamp': timestamp.isoformat(),
            'phase': phase,
            'state': state
        }
        
        # Create orchestrator directory if it doesn't exist
        orchestrator_dir = self.checkpoint_root / orchestrator_name
        orchestrator_dir.mkdir(parents=True, exist_ok=True)
        
        # Write checkpoint file atomically
        checkpoint_path = orchestrator_dir / f"{checkpoint_id}.json"
        
        with self._lock:
            # Write to temporary file first, then rename (atomic operation)
            temp_path = checkpoint_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_path.rename(checkpoint_path)
        
        logger.debug(f"💾 Checkpoint saved: {orchestrator_name}/{checkpoint_id}")
        return checkpoint_id
    
    def restore_checkpoint(
        self,
        orchestrator_name: str,
        checkpoint_id: str
    ) -> Dict[str, Any]:
        """
        Restore orchestrator state from a checkpoint.
        
        Args:
            orchestrator_name: Name of the orchestrator
            checkpoint_id: Checkpoint ID returned by save_checkpoint()
        
        Returns:
            Dict[str, Any]: Restored state dictionary
        
        Raises:
            CheckpointNotFoundError: If checkpoint doesn't exist
            CheckpointCorruptedError: If checkpoint file is corrupted
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> state = manager.restore_checkpoint('planning_orchestrator', checkpoint_id)
            >>> print(state['phase'])
            2
        """
        checkpoint_path = self.checkpoint_root / orchestrator_name / f"{checkpoint_id}.json"
        
        if not checkpoint_path.exists():
            raise CheckpointNotFoundError(
                f"Checkpoint not found: {orchestrator_name}/{checkpoint_id}"
            )
        
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            logger.debug(f"📂 Checkpoint restored: {orchestrator_name}/{checkpoint_id}")
            return checkpoint_data['state']
        
        except json.JSONDecodeError as e:
            raise CheckpointCorruptedError(
                f"Corrupted checkpoint file: {checkpoint_path}. Error: {e}"
            )
    
    def rollback(
        self,
        orchestrator_name: str,
        checkpoint_id: str
    ) -> Dict[str, Any]:
        """
        Rollback to a previous checkpoint and remove all later checkpoints.
        
        Used to recover from failed workflow execution by restoring to
        a known-good checkpoint and removing checkpoints created after that point.
        
        Args:
            orchestrator_name: Name of the orchestrator
            checkpoint_id: Target checkpoint ID to rollback to
        
        Returns:
            Dict[str, Any]: Restored state from the target checkpoint
        
        Raises:
            CheckpointNotFoundError: If target checkpoint doesn't exist
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> # Save 3 checkpoints
            >>> cp1 = manager.save_checkpoint('orch', {'phase': 1})
            >>> cp2 = manager.save_checkpoint('orch', {'phase': 2})
            >>> cp3 = manager.save_checkpoint('orch', {'phase': 3})
            >>> # Rollback to checkpoint 1 (removes cp2 and cp3)
            >>> state = manager.rollback('orch', cp1)
            >>> print(state['phase'])
            1
        """
        # First restore the target checkpoint
        restored_state = self.restore_checkpoint(orchestrator_name, checkpoint_id)
        
        # Get target checkpoint timestamp
        checkpoint_path = self.checkpoint_root / orchestrator_name / f"{checkpoint_id}.json"
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            target_checkpoint = json.load(f)
        
        target_timestamp = datetime.fromisoformat(target_checkpoint['timestamp'])
        
        # Remove all checkpoints created after the target checkpoint
        orchestrator_dir = self.checkpoint_root / orchestrator_name
        
        if orchestrator_dir.exists():
            for checkpoint_file in orchestrator_dir.glob('*.json'):
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        checkpoint_data = json.load(f)
                    
                    checkpoint_timestamp = datetime.fromisoformat(checkpoint_data['timestamp'])
                    
                    # Remove if timestamp is after target
                    if checkpoint_timestamp > target_timestamp:
                        checkpoint_file.unlink()
                        logger.debug(f"🗑️  Removed later checkpoint: {checkpoint_file.name}")
                
                except (json.JSONDecodeError, KeyError, OSError) as e:
                    logger.warning(f"Failed to process checkpoint {checkpoint_file}: {e}")
        
        logger.info(f"⏪ Rolled back to: {orchestrator_name}/{checkpoint_id}")
        return restored_state
    
    def list_checkpoints(
        self,
        orchestrator_name: str
    ) -> List[Dict[str, Any]]:
        """
        List all checkpoints for an orchestrator in chronological order.
        
        Args:
            orchestrator_name: Name of the orchestrator
        
        Returns:
            List[Dict]: List of checkpoint metadata dictionaries, sorted by timestamp
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> checkpoints = manager.list_checkpoints('planning_orchestrator')
            >>> for cp in checkpoints:
            ...     print(f"{cp['checkpoint_id']}: {cp['phase']}")
        """
        orchestrator_dir = self.checkpoint_root / orchestrator_name
        
        if not orchestrator_dir.exists():
            return []
        
        checkpoints = []
        
        for checkpoint_file in orchestrator_dir.glob('*.json'):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                checkpoints.append({
                    'checkpoint_id': checkpoint_data['checkpoint_id'],
                    'timestamp': checkpoint_data['timestamp'],
                    'phase': checkpoint_data.get('phase'),
                    'file_path': str(checkpoint_file)
                })
            
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Skipping corrupted checkpoint {checkpoint_file}: {e}")
        
        # Sort by timestamp (chronological order)
        checkpoints.sort(key=lambda x: x['timestamp'])
        
        return checkpoints
    
    def cleanup_old_checkpoints(
        self,
        retention_days: int = 30
    ) -> int:
        """
        Remove checkpoints older than retention period.
        
        Implements 30-day retention policy by default. Removes checkpoints
        across all orchestrators that exceed the retention period.
        
        Args:
            retention_days: Number of days to retain checkpoints (default: 30)
        
        Returns:
            int: Number of checkpoints removed
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> removed_count = manager.cleanup_old_checkpoints(retention_days=30)
            >>> print(f"Removed {removed_count} old checkpoints")
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        removed_count = 0
        
        # Iterate through all orchestrator directories
        for orchestrator_dir in self.checkpoint_root.iterdir():
            if not orchestrator_dir.is_dir():
                continue
            
            for checkpoint_file in orchestrator_dir.glob('*.json'):
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        checkpoint_data = json.load(f)
                    
                    checkpoint_timestamp = datetime.fromisoformat(checkpoint_data['timestamp'])
                    
                    # Remove if older than cutoff date
                    if checkpoint_timestamp < cutoff_date:
                        checkpoint_file.unlink()
                        removed_count += 1
                        logger.debug(f"🗑️  Removed old checkpoint: {checkpoint_file}")
                
                except (json.JSONDecodeError, KeyError, OSError) as e:
                    logger.warning(f"Failed to process checkpoint {checkpoint_file}: {e}")
        
        if removed_count > 0:
            logger.info(f"🧹 Cleaned up {removed_count} old checkpoints (>{retention_days} days)")
        
        return removed_count
    
    def get_latest_checkpoint(
        self,
        orchestrator_name: str
    ) -> Optional[str]:
        """
        Get the ID of the most recent checkpoint for an orchestrator.
        
        Args:
            orchestrator_name: Name of the orchestrator
        
        Returns:
            Optional[str]: Latest checkpoint ID, or None if no checkpoints exist
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> latest_id = manager.get_latest_checkpoint('planning_orchestrator')
            >>> if latest_id:
            ...     state = manager.restore_checkpoint('planning_orchestrator', latest_id)
        """
        checkpoints = self.list_checkpoints(orchestrator_name)
        
        if not checkpoints:
            return None
        
        # Return latest checkpoint (list is sorted chronologically)
        return checkpoints[-1]['checkpoint_id']
    
    def delete_checkpoint(
        self,
        orchestrator_name: str,
        checkpoint_id: str
    ) -> bool:
        """
        Delete a specific checkpoint.
        
        Args:
            orchestrator_name: Name of the orchestrator
            checkpoint_id: Checkpoint ID to delete
        
        Returns:
            bool: True if checkpoint was deleted, False if it didn't exist
        
        Example:
            >>> manager = OrchestrationCheckpointManager()
            >>> success = manager.delete_checkpoint('planning_orchestrator', checkpoint_id)
        """
        checkpoint_path = self.checkpoint_root / orchestrator_name / f"{checkpoint_id}.json"
        
        if not checkpoint_path.exists():
            return False
        
        try:
            checkpoint_path.unlink()
            logger.debug(f"🗑️  Deleted checkpoint: {orchestrator_name}/{checkpoint_id}")
            return True
        
        except OSError as e:
            logger.error(f"Failed to delete checkpoint {checkpoint_path}: {e}")
            return False
