"""
CORTEX Unified Tool Entry Point

Single entry point for all CORTEX CLI tools.
Eliminates 40+ separate script entry points.

Usage:
    python -m src.tools.toolkit <command> [args]
    
    # or via alias
    cortex <command> [args]

Commands:
    ac status <ac_id>       - Get AC status
    ac list                 - List all ACs
    audit query [options]   - Query audit logs
    validate <file>         - Validate YAML/JSON
    governance check        - Run governance checks

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import argparse
import sys
import threading
from typing import List, Optional, Callable, Dict, Any

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.path_resolver import get_project_root


# REM-CRIT-004: Thread-safe tool registry with lock
_TOOLS: Dict[str, Callable] = {}
_TOOLS_LOCK = threading.Lock()


def register_tool(name: str) -> Callable:
    """Decorator to register a tool handler (thread-safe)."""
    def decorator(func: Callable) -> Callable:
        with _TOOLS_LOCK:
            _TOOLS[name] = func
        return func
    return decorator


@register_tool("version")
def cmd_version(args: List[str]) -> Result[str]:
    """Show CORTEX version."""
    from src import __version__
    return Ok(f"CORTEX {__version__}")


@register_tool("root")
def cmd_root(args: List[str]) -> Result[str]:
    """Show project root path."""
    return Ok(str(get_project_root()))


@register_tool("help")
def cmd_help(args: List[str]) -> Result[str]:
    """Show available commands."""
    with _TOOLS_LOCK:
        commands = sorted(_TOOLS.keys())
    help_text = "Available commands:\n" + "\n".join(f"  {cmd}" for cmd in commands)
    return Ok(help_text)


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    if not argv:
        result = cmd_help([])
        print(result.unwrap())
        return 0
    
    command = argv[0]
    args = argv[1:]
    
    with _TOOLS_LOCK:
        if command not in _TOOLS:
            print(f"Unknown command: {command}")
            print("Use 'cortex help' to see available commands.")
            return 1
        tool_func = _TOOLS[command]
    
    result = tool_func(args)
    
    if result.is_ok():
        output = result.unwrap()
        if output:
            print(output)
        return 0
    else:
        print(f"Error: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
