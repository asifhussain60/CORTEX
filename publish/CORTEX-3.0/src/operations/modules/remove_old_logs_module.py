"""
Remove Old Logs Module

Deletes log files older than specified retention period.

SOLID Principles:
- Single Responsibility: Only handles old log removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

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


class RemoveOldLogsModule(BaseOperationModule):
    """
    Cleanup module for removing old log files.
    
    Responsibilities:
    1. Remove log files identified in scan
    2. Track removal success/failure
    3. Calculate space recovered
    4. Report removal results
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="remove_old_logs",
            name="Remove Old Log Files",
            description="Delete log files older than 30 days",
            phase=OperationPhase.PROCESSING,
            priority=10,
            dependencies=["scan_temporary_files"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for log removal.
        
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
        Execute old log removal.
        
        Steps:
        1. Get old log files from scan results
        2. Remove each file
        3. Track success/failure
        4. Calculate space recovered
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        scan_results = context['scan_results']
        old_logs = scan_results.get('old_log_files', [])
        
        try:
            if not old_logs:
                self.log_info("No old log files to remove")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="No old log files found",
                    data={'removed': 0, 'space_recovered': 0},
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            removal_results = {
                'removed': [],
                'failed': [],
                'space_recovered_bytes': 0,
                'files_attempted': len(old_logs)
            }
            
            self.log_info(f"Removing {len(old_logs)} old log files...")
            
            for log_info in old_logs:
                log_path = project_root / log_info['path']
                
                try:
                    if log_path.exists():
                        log_path.unlink()
                        removal_results['removed'].append(log_info['path'])
                        removal_results['space_recovered_bytes'] += log_info['size']
                        self.log_info(f"  ✓ Removed: {log_info['path']}")
                    else:
                        self.log_warning(f"  ⚠ Not found: {log_info['path']}")
                except (OSError, PermissionError) as e:
                    removal_results['failed'].append({
                        'path': log_info['path'],
                        'error': str(e)
                    })
                    self.log_error(f"  ✗ Failed: {log_info['path']} - {e}")
            
            # Update context
            context['logs_removed'] = len(removal_results['removed'])
            context['logs_space_recovered'] = removal_results['space_recovered_bytes']
            
            # Determine status
            if removal_results['failed']:
                status = OperationStatus.WARNING
                message = f"Removed {len(removal_results['removed'])}/{len(old_logs)} log files ({len(removal_results['failed'])} failed)"
            else:
                status = OperationStatus.SUCCESS
                message = f"Removed {len(removal_results['removed'])} log files ({self._format_size(removal_results['space_recovered_bytes'])} recovered)"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data=removal_results,
                warnings=[f"{len(removal_results['failed'])} files failed to remove"] if removal_results['failed'] else None,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Log removal failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Log removal failed: {str(e)}",
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
