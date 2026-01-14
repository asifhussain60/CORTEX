"""
TODO Rollback Manager - Task 2.4.3 Implementation
GREEN phase: Make tests pass

Manages checkpoint creation and rollback for TODO operations with
comprehensive audit logging.

Author: GitHub Copilot
Phase: feat02-phase4-completion Phase 2
Correlation ID: FEAT02-P4-T2.4.3
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from src.orchestrators.core.todo_lifecycle_manager import TaskState
from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditLevel, AuditCategory


@dataclass
class Checkpoint:
    """Checkpoint data structure."""
    checkpoint_id: str
    state: Dict[str, TaskState]
    description: Optional[str]
    timestamp: datetime
    rolled_back: bool = False
    rollback_timestamp: Optional[datetime] = None


class TodoRollbackManager:
    """
    Manages checkpoints and rollback for TODO operations.
    
    Features:
    - Checkpoint creation before critical operations
    - Full and partial rollback support
    - Checkpoint validation
    - Recovery status tracking
    - Comprehensive audit logging
    """
    
    def __init__(self, audit_logger: Optional[EnterpriseAuditLogger] = None):
        """Initialize rollback manager."""
        self.audit_logger = audit_logger or EnterpriseAuditLogger()
        self._checkpoints: Dict[str, Checkpoint] = {}
        
        self._log_audit(
            "rollback_manager_initialized",
            "TodoRollbackManager initialized",
            {}
        )
    
    def create_checkpoint(
        self, 
        state: Dict[str, TaskState], 
        description: Optional[str] = None
    ) -> str:
        """
        Create a checkpoint of current state.
        
        Args:
            state: Current task state dictionary
            description: Optional checkpoint description
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = str(uuid.uuid4())
        
        # Deep copy state to prevent mutation
        state_copy = {k: v for k, v in state.items()}
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            state=state_copy,
            description=description,
            timestamp=datetime.now()
        )
        
        self._checkpoints[checkpoint_id] = checkpoint
        
        self._log_audit(
            "checkpoint_created",
            f"Checkpoint {checkpoint_id} created",
            {
                "checkpoint_id": checkpoint_id,
                "task_count": len(state),
                "description": description
            }
        )
        
        return checkpoint_id
    
    def has_checkpoint(self, checkpoint_id: str) -> bool:
        """Check if checkpoint exists."""
        return checkpoint_id in self._checkpoints
    
    def rollback(self, checkpoint_id: str) -> Dict[str, TaskState]:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore
            
        Returns:
            Restored state
            
        Raises:
            ValueError: If checkpoint not found
        """
        if not self.has_checkpoint(checkpoint_id):
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint = self._checkpoints[checkpoint_id]
        
        # Mark as rolled back
        checkpoint.rolled_back = True
        checkpoint.rollback_timestamp = datetime.now()
        
        # Return copy of state
        restored_state = {k: v for k, v in checkpoint.state.items()}
        
        self._log_audit(
            "rollback_executed",
            f"Rolled back to checkpoint {checkpoint_id}",
            {
                "checkpoint_id": checkpoint_id,
                "task_count": len(restored_state),
                "checkpoint_age_seconds": (
                    datetime.now() - checkpoint.timestamp
                ).total_seconds()
            }
        )
        
        return restored_state
    
    def partial_rollback(
        self, 
        checkpoint_id: str, 
        task_ids: List[str]
    ) -> Dict[str, TaskState]:
        """
        Rollback specific tasks only.
        
        Args:
            checkpoint_id: ID of checkpoint to restore from
            task_ids: List of task IDs to rollback
            
        Returns:
            Restored state for specified tasks
            
        Raises:
            ValueError: If checkpoint not found
        """
        if not self.has_checkpoint(checkpoint_id):
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint = self._checkpoints[checkpoint_id]
        
        # Extract only specified tasks
        restored_state = {
            task_id: checkpoint.state[task_id]
            for task_id in task_ids
            if task_id in checkpoint.state
        }
        
        self._log_audit(
            "partial_rollback_executed",
            f"Partial rollback from checkpoint {checkpoint_id}",
            {
                "checkpoint_id": checkpoint_id,
                "requested_tasks": len(task_ids),
                "restored_tasks": len(restored_state)
            }
        )
        
        return restored_state
    
    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Validate checkpoint integrity.
        
        Args:
            checkpoint_id: ID of checkpoint to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.has_checkpoint(checkpoint_id):
            return False
        
        checkpoint = self._checkpoints[checkpoint_id]
        
        # Validate state
        if checkpoint.state is None:
            return False
        
        if not isinstance(checkpoint.state, dict):
            return False
        
        # Validate all values are TaskState
        for value in checkpoint.state.values():
            if not isinstance(value, TaskState):
                return False
        
        self._log_audit(
            "checkpoint_validated",
            f"Checkpoint {checkpoint_id} validated",
            {"checkpoint_id": checkpoint_id, "valid": True}
        )
        
        return True
    
    def get_recovery_status(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Get recovery status for a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint
            
        Returns:
            Recovery status dictionary
            
        Raises:
            ValueError: If checkpoint not found
        """
        if not self.has_checkpoint(checkpoint_id):
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint = self._checkpoints[checkpoint_id]
        
        return {
            "checkpoint_id": checkpoint_id,
            "rolled_back": checkpoint.rolled_back,
            "timestamp": checkpoint.timestamp.isoformat(),
            "rollback_timestamp": (
                checkpoint.rollback_timestamp.isoformat()
                if checkpoint.rollback_timestamp
                else None
            ),
            "description": checkpoint.description,
            "task_count": len(checkpoint.state)
        }
    
    def _log_audit(self, operation: str, message: str, context: Dict[str, Any]):
        """Log audit trail with correlation ID."""
        correlation_id = f"FEAT02-P4-RECOVERY-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        self.audit_logger.log(
            AuditLevel.INFO,
            AuditCategory.EXECUTION,
            "todo_rollback_manager",
            operation,
            message,
            context={
                **context,
                "correlation_id": correlation_id
            }
        )
