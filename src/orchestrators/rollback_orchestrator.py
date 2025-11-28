"""
Rollback Orchestrator - Foundation for checkpoint rollback operations.

Provides base capabilities for rolling back work to previous checkpoints created
by PhaseCheckpointManager during TDD workflows.

INCREMENT 11: Rollback Orchestrator Foundation
- Checkpoint listing from PhaseCheckpointManager
- Checkpoint validation before rollback
- Checkpoint summary formatting
- Foundation for command parsing (INCREMENT 12)

INCREMENT 13: Safety Checks with User Confirmation
- Uncommitted changes detection
- Merge conflict detection
- User confirmation with change preview
- Dry-run mode
- Forced rollback bypass

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Status: GREEN PHASE (implementing safety checks)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess
import re

from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager


# INCREMENT 13: Safety check message constants
SAFETY_MSG_UNCOMMITTED = "Uncommitted changes detected"
SAFETY_MSG_UNCOMMITTED_DETAILS = (
    "The following files have uncommitted changes:\n{files}\n\n"
    "Commit or stash changes before rollback."
)
SAFETY_MSG_MERGE = "Merge in progress - resolve conflicts first"
SAFETY_MSG_MERGE_DETAILS = "Cannot rollback during merge. Complete or abort merge before rollback."

# Rollback execution message constants
ROLLBACK_MSG_DRY_RUN = "Would rollback to {checkpoint_id} (dry-run mode)"
ROLLBACK_MSG_FORCED = "Forced rollback to {checkpoint_id} completed"
ROLLBACK_MSG_SUCCESS = "Rollback to {checkpoint_id} completed successfully"
ROLLBACK_MSG_CANCELLED = "Rollback cancelled by user"

# Git error constants
GIT_ERROR_DIFF = "Error: Could not generate diff"
GIT_ERROR_RESET = "Git reset failed: {error}"


class RollbackOrchestrator:
    """
    Orchestrates rollback operations to previous checkpoints.
    
    Uses PhaseCheckpointManager for checkpoint metadata and provides
    user-friendly rollback commands with validation and safety checks.
    """
    
    def __init__(self, cortex_dir: Optional[Path] = None, project_root: Optional[Path] = None):
        """
        Initialize rollback orchestrator.
        
        Args:
            cortex_dir: Path to CORTEX directory (optional, auto-detect if not provided)
            project_root: Path to project root (optional, used for git operations)
        """
        if cortex_dir is None:
            # Auto-detect CORTEX directory
            self.cortex_dir = Path(__file__).parent.parent.parent
        else:
            self.cortex_dir = Path(cortex_dir)
        
        if project_root is None:
            # Use CORTEX directory as default
            self.project_root = self.cortex_dir
        else:
            self.project_root = Path(project_root)
        self.checkpoint_manager = PhaseCheckpointManager(cortex_root=cortex_dir)
    
    def list_checkpoints(self, session_id: str) -> List[Dict[str, Any]]:
        """
        List all checkpoints for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of checkpoint metadata dictionaries
        """
        return self.checkpoint_manager.list_checkpoints(session_id=session_id)
    
    def validate_checkpoint(self, session_id: str, checkpoint_id: str) -> bool:
        """
        Validate that a checkpoint exists.
        
        Args:
            session_id: Session identifier
            checkpoint_id: Checkpoint identifier to validate
            
        Returns:
            True if checkpoint exists, False otherwise
            
        Example:
            >>> orchestrator = RollbackOrchestrator(cortex_dir=Path("/project"))
            >>> orchestrator.validate_checkpoint("session-1", "checkpoint-abc123")
            True
        """
        checkpoints = self.checkpoint_manager.list_checkpoints(session_id=session_id)
        
        # Handle empty checkpoint list gracefully
        if not checkpoints:
            return False
            
        return any(cp.get('checkpoint_id') == checkpoint_id for cp in checkpoints)
    
    def format_checkpoint_summary(self, session_id: str, checkpoint_id: str) -> str:
        """
        Format checkpoint metadata as human-readable summary.
        
        Searches PhaseCheckpointManager checkpoint list to find matching checkpoint_id,
        then formats phase, commit_sha, created_at, and metrics into readable string.
        
        Args:
            session_id: Session identifier
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Formatted summary string showing checkpoint details
            
        Example:
            >>> orchestrator = RollbackOrchestrator(cortex_dir=Path("/project"))
            >>> print(orchestrator.format_checkpoint_summary("session-1", "checkpoint-abc123"))
            Checkpoint: checkpoint-abc123
            Session: session-1
            Phase: implementation
            Commit SHA: abc1234
            Created: 2025-11-27T14:30:22
            Metrics:
              tests: 10
              coverage: 85.5
        """
        checkpoints = self.checkpoint_manager.list_checkpoints(session_id=session_id)
        
        # Find checkpoint by ID
        metadata = None
        for cp in checkpoints:
            if cp.get('checkpoint_id') == checkpoint_id:
                metadata = cp
                break
        
        if not metadata:
            return f"Checkpoint '{checkpoint_id}' not found"
        
        lines = []
        lines.append(f"Checkpoint: {checkpoint_id}")
        lines.append(f"Session: {session_id}")
        lines.append(f"Phase: {metadata.get('phase', 'unknown')}")
        
        # Handle commit_sha gracefully (may be None)
        commit_sha = metadata.get('commit_sha')
        if commit_sha:
            lines.append(f"Commit SHA: {commit_sha[:7]}")
        else:
            lines.append("Commit SHA: unknown")
            
        lines.append(f"Created: {metadata.get('created_at', 'unknown')}")
        
        # Format metrics if present
        metrics = metadata.get('metrics')
        if metrics:
            lines.append("Metrics:")
            for key, value in metrics.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    # INCREMENT 13: Safety Checks and User Confirmation
    
    def _get_git_status(self) -> Dict[str, Any]:
        """
        Get git repository status.
        
        Returns:
            Dict with keys:
            - clean (bool): Whether working tree is clean
            - uncommitted_changes (list): List of modified files
            - merge_in_progress (bool): Whether merge is in progress
        """
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            uncommitted = []
            if result.stdout.strip():
                # Parse git status output
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        # Format: "XY filename" where XY are status codes
                        filename = line[3:].strip()
                        uncommitted.append(filename)
            
            # Check for merge in progress
            merge_head = self.project_root / '.git' / 'MERGE_HEAD'
            merge_in_progress = merge_head.exists()
            
            return {
                'clean': len(uncommitted) == 0 and not merge_in_progress,
                'uncommitted_changes': uncommitted,
                'merge_in_progress': merge_in_progress
            }
            
        except subprocess.CalledProcessError:
            # Git command failed - assume unsafe
            return {
                'clean': False,
                'uncommitted_changes': [],
                'merge_in_progress': False
            }
    
    def check_rollback_safety(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Check if rollback is safe to perform.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            
        Returns:
            Dict with keys:
            - safe (bool): Whether rollback is safe
            - warning (str|None): Warning message if unsafe
            - details (str|None): Detailed information
        """
        git_status = self._get_git_status()
        
        # Check for uncommitted changes
        if git_status['uncommitted_changes']:
            files = '\n'.join(f"  - {f}" for f in git_status['uncommitted_changes'])
            return {
                'safe': False,
                'warning': SAFETY_MSG_UNCOMMITTED,
                'details': SAFETY_MSG_UNCOMMITTED_DETAILS.format(files=files)
            }
        
        # Check for merge in progress
        if git_status['merge_in_progress']:
            return {
                'safe': False,
                'warning': SAFETY_MSG_MERGE,
                'details': SAFETY_MSG_MERGE_DETAILS
            }
        
        # Safe to proceed
        return {
            'safe': True,
            'warning': None,
            'details': None
        }
    
    def _get_git_diff(self, checkpoint_id: str) -> str:
        """
        Get git diff between current state and checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to compare against
            
        Returns:
            Git diff output as string
        """
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD', checkpoint_id],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return GIT_ERROR_DIFF
    
    def confirm_rollback(self, checkpoint_id: str, show_diff: bool = False) -> Dict[str, Any]:
        """
        Prompt user for rollback confirmation.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            show_diff: Whether to show git diff preview
            
        Returns:
            Dict with keys:
            - confirmed (bool): Whether user confirmed
            - message (str): Confirmation/cancellation message
        """
        if show_diff:
            diff = self._get_git_diff(checkpoint_id)
            print(f"\n{'='*60}")
            print(f"ROLLBACK PREVIEW - Changes to be discarded:")
            print(f"{'='*60}")
            print(diff[:1000])  # Show first 1000 chars
            if len(diff) > 1000:
                print(f"\n... ({len(diff) - 1000} more characters)")
            print(f"{'='*60}\n")
        
        response = input(f"Rollback to '{checkpoint_id}'? (yes/no): ").strip().lower()
        
        if response == 'yes':
            return {
                'confirmed': True,
                'message': 'Rollback confirmed'
            }
        else:
            return {
                'confirmed': False,
                'message': ROLLBACK_MSG_CANCELLED
            }
    
    def execute_rollback(self, checkpoint_id: str, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Execute rollback to checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            dry_run: If True, show preview without executing
            force: If True, bypass safety checks and confirmation
            
        Returns:
            Dict with keys:
            - executed (bool): Whether rollback was executed
            - forced (bool): Whether rollback was forced
            - preview (str|None): Preview if dry_run mode
            - message (str): Result message
        """
        # Dry-run mode: show preview only
        if dry_run:
            preview = self._get_git_diff(checkpoint_id)
            return {
                'executed': False,
                'forced': False,
                'preview': preview,
                'message': ROLLBACK_MSG_DRY_RUN.format(checkpoint_id=checkpoint_id)
            }
        
        # Forced mode: skip safety checks
        if force:
            result = self._execute_git_reset(checkpoint_id)
            return {
                'executed': True,
                'forced': True,
                'preview': None,
                'message': ROLLBACK_MSG_FORCED.format(checkpoint_id=checkpoint_id)
            }
        
        # Normal mode: perform safety checks and get confirmation
        safety = self.check_rollback_safety(checkpoint_id)
        if not safety['safe']:
            return {
                'executed': False,
                'forced': False,
                'preview': None,
                'message': f"Safety check failed: {safety['warning']}\n{safety['details']}"
            }
        
        confirmation = self.confirm_rollback(checkpoint_id, show_diff=True)
        if not confirmation['confirmed']:
            return {
                'executed': False,
                'forced': False,
                'preview': None,
                'message': confirmation['message']
            }
        
        result = self._execute_git_reset(checkpoint_id)
        return {
            'executed': True,
            'forced': False,
            'preview': None,
            'message': ROLLBACK_MSG_SUCCESS.format(checkpoint_id=checkpoint_id)
        }
    
    def _execute_git_reset(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Execute git reset to checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to reset to
            
        Returns:
            Dict with success status
        """
        try:
            subprocess.run(
                ['git', 'reset', '--hard', checkpoint_id],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return {'success': True}
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': GIT_ERROR_RESET.format(error=str(e))
            }
