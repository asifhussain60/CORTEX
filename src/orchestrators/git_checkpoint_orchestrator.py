"""
Git Checkpoint Orchestrator

Manages git-based checkpoints for TDD workflow phases.
Creates lightweight commits at RED/GREEN/REFACTOR boundaries.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import uuid


class GitCheckpointOrchestrator:
    """
    Git checkpoint orchestrator for TDD workflow.
    
    Creates automatic git commits at phase boundaries to enable:
    - Rollback to previous phase
    - Progress tracking
    - Audit trail of TDD workflow
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize git checkpoint orchestrator.
        
        Args:
            project_root: Root directory of git repository
        """
        self.project_root = Path(project_root)
        self.checkpoint_prefix = "CORTEX-TDD"
    
    def create_checkpoint(
        self,
        session_id: str,
        checkpoint_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a git checkpoint.
        
        Args:
            session_id: TDD session identifier
            checkpoint_type: Type of checkpoint (e.g., "phase-RED", "phase-GREEN")
            message: Checkpoint message
            metadata: Optional metadata dict
            
        Returns:
            Dict with success, checkpoint_id, commit_sha
        """
        try:
            checkpoint_id = f"ckpt-{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Format commit message
            commit_message = (
                f"{self.checkpoint_prefix}: {checkpoint_type}\n\n"
                f"Session: {session_id}\n"
                f"Checkpoint: {checkpoint_id}\n"
                f"Message: {message}\n"
                f"Timestamp: {timestamp}"
            )
            
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            # Create commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get commit SHA
            sha_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            commit_sha = sha_result.stdout.strip()
            
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "commit_sha": commit_sha,
                "session_id": session_id,
                "checkpoint_type": checkpoint_type,
                "timestamp": timestamp
            }
        
        except subprocess.CalledProcessError as e:
            # Handle case where there are no changes to commit
            if "nothing to commit" in str(e.stderr):
                return {
                    "success": True,
                    "checkpoint_id": checkpoint_id,
                    "commit_sha": None,
                    "message": "No changes to commit",
                    "session_id": session_id
                }
            
            return {
                "success": False,
                "error": str(e),
                "checkpoint_id": checkpoint_id
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "checkpoint_id": None
            }
    
    def list_checkpoints(self, session_id: Optional[str] = None) -> list:
        """
        List git checkpoints.
        
        Args:
            session_id: Optional session filter
            
        Returns:
            List of checkpoint dicts
        """
        try:
            # Get commits with checkpoint prefix
            result = subprocess.run(
                [
                    "git", "log",
                    f"--grep={self.checkpoint_prefix}",
                    "--pretty=format:%H|%s|%ai"
                ],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            checkpoints = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('|', 2)
                if len(parts) != 3:
                    continue
                
                sha, subject, timestamp = parts
                
                # Filter by session if provided
                if session_id and session_id not in subject:
                    continue
                
                checkpoints.append({
                    "commit_sha": sha,
                    "message": subject,
                    "timestamp": timestamp
                })
            
            return checkpoints
        
        except Exception:
            return []
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            
        Returns:
            Dict with success status
        """
        try:
            # Find commit SHA for checkpoint
            result = subprocess.run(
                [
                    "git", "log",
                    f"--grep={checkpoint_id}",
                    "--pretty=format:%H",
                    "-1"
                ],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            commit_sha = result.stdout.strip()
            if not commit_sha:
                return {
                    "success": False,
                    "error": f"Checkpoint not found: {checkpoint_id}"
                }
            
            # Reset to checkpoint
            subprocess.run(
                ["git", "reset", "--hard", commit_sha],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "commit_sha": commit_sha
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
