"""
Git Checkpoint Orchestrator

Manages git checkpoints for TDD workflow automation:
- Pre-implementation checkpoint creation
- Phase completion automated commits
- Rollback capability
- SKULL Rule #8 compliance
- Auto-checkpoint triggers (before/after operations)
- Retention policy enforcement (30-day, 50-count limits)
- Dirty state detection and user consent workflow

Version: 2.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import json
import logging
import yaml

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
    - Auto-checkpoint triggers (config-driven)
    - Retention policy enforcement
    - Dirty state detection and consent workflow
    """
    
    def __init__(self, project_root: Path, brain_path: Optional[Path] = None):
        """
        Initialize GitCheckpointOrchestrator.
        
        Args:
            project_root: Path to project repository root
            brain_path: Optional path to CORTEX brain (for config loading)
        """
        self.project_root = Path(project_root)
        self.brain_path = Path(brain_path) if brain_path else self.project_root / "cortex-brain"
        self.checkpoints_file = self.project_root / ".cortex" / "checkpoints.json"
        self.config = self._load_config()
        self._ensure_checkpoints_file()
    
    def _load_config(self) -> Dict:
        """Load git checkpoint configuration from brain."""
        config_file = self.brain_path / "git-checkpoint-rules.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint config: {e}")
        
        # Default config if file not found
        return {
            "auto_checkpoint": {
                "enabled": True,
                "triggers": {
                    "before_implementation": True,
                    "after_implementation": True,
                    "before_refactoring": True,
                    "after_refactoring": True
                }
            },
            "retention": {
                "max_age_days": 30,
                "max_count": 50,
                "preserve_named": True
            },
            "naming": {
                "format": "{type}-{timestamp}",
                "timestamp_format": "%Y%m%d-%H%M%S"
            },
            "safety": {
                "detect_uncommitted_changes": True,
                "warn_on_uncommitted": True,
                "require_confirmation": True
            }
        }
    
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

    def detect_dirty_state(self) -> Dict[str, any]:
        """
        Detect if repository has uncommitted changes or is in unstable state.
        
        Returns:
            Dict with dirty state information:
            {
                "is_dirty": bool,
                "modified_files": List[str],
                "staged_files": List[str],
                "untracked_files": List[str],
                "merge_in_progress": bool,
                "rebase_in_progress": bool,
                "has_conflicts": bool
            }
        """
        # Check git status
        success, status_output = self._run_git_command(["status", "--porcelain"])
        if not success:
            logger.error("Failed to check git status")
            return {"is_dirty": False, "error": "Failed to check status"}
        
        # Parse status output
        modified_files = []
        staged_files = []
        untracked_files = []
        
        for line in status_output.split('\n'):
            if not line.strip():
                continue
            status_code = line[:2]
            filepath = line[3:].strip()
            
            if status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                staged_files.append(filepath)
            if status_code[1] in ['M', 'D']:
                modified_files.append(filepath)
            if status_code == '??':
                untracked_files.append(filepath)
        
        # Check for merge/rebase in progress
        git_dir = self.project_root / ".git"
        merge_in_progress = (git_dir / "MERGE_HEAD").exists()
        rebase_in_progress = (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()
        cherry_pick_in_progress = (git_dir / "CHERRY_PICK_HEAD").exists()
        
        # Check for conflicts
        has_conflicts = any('U' in line[:2] for line in status_output.split('\n') if line.strip())
        
        is_dirty = bool(modified_files or staged_files or merge_in_progress or rebase_in_progress)
        
        return {
            "is_dirty": is_dirty,
            "modified_files": modified_files,
            "staged_files": staged_files,
            "untracked_files": untracked_files,
            "merge_in_progress": merge_in_progress,
            "rebase_in_progress": rebase_in_progress,
            "cherry_pick_in_progress": cherry_pick_in_progress,
            "has_conflicts": has_conflicts
        }
    
    def prompt_user_consent(self, dirty_state: Dict) -> str:
        """
        Prompt user for consent to proceed with dirty state.
        
        Args:
            dirty_state: Output from detect_dirty_state()
            
        Returns:
            User choice: "commit", "stash", "proceed", "cancel"
        """
        print("\n⚠️  DIRTY STATE DETECTED - USER CONSENT REQUIRED\n")
        
        if dirty_state.get("modified_files"):
            print(f"Modified files ({len(dirty_state['modified_files'])}):")
            for f in dirty_state["modified_files"][:5]:
                print(f"  - {f}")
            if len(dirty_state["modified_files"]) > 5:
                print(f"  ... and {len(dirty_state['modified_files']) - 5} more")
        
        if dirty_state.get("staged_files"):
            print(f"\nStaged files ({len(dirty_state['staged_files'])}):")
            for f in dirty_state["staged_files"][:5]:
                print(f"  - {f}")
            if len(dirty_state["staged_files"]) > 5:
                print(f"  ... and {len(dirty_state['staged_files']) - 5} more")
        
        if dirty_state.get("untracked_files"):
            print(f"\nUntracked files ({len(dirty_state['untracked_files'])}):")
            for f in dirty_state["untracked_files"][:3]:
                print(f"  - {f}")
            if len(dirty_state["untracked_files"]) > 3:
                print(f"  ... and {len(dirty_state['untracked_files']) - 3} more")
        
        print("\nOPTIONS:")
        print("  A) Commit your changes first (RECOMMENDED)")
        print("  B) Stash changes and continue")
        print("  C) Proceed anyway (CORTEX will checkpoint current state)")
        print("  X) Cancel operation")
        
        choice = input("\nYour choice (A/B/C/X): ").strip().upper()
        
        choice_map = {
            "A": "commit",
            "B": "stash",
            "C": "proceed",
            "X": "cancel"
        }
        
        return choice_map.get(choice, "cancel")
    
    def check_dirty_state_and_consent(self, operation: str) -> Tuple[bool, Optional[str]]:
        """
        Check for dirty state and get user consent if needed.
        
        Args:
            operation: Operation being performed (for logging)
            
        Returns:
            Tuple of (can_proceed, checkpoint_id)
            - can_proceed: True if operation can proceed
            - checkpoint_id: Pre-work checkpoint ID if created
        """
        if not self.config.get("safety", {}).get("detect_uncommitted_changes", True):
            return True, None
        
        dirty_state = self.detect_dirty_state()
        
        # Block if conflicts or merge/rebase in progress
        if dirty_state.get("has_conflicts"):
            logger.error("❌ BLOCKED: Merge conflicts detected. Resolve conflicts first.")
            return False, None
        
        if dirty_state.get("merge_in_progress"):
            logger.error("❌ BLOCKED: Merge in progress. Complete or abort merge first.")
            return False, None
        
        if dirty_state.get("rebase_in_progress"):
            logger.error("❌ BLOCKED: Rebase in progress. Complete or abort rebase first.")
            return False, None
        
        # Warn if dirty (not blocked)
        if not dirty_state.get("is_dirty"):
            logger.info("✅ Clean working tree. Proceeding with operation.")
            return True, None
        
        if not self.config.get("safety", {}).get("warn_on_uncommitted", True):
            return True, None
        
        # Get user consent
        choice = self.prompt_user_consent(dirty_state)
        
        if choice == "commit":
            print("\n📝 Please commit your changes and try again.")
            print("   git add .")
            print("   git commit -m 'WIP: description'")
            return False, None
        
        elif choice == "stash":
            logger.info("💾 Stashing uncommitted changes...")
            success, _ = self._run_git_command(["stash", "push", "-m", f"CORTEX auto-stash before {operation}"])
            if success:
                logger.info("✅ Changes stashed successfully")
                return True, None
            else:
                logger.error("❌ Failed to stash changes")
                return False, None
        
        elif choice == "proceed":
            logger.info("⚠️  Proceeding with dirty state. Creating checkpoint...")
            checkpoint_id = self.create_auto_checkpoint("pre-work", f"Before {operation} (dirty state)")
            return True, checkpoint_id
        
        else:  # cancel
            logger.info("🚫 Operation cancelled by user")
            return False, None
    
    def create_auto_checkpoint(self, checkpoint_type: str, message: str) -> Optional[str]:
        """
        Create automatic checkpoint using git tag.
        
        Args:
            checkpoint_type: Type of checkpoint (pre-work, post-work, implementation, etc.)
            message: Checkpoint message
            
        Returns:
            Checkpoint ID (tag name) or None if failed
        """
        # Generate checkpoint name
        timestamp = datetime.now().strftime(
            self.config.get("naming", {}).get("timestamp_format", "%Y%m%d-%H%M%S")
        )
        checkpoint_name = f"{checkpoint_type}-{timestamp}"
        
        # Get current commit
        current_sha = self._get_current_commit_sha()
        if not current_sha:
            logger.error("Failed to get current commit SHA")
            return None
        
        # Create annotated git tag
        success, output = self._run_git_command([
            "tag", "-a", checkpoint_name, "-m", message
        ])
        
        if not success:
            logger.error(f"Failed to create checkpoint tag: {output}")
            return None
        
        # Save checkpoint metadata
        checkpoint = {
            "checkpoint_id": checkpoint_name,
            "commit_sha": current_sha,
            "type": checkpoint_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "branch": self._get_current_branch()
        }
        
        checkpoints = self._load_checkpoints()
        checkpoints.append(checkpoint)
        self._save_checkpoints(checkpoints)
        
        logger.info(f"✅ Checkpoint created: {checkpoint_name}")
        return checkpoint_name
    
    def list_all_checkpoints(self, max_age_days: Optional[int] = None) -> List[Dict]:
        """
        List all checkpoints, optionally filtered by age.
        
        Args:
            max_age_days: Maximum age in days (None = no filter)
            
        Returns:
            List of checkpoint dictionaries
        """
        checkpoints = self._load_checkpoints()
        
        if max_age_days is not None:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            checkpoints = [
                cp for cp in checkpoints
                if datetime.fromisoformat(cp["timestamp"]) >= cutoff_date
            ]
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return checkpoints
    
    def cleanup_old_checkpoints(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Clean up old checkpoints based on retention policy.
        
        Args:
            dry_run: If True, don't actually delete (just report)
            
        Returns:
            Cleanup summary dict
        """
        config = self.config.get("retention", {})
        max_age_days = config.get("max_age_days", 30)
        max_count = config.get("max_count", 50)
        preserve_named = config.get("preserve_named", True)
        
        checkpoints = self._load_checkpoints()
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        # Find checkpoints to delete
        to_delete = []
        to_keep = []
        
        for cp in checkpoints:
            cp_date = datetime.fromisoformat(cp["timestamp"])
            is_old = cp_date < cutoff_date
            is_named = cp.get("type") == "user" or preserve_named and "-user-" in cp.get("checkpoint_id", "")
            
            if is_old and not is_named:
                to_delete.append(cp)
            else:
                to_keep.append(cp)
        
        # Check count limit
        if len(to_keep) > max_count:
            # Keep newest max_count checkpoints
            to_keep.sort(key=lambda x: x["timestamp"], reverse=True)
            excess = to_keep[max_count:]
            to_keep = to_keep[:max_count]
            to_delete.extend([cp for cp in excess if not (preserve_named and "-user-" in cp.get("checkpoint_id", ""))])
        
        summary = {
            "total_checkpoints": len(checkpoints),
            "to_delete": len(to_delete),
            "to_keep": len(to_keep),
            "deleted": [],
            "errors": []
        }
        
        if dry_run:
            logger.info(f"🔍 DRY RUN: Would delete {len(to_delete)} checkpoints")
            summary["deleted"] = [cp["checkpoint_id"] for cp in to_delete]
            return summary
        
        # Delete old checkpoints
        for cp in to_delete:
            checkpoint_id = cp["checkpoint_id"]
            
            # Delete git tag
            success, output = self._run_git_command(["tag", "-d", checkpoint_id])
            if success:
                summary["deleted"].append(checkpoint_id)
                logger.info(f"🗑️  Deleted checkpoint: {checkpoint_id}")
            else:
                summary["errors"].append(f"Failed to delete {checkpoint_id}: {output}")
                logger.error(f"Failed to delete {checkpoint_id}")
        
        # Update checkpoints file
        self._save_checkpoints(to_keep)
        
        logger.info(f"✅ Cleanup complete: {len(summary['deleted'])} deleted, {len(to_keep)} kept")
        return summary
    
    def rollback_to_checkpoint_by_name(self, checkpoint_name: str, confirm: bool = True) -> bool:
        """
        Rollback to a checkpoint by name.
        
        Args:
            checkpoint_name: Checkpoint name (tag name)
            confirm: Require user confirmation
            
        Returns:
            True if rollback successful
        """
        # Find checkpoint
        checkpoints = self._load_checkpoints()
        checkpoint = next(
            (cp for cp in checkpoints if cp["checkpoint_id"] == checkpoint_name),
            None
        )
        
        if not checkpoint:
            logger.error(f"❌ Checkpoint not found: {checkpoint_name}")
            return False
        
        # Show what will be lost
        if confirm:
            current_sha = self._get_current_commit_sha()
            success, diff_output = self._run_git_command([
                "diff", "--stat", checkpoint["commit_sha"], current_sha
            ])
            
            if success and diff_output:
                print(f"\n⚠️  ROLLBACK WARNING\n")
                print(f"This will DISCARD all changes after checkpoint '{checkpoint_name}'\n")
                print("Changes to be lost:")
                print(diff_output)
                print()
                
                confirmation = input("Type 'yes' to confirm rollback: ").strip().lower()
                if confirmation != 'yes':
                    logger.info("🚫 Rollback cancelled")
                    return False
        
        # Create safety checkpoint before rollback
        if self.config.get("safety", {}).get("create_backup_before_rollback", True):
            logger.info("📸 Creating safety checkpoint before rollback...")
            self.create_auto_checkpoint("pre-rollback", f"Safety checkpoint before rollback to {checkpoint_name}")
        
        # Reset to checkpoint commit
        success, output = self._run_git_command(["reset", "--hard", checkpoint["commit_sha"]])
        if not success:
            logger.error(f"❌ Rollback failed: {output}")
            return False
        
        logger.info(f"✅ Rolled back to checkpoint: {checkpoint_name}")
        return True

