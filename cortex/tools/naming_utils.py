"""
Naming utility functions for tool and orchestrator generation.

AC_START: AC-AUDIT-2026-02-12-002
Fix: CORE-035 violation - Extract duplicate naming utilities
Resolution: Centralize _to_class_name and _to_module_name functions
Used by: tool_generator.py, orchestrator_scaffolder.py
"""

import re


def to_class_name(name: str) -> str:
    """
    Convert name to PascalCase class name.
    
    Args:
        name: Input name (can be kebab-case, snake_case, or mixed)
        
    Returns:
        PascalCase class name
        
    Examples:
        >>> to_class_name("my-tool")
        'MyTool'
        >>> to_class_name("lens_analyzer")
        'LensAnalyzer'
        >>> to_class_name("TDD Orchestrator")
        'TddOrchestrator'
    """
    parts = re.split(r'[-_\s]+', name)
    return ''.join(part.capitalize() for part in parts)


def to_module_name(name: str) -> str:
    """
    Convert name to snake_case module name.
    
    Args:
        name: Input name (can be kebab-case, PascalCase, or mixed)
        
    Returns:
        snake_case module name
        
    Examples:
        >>> to_module_name("MyTool")
        'my_tool'
        >>> to_module_name("lens-analyzer")
        'lens_analyzer'
        >>> to_module_name("TDD Orchestrator")
        'tdd_orchestrator'
    """
    # Handle camelCase/PascalCase FIRST (before lowercasing)
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    # Convert to lowercase and replace separators
    name = re.sub(r'[-\s]+', '_', name.lower())
    return name


# AC_COMPLETE: AC-AUDIT-2026-02-12-002 ✅
