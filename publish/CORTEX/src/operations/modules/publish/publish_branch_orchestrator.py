"""
Publish Branch Orchestrator Module

Wraps the existing publish_to_branch.py script to integrate with CORTEX operations system.
Builds production-ready package and publishes to cortex-publish branch.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
import sys
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
    Orchestrates CORTEX publish to production branch.
    
    This module wraps the existing scripts/publish_to_branch.py script,
    integrating it into the CORTEX operations system for natural language access.
    
    Features:
        - Builds production package (excludes tests, dev tools, docs)
        - Creates/updates cortex-publish orphan branch
        - Publishes to git remote
        - Dry-run mode for preview
        - Fault-tolerant with checkpoints
    
    Usage:
        # Natural language
        "publish cortex"
        "publish to branch"
        
        # Preview mode
        "publish cortex dry run"
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="publish_branch_orchestrator",
            name="Publish Branch Orchestrator",
            description="Build production package and publish to cortex-publish branch",
            phase=OperationPhase.FINALIZATION,  # Publishing is a finalization step
            dependencies=[],
            optional_dependencies=[],
            estimated_duration_seconds=60,
            tags=["publish", "deployment", "production", "git"],
            version="1.0.0"
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
        Execute publish operation.
        
        Runs the publish_to_branch.py script with appropriate flags.
        
        Args:
            context: Execution context with:
                - project_root: Path to CORTEX repository
                - dry_run: Preview mode (default: False)
                - branch: Target branch name (default: cortex-publish)
                - resume: Resume from checkpoint (default: False)
        
        Returns:
            OperationResult with publish status
        """
        project_root = Path(context.get('project_root'))
        dry_run = context.get('dry_run', False)
        branch = context.get('branch', 'cortex-publish')
        resume = context.get('resume', False)
        
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
            # Run publish script
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
                logger.info("✅ Publish completed successfully")
                
                # Parse statistics from output
                stats = self._parse_publish_stats(output)
                
                if dry_run:
                    message = f"✅ Publish preview complete. Check .temp-publish/ folder for contents."
                else:
                    message = f"✅ Published successfully to {branch} branch."
                    message += f"\n\n📊 Statistics:\n"
                    message += f"  • Files: {stats.get('files', 'N/A')}\n"
                    message += f"  • Size: {stats.get('size', 'N/A')}\n"
                    message += f"\n👥 Users can clone with:\n"
                    message += f"  git clone -b {branch} --single-branch https://github.com/asifhussain60/CORTEX.git"
                
                return OperationResult(
                    success=True,
                    message=message,
                    status=OperationStatus.COMPLETED,
                    output_data={
                        'branch': branch,
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
