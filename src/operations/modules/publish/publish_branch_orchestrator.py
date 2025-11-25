"""
Publish Branch Orchestrator Module

Orchestrates CORTEX deployment to remote main branch.
Builds production-ready package in publish/ folder and pushes directly to origin/main.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class PublishBranchOrchestrator(BaseOperationModule):
    """
    Orchestrates CORTEX deployment to remote main branch.
    
    This module builds the CORTEX package in publish/ folder and commits/pushes
    directly to origin/main for user distribution.
    
    Features:
        - Builds production package in publish/ folder (excludes tests, dev tools, docs)
        - Commits publish/ folder to main branch
        - Pushes directly to origin/main remote
        - Preserves user's working branch (returns to original after publish)
        - Dry-run mode for preview
        - Fault-tolerant with checkpoints
    
    Branch Preservation:
        CORTEX SHOULD BEGIN AND END ON THE BRANCH IT IS ON.
        - Saves current branch before publish
        - Switches to main only to commit/push
        - Returns to original branch after completion
    
    Usage:
        # Natural language
        "publish cortex"
        "deploy to main"
        
        # Preview mode
        "publish cortex dry run"
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="publish_branch_orchestrator",
            name="Publish Branch Orchestrator",
            description="Build production package and publish directly to origin/main",
            phase=OperationPhase.FINALIZATION,  # Publishing is a finalization step
            dependencies=[],
            optional_dependencies=[],
            estimated_duration_seconds=60,
            tags=["publish", "deployment", "production", "git", "remote"],
            version="2.0.0"
        )
    
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate execution context.
        
        Checks:
            - Project root exists
            - publish_to_branch.py script exists
            - Git repository is clean (if not dry run)
        """
        project_root = context.get('project_root')
        if not project_root:
            return False, "Project root not specified"
        
        project_root = Path(project_root)
        if not project_root.exists():
            return False, f"Project root does not exist: {project_root}"
        
        # Check for publish script
        publish_script = project_root / "scripts" / "publish_to_branch.py"
        if not publish_script.exists():
            return False, f"Publish script not found: {publish_script}"
        
        # Check for git (unless dry run)
        dry_run = context.get('dry_run', False)
        if not dry_run:
            git_dir = project_root / ".git"
            if not git_dir.exists():
                return False, f"Not a git repository: {project_root}"
        
        return True, "Validation successful"
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute publish operation to remote main branch.
        
        Process:
        1. Run publish_to_branch.py to build package in publish/ folder
        2. Save current branch
        3. Switch to main branch
        4. Commit publish/ folder changes
        5. Push to origin/main
        6. Return to original branch
        
        IMPORTANT: CORTEX SHOULD BEGIN AND END ON THE BRANCH IT IS ON.
        - Saves current branch before publishing
        - Switches to main to commit/push publish package
        - Switches back to original branch after completion
        
        Args:
            context: Execution context with:
                - project_root: Path to CORTEX repository
                - dry_run: Preview mode (default: False)
                - branch: Target branch name (default: main)
                - resume: Resume from checkpoint (default: False)
        
        Returns:
            OperationResult with publish status
        """
        project_root = Path(context.get('project_root'))
        dry_run = context.get('dry_run', False)
        branch = context.get('branch', 'main')
        resume = context.get('resume', False)
        
        # Save the current branch to restore later
        original_branch = self._get_current_branch(project_root)
        logger.info(f"📌 Current branch: {original_branch}")
        
        publish_script = project_root / "scripts" / "publish_to_branch.py"
        
        # Build command
        cmd = [sys.executable, str(publish_script)]
        
        if dry_run:
            cmd.append('--dry-run')
            logger.info("🔍 Running publish in DRY RUN mode (no git operations)")
        
        if branch != 'cortex-publish':
            cmd.extend(['--branch', branch])
        
        if resume:
            cmd.append('--resume')
            logger.info("🔄 Resuming from last checkpoint")
        
        logger.info(f"📦 Publishing CORTEX to branch: {branch}")
        logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            # Run publish script (it builds the package in publish/ folder)
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Parse output
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                logger.info("✅ Publish package built successfully")
                
                # Parse statistics from output
                stats = self._parse_publish_stats(output)
                
                if dry_run:
                    message = f"✅ Publish preview complete. Check .temp-publish/ folder for contents."
                else:
                    # Commit and push to remote main branch (only if not dry run)
                    logger.info(f"🚀 Publishing to origin/{branch}...")
                    commit_success = self._commit_and_push_to_remote(project_root, branch)
                    
                    if not commit_success:
                        return OperationResult(
                            success=False,
                            message=f"Failed to commit and push to origin/{branch}",
                            status=OperationStatus.FAILED,
                            output_data={'script_output': output},
                            error="Git operations failed"
                        )
                    
                    # Switch back to original branch
                    if original_branch and original_branch != branch:
                        self._switch_branch(project_root, original_branch)
                        logger.info(f"🔄 Switched back to original branch: {original_branch}")
                    
                    message = f"✅ Published successfully to origin/{branch}."
                    message += f"\n\n📊 Statistics:\n"
                    message += f"  • Files: {stats.get('files', 'N/A')}\n"
                    message += f"  • Size: {stats.get('size', 'N/A')}\n"
                    message += f"\n📌 Returned to branch: {original_branch}\n"
                    message += f"\n👥 Users can upgrade with:\n"
                    message += f"  cd CORTEX\n"
                    message += f"  git pull origin {branch}\n"
                    message += f"\n# Or fresh install:\n"
                    message += f"  git clone https://github.com/asifhussain60/CORTEX.git"
                
                return OperationResult(
                    success=True,
                    message=message,
                    status=OperationStatus.COMPLETED,
                    output_data={
                        'branch': branch,
                        'original_branch': original_branch,
                        'dry_run': dry_run,
                        'stats': stats,
                        'script_output': output
                    },
                    error=None
                )
            else:
                error_msg = f"Publish failed with exit code {result.returncode}"
                logger.error(error_msg)
                logger.error(f"Output: {output}")
                
                return OperationResult(
                    success=False,
                    message=error_msg,
                    status=OperationStatus.FAILED,
                    output_data={'script_output': output},
                    error=error_msg
                )
        
        except Exception as e:
            error_msg = f"Failed to execute publish script: {e}"
            logger.error(error_msg, exc_info=True)
            
            return OperationResult(
                success=False,
                message=error_msg,
                status=OperationStatus.FAILED,
                output_data={},
                error=str(e)
            )
    
    def _get_current_branch(self, project_root: Path) -> Optional[str]:
        """
        Get the current git branch name.
        
        Returns:
            Current branch name or None if detection fails
        """
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Failed to get current branch: {e}")
            return None
    
    def _switch_branch(self, project_root: Path, branch_name: str) -> bool:
        """
        Switch to specified git branch.
        
        Args:
            project_root: Repository root path
            branch_name: Target branch name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'checkout', branch_name],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to switch to branch {branch_name}: {e}")
            return False
    
    def _commit_and_push_to_remote(self, project_root: Path, target_branch: str) -> bool:
        """
        Commit and push the publish/ folder directly to the remote main branch.
        
        This is the primary deployment mechanism. Users upgrade by pulling from origin/main.
        
        Process:
        1. Switch to target branch (main)
        2. Add publish/ folder to staging
        3. Commit with descriptive message
        4. Push directly to origin/main remote
        
        Args:
            project_root: Repository root path
            target_branch: Target branch (typically 'main')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Switch to target branch (main)
            logger.info(f"🔀 Switching to {target_branch} branch for deployment...")
            switch_result = subprocess.run(
                ['git', 'checkout', target_branch],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if switch_result.returncode != 0:
                logger.error(f"❌ Failed to switch to {target_branch}: {switch_result.stderr}")
                return False
            
            logger.info(f"✅ Switched to {target_branch} branch")
            
            # Add publish folder
            logger.info("📦 Staging publish/ folder for commit...")
            add_result = subprocess.run(
                ['git', 'add', 'publish/'],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if add_result.returncode != 0:
                logger.error(f"❌ Failed to add publish folder: {add_result.stderr}")
                return False
            
            logger.info("✅ publish/ folder staged")
            
            # Commit changes
            commit_msg = f'chore: update CORTEX publish package ({datetime.now().strftime("%Y-%m-%d %H:%M")})'
            logger.info(f"💾 Committing: {commit_msg}")
            commit_result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Check if there's nothing to commit (this is okay)
            if commit_result.returncode != 0:
                if 'nothing to commit' in commit_result.stdout or 'nothing to commit' in commit_result.stderr:
                    logger.info("ℹ️  No changes to commit (publish/ folder unchanged)")
                else:
                    logger.error(f"❌ Failed to commit: {commit_result.stderr}")
                    return False
            else:
                logger.info("✅ Changes committed")
            
            # Push to remote origin/main
            logger.info(f"🚀 Pushing to origin/{target_branch}...")
            push_result = subprocess.run(
                ['git', 'push', 'origin', target_branch],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if push_result.returncode != 0:
                logger.error(f"❌ Failed to push to origin/{target_branch}: {push_result.stderr}")
                return False
            
            logger.info(f"✅ Successfully pushed to origin/{target_branch}")
            logger.info(f"🌐 Deployment complete: Remote main branch updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed during commit/push: {e}")
            return False
    
    def _parse_publish_stats(self, output: str) -> Dict[str, str]:
        """
        Parse publish statistics from script output.
        
        Looks for patterns like:
            Files: 1,090
            Size: 67.77 MB
        """
        stats = {}
        
        for line in output.split('\n'):
            if 'Files:' in line:
                try:
                    stats['files'] = line.split('Files:')[1].strip()
                except:
                    pass
            elif 'Size:' in line:
                try:
                    stats['size'] = line.split('Size:')[1].strip()
                except:
                    pass
        
        return stats
    
    def cleanup(self, context: Dict[str, Any]) -> None:
        """
        Cleanup after execution.
        
        Nothing to clean up - publish script handles its own cleanup.
        """
        pass
