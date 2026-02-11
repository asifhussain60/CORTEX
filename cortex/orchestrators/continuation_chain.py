"""
Continuation Chain - Chain multiple checkpoints with execution order preservation.
"""

from collections import deque
from typing import Any, Dict, List, Optional


class ContinuationChain:
    """Manages checkpoint chains with execution order preservation."""

    def __init__(self) -> None:
        """Initialize continuation chain."""
        self.chain: deque[str] = deque()
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def add_checkpoint(self, checkpoint_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add checkpoint to chain.

        Args:
            checkpoint_id: Checkpoint ID.
            metadata: Optional metadata for checkpoint.
        """
        self.chain.append(checkpoint_id)
        self.metadata[checkpoint_id] = metadata or {}

    def execute(self) -> List[str]:
        """
        Execute chain in order.

        Returns:
            List of executed checkpoint IDs.
        """
        executed: List[str] = []
        while self.chain:
            checkpoint_id = self.chain.popleft()
            executed.append(checkpoint_id)
        return executed

    def get_chain_length(self) -> int:
        """Get current chain length."""
        return len(self.chain)

    def get_next_checkpoint(self) -> Optional[str]:
        """Get next checkpoint without removing it."""
        if self.chain:
            return self.chain[0]
        return None

    def skip_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Skip a checkpoint in chain.

        Args:
            checkpoint_id: Checkpoint ID to skip.

        Returns:
            True if skipped.
        """
        try:
            self.chain.remove(checkpoint_id)
            del self.metadata[checkpoint_id]
            return True
        except (ValueError, KeyError):
            return False

    def clear_chain(self) -> None:
        """Clear entire chain."""
        self.chain.clear()
        self.metadata.clear()

    def get_remaining_checkpoints(self) -> List[str]:
        """Get list of remaining checkpoints."""
        return list(self.chain)
