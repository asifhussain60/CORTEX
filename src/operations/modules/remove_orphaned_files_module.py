"""
Remove Orphaned Files Module

Identifies and removes files not tracked by Git.

SOLID Principles:
- Single Responsibility: Only handles orphaned file removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
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


class RemoveOrphanedFilesModule(BaseOperationModule):
    """
    Cleanup module for removing orphaned files.
    
    Responsibilities:
    1. Identify files not tracked by Git
    2. Remove safe orphaned files
    3. Track removal success/failure
    4. Report removal results
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="remove_orphaned_files",
            name="Remove Orphaned Files",
            description="Remove files not tracked by Git",
            phase=OperationPhase.PROCESSING,
            priority=40,
            dependencies=[],
            optional=True,  # Optional - may have false positives
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for orphaned file removal.
        
        Checks:
        1. Git available
        2. Project is a Git repository
        """
        issues = []
        
        if 'project_root' not in context:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(context['project_root'])
        git_dir = project_root / ".git"
        
        if not git_dir.exists():
            issues.append("Not a Git repository")
            return False, issues
        
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Git not available")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute orphaned file removal.
        
        Steps:
        1. Get untracked files from Git
        2. Filter out safe files (.gitignore, etc.)
        3. Remove orphaned files
        4. Track success/failure
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        
        try:
            # Get untracked files
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            untracked_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            if not untracked_files:
                self.log_info("No orphaned files found")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="No orphaned files to remove",
                    data={'removed': 0, 'space_recovered': 0},
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Filter out safe files (config examples, templates, etc.)
            safe_patterns = [
                'cortex.config.example.json',
                'cortex.config.template.json',
                '.env.example',
                'LICENSE',
                'README.md'
            ]
            
            files_to_remove = [
                f for f in untracked_files
                if not any(pattern in f for pattern in safe_patterns)
            ]
            
            if not files_to_remove:
                self.log_info("All untracked files are safe, skipping removal")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message=f"{len(untracked_files)} untracked files are safe",
                    data={'removed': 0, 'skipped': len(untracked_files)},
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            removal_results = {
                'removed': [],
                'failed': [],
                'space_recovered_bytes': 0,
                'files_attempted': len(files_to_remove)
            }
            
            self.log_info(f"Removing {len(files_to_remove)} orphaned files...")
            
            for file_path_str in files_to_remove:
                file_path = project_root / file_path_str
                
                try:
                    if file_path.exists():
                        size = file_path.stat().st_size
                        file_path.unlink()
                        removal_results['removed'].append(file_path_str)
                        removal_results['space_recovered_bytes'] += size
                        self.log_info(f"  ✓ Removed: {file_path_str}")
                    else:
                        self.log_warning(f"  ⚠ Not found: {file_path_str}")
                except (OSError, PermissionError) as e:
                    removal_results['failed'].append({
                        'path': file_path_str,
                        'error': str(e)
                    })
                    self.log_error(f"  ✗ Failed: {file_path_str} - {e}")
            
            # Update context
            context['orphaned_removed'] = len(removal_results['removed'])
            context['orphaned_space_recovered'] = removal_results['space_recovered_bytes']
            
            # Determine status
            if removal_results['failed']:
                status = OperationStatus.WARNING
                message = f"Removed {len(removal_results['removed'])}/{len(files_to_remove)} orphaned files ({len(removal_results['failed'])} failed)"
            else:
                status = OperationStatus.SUCCESS
                message = f"Removed {len(removal_results['removed'])} orphaned files ({self._format_size(removal_results['space_recovered_bytes'])} recovered)"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data=removal_results,
                warnings=[f"{len(removal_results['failed'])} files failed to remove"] if removal_results['failed'] else None,
                duration_seconds=duration_seconds
            )
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Git command failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Git command failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
        except Exception as e:
            self.log_error(f"Orphaned file removal failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Orphaned file removal failed: {str(e)}",
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
