"""
MCP Tool Decorator - @mcp_tool decorator for exposing functions as MCP tools.

Implements tool registration system with metadata extraction and schema generation
for all CORTEX orchestrators and utilities exposed via MCP.

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from typing import Callable, Dict, Any, Optional, get_type_hints
from dataclasses import dataclass, field
import inspect
import json


@dataclass
class MCPToolMetadata:
    """Metadata for an MCP tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    category: str = "general"
    version: str = "1.0.0"
    func: Optional[Callable] = None


# Global registry of MCP tools
_MCP_TOOLS_REGISTRY: Dict[str, MCPToolMetadata] = {}


def mcp_tool(
    name: Optional[str] = None,
    category: str = "general",
    version: str = "1.0.0",
) -> Callable:
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        name: Tool name (defaults to function name in snake_case)
        category: Tool category for grouping
        version: Tool version (semver)
    
    Returns:
        Decorated function
    
    Example:
        @mcp_tool(category="orchestrator")
        def scaffold_orchestrator(template_name: str, output_dir: str) -> str:
            '''Generate a new orchestrator from template.'''
            ...
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        
        # Extract docstring
        description = inspect.getdoc(func) or "No description"
        
        # Extract parameter schema from function signature
        sig = inspect.signature(func)
        parameters: Dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        type_hints = get_type_hints(func)
        
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue
            
            prop_schema: Dict[str, Any] = {}
            
            # Get type from type hints
            if param_name in type_hints:
                param_type = type_hints[param_name]
                prop_schema = _type_to_schema(param_type)
            else:
                prop_schema = {"type": "string"}
            
            # Add parameter description from docstring if available
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
            
            parameters["properties"][param_name] = prop_schema
        
        # Register tool
        metadata = MCPToolMetadata(
            name=tool_name,
            description=description,
            parameters=parameters,
            category=category,
            version=version,
            func=func
        )
        
        _MCP_TOOLS_REGISTRY[tool_name] = metadata
        
        # Return original function unchanged
        return func
    
    return decorator


def _type_to_schema(param_type: Any) -> Dict[str, Any]:
    """
    Convert Python type to JSON Schema.
    
    Args:
        param_type: Python type annotation
    
    Returns:
        JSON Schema fragment
    """
    import typing
    
    # Handle Optional types (Union[T, None])
    if hasattr(param_type, "__origin__"):
        origin = param_type.__origin__
        
        # Handle Union (including Optional which is Union[T, None])
        if origin is typing.Union:
            # Get the first non-None type
            if hasattr(param_type, "__args__"):
                for arg in param_type.__args__:
                    if arg is not type(None):
                        return _type_to_schema(arg)
        
        # Handle generic types like Dict, List
        if origin is dict:
            return {"type": "object"}
        elif origin is list:
            return {"type": "array"}
    
    # Direct type checks
    if param_type == str:
        return {"type": "string"}
    elif param_type == int:
        return {"type": "integer"}
    elif param_type == float:
        return {"type": "number"}
    elif param_type == bool:
        return {"type": "boolean"}
    elif param_type == dict:
        return {"type": "object"}
    elif param_type == list:
        return {"type": "array"}
    else:
        # Default to string for unknown types
        return {"type": "string"}


def get_registered_tools() -> Dict[str, MCPToolMetadata]:
    """
    Get all registered MCP tools.
    
    Returns:
        Dictionary of tool_name -> MCPToolMetadata
    """
    return _MCP_TOOLS_REGISTRY.copy()


def get_tool(name: str) -> Optional[MCPToolMetadata]:
    """
    Get a registered MCP tool by name.
    
    Args:
        name: Tool name
    
    Returns:
        MCPToolMetadata if found, None otherwise
    """
    return _MCP_TOOLS_REGISTRY.get(name)


def unregister_tool(name: str) -> bool:
    """
    Unregister an MCP tool (mainly for testing).
    
    Args:
        name: Tool name
    
    Returns:
        True if tool was unregistered, False if not found
    """
    if name in _MCP_TOOLS_REGISTRY:
        del _MCP_TOOLS_REGISTRY[name]
        return True
    return False


def clear_tools() -> None:
    """Clear all registered tools (mainly for testing)."""
    _MCP_TOOLS_REGISTRY.clear()
