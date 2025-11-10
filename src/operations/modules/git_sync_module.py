"""
Git Synchronization Setup Module

Synchronizes CORTEX project with remote repository.

SOLID Principles:
- Single Responsibility: Only handles git synchronization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class GitSyncModule(BaseOperationModule):
    """
    Setup module for git repository synchronization.
    
    Responsibilities:
    1. Verify git is installed and available
    2. Check if project is a git repository
    3. Fetch latest changes from remote
    4. Pull changes if safe to do so
    5. Report sync status
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="git_sync",
            name="Git Repository Synchronization",
            description="Sync CORTEX project with remote git repository",
            phase=OperationPhase.ENVIRONMENT,
            priority=15,  # After platform detection
            dependencies=["platform_detection"],
            optional=True,  # Optional - can proceed without git
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for git sync.
        
        Checks:
        1. Project root exists
        2. Git command available (not blocking)
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(project_root)
        if not project_root.exists():
            issues.append(f"Project root does not exist: {project_root}")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute git synchronization.
        
        Steps:
        1. Check if git is installed
        2. Verify project is a git repository
        3. Check for uncommitted changes
        4. Fetch remote changes
        5. Pull if safe (no conflicts)
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        
        try:
            # Check if git is installed
            git_available, git_version = self._check_git_available()
            if not git_available:
                self.log_warning("Git not available, skipping synchronization")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="Git not installed, synchronization skipped",
                    data={'git_available': False},
                    warnings=["Git not available on this system"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            self.log_info(f"Git version: {git_version}")
            
            # Check if project is a git repository
            if not self._is_git_repository(project_root):
                self.log_warning("Project is not a git repository")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="Not a git repository, synchronization skipped",
                    data={'is_git_repo': False},
                    warnings=["Project is not under git version control"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Get current branch
            current_branch = self._get_current_branch(project_root)
            self.log_info(f"Current branch: {current_branch}")
            
            # Check for uncommitted changes
            has_changes = self._has_uncommitted_changes(project_root)
            if has_changes:
                self.log_warning("Uncommitted changes detected, skipping pull")
                return OperationResult(
                    success=True,
                    status=OperationStatus.WARNING,
                    message="Uncommitted changes present, skipped pull",
                    data={
                        'git_available': True,
                        'is_git_repo': True,
                        'current_branch': current_branch,
                        'has_uncommitted_changes': True,
                        'synced': False
                    },
                    warnings=["Uncommitted changes present, automatic pull skipped"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # OPTIMIZATION: Check if already up-to-date before expensive fetch
            # Use ls-remote to check remote HEAD without fetching all objects
            remote_up_to_date = self._check_remote_up_to_date(project_root, current_branch)
            if remote_up_to_date:
                self.log_info("Already up to date with remote (fast check)")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Repository already up to date (fast check)",
                    data={
                        'git_available': True,
                        'is_git_repo': True,
                        'current_branch': current_branch,
                        'has_uncommitted_changes': False,
                        'behind_count': 0,
                        'synced': True,
                        'up_to_date': True,
                        'fast_check': True
                    },
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Fetch remote changes (only if fast check shows we might be behind)
            fetch_success, fetch_output = self._git_fetch(project_root)
            if not fetch_success:
                self.log_error(f"Git fetch failed: {fetch_output}")
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Git fetch failed",
                    data={'fetch_output': fetch_output},
                    errors=[f"Git fetch failed: {fetch_output}"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Check if we're behind remote
            behind_count = self._get_behind_count(project_root, current_branch)
            
            if behind_count == 0:
                self.log_info("Already up to date with remote")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Repository already up to date",
                    data={
                        'git_available': True,
                        'is_git_repo': True,
                        'current_branch': current_branch,
                        'has_uncommitted_changes': False,
                        'behind_count': 0,
                        'synced': True,
                        'up_to_date': True
                    },
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Pull changes
            self.log_info(f"Pulling {behind_count} commits from remote")
            pull_success, pull_output = self._git_pull(project_root)
            
            if not pull_success:
                self.log_error(f"Git pull failed: {pull_output}")
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Git pull failed",
                    data={
                        'pull_output': pull_output,
                        'behind_count': behind_count
                    },
                    errors=[f"Git pull failed: {pull_output}"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            self.log_info("Successfully synced with remote")
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Successfully pulled {behind_count} commits",
                data={
                    'git_available': True,
                    'is_git_repo': True,
                    'current_branch': current_branch,
                    'has_uncommitted_changes': False,
                    'behind_count': behind_count,
                    'synced': True,
                    'pull_output': pull_output
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Git sync failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Git sync failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _check_git_available(self) -> Tuple[bool, str]:
        """Check if git command is available."""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, ""
        except (subprocess.SubprocessError, FileNotFoundError):
            return False, ""
    
    def _is_git_repository(self, project_root: Path) -> bool:
        """Check if directory is a git repository."""
        git_dir = project_root / ".git"
        return git_dir.is_dir()
    
    def _get_current_branch(self, project_root: Path) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except subprocess.SubprocessError:
            return "unknown"
    
    def _has_uncommitted_changes(self, project_root: Path) -> bool:
        """Check for uncommitted changes."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            return len(result.stdout.strip()) > 0
        except subprocess.SubprocessError:
            return True  # Assume changes if we can't check
    
    def _check_remote_up_to_date(self, project_root: Path, branch: str) -> bool:
        """
        Fast check if local is up-to-date with remote using ls-remote.
        This avoids expensive fetch operation when already current.
        
        Performance: ~50-100ms vs 2-5s for full fetch
        """
        try:
            # Get local HEAD commit
            result_local = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result_local.returncode != 0:
                return False  # Can't check, assume not up-to-date
            
            local_commit = result_local.stdout.strip()
            
            # Get remote HEAD commit without fetching
            result_remote = subprocess.run(
                ['git', 'ls-remote', 'origin', branch],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result_remote.returncode != 0:
                return False  # Can't check remote, assume not up-to-date
            
            # Parse remote commit (format: "commit_hash\trefs/heads/branch")
            remote_line = result_remote.stdout.strip()
            if not remote_line:
                return False
            
            remote_commit = remote_line.split('\t')[0]
            
            # Compare commits
            return local_commit == remote_commit
            
        except subprocess.SubprocessError:
            return False  # Can't check, assume not up-to-date
    
    def _git_fetch(self, project_root: Path) -> Tuple[bool, str]:
        """Fetch from remote repository."""
        try:
            result = subprocess.run(
                ['git', 'fetch'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.SubprocessError as e:
            return False, str(e)
    
    def _get_behind_count(self, project_root: Path, branch: str) -> int:
        """Get number of commits behind remote."""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'HEAD..origin/{branch}'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (subprocess.SubprocessError, ValueError):
            return 0
    
    def _git_pull(self, project_root: Path) -> Tuple[bool, str]:
        """Pull changes from remote repository."""
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.SubprocessError as e:
            return False, str(e)
