"""
Commit Orchestrator - Intelligent Git Sync Workflow

Purpose:
- Pull from origin and merge preserving local work
- Ensure zero untracked files (prompt user to add/ignore)
- Push merged result to origin
- Create git checkpoints for rollback safety
- Handle merge conflicts with clear guidance

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging

from .git_checkpoint_orchestrator import GitCheckpointOrchestrator

logger = logging.getLogger(__name__)


class CommitOrchestrator:
    """
    Orchestrates intelligent git commit and sync workflow.
    
    Features:
    - Pre-flight validation (dirty state, untracked files)
    - Pull from origin with conflict detection
    - Intelligent merge strategy (preserve local work)
    - Untracked file handling (prompt user to add/ignore)
    - Push to origin with verification
    - Git checkpoint integration for safety
    - Progress reporting
    """
    
    def __init__(self, project_root: Path, brain_path: Optional[Path] = None):
        """
        Initialize CommitOrchestrator.
        
        Args:
            project_root: Path to project repository root
            brain_path: Optional path to CORTEX brain
        """
        self.project_root = Path(project_root)
        self.brain_path = Path(brain_path) if brain_path else self.project_root / "cortex-brain"
        self.checkpoint_orchestrator = GitCheckpointOrchestrator(project_root, brain_path)
    
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
        """Get current git branch name."""
        success, output = self._run_git_command(["branch", "--show-current"])
        return output if success else None
    
    def _get_untracked_files(self) -> List[str]:
        """
        Get list of untracked files.
        
        Returns:
            List of untracked file paths
        """
        success, output = self._run_git_command(["ls-files", "--others", "--exclude-standard"])
        if not success:
            return []
        
        return [f.strip() for f in output.split('\n') if f.strip()]
    
    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        success, output = self._run_git_command(["status", "--porcelain"])
        return bool(output.strip()) if success else False
    
    def _has_merge_conflicts(self) -> bool:
        """Check if there are merge conflicts."""
        success, output = self._run_git_command(["diff", "--name-only", "--diff-filter=U"])
        return bool(output.strip()) if success else False
    
    def _get_remote_name(self) -> str:
        """
        Get remote name (usually 'origin').
        
        Returns:
            Remote name or 'origin' as default
        """
        success, output = self._run_git_command(["remote"])
        if success and output.strip():
            remotes = output.strip().split('\n')
            return remotes[0] if remotes else "origin"
        return "origin"
    
    def pre_flight_check(self) -> Dict:
        """
        Perform pre-flight validation before commit workflow.
        
        Returns:
            Dict with validation results:
            - success: bool
            - branch: str
            - untracked_files: List[str]
            - uncommitted_changes: bool
            - issues: List[str]
        """
        logger.info("🔍 Running pre-flight checks...")
        
        issues = []
        
        # Check current branch
        branch = self._get_current_branch()
        if not branch:
            issues.append("Failed to get current branch")
            return {
                "success": False,
                "branch": None,
                "untracked_files": [],
                "uncommitted_changes": False,
                "issues": issues
            }
        
        # Check for untracked files
        untracked = self._get_untracked_files()
        if untracked:
            issues.append(f"Found {len(untracked)} untracked file(s)")
        
        # Check for uncommitted changes
        has_changes = self._has_uncommitted_changes()
        if has_changes:
            issues.append("Found uncommitted changes")
        
        return {
            "success": len(issues) == 0,
            "branch": branch,
            "untracked_files": untracked,
            "uncommitted_changes": has_changes,
            "issues": issues
        }
    
    def handle_untracked_files(self, untracked_files: List[str], auto_add: bool = False) -> Tuple[bool, str]:
        """
        Handle untracked files by prompting user or auto-adding.
        
        Args:
            untracked_files: List of untracked file paths
            auto_add: If True, automatically add all files (default: False)
            
        Returns:
            Tuple of (success, message)
        """
        if not untracked_files:
            return True, "No untracked files"
        
        logger.info(f"📝 Found {len(untracked_files)} untracked file(s):")
        for file in untracked_files:
            logger.info(f"   - {file}")
        
        if auto_add:
            logger.info("➕ Auto-adding all untracked files...")
            success, output = self._run_git_command(["add"] + untracked_files)
            if success:
                return True, f"Added {len(untracked_files)} file(s)"
            else:
                return False, f"Failed to add files: {output}"
        else:
            return False, f"Please handle {len(untracked_files)} untracked file(s) manually (git add or .gitignore)"
    
    def pull_from_origin(self, rebase: bool = False) -> Tuple[bool, str]:
        """
        Pull changes from origin.
        
        Args:
            rebase: Use rebase instead of merge (default: False)
            
        Returns:
            Tuple of (success, message)
        """
        logger.info("⬇️ Pulling from origin...")
        
        remote = self._get_remote_name()
        branch = self._get_current_branch()
        
        if not branch:
            return False, "Failed to get current branch"
        
        # Fetch first
        success, output = self._run_git_command(["fetch", remote])
        if not success:
            return False, f"Failed to fetch from {remote}: {output}"
        
        # Pull with merge or rebase
        pull_args = ["pull", remote, branch]
        if rebase:
            pull_args.append("--rebase")
        
        success, output = self._run_git_command(pull_args)
        
        if not success:
            if "conflict" in output.lower():
                return False, f"Merge conflict detected. Please resolve conflicts manually:\n{output}"
            return False, f"Failed to pull: {output}"
        
        # Check for conflicts after pull
        if self._has_merge_conflicts():
            return False, "Merge conflicts detected. Please resolve conflicts and run 'commit' again."
        
        return True, f"Successfully pulled from {remote}/{branch}"
    
    def push_to_origin(self) -> Tuple[bool, str]:
        """
        Push changes to origin.
        
        Returns:
            Tuple of (success, message)
        """
        logger.info("⬆️ Pushing to origin...")
        
        remote = self._get_remote_name()
        branch = self._get_current_branch()
        
        if not branch:
            return False, "Failed to get current branch"
        
        success, output = self._run_git_command(["push", remote, branch])
        
        if not success:
            return False, f"Failed to push to {remote}/{branch}: {output}"
        
        return True, f"Successfully pushed to {remote}/{branch}"
    
    def execute(
        self,
        auto_add_untracked: bool = False,
        rebase: bool = False,
        commit_message: Optional[str] = None
    ) -> Dict:
        """
        Execute complete commit workflow.
        
        Args:
            auto_add_untracked: Automatically add untracked files (default: False)
            rebase: Use rebase instead of merge (default: False)
            commit_message: Optional commit message for uncommitted changes
            
        Returns:
            Dict with execution results:
            - success: bool
            - message: str
            - checkpoint_created: bool
            - checkpoint_id: Optional[str]
            - steps_completed: List[str]
        """
        start_time = datetime.now()
        steps_completed = []
        checkpoint_id = None
        
        logger.info("🚀 Starting commit workflow...")
        logger.info("=" * 60)
        
        # Step 1: Pre-flight check
        logger.info("\n📋 Step 1/6: Pre-flight validation")
        pre_flight = self.pre_flight_check()
        
        if not pre_flight["success"]:
            logger.warning(f"⚠️ Pre-flight issues found: {', '.join(pre_flight['issues'])}")
        
        # Step 2: Handle untracked files
        if pre_flight["untracked_files"]:
            logger.info(f"\n📝 Step 2/6: Handling {len(pre_flight['untracked_files'])} untracked file(s)")
            success, msg = self.handle_untracked_files(pre_flight["untracked_files"], auto_add_untracked)
            if not success:
                return {
                    "success": False,
                    "message": msg,
                    "checkpoint_created": False,
                    "checkpoint_id": None,
                    "steps_completed": steps_completed
                }
            steps_completed.append("Handled untracked files")
            logger.info(f"✅ {msg}")
        else:
            logger.info("\n📝 Step 2/6: No untracked files")
            steps_completed.append("No untracked files")
        
        # Step 3: Commit uncommitted changes (if any)
        if pre_flight["uncommitted_changes"] or pre_flight["untracked_files"]:
            logger.info("\n💾 Step 3/6: Committing changes")
            
            if not commit_message:
                commit_message = f"CORTEX: Auto-commit before sync ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            
            # Stage all changes
            success, output = self._run_git_command(["add", "-A"])
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to stage changes: {output}",
                    "checkpoint_created": False,
                    "checkpoint_id": None,
                    "steps_completed": steps_completed
                }
            
            # Commit
            success, output = self._run_git_command(["commit", "-m", commit_message])
            if not success and "nothing to commit" not in output.lower():
                return {
                    "success": False,
                    "message": f"Failed to commit: {output}",
                    "checkpoint_created": False,
                    "checkpoint_id": None,
                    "steps_completed": steps_completed
                }
            
            steps_completed.append("Committed changes")
            logger.info("✅ Changes committed")
        else:
            logger.info("\n💾 Step 3/6: No changes to commit")
            steps_completed.append("No changes to commit")
        
        # Step 4: Create checkpoint before pull
        logger.info("\n🔖 Step 4/6: Creating safety checkpoint")
        session_id = f"commit-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        checkpoint_id = self.checkpoint_orchestrator.create_checkpoint(
            session_id=session_id,
            phase="pre-sync",
            message="Before pull from origin"
        )
        
        if checkpoint_id:
            steps_completed.append("Checkpoint created")
            logger.info(f"✅ Checkpoint created: {checkpoint_id[:8]}")
        else:
            logger.warning("⚠️ Failed to create checkpoint (continuing anyway)")
        
        # Step 5: Pull from origin
        logger.info(f"\n⬇️ Step 5/6: Pulling from origin (rebase={rebase})")
        success, msg = self.pull_from_origin(rebase=rebase)
        
        if not success:
            return {
                "success": False,
                "message": msg,
                "checkpoint_created": bool(checkpoint_id),
                "checkpoint_id": checkpoint_id,
                "steps_completed": steps_completed
            }
        
        steps_completed.append("Pulled from origin")
        logger.info(f"✅ {msg}")
        
        # Step 6: Push to origin
        logger.info("\n⬆️ Step 6/6: Pushing to origin")
        success, msg = self.push_to_origin()
        
        if not success:
            return {
                "success": False,
                "message": msg,
                "checkpoint_created": bool(checkpoint_id),
                "checkpoint_id": checkpoint_id,
                "steps_completed": steps_completed
            }
        
        steps_completed.append("Pushed to origin")
        logger.info(f"✅ {msg}")
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Commit workflow completed successfully in {duration:.1f}s")
        logger.info(f"📊 Steps completed: {len(steps_completed)}/6")
        
        return {
            "success": True,
            "message": f"Successfully synced with origin (pulled and pushed to {pre_flight['branch']})",
            "checkpoint_created": bool(checkpoint_id),
            "checkpoint_id": checkpoint_id,
            "steps_completed": steps_completed,
            "duration_seconds": duration
        }


def main():
    """CLI entry point for testing."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Commit Orchestrator")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                        help="Project root directory")
    parser.add_argument("--auto-add", action="store_true",
                        help="Automatically add untracked files")
    parser.add_argument("--rebase", action="store_true",
                        help="Use rebase instead of merge")
    parser.add_argument("--message", type=str,
                        help="Commit message for uncommitted changes")
    
    args = parser.parse_args()
    
    orchestrator = CommitOrchestrator(args.project_root)
    result = orchestrator.execute(
        auto_add_untracked=args.auto_add,
        rebase=args.rebase,
        commit_message=args.message
    )
    
    print(f"\n{'='*60}")
    print(f"Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    print(f"Steps completed: {result['steps_completed']}")
    
    if result['checkpoint_created']:
        print(f"Checkpoint: {result['checkpoint_id'][:8]}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
