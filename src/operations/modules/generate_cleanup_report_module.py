"""
Generate Cleanup Report Module

Creates comprehensive cleanup summary report.

SOLID Principles:
- Single Responsibility: Only handles report generation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

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


class GenerateCleanupReportModule(BaseOperationModule):
    """
    Finalization module for generating cleanup report.
    
    Responsibilities:
    1. Collect cleanup results from all modules
    2. Calculate total space recovered
    3. Generate formatted report
    4. Display summary
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="generate_cleanup_report",
            name="Generate Cleanup Report",
            description="Create comprehensive cleanup summary",
            phase=OperationPhase.FINALIZATION,
            priority=100,
            dependencies=[],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for report generation.
        
        Checks:
        1. Context available
        """
        issues = []
        
        if not context:
            issues.append("Context not available")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute cleanup report generation.
        
        Steps:
        1. Collect cleanup results
        2. Calculate totals
        3. Generate formatted report
        4. Display summary
        """
        start_time = datetime.now()
        
        try:
            # Collect cleanup results
            scan_results = context.get('scan_results', {})
            logs_removed = context.get('logs_removed', 0)
            logs_space = context.get('logs_space_recovered', 0)
            cache_removed = context.get('cache_removed', 0)
            cache_space = context.get('cache_space_recovered', 0)
            databases_optimized = context.get('databases_optimized', 0)
            database_space = context.get('database_space_recovered', 0)
            orphaned_removed = context.get('orphaned_removed', 0)
            orphaned_space = context.get('orphaned_space_recovered', 0)
            
            # Calculate totals
            total_items_removed = logs_removed + cache_removed + orphaned_removed
            total_space_recovered = logs_space + cache_space + database_space + orphaned_space
            
            # Generate report
            report_lines = [
                "",
                "═" * 70,
                "🧹 CORTEX WORKSPACE CLEANUP REPORT",
                "═" * 70,
                "",
                "📊 CLEANUP SUMMARY",
                "─" * 70,
                f"  Old Log Files Removed:        {logs_removed:>6} files ({self._format_size(logs_space)})",
                f"  Python Cache Removed:         {cache_removed:>6} dirs  ({self._format_size(cache_space)})",
                f"  Orphaned Files Removed:       {orphaned_removed:>6} files ({self._format_size(orphaned_space)})",
                f"  Databases Optimized:          {databases_optimized:>6} dbs   ({self._format_size(database_space)})",
                "─" * 70,
                f"  Total Items Removed:          {total_items_removed:>6}",
                f"  Total Space Recovered:        {self._format_size(total_space_recovered)}",
                "",
            ]
            
            # Add scan statistics if available
            if scan_results:
                report_lines.extend([
                    "📈 WORKSPACE HEALTH",
                    "─" * 70,
                    f"  Files Scanned:                {scan_results.get('files_scanned', 0):>6}",
                    f"  Directories Scanned:          {scan_results.get('directories_scanned', 0):>6}",
                    f"  Total Workspace Size:         {self._format_size(scan_results.get('total_size', 0))}",
                    "",
                ])
            
            # Add recommendations
            report_lines.extend([
                "💡 RECOMMENDATIONS",
                "─" * 70,
            ])
            
            if total_items_removed == 0:
                report_lines.append("  ✓ Workspace is clean - no cleanup needed")
            else:
                report_lines.append(f"  ✓ Successfully cleaned up {total_items_removed} items")
                report_lines.append(f"  ✓ Recovered {self._format_size(total_space_recovered)} of disk space")
            
            if databases_optimized > 0:
                report_lines.append(f"  ✓ Optimized {databases_optimized} SQLite databases for better performance")
            
            # Add next steps
            report_lines.extend([
                "",
                "🎯 NEXT STEPS",
                "─" * 70,
                "  • Run tests to ensure everything still works: pytest",
                "  • Commit any important changes: git status",
                "  • Run cleanup periodically: /CORTEX cleanup",
                "",
                "═" * 70,
                f"⏱️  Cleanup completed in {(datetime.now() - start_time).total_seconds():.2f}s",
                "═" * 70,
                ""
            ])
            
            report = "\n".join(report_lines)
            
            # Display report
            self.log_info("\n" + report)
            
            # Update context
            context['cleanup_report'] = report
            context['cleanup_summary'] = {
                'total_items_removed': total_items_removed,
                'total_space_recovered': total_space_recovered,
                'logs_removed': logs_removed,
                'cache_removed': cache_removed,
                'databases_optimized': databases_optimized,
                'orphaned_removed': orphaned_removed
            }
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Cleanup complete: {total_items_removed} items removed, {self._format_size(total_space_recovered)} recovered",
                data={
                    'report': report,
                    'summary': context['cleanup_summary']
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Report generation failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Report generation failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        if size_bytes < 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
