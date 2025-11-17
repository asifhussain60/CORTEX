"""
Setup Completion Module

Generates comprehensive setup summary report.

SOLID Principles:
- Single Responsibility: Only handles setup completion and reporting
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


class SetupCompletionModule(BaseOperationModule):
    """
    Setup module for generating completion summary.
    
    Responsibilities:
    1. Collect results from all setup modules
    2. Generate human-readable summary
    3. Identify any warnings or issues
    4. Provide next steps
    5. Output comprehensive setup report
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="setup_completion",
            name="Setup Completion & Summary",
            description="Generate comprehensive setup summary report",
            phase=OperationPhase.FINALIZATION,
            priority=100,  # Runs last
            dependencies=[],  # No strict dependencies - summarizes all
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for setup completion.
        
        Minimal requirements - can always run.
        """
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute setup completion and generate summary.
        
        Steps:
        1. Collect module execution results from context
        2. Categorize results (success, warning, failure)
        3. Generate summary report
        4. Provide next steps
        """
        start_time = datetime.now()
        
        try:
            # Build summary from context
            summary = self._build_summary(context)
            
            # Generate report text
            report = self._generate_report(summary)
            
            # Log summary
            self.log_info("=" * 60)
            self.log_info("CORTEX SETUP SUMMARY")
            self.log_info("=" * 60)
            for line in report.split('\n'):
                self.log_info(line)
            self.log_info("=" * 60)
            
            # Determine overall status
            if summary['critical_failures'] > 0:
                status = OperationStatus.FAILED
                message = f"Setup completed with {summary['critical_failures']} critical failures"
            elif summary['warnings'] > 0:
                status = OperationStatus.WARNING
                message = f"Setup completed with {summary['warnings']} warnings"
            else:
                status = OperationStatus.SUCCESS
                message = "Setup completed successfully!"
            
            context['setup_complete'] = True
            context['setup_summary'] = summary
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=summary['critical_failures'] == 0,
                status=status,
                message=message,
                data={
                    'summary': summary,
                    'report': report,
                    'total_modules': summary['total_modules'],
                    'successful': summary['successful'],
                    'warnings': summary['warnings'],
                    'failures': summary['failures']
                },
                warnings=summary['warning_messages'] if summary['warning_messages'] else None,
                errors=summary['error_messages'] if summary['error_messages'] else None,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Setup completion failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Setup completion failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _build_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build summary from context.
        
        Args:
            context: Operation context with module results
        
        Returns:
            Summary dictionary
        """
        summary = {
            'total_modules': 0,
            'successful': 0,
            'warnings': 0,
            'failures': 0,
            'critical_failures': 0,
            'skipped': 0,
            'module_details': [],
            'warning_messages': [],
            'error_messages': [],
            'next_steps': []
        }
        
        # Extract key information from context
        project_root = context.get('project_root', 'Unknown')
        platform = context.get('platform_display', 'Unknown')
        brain_initialized = context.get('brain_initialized', False)
        venv_active = context.get('venv_active', False)
        git_synced = context.get('git_synced', False)
        
        # Platform detection
        summary['module_details'].append({
            'name': 'Platform Detection',
            'status': '✓ Success' if platform != 'Unknown' else '✗ Failed',
            'info': f'Platform: {platform}'
        })
        if platform != 'Unknown':
            summary['successful'] += 1
        else:
            summary['failures'] += 1
        
        # Project validation
        if project_root != 'Unknown':
            summary['module_details'].append({
                'name': 'Project Validation',
                'status': '✓ Success',
                'info': f'Root: {project_root}'
            })
            summary['successful'] += 1
        else:
            summary['module_details'].append({
                'name': 'Project Validation',
                'status': '✗ Failed',
                'info': 'Project root not found'
            })
            summary['critical_failures'] += 1
            summary['error_messages'].append("Project validation failed")
        
        # Virtual environment
        if venv_active:
            summary['module_details'].append({
                'name': 'Virtual Environment',
                'status': '✓ Active',
                'info': context.get('venv_path', 'Unknown')
            })
            summary['successful'] += 1
        else:
            venv_path = context.get('venv_path')
            activation_cmd = context.get('activation_command')
            if venv_path and activation_cmd:
                summary['module_details'].append({
                    'name': 'Virtual Environment',
                    'status': '⚠ Not Active',
                    'info': f'Please activate: {activation_cmd}'
                })
                summary['warnings'] += 1
                summary['warning_messages'].append(f"Virtual environment not active: {activation_cmd}")
                summary['next_steps'].append(f"Activate virtual environment: {activation_cmd}")
            else:
                summary['module_details'].append({
                    'name': 'Virtual Environment',
                    'status': '⊘ Skipped',
                    'info': 'Virtual environment not configured'
                })
                summary['skipped'] += 1
        
        # Brain initialization
        if brain_initialized:
            summary['module_details'].append({
                'name': 'Brain Initialization',
                'status': '✓ Success',
                'info': 'All tiers initialized'
            })
            summary['successful'] += 1
        else:
            summary['module_details'].append({
                'name': 'Brain Initialization',
                'status': '⊘ Skipped',
                'info': 'Brain not initialized'
            })
            summary['skipped'] += 1
        
        # Git sync
        if git_synced:
            summary['module_details'].append({
                'name': 'Git Sync',
                'status': '✓ Synced',
                'info': 'Repository up to date'
            })
            summary['successful'] += 1
        else:
            summary['module_details'].append({
                'name': 'Git Sync',
                'status': '⊘ Skipped',
                'info': 'Git sync not performed'
            })
            summary['skipped'] += 1
        
        # Update totals
        summary['total_modules'] = (
            summary['successful'] + 
            summary['warnings'] + 
            summary['failures'] + 
            summary['skipped']
        )
        
        # Add general next steps
        if not venv_active and context.get('activation_command'):
            summary['next_steps'].append("1. Activate virtual environment")
        if venv_active:
            summary['next_steps'].append("1. Start using CORTEX!")
            summary['next_steps'].append("2. Try: '/CORTEX' in GitHub Copilot Chat")
            summary['next_steps'].append("3. Or say: 'setup environment' in natural language")
        
        return summary
    
    def _generate_report(self, summary: Dict[str, Any]) -> str:
        """
        Generate human-readable report.
        
        Args:
            summary: Summary dictionary
        
        Returns:
            Report string
        """
        lines = []
        
        # Header
        lines.append("")
        lines.append("CORTEX Setup Complete!")
        lines.append("")
        
        # Statistics
        lines.append(f"Modules Processed: {summary['total_modules']}")
        lines.append(f"  ✓ Successful:    {summary['successful']}")
        lines.append(f"  ⚠ Warnings:      {summary['warnings']}")
        lines.append(f"  ✗ Failures:      {summary['failures']}")
        lines.append(f"  ⊘ Skipped:       {summary['skipped']}")
        lines.append("")
        
        # Module details
        lines.append("Module Status:")
        for detail in summary['module_details']:
            lines.append(f"  {detail['status']:15} {detail['name']}")
            if detail.get('info'):
                lines.append(f"                    └─ {detail['info']}")
        lines.append("")
        
        # Warnings
        if summary['warning_messages']:
            lines.append("Warnings:")
            for warning in summary['warning_messages']:
                lines.append(f"  ⚠ {warning}")
            lines.append("")
        
        # Errors
        if summary['error_messages']:
            lines.append("Errors:")
            for error in summary['error_messages']:
                lines.append(f"  ✗ {error}")
            lines.append("")
        
        # Next steps
        if summary['next_steps']:
            lines.append("Next Steps:")
            for step in summary['next_steps']:
                lines.append(f"  {step}")
            lines.append("")
        
        return '\n'.join(lines)
