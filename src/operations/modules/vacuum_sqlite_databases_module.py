"""
Vacuum SQLite Databases Module

Optimizes SQLite databases to recover space and improve performance.

SOLID Principles:
- Single Responsibility: Only handles SQLite optimization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
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


class VacuumSQLiteDatabasesModule(BaseOperationModule):
    """
    Cleanup module for optimizing SQLite databases.
    
    Responsibilities:
    1. Vacuum CORTEX brain databases
    2. Calculate space recovered
    3. Report optimization results
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="vacuum_sqlite_databases",
            name="Vacuum SQLite Databases",
            description="Optimize CORTEX brain databases",
            phase=OperationPhase.PROCESSING,
            priority=30,
            dependencies=[],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for database optimization.
        
        Checks:
        1. Project root available
        2. Brain directory exists
        """
        issues = []
        
        if 'project_root' not in context:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(context['project_root'])
        brain_dir = project_root / "cortex-brain"
        
        if not brain_dir.exists():
            issues.append("cortex-brain directory not found")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute SQLite database optimization.
        
        Steps:
        1. Find all SQLite databases in cortex-brain
        2. Get size before vacuum
        3. Run VACUUM on each database
        4. Calculate space recovered
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        brain_dir = project_root / "cortex-brain"
        
        try:
            # Find all SQLite databases
            db_files = list(brain_dir.glob("**/*.db")) + list(brain_dir.glob("**/*.sqlite"))
            
            if not db_files:
                self.log_info("No SQLite databases found")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="No databases to vacuum",
                    data={'optimized': 0, 'space_recovered': 0},
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            vacuum_results = {
                'optimized': [],
                'failed': [],
                'space_recovered_bytes': 0,
                'databases_attempted': len(db_files)
            }
            
            self.log_info(f"Vacuuming {len(db_files)} SQLite databases...")
            
            for db_path in db_files:
                try:
                    # Get size before vacuum
                    size_before = db_path.stat().st_size
                    
                    # Run VACUUM
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("VACUUM")
                    conn.close()
                    
                    # Get size after vacuum
                    size_after = db_path.stat().st_size
                    space_recovered = size_before - size_after
                    
                    vacuum_results['optimized'].append({
                        'path': str(db_path.relative_to(project_root)),
                        'size_before': size_before,
                        'size_after': size_after,
                        'space_recovered': space_recovered
                    })
                    vacuum_results['space_recovered_bytes'] += space_recovered
                    
                    self.log_info(f"  ✓ Vacuumed: {db_path.name} ({self._format_size(space_recovered)} recovered)")
                    
                except (sqlite3.Error, OSError) as e:
                    vacuum_results['failed'].append({
                        'path': str(db_path.relative_to(project_root)),
                        'error': str(e)
                    })
                    self.log_error(f"  ✗ Failed: {db_path.name} - {e}")
            
            # Update context
            context['databases_optimized'] = len(vacuum_results['optimized'])
            context['database_space_recovered'] = vacuum_results['space_recovered_bytes']
            
            # Determine status
            if vacuum_results['failed']:
                status = OperationStatus.WARNING
                message = f"Optimized {len(vacuum_results['optimized'])}/{len(db_files)} databases ({len(vacuum_results['failed'])} failed)"
            else:
                status = OperationStatus.SUCCESS
                message = f"Optimized {len(vacuum_results['optimized'])} databases ({self._format_size(vacuum_results['space_recovered_bytes'])} recovered)"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data=vacuum_results,
                warnings=[f"{len(vacuum_results['failed'])} databases failed to optimize"] if vacuum_results['failed'] else None,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Database optimization failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Database optimization failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        if size_bytes < 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
