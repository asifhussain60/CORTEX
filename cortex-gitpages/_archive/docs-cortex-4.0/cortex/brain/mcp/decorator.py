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
from typing import Any, Callable, Dict, Optional


# Global registry for decorated tools
_REGISTERED_TOOLS = {}


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
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Store metadata
        wrapper._mcp_tool = True
        wrapper._mcp_name = name
        wrapper._mcp_description = description
        wrapper._mcp_category = category
        wrapper._mcp_parameters = parameters or {}
        
        # Register in global registry
        _REGISTERED_TOOLS[name] = {
            "func": wrapper,
            "name": name,
            "description": description,
            "category": category,
            "parameters": parameters or {}
        }
        
        return wrapper
    
    return decorator


def get_registered_tools():
    """Get all registered MCP tools."""
    return _REGISTERED_TOOLS.copy()


def get_tool(name: str):
    """Get a specific registered tool by name."""
    return _REGISTERED_TOOLS.get(name)
