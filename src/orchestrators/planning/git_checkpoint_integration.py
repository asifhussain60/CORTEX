"""
CORTEX 4.0 Git Checkpoint Integration - Rollback Safety System

Purpose: Git checkpoint management for safe rollback at phase boundaries during
         plan execution. Provides automatic checkpoint creation, restoration,
         and cleanup for execution error recovery.
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19 (Week 8 Day 3)

Key Features:
- Automatic git checkpoint creation at phase boundaries
- Checkpoint restoration for rollback on errors
- Checkpoint history tracking and management
- Clean workspace validation before checkpoints
- Stash management for uncommitted changes
- Checkpoint cleanup after successful execution

Architecture:
- GitCheckpointManager: Main checkpoint coordinator
- CheckpointMetadata: Checkpoint information and metadata
- WorkspaceValidator: Ensures clean git state
- StashManager: Handles uncommitted changes

Integration Points:
- PlanExecutor: Execution engine (checkpoint triggers)
- PhaseManagerIntegration: Phase transition coordination
- BaseOrchestrator: Orchestrator lifecycle management
"""

import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Domain Models
# ============================================================================

class CheckpointType(Enum):
    """Checkpoint types."""
    INITIAL = "initial"           # Before execution starts
    PHASE = "phase"               # After phase completion
    FINAL = "final"               # After successful execution
    MANUAL = "manual"             # User-triggered checkpoint


@dataclass
class CheckpointMetadata:
    """Checkpoint metadata."""
    checkpoint_id: str
    checkpoint_type: CheckpointType
    phase_name: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    commit_sha: Optional[str] = None
    branch_name: Optional[str] = None
    message: str = ""
    files_changed: int = 0
    stash_ref: Optional[str] = None  # Stash reference if uncommitted changes


# ============================================================================
# Git Checkpoint Manager
# ============================================================================

class GitCheckpointManager:
    """
    Git checkpoint manager for rollback safety.
    
    Responsibilities:
    - Create checkpoints at phase boundaries
    - Validate git workspace state
    - Stash uncommitted changes
    - Restore checkpoints on errors
    - Manage checkpoint history
    - Clean up checkpoints after success
    """
    
    def __init__(
        self,
        workspace_root: Path,
        checkpoint_prefix: str = "cortex-checkpoint",
        logger_instance: Optional[logging.Logger] = None
    ):
        """
        Initialize git checkpoint manager.
        
        Args:
            workspace_root: User workspace root directory (must be git repo)
            checkpoint_prefix: Prefix for checkpoint commit messages
            logger_instance: Optional logger instance
        """
        self.workspace_root = Path(workspace_root)
        self.checkpoint_prefix = checkpoint_prefix
        self.logger = logger_instance or logger
        
        # Checkpoint tracking
        self.checkpoints: List[CheckpointMetadata] = []
        self.checkpoint_file = self.workspace_root / ".cortex" / "checkpoints.json"
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate git repo
        if not self._is_git_repo():
            self.logger.warning("⚠️  Workspace is not a git repository - checkpoints disabled")
    
    def create_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        phase_name: Optional[str] = None,
        message: Optional[str] = None
    ) -> Optional[CheckpointMetadata]:
        """
        Create git checkpoint.
        
        Workflow:
        1. Validate git workspace (clean or stash changes)
        2. Create commit with checkpoint message
        3. Record checkpoint metadata
        4. Persist checkpoint history
        
        Args:
            checkpoint_type: Type of checkpoint
            phase_name: Phase name (if phase checkpoint)
            message: Optional checkpoint message
        
        Returns:
            CheckpointMetadata or None if failed
        """
        if not self._is_git_repo():
            self.logger.warning("⚠️  Cannot create checkpoint: not a git repository")
            return None
        
        try:
            self.logger.info(f"📍 Creating checkpoint: {checkpoint_type.value}")
            
            # Validate workspace
            is_clean, stash_ref = self._ensure_clean_workspace()
            
            # Generate checkpoint ID and message
            checkpoint_id = f"{self.checkpoint_prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            commit_message = message or self._generate_checkpoint_message(checkpoint_type, phase_name)
            
            # Get current branch and commit
            branch_name = self._get_current_branch()
            
            # Create commit (if changes exist)
            files_changed = self._count_changed_files()
            if files_changed > 0 or not is_clean:
                commit_sha = self._create_commit(commit_message)
                if not commit_sha:
                    self.logger.error("❌ Failed to create checkpoint commit")
                    return None
            else:
                # No changes - use current commit
                commit_sha = self._get_current_commit()
            
            # Create checkpoint metadata
            checkpoint = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                checkpoint_type=checkpoint_type,
                phase_name=phase_name,
                commit_sha=commit_sha,
                branch_name=branch_name,
                message=commit_message,
                files_changed=files_changed,
                stash_ref=stash_ref
            )
            
            # Store checkpoint
            self.checkpoints.append(checkpoint)
            self._persist_checkpoints()
            
            self.logger.info(f"✅ Checkpoint created: {checkpoint_id} ({commit_sha[:8]})")
            return checkpoint
        
        except Exception as e:
            self.logger.error(f"❌ Failed to create checkpoint: {e}", exc_info=True)
            return None
    
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore workspace to specific checkpoint.
        
        Workflow:
        1. Find checkpoint by ID
        2. Stash any uncommitted changes
        3. Reset to checkpoint commit
        4. Restore stashed changes (if any from checkpoint)
        
        Args:
            checkpoint_id: Checkpoint ID to restore
        
        Returns:
            True if restored successfully, False otherwise
        """
        if not self._is_git_repo():
            self.logger.warning("⚠️  Cannot restore checkpoint: not a git repository")
            return False
        
        # Find checkpoint
        checkpoint = self._find_checkpoint(checkpoint_id)
        if not checkpoint:
            self.logger.error(f"❌ Checkpoint not found: {checkpoint_id}")
            return False
        
        try:
            self.logger.info(f"🔄 Restoring checkpoint: {checkpoint_id}")
            
            # Stash current changes
            self._ensure_clean_workspace()
            
            # Reset to checkpoint commit
            if not self._reset_to_commit(checkpoint.commit_sha):
                self.logger.error(f"❌ Failed to reset to commit: {checkpoint.commit_sha}")
                return False
            
            # Restore checkpoint stash (if any)
            if checkpoint.stash_ref:
                if not self._pop_stash(checkpoint.stash_ref):
                    self.logger.warning(f"⚠️  Failed to restore stash: {checkpoint.stash_ref}")
            
            self.logger.info(f"✅ Checkpoint restored: {checkpoint_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to restore checkpoint: {e}", exc_info=True)
            return False
    
    def cleanup_checkpoints(self, keep_final: bool = True) -> int:
        """
        Clean up checkpoint commits after successful execution.
        
        Args:
            keep_final: Keep final checkpoint (default: True)
        
        Returns:
            Number of checkpoints cleaned up
        """
        if not self._is_git_repo():
            return 0
        
        cleaned = 0
        checkpoints_to_remove = []
        
        for checkpoint in self.checkpoints:
            # Keep final checkpoint if requested
            if keep_final and checkpoint.checkpoint_type == CheckpointType.FINAL:
                continue
            
            # Remove checkpoint-specific commits (optional - can be noisy in git history)
            # For now, just remove from tracking
            checkpoints_to_remove.append(checkpoint)
            cleaned += 1
        
        # Remove from tracking
        for checkpoint in checkpoints_to_remove:
            self.checkpoints.remove(checkpoint)
        
        # Persist updated list
        self._persist_checkpoints()
        
        self.logger.info(f"🗑️  Cleaned up {cleaned} checkpoints")
        return cleaned
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """
        Get checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint ID
        
        Returns:
            CheckpointMetadata or None if not found
        """
        return self._find_checkpoint(checkpoint_id)
    
    def get_all_checkpoints(self) -> List[CheckpointMetadata]:
        """
        Get all checkpoints.
        
        Returns:
            List of CheckpointMetadata
        """
        return self.checkpoints.copy()
    
    def _is_git_repo(self) -> bool:
        """Check if workspace is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _ensure_clean_workspace(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure workspace is clean (stash uncommitted changes if needed).
        
        Returns:
            (is_clean, stash_ref): Clean status and stash reference
        """
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return False, None
            
            if not result.stdout.strip():
                # Workspace is clean
                return True, None
            
            # Stash uncommitted changes
            stash_message = f"CORTEX checkpoint stash - {datetime.now().isoformat()}"
            stash_result = subprocess.run(
                ["git", "stash", "push", "-m", stash_message],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if stash_result.returncode != 0:
                self.logger.error(f"❌ Failed to stash changes: {stash_result.stderr}")
                return False, None
            
            # Get stash reference
            stash_ref = self._get_latest_stash_ref()
            self.logger.info(f"💾 Stashed uncommitted changes: {stash_ref}")
            
            return True, stash_ref
        
        except Exception as e:
            self.logger.error(f"❌ Failed to ensure clean workspace: {e}", exc_info=True)
            return False, None
    
    def _create_commit(self, message: str) -> Optional[str]:
        """Create git commit and return commit SHA."""
        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.workspace_root,
                capture_output=True,
                timeout=10
            )
            
            # Create commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            # Get commit SHA
            return self._get_current_commit()
        
        except Exception as e:
            self.logger.error(f"❌ Failed to create commit: {e}", exc_info=True)
            return None
    
    def _get_current_commit(self) -> Optional[str]:
        """Get current commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def _get_current_branch(self) -> Optional[str]:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def _count_changed_files(self) -> int:
        """Count changed files in workspace."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return len([line for line in result.stdout.split('\n') if line.strip()])
            return 0
        except Exception:
            return 0
    
    def _reset_to_commit(self, commit_sha: str) -> bool:
        """Reset workspace to specific commit."""
        try:
            result = subprocess.run(
                ["git", "reset", "--hard", commit_sha],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"❌ Failed to reset to commit: {e}", exc_info=True)
            return False
    
    def _get_latest_stash_ref(self) -> Optional[str]:
        """Get latest stash reference."""
        try:
            result = subprocess.run(
                ["git", "stash", "list", "-1"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Format: stash@{0}: ...
                return result.stdout.split(':')[0].strip()
            return None
        except Exception:
            return None
    
    def _pop_stash(self, stash_ref: str) -> bool:
        """Pop specific stash."""
        try:
            result = subprocess.run(
                ["git", "stash", "pop", stash_ref],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"❌ Failed to pop stash: {e}", exc_info=True)
            return False
    
    def _generate_checkpoint_message(self, checkpoint_type: CheckpointType, phase_name: Optional[str]) -> str:
        """Generate checkpoint commit message."""
        if phase_name:
            return f"{self.checkpoint_prefix}: After phase {phase_name} ({checkpoint_type.value})"
        return f"{self.checkpoint_prefix}: {checkpoint_type.value} checkpoint"
    
    def _find_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Find checkpoint by ID."""
        for checkpoint in self.checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                return checkpoint
        return None
    
    def _persist_checkpoints(self) -> None:
        """Persist checkpoint history to disk."""
        try:
            data = {
                "checkpoints": [
                    {
                        "checkpoint_id": c.checkpoint_id,
                        "checkpoint_type": c.checkpoint_type.value,
                        "phase_name": c.phase_name,
                        "timestamp": c.timestamp.isoformat(),
                        "commit_sha": c.commit_sha,
                        "branch_name": c.branch_name,
                        "message": c.message,
                        "files_changed": c.files_changed,
                        "stash_ref": c.stash_ref
                    }
                    for c in self.checkpoints
                ]
            }
            
            self.checkpoint_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f"❌ Failed to persist checkpoints: {e}", exc_info=True)
    
    def restore_checkpoint_history(self) -> int:
        """
        Restore checkpoint history from disk.
        
        Returns:
            Number of checkpoints restored
        """
        if not self.checkpoint_file.exists():
            return 0
        
        try:
            data = json.loads(self.checkpoint_file.read_text())
            
            self.checkpoints = [
                CheckpointMetadata(
                    checkpoint_id=c["checkpoint_id"],
                    checkpoint_type=CheckpointType(c["checkpoint_type"]),
                    phase_name=c.get("phase_name"),
                    timestamp=datetime.fromisoformat(c["timestamp"]),
                    commit_sha=c.get("commit_sha"),
                    branch_name=c.get("branch_name"),
                    message=c.get("message", ""),
                    files_changed=c.get("files_changed", 0),
                    stash_ref=c.get("stash_ref")
                )
                for c in data.get("checkpoints", [])
            ]
            
            self.logger.info(f"✅ Restored {len(self.checkpoints)} checkpoints")
            return len(self.checkpoints)
        
        except Exception as e:
            self.logger.error(f"❌ Failed to restore checkpoint history: {e}", exc_info=True)
            return 0
