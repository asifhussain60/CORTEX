"""
Execution Mode Parser - Natural Language Detection

This module parses user requests to detect whether they want dry-run or live execution.

Natural Language Patterns:
    Dry-run: "preview", "test", "simulate", "dry run", "what would", "show me what"
    Live: "execute", "run", "apply", "do it", "make changes"

Author: Asif Hussain
Version: 1.0
"""

import re
from typing import Tuple
from src.operations.base_operation_module import ExecutionMode


# Dry-run indicators (user wants preview only)
DRY_RUN_PATTERNS = [
    r'\bdry[\s-]?run\b',
    r'\bpreview\b',
    r'\bsimulate\b',
    r'\btest\b',
    r'\bwhat would\b',
    r'\bshow me what\b',
    r'\bwhat happens if\b',
    r'\bcheck what\b',
    r'\bjust show\b',
    r'\bdon\'?t (actually )?change\b',
    r'\bwithout (making )?changes\b',
    r'\bno changes\b',
    r'\bsafe mode\b',
    r'\bread[\s-]?only\b',
]

# Live execution indicators (user wants actual changes)
LIVE_RUN_PATTERNS = [
    r'\bexecute\b',
    r'\brun\b',
    r'\bapply\b',
    r'\bdo it\b',
    r'\bmake changes\b',
    r'\bactually (do|run|execute)\b',
    r'\bfor real\b',
    r'\bcommit\b',
    r'\blive\b',
    r'\bproceed\b',
]

# Default mode when no indicators found
DEFAULT_MODE = ExecutionMode.LIVE


def detect_execution_mode(request: str) -> Tuple[ExecutionMode, str]:
    """
    Detect execution mode from natural language request.
    
    Args:
        request: User's natural language request
    
    Returns:
        Tuple of (ExecutionMode, reason)
        - ExecutionMode: LIVE or DRY_RUN
        - reason: Human-readable explanation of why mode was selected
    
    Examples:
        >>> detect_execution_mode("cleanup workspace")
        (ExecutionMode.LIVE, "No mode specified, defaulting to live execution")
        
        >>> detect_execution_mode("preview cleanup changes")
        (ExecutionMode.DRY_RUN, "Detected 'preview' - dry-run mode")
        
        >>> detect_execution_mode("dry run optimization")
        (ExecutionMode.DRY_RUN, "Detected 'dry-run' - dry-run mode")
        
        >>> detect_execution_mode("actually run cleanup")
        (ExecutionMode.LIVE, "Detected 'actually run' - live execution")
    """
    request_lower = request.lower()
    
    # Check for dry-run indicators
    for pattern in DRY_RUN_PATTERNS:
        match = re.search(pattern, request_lower)
        if match:
            matched_text = match.group(0)
            return (
                ExecutionMode.DRY_RUN,
                f"Detected '{matched_text}' - dry-run mode (preview only, no changes)"
            )
    
    # Check for explicit live execution indicators
    for pattern in LIVE_RUN_PATTERNS:
        match = re.search(pattern, request_lower)
        if match:
            matched_text = match.group(0)
            return (
                ExecutionMode.LIVE,
                f"Detected '{matched_text}' - live execution (will make changes)"
            )
    
    # Default to live execution if no indicators
    return (
        DEFAULT_MODE,
        "No mode specified, defaulting to live execution"
    )


def parse_mode_from_args(args_dict: dict) -> ExecutionMode:
    """
    Parse execution mode from CLI arguments.
    
    Args:
        args_dict: Dictionary of CLI arguments
    
    Returns:
        ExecutionMode based on --dry-run flag
    
    Examples:
        >>> parse_mode_from_args({'dry_run': True})
        ExecutionMode.DRY_RUN
        
        >>> parse_mode_from_args({'dry_run': False})
        ExecutionMode.LIVE
        
        >>> parse_mode_from_args({})
        ExecutionMode.LIVE
    """
    if args_dict.get('dry_run', False):
        return ExecutionMode.DRY_RUN
    return ExecutionMode.LIVE


def format_mode_message(mode: ExecutionMode) -> str:
    """
    Format execution mode as user-friendly message.
    
    Args:
        mode: ExecutionMode to format
    
    Returns:
        Formatted message string
    
    Examples:
        >>> format_mode_message(ExecutionMode.DRY_RUN)
        "🔍 DRY RUN MODE - Preview only, no changes will be made"
        
        >>> format_mode_message(ExecutionMode.LIVE)
        "▶️  LIVE MODE - Changes will be applied"
    """
    if mode == ExecutionMode.DRY_RUN:
        return "🔍 DRY RUN MODE - Preview only, no changes will be made"
    else:
        return "▶️  LIVE MODE - Changes will be applied"


def should_prompt_confirmation(mode: ExecutionMode, operation: str) -> bool:
    """
    Determine if user confirmation should be requested.
    
    Args:
        mode: Current execution mode
        operation: Name of operation being performed
    
    Returns:
        True if confirmation recommended, False otherwise
    
    Logic:
        - Dry-run: Never prompt (safe preview)
        - Live mode + destructive operation: Always prompt
        - Live mode + safe operation: No prompt
    
    Examples:
        >>> should_prompt_confirmation(ExecutionMode.DRY_RUN, "cleanup")
        False  # Dry-run is always safe
        
        >>> should_prompt_confirmation(ExecutionMode.LIVE, "cleanup")
        True  # Cleanup is destructive
        
        >>> should_prompt_confirmation(ExecutionMode.LIVE, "status")
        False  # Status is read-only
    """
    if mode == ExecutionMode.DRY_RUN:
        return False  # Dry-run is always safe
    
    # Destructive operations that should prompt in live mode
    destructive_operations = {
        'cleanup',
        'optimize',
        'refactor',
        'migrate',
        'delete',
        'reset',
    }
    
    operation_lower = operation.lower()
    return any(dest_op in operation_lower for dest_op in destructive_operations)


# Example usage and testing
if __name__ == '__main__':
    test_requests = [
        "cleanup workspace",
        "preview cleanup changes",
        "dry run optimization",
        "test the cleanup process",
        "what would happen if I cleanup",
        "actually run cleanup",
        "execute optimization for real",
        "simulate story refresh",
        "show me what cleanup would do",
    ]
    
    print("=" * 80)
    print("EXECUTION MODE DETECTION TESTS")
    print("=" * 80)
    print()
    
    for request in test_requests:
        mode, reason = detect_execution_mode(request)
        print(f"Request: '{request}'")
        print(f"  Mode: {mode.value}")
        print(f"  Reason: {reason}")
        print(f"  Message: {format_mode_message(mode)}")
        print()
