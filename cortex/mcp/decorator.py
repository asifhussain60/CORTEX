"""MCP Decorator

DEPRECATED: Use cortex.mcp.decorators (plural) instead.
This module will be removed in Phase 9 cleanup.

Migration: Replace `from cortex.mcp.decorator import mcp_tool`
           with `from cortex.mcp.decorators import mcp_tool`

Author: CORTEX Framework
Status: DEPRECATED (2026-02-01)
"""

import warnings
import inspect
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, List, get_type_hints

# Deprecation warning
warnings.warn(
    "cortex.mcp.decorator is deprecated. Use cortex.mcp.decorators instead.",
    DeprecationWarning,
    stacklevel=2
)

# Global registry for tools
_tool_registry: Dict[str, 'MCPToolRegistration'] = {}


@dataclass
class MCPToolRegistration:
    """Registration entry for an MCP tool."""
    name: str
    func: Callable
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    category: Optional[str] = None
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    

def _python_type_to_json_schema(py_type) -> str:
    """Convert Python type to JSON schema type."""
    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    return type_mapping.get(py_type, "string")


def _extract_parameters(func: Callable) -> Dict[str, Any]:
    """Extract parameter schema from function signature."""
    sig = inspect.signature(func)
    type_hints = {}
    try:
        type_hints = get_type_hints(func)
    except Exception:
        pass
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue
        
        # Get type
        param_type = type_hints.get(param_name, str)
        json_type = _python_type_to_json_schema(param_type)
        
        properties[param_name] = {
            "type": json_type,
            "description": f"Parameter {param_name}"
        }
        
        # Check if required (no default value)
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        else:
            properties[param_name]["default"] = param.default
    
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    version: str = "1.0.0",
    tags: Optional[List[str]] = None
):
    """MCP tool decorator.
    
    Registers a function as an MCP tool with automatic parameter extraction.
    
    Args:
        name: Custom tool name (defaults to function name).
        description: Tool description (defaults to docstring).
        category: Tool category for organization.
        version: Tool version (semantic versioning).
        tags: List of tags for categorization.
        
    Returns:
        Decorated function registered as MCP tool.
    """
    def decorator(func: Callable):
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").strip().split('\n')[0]
        
        # Extract parameters from function signature
        parameters = _extract_parameters(func)
        
        # Create registration
        registration = MCPToolRegistration(
            name=tool_name,
            func=func,
            description=tool_description,
            parameters=parameters,
            category=category,
            version=version,
            tags=tags or []
        )
        
        # Register in global registry
        _tool_registry[tool_name] = registration
        
        # Store metadata on function
        func._mcp_tool = True
        func._mcp_name = tool_name
        func._mcp_description = tool_description
        func._mcp_registration = registration
        
        return func
    return decorator


def get_tool(tool_id: str) -> Optional[MCPToolRegistration]:
    """Get MCP tool by ID.
    
    Args:
        tool_id: The tool identifier.
        
    Returns:
        Tool registration or None if not found.
    """
    return _tool_registry.get(tool_id)


def get_registered_tools() -> Dict[str, MCPToolRegistration]:
    """Get dictionary of all registered MCP tools.
    
    Returns:
        Dictionary mapping tool names to registrations.
    """
    return _tool_registry.copy()


def clear_tools() -> None:
    """Clear all registered MCP tools."""
    global _tool_registry
    _tool_registry.clear()


__all__ = [
    "get_tool",
    "mcp_tool", 
    "get_registered_tools", 
    "clear_tools",
    "MCPToolRegistration"
]
