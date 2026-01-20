"""MCP Decorator

Author: CORTEX Framework
"""

def get_tool(tool_id: str):
    """Get MCP tool decorator."""
    def decorator(func):
        func._mcp_tool_id = tool_id
        return func
    return decorator


def mcp_tool(name: str = None, description: str = None):
    """MCP tool decorator."""
    def decorator(func):
        func._mcp_tool = True
        func._mcp_name = name or func.__name__
        func._mcp_description = description or func.__doc__
        return func
    return decorator


def get_registered_tools() -> list:
    """Get list of all registered MCP tools."""
    return []


__all__ = ["get_tool", "mcp_tool", "get_registered_tools"]
