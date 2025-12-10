"""
Git Operations - CORTEX 4.0 DevOps Orchestrator

Low-level git operations wrapper.

Author: Asif Hussain
Date: December 10, 2025
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class GitOperations:
    """Git operations wrapper for DevOps orchestrator."""
    
    def __init__(self):
        """Initialize git operations."""
        self.git_cmd = "git"
    
    def is_git_repository(self, project_path: str) -> bool:
        """
        Check if directory is a git repository.
        
        Args:
            project_path: Project directory path
            
        Returns:
            True if git repository
        """
        git_dir = Path(project_path) / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def has_uncommitted_changes(self, project_path: str) -> bool:
        """
        Check for uncommitted changes.
        
        Args:
            project_path: Project directory path
            
        Returns:
            True if uncommitted changes exist
        """
        try:
            result = subprocess.run(
                [self.git_cmd, "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) > 0
        except subprocess.CalledProcessError:
            return False
    
    def has_git_credentials(self) -> bool:
        """
        Check if git credentials are configured.
        
        Returns:
            True if credentials configured
        """
        try:
            result = subprocess.run(
                [self.git_cmd, "config", "user.name"],
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) > 0
        except subprocess.CalledProcessError:
            return False
    
    def commit(
        self,
        project_path: str,
        message: str,
        add_all: bool = True
    ) -> Dict[str, Any]:
        """
        Create git commit.
        
        Args:
            project_path: Project directory path
            message: Commit message
            add_all: Add all changes before committing
            
        Returns:
            Commit result
        """
        try:
            if add_all:
                subprocess.run(
                    [self.git_cmd, "add", "."],
                    cwd=project_path,
                    check=True
                )
            
            result = subprocess.run(
                [self.git_cmd, "commit", "-m", message],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get commit hash
            hash_result = subprocess.run(
                [self.git_cmd, "rev-parse", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = hash_result.stdout.strip()
            
            return {
                'success': True,
                'commit_hash': commit_hash,
                'message': message
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def push(
        self,
        project_path: str,
        branch: Optional[str] = None,
        remote: str = "origin"
    ) -> Dict[str, Any]:
        """
        Push to remote repository.
        
        Args:
            project_path: Project directory path
            branch: Branch to push (current if None)
            remote: Remote name
            
        Returns:
            Push result
        """
        try:
            if branch:
                cmd = [self.git_cmd, "push", remote, branch]
            else:
                cmd = [self.git_cmd, "push"]
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'output': result.stdout
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git push failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def pull(
        self,
        project_path: str,
        branch: Optional[str] = None,
        remote: str = "origin"
    ) -> Dict[str, Any]:
        """
        Pull from remote repository.
        
        Args:
            project_path: Project directory path
            branch: Branch to pull (current if None)
            remote: Remote name
            
        Returns:
            Pull result
        """
        try:
            if branch:
                cmd = [self.git_cmd, "pull", remote, branch]
            else:
                cmd = [self.git_cmd, "pull"]
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'output': result.stdout
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git pull failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_current_branch(self, project_path: str) -> Optional[str]:
        """
        Get current git branch.
        
        Args:
            project_path: Project directory path
            
        Returns:
            Branch name or None
        """
        try:
            result = subprocess.run(
                [self.git_cmd, "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def checkout(
        self,
        project_path: str,
        branch: str,
        create: bool = False
    ) -> Dict[str, Any]:
        """
        Checkout git branch.
        
        Args:
            project_path: Project directory path
            branch: Branch name
            create: Create branch if it doesn't exist
            
        Returns:
            Checkout result
        """
        try:
            if create:
                cmd = [self.git_cmd, "checkout", "-b", branch]
            else:
                cmd = [self.git_cmd, "checkout", branch]
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'success': True,
                'branch': branch
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git checkout failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
