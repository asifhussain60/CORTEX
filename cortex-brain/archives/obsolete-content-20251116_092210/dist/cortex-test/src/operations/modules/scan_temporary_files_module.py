"""
Scan Temporary Files Module

Identifies temporary files for cleanup in CORTEX workspace.

SOLID Principles:
- Single Responsibility: Only handles temporary file scanning
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, List, Set
from datetime import datetime, timedelta

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class ScanTemporaryFilesModule(BaseOperationModule):
    """
    Cleanup module for scanning temporary files.
    
    Responsibilities:
    1. Scan for temporary files (*.tmp, *.cache, etc.)
    2. Identify build artifacts
    3. Find Python cache directories
    4. Locate old log files
    5. Track file locations and sizes
    """
    
    # Temporary file patterns
    TEMP_EXTENSIONS = {'.tmp', '.temp', '.cache', '.bak', '.backup', '.old'}
    
    # Directories to scan
    SCAN_DIRS = ['logs', 'cortex-brain', 'tests', 'scripts']
    
    # Directories to skip
    SKIP_DIRS = {'.git', '.venv', 'venv', 'node_modules', '.env', 'site'}
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="scan_temporary_files",
            name="Scan Temporary Files",
            description="Identify temporary files and build artifacts for cleanup",
            phase=OperationPhase.PREPARATION,
            priority=10,
            dependencies=[],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for scanning.
        
        Checks:
        1. Project root exists
        """
        issues = []
        
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
        Execute temporary file scanning.
        
        Steps:
        1. Scan for temporary files by extension
        2. Find Python cache directories
        3. Identify old log files
        4. Calculate total size
        5. Store scan results in context
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        
        try:
            scan_results = {
                'temp_files': [],
                'python_cache_dirs': [],
                'old_log_files': [],
                'total_temp_size_bytes': 0,
                'total_cache_size_bytes': 0,
                'total_log_size_bytes': 0,
                'scan_time': None
            }
            
            # Scan for temporary files
            self.log_info("Scanning for temporary files...")
            temp_files = self._scan_temp_files(project_root)
            scan_results['temp_files'] = temp_files
            scan_results['total_temp_size_bytes'] = sum(f['size'] for f in temp_files)
            
            self.log_info(f"Found {len(temp_files)} temporary files ({self._format_size(scan_results['total_temp_size_bytes'])})")
            
            # Scan for Python cache directories
            self.log_info("Scanning for Python cache directories...")
            cache_dirs = self._scan_python_cache(project_root)
            scan_results['python_cache_dirs'] = cache_dirs
            scan_results['total_cache_size_bytes'] = sum(d['size'] for d in cache_dirs)
            
            self.log_info(f"Found {len(cache_dirs)} __pycache__ directories ({self._format_size(scan_results['total_cache_size_bytes'])})")
            
            # Scan for old log files (>30 days)
            logs_dir = project_root / "logs"
            if logs_dir.exists():
                self.log_info("Scanning for old log files (>30 days)...")
                old_logs = self._scan_old_logs(logs_dir, days=30)
                scan_results['old_log_files'] = old_logs
                scan_results['total_log_size_bytes'] = sum(f['size'] for f in old_logs)
                
                self.log_info(f"Found {len(old_logs)} old log files ({self._format_size(scan_results['total_log_size_bytes'])})")
            
            # Calculate totals
            total_size = (
                scan_results['total_temp_size_bytes'] +
                scan_results['total_cache_size_bytes'] +
                scan_results['total_log_size_bytes']
            )
            
            total_items = (
                len(scan_results['temp_files']) +
                len(scan_results['python_cache_dirs']) +
                len(scan_results['old_log_files'])
            )
            
            scan_results['scan_time'] = (datetime.now() - start_time).total_seconds()
            
            # Store in context for other modules
            context['scan_results'] = scan_results
            context['cleanup_candidates'] = total_items
            context['cleanup_size_bytes'] = total_size
            
            message = f"Scan complete: {total_items} items found ({self._format_size(total_size)})"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=message,
                data=scan_results,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Scan failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Scan failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _scan_temp_files(self, root: Path) -> List[Dict[str, Any]]:
        """Scan for temporary files by extension."""
        temp_files = []
        
        for scan_dir in self.SCAN_DIRS:
            dir_path = root / scan_dir
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.rglob('*'):
                # Skip directories
                if file_path.is_dir():
                    continue
                
                # Skip if in excluded directory
                if any(skip in file_path.parts for skip in self.SKIP_DIRS):
                    continue
                
                # Check extension
                if file_path.suffix.lower() in self.TEMP_EXTENSIONS:
                    try:
                        size = file_path.stat().st_size
                        temp_files.append({
                            'path': str(file_path.relative_to(root)),
                            'size': size,
                            'type': 'temp_file'
                        })
                    except (OSError, PermissionError):
                        pass
        
        return temp_files
    
    def _scan_python_cache(self, root: Path) -> List[Dict[str, Any]]:
        """Scan for Python __pycache__ directories."""
        cache_dirs = []
        
        for cache_dir in root.rglob('__pycache__'):
            # Skip if in excluded directory
            if any(skip in cache_dir.parts for skip in self.SKIP_DIRS):
                continue
            
            try:
                # Calculate directory size
                total_size = sum(
                    f.stat().st_size 
                    for f in cache_dir.rglob('*') 
                    if f.is_file()
                )
                
                cache_dirs.append({
                    'path': str(cache_dir.relative_to(root)),
                    'size': total_size,
                    'type': 'python_cache'
                })
            except (OSError, PermissionError):
                pass
        
        return cache_dirs
    
    def _scan_old_logs(self, logs_dir: Path, days: int = 30) -> List[Dict[str, Any]]:
        """Scan for log files older than specified days."""
        old_logs = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in logs_dir.rglob('*.log'):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    size = log_file.stat().st_size
                    old_logs.append({
                        'path': str(log_file.relative_to(logs_dir.parent)),
                        'size': size,
                        'age_days': (datetime.now() - mtime).days,
                        'type': 'old_log'
                    })
            except (OSError, PermissionError):
                pass
        
        return old_logs
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
