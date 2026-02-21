"""
MCP Tool Decorator for CORTEX Orchestrators.

Provides the @mcp_tool decorator for marking methods as MCP-exposable tools.
Used by MasterOrchestrator and domain orchestrators to register tool metadata.

The decorator:
1. Marks functions with _mcp_tool_name, _mcp_tool_description metadata
2. Preserves original function behavior (transparent decorator)
3. Enables get_mcp_tools() discovery of all decorated methods on a class

Authority: MCP-FIRST, CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-P0-MCP-DECORATOR-GREEN-001
"""

import functools
from typing import Any, Callable, Dict, List, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def mcp_tool(
    *,
    name: str,
    description: str,
    category: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator to mark a method as an MCP-exposable tool.

    Attaches metadata to the function without altering behavior.
    MasterOrchestrator and other orchestrators use this to register
    tool definitions discoverable via get_mcp_tools().

    Args:
        name: Unique tool name (e.g., 'register_orchestrator').
        description: Human-readable description of the tool.
        category: Optional tool category (e.g., 'governance').

    Returns:
        Decorated function with _mcp_tool_name, _mcp_tool_description,
        and optionally _mcp_tool_category attributes.

    Raises:
        TypeError: If name or description not provided.

    Example:
        @mcp_tool(name="my_tool", description="Does something")
        def my_method(self, x: int) -> int:
            return x * 2
    """

    def decorator(func: F) -> F:
        """Create decorated function wrapper."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Execute wrapped function with applied decoration."""
            return func(*args, **kwargs)

        wrapper._mcp_tool_name = name  # type: ignore[attr-defined]
        wrapper._mcp_tool_description = description  # type: ignore[attr-defined]
        if category is not None:
            wrapper._mcp_tool_category = category  # type: ignore[attr-defined]

        return wrapper  # type: ignore[return-value]

    return decorator


def get_mcp_tools(instance: Any) -> List[Dict[str, Any]]:
    """
    Discover all @mcp_tool decorated methods on a class instance.

    Scans instance methods for _mcp_tool_name attribute and returns
    metadata for each discovered tool.

    Args:
        instance: Object instance to scan for decorated methods.

    Returns:
        List of dicts with 'name', 'description', and optionally 'category'
        for each @mcp_tool decorated method.

    Example:
        tools = get_mcp_tools(my_orchestrator)
        # [{"name": "tool_a", "description": "...", "method": "method_a"}, ...]
    """
    tools: List[Dict[str, Any]] = []

    for attr_name in dir(instance):
        if attr_name.startswith("_"):
            continue
        try:
            attr = getattr(instance, attr_name)
        except AttributeError:
            continue

        if callable(attr) and hasattr(attr, "_mcp_tool_name"):
            tool_info: Dict[str, Any] = {
                "name": attr._mcp_tool_name,
                "description": attr._mcp_tool_description,
                "method": attr_name,
            }
            if hasattr(attr, "_mcp_tool_category"):
                tool_info["category"] = attr._mcp_tool_category
            tools.append(tool_info)

    return tools


# AC_COMPLETE: AC-P0-MCP-DECORATOR-GREEN-001
