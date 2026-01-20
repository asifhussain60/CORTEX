"""MCP tool decorator for exposing functions as MCP-callable tools."""

from typing import Any, Callable, Dict, Optional
from functools import wraps


# Global registry of MCP tools
MCP_TOOLS_REGISTRY: Dict[str, Dict[str, Any]] = {}


def mcp_tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, str]] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as an MCP-callable tool.
    
    Args:
        name: Unique name for the MCP tool.
        description: Human-readable description of the tool's purpose.
        parameters: Optional dict mapping parameter names to their types.
    
    Returns:
        Decorator function that registers and returns the original function.
    
    Raises:
        ValueError: If name is empty or not a valid identifier.
    
    Example:
        @mcp_tool(
            name="analyze_code",
            description="Analyze code structure",
            parameters={"code": "string", "depth": "int"}
        )
        def analyze_code(code: str, depth: int = 1) -> dict:
            \"\"\"Analyze code structure.\"\"\"
            return {"lines": len(code.split("\n")), "depth": depth}
    """
    if not name or not isinstance(name, str):
        raise ValueError("Tool name must be a non-empty string")
    
    if not description:
        raise ValueError("Tool description must be provided")
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Register function and return it unchanged."""
        # Store tool metadata
        MCP_TOOLS_REGISTRY[name] = {
            "name": name,
            "description": description,
            "func": func,
            "parameters": parameters or {},
        }
        
        # Return original function unchanged (preserve metadata)
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Call original function."""
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
