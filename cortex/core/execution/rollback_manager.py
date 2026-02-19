"""
Rollback Manager for Autonomous Execution (ENH-067)

Provides git-backed rollback capabilities with:
- Checkpoint creation after each stage
- Rollback to previous checkpoints
- Git commit hash tracking
- Execution state recovery

Author: Asif Hussain
AC_START: AC-WAVE-N-003
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Checkpoint:
    """Represents an execution checkpoint."""
    id: str
    stage_id: str
    commit_hash: str
    timestamp: float
    description: str
    metadata: Dict[str, str]


class RollbackManager:
    """
    Git-backed rollback manager for autonomous execution.
    
    Features:
    - Create checkpoints after stage completion
    - Store git commit hashes for rollback
    - Restore execution state from checkpoints
    - Track checkpoint history
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize rollback manager.
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
        """
        self.repo_path = repo_path or Path.cwd()
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.checkpoint_history: List[str] = []
    
    def create_checkpoint(
        self,
        checkpoint_id: str,
        description: Optional[str] = None
    ) -> Checkpoint:
        """
        Create a checkpoint at current git state.
        
        Args:
            checkpoint_id: Unique identifier for checkpoint
            description: Optional description
        
        Returns:
            Created Checkpoint object
        """
        import time
        
        # Get current commit hash
        commit_hash = self._get_current_commit_hash()
        
        # Create checkpoint
        checkpoint = Checkpoint(
            id=checkpoint_id,
            stage_id=checkpoint_id,  # Assuming checkpoint_id is stage_id
            commit_hash=commit_hash,
            timestamp=time.time(),
            description=description or f"Checkpoint at {checkpoint_id}",
            metadata={}
        )
        
        # Store checkpoint
        self.checkpoints[checkpoint_id] = checkpoint
        self.checkpoint_history.append(checkpoint_id)
        
        return checkpoint
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Rollback to a previous checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
        
        Returns:
            True if successful, False otherwise
        """
        if checkpoint_id not in self.checkpoints:
            return False
        
        checkpoint = self.checkpoints[checkpoint_id]
        
        # Perform git reset to checkpoint commit
        success = self._git_reset(checkpoint.commit_hash)
        
        if success:
            # Remove checkpoints after this one
            idx = self.checkpoint_history.index(checkpoint_id)
            removed_checkpoints = self.checkpoint_history[idx + 1:]
            
            for cp_id in removed_checkpoints:
                if cp_id in self.checkpoints:
                    del self.checkpoints[cp_id]
            
            self.checkpoint_history = self.checkpoint_history[:idx + 1]
        
        return success
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Get checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            Checkpoint object if found, None otherwise
        """
        return self.checkpoints.get(checkpoint_id)
    
    def list_checkpoints(self) -> List[Checkpoint]:
        """
        List all checkpoints in chronological order.
        
        Returns:
            List of checkpoints
        """
        return [
            self.checkpoints[cp_id]
            for cp_id in self.checkpoint_history
            if cp_id in self.checkpoints
        ]
    
    def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """
        Get most recent checkpoint.
        
        Returns:
            Latest checkpoint or None if no checkpoints
        """
        if not self.checkpoint_history:
            return None
        
        latest_id = self.checkpoint_history[-1]
        return self.checkpoints.get(latest_id)
    
    def _get_current_commit_hash(self) -> str:
        """
        Get current git commit hash.
        
        Returns:
            Commit hash string
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "unknown"
        
        except Exception:
            return "unknown"
    
    def _git_reset(self, commit_hash: str) -> bool:
        """
        Perform git reset to specified commit.
        
        Args:
            commit_hash: Commit to reset to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        
        except Exception:
            return False
    
    def checkpoint_exists(self, checkpoint_id: str) -> bool:
        """
        Check if checkpoint exists.
        
        Args:
            checkpoint_id: Checkpoint to check
        
        Returns:
            True if exists, False otherwise
        """
        return checkpoint_id in self.checkpoints


# AC_COMPLETE: AC-WAVE-N-003 ✅ Rollback manager implementation
