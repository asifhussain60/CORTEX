"""Checkpoint Manager - Manages execution checkpoints.

Manages checkpoints for resuming interrupted executions.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum


class CheckpointStatus(Enum):
    """Checkpoint status."""

    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"


@dataclass
class Checkpoint:
    """Execution checkpoint.

    Attributes:
        checkpoint_id: Unique checkpoint identifier.
        execution_state: Saved execution state.
        status: Checkpoint status.
        timestamp: When checkpoint was created.
        metadata: Additional metadata.
    """

    checkpoint_id: str
    execution_state: Dict[str, Any]
    status: CheckpointStatus = CheckpointStatus.CREATED
    timestamp: datetime = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CheckpointManager:
    """Manages execution checkpoints."""

    def __init__(self) -> None:
        """Initialize checkpoint manager."""
        self.checkpoints: Dict[str, Checkpoint] = {}

    def create_checkpoint(
        self, checkpoint_id: str, execution_state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """Create a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.
            execution_state: State to checkpoint.
            metadata: Optional metadata.

        Returns:
            Checkpoint.
        """
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id, execution_state=execution_state, metadata=metadata or {}
        )
        self.checkpoints[checkpoint_id] = checkpoint
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            Checkpoint or None.
        """
        return self.checkpoints.get(checkpoint_id)

    def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore execution state from checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            Execution state or None.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if checkpoint:
            checkpoint.status = CheckpointStatus.RECOVERED
            return checkpoint.execution_state
        return None

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            True if deleted.
        """
        if checkpoint_id in self.checkpoints:
            del self.checkpoints[checkpoint_id]
            return True
        return False


__all__ = ["CheckpointManager", "Checkpoint", "CheckpointStatus"]
