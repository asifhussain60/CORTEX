"""
Recovery Manager - Checkpoint and Rollback System.

Phase 3 of Toolkit Manager Implementation
Provides transaction-like operations with checkpoint/rollback capability.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
import subprocess

from .checkpoint import Checkpoint, CheckpointState


class RecoveryError(Exception):
    """Base exception for recovery operations."""
    pass


class CheckpointNotFoundError(RecoveryError):
    """Raised when a checkpoint cannot be found."""
    pass


@dataclass
class ExecutionContext:
    """
    Context for a tool execution that may need rollback.
    
    Attributes:
        tool: Name of the tool being executed
        args: Arguments passed to the tool
        affected_paths: List of paths that may be modified
        is_destructive: Whether the operation is destructive
        metadata: Optional additional context
    """
    tool: str
    args: List[str]
    affected_paths: List[Path]
    is_destructive: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackResult:
    """
    Result of a rollback operation.
    
    Attributes:
        success: Whether rollback completed successfully
        checkpoint_id: ID of checkpoint rolled back to
        restored_paths: List of paths that were restored
        errors: List of error messages if any failures
    """
    success: bool
    checkpoint_id: str
    restored_paths: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class RecoveryManager:
    """
    Transaction-like operations with checkpoint/rollback capability.
    
    Provides:
    - Checkpoint creation before destructive operations
    - State snapshot capture of affected files
    - Rollback to restore files to checkpoint state
    - Auto-pruning of old checkpoints
    
    Example:
        manager = RecoveryManager(toolkit_root)
        
        context = ExecutionContext(
            tool="cleanup",
            args=["--force"],
            affected_paths=[Path("config.yaml")],
            is_destructive=True
        )
        
        checkpoint = manager.create_checkpoint(context)
        
        # ... perform destructive operation ...
        
        if something_went_wrong:
            manager.rollback(checkpoint.id)
    """
    
    # Binary file markers
    BINARY_MARKER = "<binary>"
    NOT_EXISTS_MARKER = "<not_exists>"
    
    def __init__(
        self,
        toolkit_root: Path,
        max_checkpoints: int = 50,
    ):
        """
        Initialize RecoveryManager.
        
        Args:
            toolkit_root: Root directory of the toolkit
            max_checkpoints: Maximum checkpoints to keep (auto-prune when exceeded)
        """
        self.toolkit_root = toolkit_root
        self.max_checkpoints = max_checkpoints
        self.checkpoint_dir = toolkit_root / ".checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def create_checkpoint(self, context: ExecutionContext) -> Checkpoint:
        """
        Create a checkpoint before an operation.
        
        Captures:
        - Current state of affected files
        - Git SHA if in a git repository
        - Execution context metadata
        
        Args:
            context: Execution context with affected paths
            
        Returns:
            Created checkpoint with unique ID
        """
        # Generate unique ID
        checkpoint_id = str(uuid4())
        
        # Capture state snapshot
        state_snapshot = self._capture_state(context.affected_paths)
        
        # Get git SHA if available
        git_sha = self._get_current_sha()
        
        # Create checkpoint
        checkpoint = Checkpoint(
            id=checkpoint_id,
            timestamp=datetime.now(),
            tool=context.tool,
            args=context.args,
            affected_paths=context.affected_paths,
            git_sha=git_sha,
            state_snapshot=state_snapshot,
            state=CheckpointState.ACTIVE,
        )
        
        # Persist to disk
        self._persist_checkpoint(checkpoint)
        
        # Auto-prune if needed
        self._auto_prune()
        
        return checkpoint
    
    def rollback(self, checkpoint_id: str) -> RollbackResult:
        """
        Restore system to a checkpoint state.
        
        Args:
            checkpoint_id: ID of checkpoint to rollback to
            
        Returns:
            RollbackResult with success status and details
            
        Raises:
            CheckpointNotFoundError: If checkpoint doesn't exist
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        
        restored_paths = []
        errors = []
        
        for path_str, content in checkpoint.state_snapshot.items():
            path = Path(path_str)
            
            try:
                if content == self.NOT_EXISTS_MARKER:
                    # File didn't exist - skip (don't delete new files)
                    continue
                elif content == self.BINARY_MARKER:
                    # Binary file - can't restore from snapshot
                    errors.append(f"Cannot restore binary file: {path}")
                    continue
                else:
                    # Restore file content
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
                    restored_paths.append(path)
            except PermissionError as e:
                errors.append(f"Permission denied: {path}")
            except Exception as e:
                errors.append(f"Error restoring {path}: {str(e)}")
        
        # Update checkpoint state
        checkpoint.state = CheckpointState.ROLLED_BACK
        self._persist_checkpoint(checkpoint)
        
        return RollbackResult(
            success=len(errors) == 0,
            checkpoint_id=checkpoint_id,
            restored_paths=restored_paths,
            errors=errors,
        )
    
    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint:
        """
        Retrieve a checkpoint by ID.
        
        Args:
            checkpoint_id: Unique checkpoint identifier
            
        Returns:
            The checkpoint
            
        Raises:
            CheckpointNotFoundError: If checkpoint doesn't exist
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            raise CheckpointNotFoundError(
                f"Checkpoint not found: {checkpoint_id}"
            )
        
        return Checkpoint.from_json(checkpoint_file.read_text())
    
    def list_checkpoints(self, limit: int = 0) -> List[Checkpoint]:
        """
        List all checkpoints, newest first.
        
        Args:
            limit: Maximum number to return (0 = all)
            
        Returns:
            List of checkpoints sorted by timestamp (newest first)
        """
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                checkpoint = Checkpoint.from_json(checkpoint_file.read_text())
                checkpoints.append(checkpoint)
            except Exception:
                # Skip invalid checkpoint files
                continue
        
        # Sort by timestamp, newest first
        checkpoints.sort(key=lambda c: c.timestamp, reverse=True)
        
        if limit > 0:
            return checkpoints[:limit]
        
        return checkpoints
    
    def prune_checkpoints(
        self,
        max_age_seconds: Optional[int] = None,
        keep_count: Optional[int] = None,
    ) -> List[str]:
        """
        Manually prune old checkpoints.
        
        Args:
            max_age_seconds: Remove checkpoints older than this
            keep_count: Keep only this many checkpoints
            
        Returns:
            List of pruned checkpoint IDs
        """
        pruned = []
        checkpoints = self.list_checkpoints()
        
        if keep_count is not None:
            # Prune to keep only N
            for checkpoint in checkpoints[keep_count:]:
                self._delete_checkpoint(checkpoint.id)
                pruned.append(checkpoint.id)
        elif max_age_seconds is not None:
            # Prune by age
            cutoff = datetime.now()
            for checkpoint in checkpoints:
                age = (cutoff - checkpoint.timestamp).total_seconds()
                if age > max_age_seconds:
                    self._delete_checkpoint(checkpoint.id)
                    pruned.append(checkpoint.id)
        
        return pruned
    
    def _capture_state(self, paths: List[Path]) -> Dict[str, str]:
        """Capture current state of files."""
        snapshot = {}
        
        for path in paths:
            path_str = str(path)
            
            if not path.exists():
                snapshot[path_str] = self.NOT_EXISTS_MARKER
            elif self._is_binary(path):
                snapshot[path_str] = self.BINARY_MARKER
            else:
                try:
                    snapshot[path_str] = path.read_text()
                except Exception:
                    snapshot[path_str] = self.BINARY_MARKER
        
        return snapshot
    
    def _is_binary(self, path: Path) -> bool:
        """Check if file is binary."""
        try:
            chunk = path.read_bytes()[:8192]
            # Check for null bytes (common in binary files)
            return b'\x00' in chunk
        except Exception:
            return True
    
    def _get_current_sha(self) -> Optional[str]:
        """Get current git SHA if in a git repo."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.toolkit_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _persist_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk."""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint.id}.json"
        checkpoint_file.write_text(checkpoint.to_json())
    
    def _delete_checkpoint(self, checkpoint_id: str) -> None:
        """Delete a checkpoint file."""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
    
    def _auto_prune(self) -> None:
        """Automatically prune if we exceed max_checkpoints."""
        checkpoints = self.list_checkpoints()
        
        if len(checkpoints) > self.max_checkpoints:
            # Remove oldest checkpoints
            for checkpoint in checkpoints[self.max_checkpoints:]:
                self._delete_checkpoint(checkpoint.id)
