"""
Sync Coordinator - CORTEX 4.0 DevOps Orchestrator

Git sync and repository optimization.

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any
import logging
import subprocess

from .git_operations import GitOperations

logger = logging.getLogger(__name__)


class SyncCoordinator:
    """
    Sync coordinator for DevOps orchestrator.
    
    Handles:
    - Remote synchronization
    - Conflict resolution
    - Repository optimization
    """
    
    def __init__(self, git_ops: GitOperations):
        """
        Initialize sync coordinator.
        
        Args:
            git_ops: Git operations wrapper
        """
        self.git_ops = git_ops
    
    def sync_with_remote(
        self,
        project_path: str,
        branch: str = 'main',
        auto_resolve_conflicts: bool = False
    ) -> Dict[str, Any]:
        """
        Sync with remote repository.
        
        Args:
            project_path: Project directory path
            branch: Branch to sync
            auto_resolve_conflicts: Automatically resolve conflicts
            
        Returns:
            Sync result
        """
        # Pull from remote
        pull_result = self.git_ops.pull(
            project_path=project_path,
            branch=branch
        )
        
        if not pull_result['success']:
            # Check for conflicts
            if 'conflict' in pull_result.get('error', '').lower():
                if auto_resolve_conflicts:
                    conflicts_resolved = self._resolve_conflicts(project_path)
                    return {
                        'success': conflicts_resolved > 0,
                        'conflicts_resolved': conflicts_resolved
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Conflicts detected',
                        'conflicts_resolved': 0
                    }
        
        # Push any local changes
        push_result = self.git_ops.push(
            project_path=project_path,
            branch=branch
        )
        
        return {
            'success': push_result['success'],
            'conflicts_resolved': 0
        }
    
    def optimize_repository(self, project_path: str) -> Dict[str, Any]:
        """
        Optimize git repository.
        
        Args:
            project_path: Project directory path
            
        Returns:
            Optimization result
        """
        try:
            # Run git gc
            subprocess.run(
                ['git', 'gc', '--auto'],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            
            # Run git prune
            subprocess.run(
                ['git', 'prune'],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            
            logger.info("Repository optimized")
            
            return {
                'success': True,
                'operations': ['gc', 'prune']
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Optimization failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _resolve_conflicts(self, project_path: str) -> int:
        """
        Resolve git conflicts automatically.
        
        Args:
            project_path: Project directory path
            
        Returns:
            Number of conflicts resolved
        """
        # Simple conflict resolution: accept ours
        try:
            subprocess.run(
                ['git', 'checkout', '--ours', '.'],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            
            subprocess.run(
                ['git', 'add', '.'],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            
            return 1
        
        except subprocess.CalledProcessError:
            return 0
