"""
Git Checkpoint Orchestrator

Manages git checkpoints for TDD workflow automation:
- Pre-implementation checkpoint creation
- Phase completion automated commits
- Rollback capability
- SKULL Rule #8 compliance

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class GitCheckpointOrchestrator:
    """
    Orchestrates git checkpoint creation and management for TDD workflows.
    
    Ensures SKULL Rule #8 compliance:
    "Always create git checkpoint before major refactoring"
    
    Features:
    - Pre-implementation checkpoints
    - Automated phase completion commits
    - Rollback to any checkpoint
    - Commit message generation with metadata
    - Branch preservation
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize GitCheckpointOrchestrator.
        
        Args:
            project_root: Path to project repository root
        """
        self.project_root = Path(project_root)
        self.checkpoints_file = self.project_root / ".cortex" / "checkpoints.json"
        self._ensure_checkpoints_file()
    
    def _ensure_checkpoints_file(self) -> None:
        """Ensure checkpoints tracking file exists."""
        self.checkpoints_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.checkpoints_file.exists():
            self.checkpoints_file.write_text(json.dumps({"checkpoints": []}, indent=2))
    
    def _run_git_command(self, args: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """
        Run git command and return success status and output.
        
        Args:
            args: Git command arguments
            capture_output: Whether to capture command output
            
        Returns:
            Tuple of (success, output/error_message)
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip() if capture_output else ""
            else:
                error_msg = result.stderr.strip() if capture_output else f"Command failed with code {result.returncode}"
                logger.error(f"Git command failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Exception running git command: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _get_current_branch(self) -> Optional[str]:
        """
        Get current git branch name.
        
        Returns:
            Branch name or None if failed
        """
        success, output = self._run_git_command(["branch", "--show-current"])
        return output if success else None
    
    def _get_current_commit_sha(self) -> Optional[str]:
        """
        Get current commit SHA.
        
        Returns:
            Commit SHA or None if failed
        """
        success, output = self._run_git_command(["rev-parse", "HEAD"])
        return output if success else None
    
    def _has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes.
        
        Returns:
            True if there are uncommitted changes
        """
        success, output = self._run_git_command(["status", "--porcelain"])
        return bool(output.strip()) if success else False
    
    def _load_checkpoints(self) -> List[Dict]:
        """Load checkpoints from tracking file."""
        try:
            data = json.loads(self.checkpoints_file.read_text())
            return data.get("checkpoints", [])
        except Exception as e:
            logger.error(f"Failed to load checkpoints: {e}")
            return []
    
    def _save_checkpoints(self, checkpoints: List[Dict]) -> None:
        """Save checkpoints to tracking file."""
        try:
            self.checkpoints_file.write_text(
                json.dumps({"checkpoints": checkpoints}, indent=2)
            )
        except Exception as e:
            logger.error(f"Failed to save checkpoints: {e}")
    
    def create_checkpoint(
        self, 
        session_id: str, 
        phase: str, 
        message: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a git checkpoint before starting work.
        
        Implements SKULL Rule #8: Pre-implementation checkpoint.
        
        Args:
            session_id: TDD session identifier
            phase: Current phase (RED, GREEN, REFACTOR)
            message: Optional custom message
            
        Returns:
            Checkpoint ID (commit SHA) or None if failed
        """
        logger.info(f"🔖 Creating checkpoint for session {session_id}, phase {phase}")
        
        # Check for uncommitted changes
        if self._has_uncommitted_changes():
            logger.warning("⚠️ Uncommitted changes detected. Stashing before checkpoint.")
            success, _ = self._run_git_command(["stash", "push", "-m", f"CORTEX auto-stash before {phase}"])
            if not success:
                logger.error("❌ Failed to stash changes")
                return None
        
        # Get current state
        current_branch = self._get_current_branch()
        current_sha = self._get_current_commit_sha()
        
        if not current_branch or not current_sha:
            logger.error("❌ Failed to get current git state")
            return None
        
        # Create checkpoint record
        checkpoint = {
            "checkpoint_id": current_sha,
            "session_id": session_id,
            "phase": phase,
            "branch": current_branch,
            "timestamp": datetime.now().isoformat(),
            "message": message or f"Pre-{phase} checkpoint"
        }
        
        # Save checkpoint
        checkpoints = self._load_checkpoints()
        checkpoints.append(checkpoint)
        self._save_checkpoints(checkpoints)
        
        logger.info(f"✅ Checkpoint created: {current_sha[:8]} on {current_branch}")
        return current_sha
    
    def commit_phase_completion(
        self,
        session_id: str,
        phase: str,
        metrics: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Commit phase completion with metadata.
        
        Args:
            session_id: TDD session identifier
            phase: Completed phase (RED, GREEN, REFACTOR)
            metrics: Optional metrics (duration, lines changed, etc.)
            
        Returns:
            Commit SHA or None if failed
        """
        logger.info(f"💾 Committing phase completion: {phase}")
        
        # Check if there are changes to commit
        if not self._has_uncommitted_changes():
            logger.info("ℹ️ No changes to commit")
            return self._get_current_commit_sha()
        
        # Generate commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg_lines = [
            f"CORTEX TDD: {phase} phase complete",
            "",
            f"Session: {session_id}",
            f"Phase: {phase}",
            f"Timestamp: {timestamp}"
        ]
        
        if metrics:
            commit_msg_lines.append("")
            commit_msg_lines.append("Metrics:")
            for key, value in metrics.items():
                commit_msg_lines.append(f"  {key}: {value}")
        
        commit_msg = "\n".join(commit_msg_lines)
        
        # Stage all changes
        success, _ = self._run_git_command(["add", "-A"])
        if not success:
            logger.error("❌ Failed to stage changes")
            return None
        
        # Commit changes
        success, output = self._run_git_command(["commit", "-m", commit_msg])
        if not success:
            logger.error(f"❌ Failed to commit: {output}")
            return None
        
        # Get new commit SHA
        commit_sha = self._get_current_commit_sha()
        logger.info(f"✅ Phase committed: {commit_sha[:8] if commit_sha else 'unknown'}")
        
        return commit_sha
    
    def rollback_to_checkpoint(
        self,
        session_id: str,
        checkpoint_id: Optional[str] = None
    ) -> bool:
        """
        Rollback to a specific checkpoint.
        
        Args:
            session_id: TDD session identifier
            checkpoint_id: Checkpoint ID (commit SHA). If None, uses last checkpoint for session.
            
        Returns:
            True if rollback successful
        """
        logger.info(f"🔄 Rolling back session {session_id}")
        
        # Find checkpoint
        checkpoints = self._load_checkpoints()
        session_checkpoints = [
            cp for cp in checkpoints 
            if cp["session_id"] == session_id
        ]
        
        if not session_checkpoints:
            logger.error(f"❌ No checkpoints found for session {session_id}")
            return False
        
        # Use specified checkpoint or last one
        if checkpoint_id:
            checkpoint = next(
                (cp for cp in session_checkpoints if cp["checkpoint_id"] == checkpoint_id),
                None
            )
            if not checkpoint:
                logger.error(f"❌ Checkpoint {checkpoint_id} not found")
                return False
        else:
            checkpoint = session_checkpoints[-1]
            logger.info(f"ℹ️ Using last checkpoint: {checkpoint['checkpoint_id'][:8]}")
        
        # Confirm rollback
        target_sha = checkpoint["checkpoint_id"]
        logger.warning(f"⚠️ Rolling back to {target_sha[:8]}")
        
        # Reset to checkpoint
        success, output = self._run_git_command(["reset", "--hard", target_sha])
        if not success:
            logger.error(f"❌ Rollback failed: {output}")
            return False
        
        logger.info(f"✅ Rolled back to checkpoint {target_sha[:8]}")
        return True
    
    def list_checkpoints(self, session_id: Optional[str] = None) -> List[Dict]:
        """
        List all checkpoints, optionally filtered by session.
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            List of checkpoint dictionaries
        """
        checkpoints = self._load_checkpoints()
        
        if session_id:
            checkpoints = [
                cp for cp in checkpoints 
                if cp["session_id"] == session_id
            ]
        
        return checkpoints
    
    def validate_skull_rule_8(self, session_id: str) -> bool:
        """
        Validate SKULL Rule #8 compliance for a session.
        
        Rule #8: "Always create git checkpoint before major refactoring"
        
        Args:
            session_id: TDD session identifier
            
        Returns:
            True if rule is satisfied (checkpoint exists)
        """
        checkpoints = self.list_checkpoints(session_id)
        has_checkpoint = len(checkpoints) > 0
        
        if has_checkpoint:
            logger.info(f"✅ SKULL Rule #8: Checkpoint exists for session {session_id}")
        else:
            logger.error(f"❌ SKULL Rule #8: No checkpoint for session {session_id}")
        
        return has_checkpoint
