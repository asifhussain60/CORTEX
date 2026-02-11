"""MCP endpoints for tool discovery and management."""

from typing import Any, Dict, List

from cortex.mcp.decorators import MCP_TOOLS_REGISTRY


def list_tools_endpoint() -> Dict[str, Any]:
    """
    MCP endpoint for discovering all available tools.

    Returns:
        Dictionary containing list of available tools with metadata.

    Response Format:
        {
            "tools": [
                {
                    "name": "tool_name",
                    "description": "Tool description",
                    "parameters": {"param1": "type1", ...}
                },
                ...
            ]
        }

    Example:
        response = list_tools_endpoint()
        for tool in response["tools"]:
            print(f"{tool['name']}: {tool['description']}")
    """
    tools: List[Dict[str, Any]] = []

    # Convert registry entries to API response format
    for tool_name, tool_metadata in MCP_TOOLS_REGISTRY.items():
        tool_entry: Dict[str, Any] = {
            "name": tool_metadata.get("name", tool_name),
            "description": tool_metadata.get("description", ""),
        }

        # Include parameters if present
        if tool_metadata.get("parameters"):
            tool_entry["parameters"] = tool_metadata["parameters"]

        tools.append(tool_entry)

    return {
        "tools": tools,
        "count": len(tools),
    }


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """
    Get detailed metadata for a specific tool.

    Args:
        tool_name: Name of the tool.

    Returns:
        Dictionary containing tool metadata.

    Raises:
        KeyError: If tool not found.
    """
    if tool_name not in MCP_TOOLS_REGISTRY:
        raise KeyError(f"Tool '{tool_name}' not found in registry")

    tool_metadata = MCP_TOOLS_REGISTRY[tool_name]

    return {
        "name": tool_metadata.get("name"),
        "description": tool_metadata.get("description"),
        "parameters": tool_metadata.get("parameters", {}),
        "callable": callable(tool_metadata.get("func")),
    }


def filter_tools_by_domain(domain: str) -> List[Dict[str, Any]]:
    """
    Filter tools by domain.

    Args:
        domain: Domain name to filter by.

    Returns:
        List of tools matching the domain.
    """
    tools: List[Dict[str, Any]] = []

    for tool_name, tool_metadata in MCP_TOOLS_REGISTRY.items():
        description = tool_metadata.get("description", "").lower()

        # Simple domain matching on tool name or description
        if domain.lower() in tool_name.lower() or domain.lower() in description:
            tools.append({
                "name": tool_metadata.get("name"),
                "description": tool_metadata.get("description"),
            })

    return tools


def get_tool_count() -> int:
    """
    Get total count of registered tools.

    Returns:
        Number of tools in registry.
    """
    return len(MCP_TOOLS_REGISTRY)


def is_tool_registered(tool_name: str) -> bool:
    """
    Check if a tool is registered.

    Args:
        tool_name: Name of the tool to check.

    Returns:
        True if tool is registered, False otherwise.
    """
    return tool_name in MCP_TOOLS_REGISTRY


def call_tool(tool_name: str, *args: Any, **kwargs: Any) -> Any:
    """
    Call a registered tool by name.

    Args:
        tool_name: Name of the tool to call.
        *args: Positional arguments for the tool.
        **kwargs: Keyword arguments for the tool.

    Returns:
        Result of tool execution.

    Raises:
        KeyError: If tool not found.
        TypeError: If arguments don't match tool signature.
    """
    if tool_name not in MCP_TOOLS_REGISTRY:
        raise KeyError(f"Tool '{tool_name}' not found in registry")

    tool_func = MCP_TOOLS_REGISTRY[tool_name].get("func")

    if not callable(tool_func):
        raise TypeError(f"Tool '{tool_name}' is not callable")

    return tool_func(*args, **kwargs)
