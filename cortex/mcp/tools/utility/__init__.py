"""MCP Utility Tools - Echo, testing, and transformation utilities.

Provides MCP-exposed utility operations for testing, echo functionality,
and basic data transformations.

Category: UTILITY
Authorization: PUBLIC
Compliance: LIGHTWEIGHT

Author: CORTEX Framework
"""

from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool


@mcp_tool(
    name="echo_tool",
    description="Echo tool for testing MCP connectivity",
    parameters={"message": "string"}
)
def echo_tool(message: str) -> Dict[str, Any]:
    """Echo tool for testing.

    Args:
        message: Message to echo

    Returns:
        Echo response
    """
    return {
        "echo": message,
        "timestamp": None,
    }


@mcp_tool(
    name="sample_tool",
    description="Sample tool demonstrating basic MCP functionality",
    parameters={"input": "dict"}
)
def sample_tool(input: Dict[str, Any]) -> Dict[str, Any]:
    """Sample tool.

    Args:
        input: Input data

    Returns:
        Processed sample result
    """
    return {
        "input": input,
        "output": input,
        "status": "success",
    }


@mcp_tool(
    name="transform_tool",
    description="Transform data using specified transformation",
    parameters={"data": "dict", "transformation": "string"}
)
def transform_tool(data: Dict[str, Any], transformation: str) -> Dict[str, Any]:
    """Transform tool.

    Args:
        data: Data to transform
        transformation: Transformation type

    Returns:
        Transformed data
    """
    return {
        "original": data,
        "transformed": data,
        "transformation": transformation,
    }


__all__ = [
    "echo_tool",
    "sample_tool",
    "transform_tool",
]
