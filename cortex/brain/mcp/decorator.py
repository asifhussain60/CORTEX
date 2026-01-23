"""
MCP Tool Decorator

Provides @mcp_tool decorator for registering functions as MCP tools.

Usage:
    @mcp_tool(
        name="ac_status",
        description="Get acceptance criteria status"
    )
    def ac_status(ac_id: str) -> Result[Dict]:
        ...

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import functools
import threading
from typing import Any, Callable, Dict, Optional


# REM-CRIT-004: Thread-safe tool registry with lock
_REGISTERED_TOOLS: Dict[str, Any] = {}
_REGISTRY_LOCK = threading.Lock()


def mcp_tool(
    name: str,
    description: str,
    category: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
):
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        name: Tool name (must be unique)
        description: Human-readable description
        category: Optional category for grouping
        parameters: Optional parameter schema for MCP
    
    Returns:
        Decorated function registered as MCP tool
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        
        # Store metadata
        wrapper._mcp_tool = True  # type: ignore
        wrapper._mcp_name = name  # type: ignore
        wrapper._mcp_description = description  # type: ignore
        wrapper._mcp_category = category  # type: ignore
        wrapper._mcp_parameters = parameters or {}  # type: ignore
        
        # Register in thread-safe registry
        with _REGISTRY_LOCK:
            _REGISTERED_TOOLS[name] = {
                "func": wrapper,
                "name": name,
                "description": description,
                "category": category,
                "parameters": parameters or {}
            }
        
        return wrapper
    
    return decorator


def get_registered_tools() -> Dict[str, Any]:
    """Get all registered MCP tools (thread-safe)."""
    with _REGISTRY_LOCK:
        return _REGISTERED_TOOLS.copy()


def get_tool(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific registered tool by name (thread-safe)."""
    with _REGISTRY_LOCK:
        return _REGISTERED_TOOLS.get(name)
