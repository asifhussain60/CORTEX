"""
Dry-Run Support Mixin for Orchestrators

Provides dry-run functionality to all entry point orchestrators with:
- Copyright header rendering
- Execution mode detection
- Preview mode support
- Result formatting

Author: Asif Hussain
Version: 1.0
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from src.operations.base_operation_module import ExecutionMode, OperationResult
from src.operations.execution_mode_parser import (
    detect_execution_mode,
    format_mode_message,
    should_prompt_confirmation
)


class DryRunOrchestratorMixin:
    """
    Mixin class to add dry-run support to orchestrators.
    
    Features:
        - Copyright header rendering
        - Execution mode detection from natural language
        - Dry-run preview mode
        - User confirmation prompts
        - Result formatting with mode indicator
    
    Usage:
        class MyOrchestrator(DryRunOrchestratorMixin):
            def execute(self, context, execution_mode=ExecutionMode.LIVE):
                # Render copyright header
                self.print_copyright_header("My Operation", "1.0", execution_mode)
                
                # Execute with mode awareness
                if self.is_dry_run(execution_mode):
                    # Preview only logic
                    result = self.preview_operation(context)
                else:
                    # Actual execution logic
                    result = self.execute_operation(context)
                
                # Render footer
                self.print_operation_footer("My Operation", result, execution_mode)
                
                return result
    """
    
    # Template cache
    _templates = None
    
    @classmethod
    def _load_templates(cls) -> Dict:
        """Load response templates for copyright headers."""
        if cls._templates is None:
            template_file = Path(__file__).parent.parent.parent / 'cortex-brain' / 'response-templates.yaml'
            if template_file.exists():
                with open(template_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    cls._templates = data.get('templates', {})
            else:
                cls._templates = {}
        return cls._templates
    
    @staticmethod
    def detect_mode_from_request(request: str) -> ExecutionMode:
        """
        Detect execution mode from natural language request.
        
        Args:
            request: User's natural language request
        
        Returns:
            ExecutionMode (LIVE or DRY_RUN)
        
        Examples:
            >>> self.detect_mode_from_request("preview cleanup")
            ExecutionMode.DRY_RUN
            
            >>> self.detect_mode_from_request("run cleanup")
            ExecutionMode.LIVE
        """
        mode, _ = detect_execution_mode(request)
        return mode
    
    @staticmethod
    def is_dry_run(mode: ExecutionMode) -> bool:
        """Check if mode is dry-run."""
        return mode == ExecutionMode.DRY_RUN
    
    def print_copyright_header(
        self,
        operation_name: str,
        version: str,
        execution_mode: ExecutionMode,
        profile: str = "standard"
    ) -> None:
        """
        Print copyright header for orchestrator execution.
        
        Args:
            operation_name: Name of operation (e.g., "Cleanup", "Optimization")
            version: Operation version
            execution_mode: LIVE or DRY_RUN
            profile: Execution profile (quick/standard/comprehensive)
        """
        templates = self._load_templates()
        
        # Try to use template, fallback to default
        if 'orchestrator_header' in templates:
            # Would use template rendering here - simplified for now
            header = self._render_header_template(
                operation_name, version, execution_mode, profile
            )
        else:
            header = self._default_header(operation_name, version, execution_mode, profile)
        
        print(header)
    
    def _render_header_template(
        self,
        operation_name: str,
        version: str,
        execution_mode: ExecutionMode,
        profile: str
    ) -> str:
        """Render header from template."""
        mode_str = "LIVE" if execution_mode == ExecutionMode.LIVE else "DRY RUN"
        dry_run_note = " (Preview Only - No Changes)" if execution_mode == ExecutionMode.DRY_RUN else ""
        
        return f"""
================================================================================
CORTEX {operation_name} Orchestrator
================================================================================

Version:    {version}
Profile:    {profile}
Mode:       {mode_str}{dry_run_note}
Started:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Author:     Asif Hussain
Copyright:  © 2024-2025 Asif Hussain. All rights reserved.
License:    Proprietary
Repository: https://github.com/asifhussain60/CORTEX

================================================================================
"""
    
    def _default_header(
        self,
        operation_name: str,
        version: str,
        execution_mode: ExecutionMode,
        profile: str
    ) -> str:
        """Default header if template not available."""
        return self._render_header_template(operation_name, version, execution_mode, profile)
    
    def print_operation_footer(
        self,
        operation_name: str,
        result: Any,
        execution_mode: ExecutionMode
    ) -> None:
        """
        Print operation completion footer.
        
        Args:
            operation_name: Name of operation
            result: Operation result (dict or OperationResult)
            execution_mode: LIVE or DRY_RUN
        """
        # Extract metrics from result
        if hasattr(result, 'success'):
            success = result.success
            duration = getattr(result, 'duration_seconds', 0)
            modules_total = len(getattr(result, 'modules_executed', []))
            modules_succeeded = len(getattr(result, 'modules_succeeded', []))
            warnings = len(getattr(result, 'warnings', []))
            errors = len(getattr(result, 'errors', []))
        elif isinstance(result, dict):
            success = result.get('success', False)
            duration = result.get('duration_seconds', 0)
            metrics = result.get('data', {}).get('metrics', {})
            modules_total = metrics.get('modules_total', 0)
            modules_succeeded = metrics.get('modules_succeeded', 0)
            warnings = metrics.get('warnings_count', 0)
            errors = metrics.get('errors_count', 0)
        else:
            success = True
            duration = 0
            modules_total = 0
            modules_succeeded = 0
            warnings = 0
            errors = 0
        
        status = "COMPLETED" if success else "FAILED"
        mode_note = " (DRY RUN - No Changes Made)" if execution_mode == ExecutionMode.DRY_RUN else ""
        
        footer = f"""
================================================================================
CORTEX {operation_name} - {status}{mode_note}
================================================================================

Duration:   {duration:.2f}s
Modules:    {modules_succeeded}/{modules_total} succeeded
"""
        
        if warnings > 0:
            footer += f"Warnings:   {warnings}\n"
        if errors > 0:
            footer += f"Errors:     {errors}\n"
        
        footer += f"""
This orchestration is powered by CORTEX
Copyright © 2024-2025 Asif Hussain. All rights reserved.

================================================================================
"""
        
        print(footer)
    
    def should_confirm(self, operation_name: str, execution_mode: ExecutionMode) -> bool:
        """
        Determine if user confirmation should be requested.
        
        Args:
            operation_name: Name of operation
            execution_mode: Current execution mode
        
        Returns:
            True if confirmation recommended
        """
        return should_prompt_confirmation(execution_mode, operation_name)
    
    def prompt_confirmation(self, operation_name: str, preview_data: Dict) -> bool:
        """
        Prompt user for confirmation before executing.
        
        Args:
            operation_name: Name of operation
            preview_data: Dictionary with preview information
        
        Returns:
            True if user confirms, False otherwise
        """
        print(f"\n⚠️  {operation_name} will make the following changes:\n")
        
        # Display preview
        for key, value in preview_data.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
                for item in value[:5]:  # Show first 5
                    print(f"    • {item}")
                if len(value) > 5:
                    print(f"    ... and {len(value) - 5} more")
            else:
                print(f"  {key}: {value}")
        
        print()
        response = input("Proceed? (yes/no): ").strip().lower()
        return response in ('yes', 'y')
    
    def format_dry_run_result(self, operation_name: str, preview_data: Dict) -> str:
        """
        Format dry-run result for display.
        
        Args:
            operation_name: Name of operation
            preview_data: Dictionary with preview information
        
        Returns:
            Formatted preview string
        """
        lines = [
            f"\n🔍 DRY RUN PREVIEW: {operation_name}",
            "=" * 80,
            "",
            "The following changes WOULD be made in live mode:",
            ""
        ]
        
        for key, value in preview_data.items():
            lines.append(f"• {key}:")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"  {value}")
            lines.append("")
        
        lines.extend([
            "=" * 80,
            "To execute these changes, run without --dry-run or 'preview' keyword",
            ""
        ])
        
        return "\n".join(lines)
    
    def apply_mode_to_modules(self, modules: list, execution_mode: ExecutionMode) -> None:
        """
        Apply execution mode to all modules.
        
        Args:
            modules: List of BaseOperationModule instances
            execution_mode: Mode to apply
        """
        for module in modules:
            if hasattr(module, 'execution_mode'):
                module.execution_mode = execution_mode
