"""
CORTEX Operations Package - Universal Command Execution

This package provides the universal operations system that powers ALL CORTEX commands:
    - Environment setup (/setup)
    - Story refresh (/CORTEX, refresh cortex story)
    - Workspace cleanup (/CORTEX, cleanup)
    - Documentation updates (/CORTEX, generate documentation)
    - And all future operations

Main API:
    execute_operation(operation_id_or_input, **kwargs) → OperationExecutionReport

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)
from src.operations.operations_orchestrator import (
    OperationsOrchestrator,
    OperationExecutionReport
)
from src.operations.operation_factory import OperationFactory

logger = logging.getLogger(__name__)

# Global factory instance (lazy initialization)
_factory: Optional[OperationFactory] = None


def _get_factory() -> OperationFactory:
    """Get or create global operation factory."""
    global _factory
    if _factory is None:
        _factory = OperationFactory()
    return _factory


def execute_operation(
    operation_id_or_input: str,
    profile: str = 'standard',
    project_root: Optional[Path] = None,
    **kwargs
) -> OperationExecutionReport:
    """
    Execute a CORTEX operation.
    
    This is the main entry point for the universal operations system.
    Supports both operation IDs and natural language input.
    
    Args:
        operation_id_or_input: Either:
            - Operation ID: 'refresh_cortex_story', 'workspace_cleanup'
            - Natural language: 'refresh story', 'cleanup workspace'
            - Slash command: '/CORTEX, refresh cortex story'
            - Help command: 'help', '/CORTEX help', '/help'
        profile: Profile to use (minimal/standard/full) - default 'standard'
        project_root: Project root path (auto-detected if None)
        **kwargs: Additional context to pass to operation
    
    Returns:
        OperationExecutionReport with execution details
    
    Examples:
        # Show help
        report = execute_operation('help')
        
        # By operation ID
        report = execute_operation('refresh_cortex_story')
        
        # By natural language
        report = execute_operation('refresh the story')
        
        # By slash command
        report = execute_operation('/CORTEX, refresh cortex story')
        
        # With profile
        report = execute_operation('environment_setup', profile='full')
        
        # With custom context
        report = execute_operation(
            'refresh_cortex_story',
            project_root=Path('/path/to/cortex'),
            dry_run=True
        )
    """
    try:
        # Special case: help command
        if operation_id_or_input.lower().strip() in ['help', '/help', '/cortex help', 'show help']:
            help_format = kwargs.get('format', 'table')
            help_text = show_help(help_format)
            return OperationExecutionReport(
                operation_id="help",
                operation_name="CORTEX Help",
                success=True,
                modules_executed=[],
                modules_succeeded=[],
                modules_failed=[],
                modules_skipped=[],
                module_results={},
                total_duration_seconds=0.0,
                context={'help_text': help_text},
                errors=[]
            )
        
        factory = _get_factory()
        
        # Resolve operation ID from input
        operation_id = _resolve_operation_id(operation_id_or_input, factory)
        
        if not operation_id:
            logger.error(f"Could not resolve operation from input: {operation_id_or_input}")
            return _create_error_report(
                f"Unknown operation: {operation_id_or_input}",
                f"Available operations: {', '.join(factory.get_available_operations())}"
            )
        
        logger.info(f"Executing operation: {operation_id} (profile: {profile})")
        
        # Auto-detect project root if not provided
        if project_root is None:
            project_root = _find_project_root()
        
        # Build context
        context = {
            'project_root': project_root,
            'profile': profile,
            **kwargs
        }
        
        # Create orchestrator
        orchestrator = factory.create_operation(operation_id, profile, context)
        
        if not orchestrator:
            return _create_error_report(
                f"Failed to create orchestrator for operation: {operation_id}",
                "Check logs for details"
            )
        
        # Execute operation
        report = orchestrator.execute_operation(context)
        
        return report
    
    except Exception as e:
        logger.error(f"Operation execution failed: {e}", exc_info=True)
        return _create_error_report(
            f"Fatal error executing operation: {e}",
            str(e)
        )


def _resolve_operation_id(user_input: str, factory: OperationFactory) -> Optional[str]:
    """
    Resolve operation ID from user input.
    
    Tries:
        1. Direct match (if input is already an operation ID)
        2. Natural language/slash command lookup
    """
    # Check if input is already a valid operation ID
    available_ops = factory.get_available_operations()
    if user_input in available_ops:
        return user_input
    
    # Try natural language/slash command mapping
    operation_id = factory.find_operation_by_input(user_input)
    if operation_id:
        logger.info(f"Resolved '{user_input}' → operation '{operation_id}'")
        return operation_id
    
    return None


def _find_project_root() -> Path:
    """Find CORTEX project root by looking for cortex-operations.yaml."""
    current = Path.cwd()
    
    # Check current directory
    if (current / "cortex-operations.yaml").exists():
        return current
    
    # Check parent directories
    for parent in current.parents:
        if (parent / "cortex-operations.yaml").exists():
            return parent
    
    # Default to current directory
    logger.warning("Could not find project root, using current directory")
    return current


def _create_error_report(message: str, details: str) -> OperationExecutionReport:
    """Create error report for failed operations."""
    return OperationExecutionReport(
        operation_id="error",
        operation_name="Error",
        success=False,
        modules_executed=[],
        modules_succeeded=[],
        modules_failed=[],
        modules_skipped=[],
        module_results={},
        total_duration_seconds=0.0,
        context={},
        errors=[message, details]
    )


def list_operations() -> Dict[str, Dict[str, Any]]:
    """
    List all available operations with their metadata.
    
    Returns:
        Dict mapping operation IDs to operation info
    
    Example:
        ops = list_operations()
        for op_id, info in ops.items():
            print(f"{op_id}: {info['name']}")
            print(f"  Commands: {info['natural_language']}")
            print(f"  Modules: {len(info['modules'])}")
    """
    factory = _get_factory()
    operations = {}
    
    for op_id in factory.get_available_operations():
        op_info = factory.get_operation_info(op_id)
        if op_info:
            operations[op_id] = op_info
    
    return operations


def get_operation_modules(operation_id: str, profile: str = 'standard') -> list[str]:
    """
    Get list of modules for an operation.
    
    Args:
        operation_id: Operation identifier
        profile: Profile to use
    
    Returns:
        List of module IDs
    
    Example:
        modules = get_operation_modules('refresh_cortex_story')
        # ['load_story_template', 'apply_narrator_voice', 'save_story_markdown']
    """
    factory = _get_factory()
    return factory.list_operation_modules(operation_id, profile)


def create_orchestrator(
    operation_id: str,
    profile: str = 'standard',
    context: Optional[Dict[str, Any]] = None
) -> Optional[OperationsOrchestrator]:
    """
    Create orchestrator without executing it.
    
    Useful for:
        - Previewing execution order
        - Custom execution flow
        - Testing
    
    Args:
        operation_id: Operation identifier
        profile: Profile to use
        context: Initial context
    
    Returns:
        Configured orchestrator, or None if failed
    
    Example:
        orchestrator = create_orchestrator('refresh_cortex_story')
        if orchestrator:
            # Preview execution order
            modules = orchestrator.get_module_execution_order()
            print(f"Will execute: {modules}")
            
            # Execute with custom context
            report = orchestrator.execute_operation({'dry_run': True})
    """
    factory = _get_factory()
    return factory.create_operation(operation_id, profile, context)


def show_help(format: str = 'table') -> str:
    """
    Display CORTEX command help.
    
    Shows all available operations with status, examples, and module info.
    
    Args:
        format: Output format - 'table' (default), 'list', or 'detailed'
    
    Returns:
        Formatted help text
    
    Example:
        # Show quick reference table
        print(show_help())
        
        # Show detailed with categories
        print(show_help('detailed'))
        
        # Show simple list
        print(show_help('list'))
    """
    from src.operations.help_command import show_help as _show_help
    return _show_help(format)


# Public API exports
__all__ = [
    # Main execution API
    'execute_operation',
    'list_operations',
    'get_operation_modules',
    'create_orchestrator',
    'show_help',
    
    # Core classes (for advanced usage)
    'BaseOperationModule',
    'OperationModuleMetadata',
    'OperationResult',
    'OperationPhase',
    'OperationStatus',
    'OperationsOrchestrator',
    'OperationExecutionReport',
    'OperationFactory',
]
