"""
Clear Python Cache Module

Removes all __pycache__ directories in the workspace.

SOLID Principles:
- Single Responsibility: Only handles Python cache removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import shutil
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


class ClearPythonCacheModule(BaseOperationModule):
    """
    Cleanup module for removing Python cache directories.
    
    Responsibilities:
    1. Remove __pycache__ directories identified in scan
    2. Track removal success/failure
    3. Calculate space recovered
    4. Report removal results
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="clear_python_cache",
            name="Clear Python Cache",
            description="Remove all __pycache__ directories",
            phase=OperationPhase.PROCESSING,
            priority=20,
            dependencies=["scan_temporary_files"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for cache removal.
        
        Checks:
        1. Scan results available
        """
        issues = []
        
        if 'scan_results' not in context:
            issues.append("Scan results not found in context")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute Python cache removal.
        
        Steps:
        1. Get cache directories from scan results
        2. Remove each directory
        3. Track success/failure
        4. Calculate space recovered
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        scan_results = context['scan_results']
        cache_dirs = scan_results.get('python_cache_dirs', [])
        
        try:
            if not cache_dirs:
                self.log_info("No Python cache directories to remove")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="No Python cache found",
                    data={'removed': 0, 'space_recovered': 0},
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            removal_results = {
                'removed': [],
                'failed': [],
                'space_recovered_bytes': 0,
                'dirs_attempted': len(cache_dirs)
            }
            
            self.log_info(f"Removing {len(cache_dirs)} __pycache__ directories...")
            
            for cache_info in cache_dirs:
                cache_path = project_root / cache_info['path']
                
                try:
                    if cache_path.exists():
                        shutil.rmtree(cache_path)
                        removal_results['removed'].append(cache_info['path'])
                        removal_results['space_recovered_bytes'] += cache_info['size']
                        self.log_info(f"  ✓ Removed: {cache_info['path']}")
                    else:
                        self.log_warning(f"  ⚠ Not found: {cache_info['path']}")
                except (OSError, PermissionError) as e:
                    removal_results['failed'].append({
                        'path': cache_info['path'],
                        'error': str(e)
                    })
                    self.log_error(f"  ✗ Failed: {cache_info['path']} - {e}")
            
            # Update context
            context['cache_removed'] = len(removal_results['removed'])
            context['cache_space_recovered'] = removal_results['space_recovered_bytes']
            
            # Determine status
            if removal_results['failed']:
                status = OperationStatus.WARNING
                message = f"Removed {len(removal_results['removed'])}/{len(cache_dirs)} cache directories ({len(removal_results['failed'])} failed)"
            else:
                status = OperationStatus.SUCCESS
                message = f"Removed {len(removal_results['removed'])} cache directories ({self._format_size(removal_results['space_recovered_bytes'])} recovered)"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data=removal_results,
                warnings=[f"{len(removal_results['failed'])} directories failed to remove"] if removal_results['failed'] else None,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Cache removal failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Cache removal failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
