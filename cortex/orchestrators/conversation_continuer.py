"""
Conversation Continuer - Resume conversations from checkpoints.
"""

import uuid
from typing import Any, Dict, Optional


class ConversationContinuer:
    """Manages conversation checkpoints and resumption."""

    def __init__(self) -> None:
        """Initialize the conversation continuer."""
        self.checkpoints: Dict[str, Dict[str, Any]] = {}

    def create_checkpoint(self, state: Dict[str, Any]) -> str:
        """
        Create a checkpoint from current state.

        Args:
            state: Current conversation state.

        Returns:
            Checkpoint ID.
        """
        checkpoint_id = str(uuid.uuid4())
        self.checkpoints[checkpoint_id] = dict(state)
        return checkpoint_id

    def resume_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Resume conversation from checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to resume from.

        Returns:
            Restored state or None if not found.
        """
        if checkpoint_id in self.checkpoints:
            return dict(self.checkpoints[checkpoint_id])
        return None

    def list_checkpoints(self) -> list[str]:
        """Get list of all checkpoint IDs."""
        return list(self.checkpoints.keys())

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        if checkpoint_id in self.checkpoints:
            del self.checkpoints[checkpoint_id]
            return True
        return False
