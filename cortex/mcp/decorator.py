"""MCP Decorator

Author: CORTEX Framework
"""

def get_tool(tool_id: str):
    """Get MCP tool decorator."""
    def decorator(func):
        func._mcp_tool_id = tool_id
        return func
    return decorator

__all__ = ["get_tool"]
