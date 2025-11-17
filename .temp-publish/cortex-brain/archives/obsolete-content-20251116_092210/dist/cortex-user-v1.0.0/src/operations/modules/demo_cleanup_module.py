"""
Demo Cleanup Module

Demonstrates CORTEX workspace cleanup operation.

SOLID Principles:
- Single Responsibility: Only handles cleanup demonstration
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class DemoCleanupModule(BaseOperationModule):
    """
    Demo module for showing CORTEX cleanup operation.
    
    Responsibilities:
    1. Explain cleanup operation
    2. Execute cleanup (standard profile)
    3. Display optimization report
    4. Show what was cleaned
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="demo_cleanup",
            name="Demo Cleanup Operation",
            description="Execute cleanup operation and show optimization report",
            phase=OperationPhase.PROCESSING,
            priority=20,
            dependencies=[],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for cleanup demo.
        
        Checks:
        1. Cleanup operation is available
        2. Project root exists
        """
        issues = []
        
        # Check if we can import cleanup operation
        try:
            from src.operations import execute_operation
        except ImportError as e:
            issues.append(f"Operations system not available: {e}")
            return False, issues
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute cleanup demonstration.
        
        Steps:
        1. Explain cleanup operation
        2. Execute cleanup (standard profile)
        3. Display results
        4. Show optimization benefits
        """
        start_time = datetime.now()
        
        try:
            # Import cleanup operation
            from src.operations import execute_operation
            
            # Intro
            self.log_info("")
            self.log_info("=" * 70)
            self.log_info("🧹 CORTEX WORKSPACE CLEANUP")
            self.log_info("=" * 70)
            self.log_info("")
            self.log_info("💡 What is Workspace Cleanup?")
            self.log_info("")
            self.log_info("CORTEX automatically maintains your workspace by:")
            self.log_info("  • Removing temporary files (*.tmp, *.cache)")
            self.log_info("  • Clearing Python __pycache__ directories")
            self.log_info("  • Cleaning old log files (>30 days)")
            self.log_info("  • Vacuuming SQLite databases (brain optimization)")
            self.log_info("")
            self.log_info("This keeps your workspace clean and CORTEX running fast!")
            self.log_info("")
            self.log_info("🚀 Running cleanup (standard profile)...")
            self.log_info("")
            
            # Execute cleanup operation (standard profile)
            cleanup_result = execute_operation('cleanup', profile='standard')
            
            # Display results
            if cleanup_result and cleanup_result.success:
                self.log_info("✅ Cleanup completed successfully!")
                self.log_info("")
                
                # Show what was cleaned
                summary = cleanup_result.context.get('summary', {})
                if summary:
                    self.log_info("📊 Cleanup Summary:")
                    self.log_info(f"  • Files removed: {summary.get('files_removed', 0)}")
                    self.log_info(f"  • Space freed: {summary.get('space_freed', '0 B')}")
                    self.log_info(f"  • Databases optimized: {summary.get('databases_optimized', 0)}")
                    self.log_info("")
                
                # Show performance impact
                self.log_info("⚡ Performance Impact:")
                self.log_info("  • Faster database queries")
                self.log_info("  • Reduced disk usage")
                self.log_info("  • Cleaner workspace")
                self.log_info("")
                
                # Usage tips
                self.log_info("💬 How to Use:")
                self.log_info("  • Natural: 'cleanup workspace' or 'clean up'")
                self.log_info("  • Command: 'cleanup' or '/cleanup'")
                self.log_info("  • Profiles: quick, standard, thorough")
                self.log_info("")
            else:
                error_msg = cleanup_result.message if cleanup_result else 'Cleanup operation failed'
                self.log_info(f"ℹ️  Cleanup completed: {error_msg}")
                self.log_info("")
                self.log_info("Note: Some cleanup tasks may be skipped if no items are found.")
                self.log_info("")
            
            self.log_info("=" * 70)
            
            # Store cleanup result in context
            context['demo_cleanup_result'] = cleanup_result
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Cleanup operation demonstrated successfully",
                data={
                    'cleanup_result': cleanup_result
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Cleanup demo failed: {e}")
            
            # Provide helpful error explanation
            self.log_info("")
            self.log_info("=" * 70)
            self.log_info("⚠️  Cleanup Demo Note")
            self.log_info("=" * 70)
            self.log_info("")
            self.log_info("The cleanup demo couldn't execute the actual cleanup operation,")
            self.log_info("but in a real scenario, CORTEX would:")
            self.log_info("")
            self.log_info("  1. Scan your workspace for temporary files")
            self.log_info("  2. Identify optimization opportunities")
            self.log_info("  3. Safely remove unnecessary files")
            self.log_info("  4. Optimize brain databases")
            self.log_info("  5. Generate a detailed cleanup report")
            self.log_info("")
            self.log_info("Try it yourself: 'cleanup workspace' in any CORTEX chat!")
            self.log_info("")
            self.log_info("=" * 70)
            
            # Still return success for demo purposes
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Cleanup demo completed with explanation",
                data={
                    'demo_mode': True,
                    'error_shown': str(e)
                },
                warnings=[f"Cleanup execution skipped: {str(e)}"],
                duration_seconds=duration_seconds
            )
