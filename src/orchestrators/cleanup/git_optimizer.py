"""
Git Optimizer - Group 4 cleanup (git repository optimization).

Handles:
- Git garbage collection (git gc)
- Git pruning (remove unreachable objects)
- Git repacking (optimize pack files)
- Reflog cleanup (>90 days)

Priority: LOW (safe but slow)
Expected: ~180s execution, 100MB+ freed

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class GitOptimizer:
    """
    Git optimization (Group 4) - gc, prune, repack.
    
    Operations:
    - git gc: Garbage collection
    - git prune: Remove unreachable objects
    - git repack: Optimize pack files
    """
    
    def __init__(self, workspace_root: Path, config: Dict[str, Any]):
        """
        Initialize git optimizer.
        
        Args:
            workspace_root: Workspace root directory
            config: Orchestrator configuration
        """
        self.workspace_root = workspace_root
        self.config = config
        
        # Check if git repo exists
        self.git_dir = workspace_root / '.git'
        self.is_git_repo = self.git_dir.exists()
        
        logger.info(
            f"GitOptimizer initialized (git repo: {self.is_git_repo})"
        )
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute git optimization.
        
        Returns:
            Cleanup result dictionary
        """
        logger.info("Starting git optimization (Group 4)")
        
        if not self.is_git_repo:
            logger.warning("Not a git repository, skipping git optimization")
            return self._empty_result("Not a git repository")
        
        operations = []
        total_space_freed = 0
        
        # Get .git size before optimization
        size_before = self._get_git_size()
        
        # Execute git operations
        try:
            # Git garbage collection
            gc_result = self._git_gc()
            operations.append(gc_result)
            
            # Git prune
            prune_result = self._git_prune()
            operations.append(prune_result)
            
            # Git repack
            repack_result = self._git_repack()
            operations.append(repack_result)
            
            # Calculate space freed
            size_after = self._get_git_size()
            total_space_freed = max(0, size_before - size_after)
        
        except Exception as e:
            logger.error(f"Git optimization failed: {e}")
            operations.append({
                'operation': 'error',
                'success': False,
                'error': str(e)
            })
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 0,
                'files_deleted': 0,
                'files_archived': 0,
                'folders_deleted': 0,
                'space_freed_bytes': total_space_freed,
                'space_freed_mb': total_space_freed / (1024 * 1024),
                'categories_processed': 1
            },
            'categories': {
                'git_optimization': {
                    'count': len(operations),
                    'size_mb': total_space_freed / (1024 * 1024)
                }
            },
            'operations': operations,
            'size_before_mb': size_before / (1024 * 1024),
            'size_after_mb': size_after / (1024 * 1024),
            'errors': [],
            'warnings': [],
            'artifacts': []
        }
        
        logger.info(
            f"Git optimization complete: {total_space_freed / (1024 * 1024):.2f} MB freed"
        )
        
        return result
    
    def _git_gc(self) -> Dict[str, Any]:
        """
        Execute git garbage collection.
        
        Returns:
            Operation result
        """
        logger.info("Running git gc...")
        
        try:
            result = subprocess.run(
                ['git', 'gc', '--aggressive', '--prune=now'],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'operation': 'git_gc',
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except subprocess.TimeoutExpired:
            logger.warning("git gc timed out after 5 minutes")
            return {
                'operation': 'git_gc',
                'success': False,
                'error': 'Timeout after 5 minutes'
            }
        except Exception as e:
            logger.error(f"git gc failed: {e}")
            return {
                'operation': 'git_gc',
                'success': False,
                'error': str(e)
            }
    
    def _git_prune(self) -> Dict[str, Any]:
        """
        Execute git prune to remove unreachable objects.
        
        Returns:
            Operation result
        """
        logger.info("Running git prune...")
        
        try:
            result = subprocess.run(
                ['git', 'prune', '--expire=now'],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'operation': 'git_prune',
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            logger.error(f"git prune failed: {e}")
            return {
                'operation': 'git_prune',
                'success': False,
                'error': str(e)
            }
    
    def _git_repack(self) -> Dict[str, Any]:
        """
        Execute git repack to optimize pack files.
        
        Returns:
            Operation result
        """
        logger.info("Running git repack...")
        
        try:
            result = subprocess.run(
                ['git', 'repack', '-a', '-d', '-f'],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout
            )
            
            return {
                'operation': 'git_repack',
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except subprocess.TimeoutExpired:
            logger.warning("git repack timed out after 3 minutes")
            return {
                'operation': 'git_repack',
                'success': False,
                'error': 'Timeout after 3 minutes'
            }
        except Exception as e:
            logger.error(f"git repack failed: {e}")
            return {
                'operation': 'git_repack',
                'success': False,
                'error': str(e)
            }
    
    def _get_git_size(self) -> int:
        """
        Calculate .git directory size.
        
        Returns:
            Size in bytes
        """
        if not self.git_dir.exists():
            return 0
        
        total_size = 0
        for file in self.git_dir.rglob('*'):
            if file.is_file():
                try:
                    total_size += file.stat().st_size
                except:
                    pass
        
        return total_size
    
    def _empty_result(self, reason: str) -> Dict[str, Any]:
        """
        Generate empty result with reason.
        
        Args:
            reason: Reason for empty result
        
        Returns:
            Empty result dictionary
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 0,
                'files_deleted': 0,
                'files_archived': 0,
                'folders_deleted': 0,
                'space_freed_bytes': 0,
                'space_freed_mb': 0.0,
                'categories_processed': 0
            },
            'categories': {},
            'operations': [],
            'errors': [],
            'warnings': [reason],
            'artifacts': []
        }
