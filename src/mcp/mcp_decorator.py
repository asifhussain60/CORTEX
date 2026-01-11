"""
CORTEX 6.0 MCP Tool Decorator

Implements AC-MCP-EXPOSE-001: Decorator-based auto-registration for MCP tools.

Provides @mcp_tool decorator that automatically registers tool functions
with the CapabilityRegistry at import time, preventing registration drift.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
Version: 1.0.0
Created: 2026-01-10
AC-ID: AC-MCP-EXPOSE-001
"""

from typing import Dict, Any, Callable, Optional
from functools import wraps
import inspect


# Global registry for decorated tools (populated at import time)
_DECORATED_TOOLS = []


def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: str = "general",
    orchestrator_id: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    returns: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator for automatic MCP tool registration.
    
    Usage:
        @mcp_tool(
            name="cortex_audit_query",
            description="Query audit logs with filters",
            category="audit",
            parameters={
                "db_path": {"type": "string", "required": True, "description": "..."},
                "filters": {"type": "object", "required": False, "description": "..."}
            },
            returns={"type": "object", "description": "Query results"}
        )
        def audit_query(db_path: str, filters: Optional[Dict] = None):
            ...
    
    Args:
        name: Tool name (defaults to function name with cortex_ prefix)
        description: Tool description (defaults to docstring first line)
        category: Tool category for grouping
        orchestrator_id: Associated orchestrator (optional)
        parameters: Parameter definitions with JSON Schema
        returns: Return value definition
        metadata: Additional metadata (tags, version, etc.)
    
    Returns:
        Decorated function with MCP metadata attached
    """
    def decorator(func: Callable) -> Callable:
        # Extract function metadata
        func_name = func.__name__
        tool_name = name or f"cortex_{func_name}"
        
        # Extract description from docstring if not provided
        if description is None:
            doc = inspect.getdoc(func)
            tool_description = doc.split('\n')[0] if doc else f"{func_name} tool"
        else:
            tool_description = description
        
        # Auto-generate parameters from function signature if not provided
        if parameters is None:
            sig = inspect.signature(func)
            tool_parameters = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # Determine type from annotation
                param_type = "string"
                if param.annotation != inspect.Parameter.empty:
                    type_map = {
                        str: "string",
                        int: "integer",
                        float: "number",
                        bool: "boolean",
                        dict: "object",
                        list: "array"
                    }
                    # Handle Optional types
                    origin = getattr(param.annotation, '__origin__', None)
                    if origin is not None:
                        args = getattr(param.annotation, '__args__', ())
                        if args:
                            param_type = type_map.get(args[0], "string")
                    else:
                        param_type = type_map.get(param.annotation, "string")
                
                # Required if no default value
                required = param.default == inspect.Parameter.empty
                
                tool_parameters[param_name] = {
                    "type": param_type,
                    "required": required,
                    "description": f"{param_name} parameter"
                }
        else:
            tool_parameters = parameters
        
        # Default return value
        tool_returns = returns or {"type": "object", "description": "Operation result"}
        
        # Build metadata
        tool_metadata = metadata or {}
        tool_metadata.update({
            "category": category,
            "function_name": func_name,
            "auto_registered": True
        })
        
        # Attach MCP metadata to function
        func._mcp_metadata = {
            "name": tool_name,
            "description": tool_description,
            "parameters": tool_parameters,
            "returns": tool_returns,
            "orchestrator_id": orchestrator_id,
            "metadata": tool_metadata,
            "function": func
        }
        
        # Register in global list
        _DECORATED_TOOLS.append(func._mcp_metadata)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Preserve metadata on wrapper
        wrapper._mcp_metadata = func._mcp_metadata
        
        return wrapper
    
    return decorator


def get_decorated_tools():
    """
    Get all decorated MCP tools.
    
    Returns:
        List of MCP tool metadata dicts
    """
    return _DECORATED_TOOLS.copy()


def clear_decorated_tools():
    """
    Clear the decorated tools registry.
    
    Used for testing.
    """
    global _DECORATED_TOOLS
    _DECORATED_TOOLS = []
