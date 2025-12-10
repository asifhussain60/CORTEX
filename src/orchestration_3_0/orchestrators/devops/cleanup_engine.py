"""
Cleanup Engine - CORTEX 4.0 DevOps Orchestrator

System cleanup and optimization.

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CleanupEngine:
    """
    System cleanup engine for DevOps orchestrator.
    
    Cleanup types:
    - standard: Remove pycache, temp files
    - deep: Remove all generated files, logs
    - full: Complete cleanup including caches
    """
    
    def __init__(self):
        """Initialize cleanup engine."""
        self.cleanup_patterns = {
            'pycache': '**/__pycache__',
            'pyc': '**/*.pyc',
            'temp': '**/*.tmp',
            'logs': '**/*.log',
            'cache': '**/cache/**'
        }
    
    def cleanup(
        self,
        project_path: str,
        cleanup_type: str = 'standard',
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute cleanup operation.
        
        Args:
            project_path: Project directory path
            cleanup_type: Type of cleanup (standard/deep/full)
            dry_run: Preview cleanup without deleting
            
        Returns:
            Cleanup result
        """
        files_removed = 0
        bytes_freed = 0
        
        project = Path(project_path)
        
        patterns = self._get_cleanup_patterns(cleanup_type)
        
        for pattern in patterns:
            for path in project.glob(pattern):
                if path.is_file():
                    size = path.stat().st_size
                    
                    if not dry_run:
                        try:
                            path.unlink()
                            files_removed += 1
                            bytes_freed += size
                        except Exception as e:
                            logger.warning(f"Failed to remove {path}: {e}")
                    else:
                        files_removed += 1
                        bytes_freed += size
        
        logger.info(
            f"Cleanup ({cleanup_type}): {files_removed} files, "
            f"{bytes_freed / 1024 / 1024:.2f} MB freed"
        )
        
        return {
            'success': True,
            'cleanup_type': cleanup_type,
            'files_removed': files_removed,
            'bytes_freed': bytes_freed,
            'dry_run': dry_run
        }
    
    def _get_cleanup_patterns(self, cleanup_type: str) -> list[str]:
        """Get cleanup patterns for type."""
        if cleanup_type == 'standard':
            return [
                self.cleanup_patterns['pycache'],
                self.cleanup_patterns['pyc'],
                self.cleanup_patterns['temp']
            ]
        elif cleanup_type == 'deep':
            return [
                self.cleanup_patterns['pycache'],
                self.cleanup_patterns['pyc'],
                self.cleanup_patterns['temp'],
                self.cleanup_patterns['logs']
            ]
        elif cleanup_type == 'full':
            return list(self.cleanup_patterns.values())
        else:
            return []
