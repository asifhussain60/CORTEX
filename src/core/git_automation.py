"""
Git Automation for CORTEX 4.0

Provides automatic git operations for autonomous execution:
- Auto-commit on phase completion
- Checkpoint creation for rollback
- Auto-push on milestone completion
- Conflict detection

Phase 0.5 Component
"""

import logging
import subprocess
from datetime import datetime
from typing import Optional


class GitAutomation:
    """
    Git automation for autonomous execution.
    
    Capabilities:
    - Auto-commit with formatted messages
    - Create checkpoints (git tags) for rollback
    - Auto-push to remote
    - Conflict detection
    
    Usage:
        git = GitAutomation(logger, enable_push=True)
        git.auto_commit(
            phase_name="Phase 1",
            validation_passed=True,
            test_summary="10/10 tests passing"
        )
        checkpoint_id = git.create_checkpoint("phase_1_complete")
        git.rollback_to_checkpoint(checkpoint_id)
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        enable_push: bool = False,
        dry_run: bool = False
    ):
        """
        Initialize git automation.
        
        Args:
            logger: Logger instance
            enable_push: Enable auto-push to remote (default: False)
            dry_run: Simulate git operations without executing (default: False)
        """
        self.logger = logger
        self.enable_push = enable_push
        self.dry_run = dry_run
    
    def auto_commit(
        self,
        phase_name: str,
        validation_passed: bool,
        test_summary: str = "",
        coverage: Optional[float] = None
    ) -> bool:
        """
        Auto-commit phase completion.
        
        Args:
            phase_name: Phase name
            validation_passed: Whether validation passed
            test_summary: Test results summary
            coverage: Coverage percentage
        
        Returns:
            True if commit succeeded
        """
        # Format commit message
        status_emoji = "✅" if validation_passed else "❌"
        status_text = "Complete" if validation_passed else "Failed"
        
        message = f"{status_emoji} {phase_name} {status_text}\n\n"
        
        if test_summary:
            message += f"Tests: {test_summary}\n"
        
        if coverage is not None:
            message += f"Coverage: {coverage:.1f}%\n"
        
        message += f"\n[Autonomous Execution - {datetime.now().isoformat()}]"
        
        # Execute git commit
        return self._git_commit(message)
    
    def create_checkpoint(self, checkpoint_name: str) -> Optional[str]:
        """
        Create git checkpoint (tag) for rollback.
        
        Args:
            checkpoint_name: Checkpoint identifier
        
        Returns:
            Commit hash if successful, None otherwise
        """
        self.logger.info(f"⏸️  Creating checkpoint: {checkpoint_name}")
        
        if self.dry_run:
            self.logger.info("   [DRY RUN] Would create checkpoint")
            return "dry_run_checkpoint"
        
        try:
            # Get current commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()
            
            # Create tag
            subprocess.run(
                ["git", "tag", "-a", checkpoint_name, "-m", f"Checkpoint: {checkpoint_name}"],
                check=True
            )
            
            self.logger.info(f"   ✓ Checkpoint created: {checkpoint_name} @ {commit_hash[:8]}")
            return commit_hash
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"   ❌ Failed to create checkpoint: {e}")
            return None
    
    def rollback_to_checkpoint(self, checkpoint_name: str) -> bool:
        """
        Rollback to checkpoint.
        
        WARNING: This performs a hard reset and will lose uncommitted changes.
        
        Args:
            checkpoint_name: Checkpoint identifier
        
        Returns:
            True if rollback succeeded
        """
        self.logger.warning(f"↩️  Rolling back to checkpoint: {checkpoint_name}")
        
        if self.dry_run:
            self.logger.info("   [DRY RUN] Would rollback to checkpoint")
            return True
        
        try:
            # Hard reset to checkpoint
            subprocess.run(
                ["git", "reset", "--hard", checkpoint_name],
                check=True
            )
            
            self.logger.info(f"   ✓ Rolled back to: {checkpoint_name}")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"   ❌ Rollback failed: {e}")
            return False
    
    def auto_push(self, branch: Optional[str] = None) -> bool:
        """
        Auto-push to remote.
        
        Checks for conflicts before pushing.
        
        Args:
            branch: Branch name (default: current branch)
        
        Returns:
            True if push succeeded
        """
        if not self.enable_push:
            self.logger.info("⏸️  Auto-push disabled")
            return False
        
        self.logger.info("📤 Auto-push to remote")
        
        if self.dry_run:
            self.logger.info("   [DRY RUN] Would push to remote")
            return True
        
        try:
            # Pull first to check for conflicts
            result = subprocess.run(
                ["git", "pull", "--rebase"],
                capture_output=True,
                text=True
            )
            
            if "CONFLICT" in result.stdout or result.returncode != 0:
                self.logger.error("   ❌ Conflict detected - manual intervention required")
                return False
            
            # Push
            push_cmd = ["git", "push"]
            if branch:
                push_cmd.extend(["origin", branch])
            
            subprocess.run(push_cmd, check=True)
            
            self.logger.info("   ✓ Pushed to remote")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"   ❌ Push failed: {e}")
            return False
    
    def _git_commit(self, message: str) -> bool:
        """
        Execute git commit.
        
        Args:
            message: Commit message
        
        Returns:
            True if commit succeeded
        """
        self.logger.info(f"💾 Auto-commit: {message.split()[1] if len(message.split()) > 1 else 'changes'}")
        
        if self.dry_run:
            self.logger.info("   [DRY RUN] Would commit with message:")
            self.logger.info(f"   {message[:100]}...")
            return True
        
        try:
            # Stage all changes
            subprocess.run(["git", "add", "."], check=True)
            
            # Check if there are changes to commit
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if not status.stdout.strip():
                self.logger.info("   ⏸️  No changes to commit")
                return True
            
            # Commit
            subprocess.run(["git", "commit", "-m", message], check=True)
            
            self.logger.info("   ✓ Committed successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"   ❌ Commit failed: {e}")
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
