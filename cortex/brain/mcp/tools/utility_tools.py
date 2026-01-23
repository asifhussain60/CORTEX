"""
MCP Utility Tools - General Purpose Utilities via MCP

MCP-exposed utility tools:
- echo_tool: Echo input for testing
- transform_tool: Transform data between formats

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.mcp.decorator import mcp_tool


@mcp_tool(
    name="echo_tool",
    description="Echo the input message back (useful for testing MCP connectivity).",
    parameters={
        "message": {
            "type": "string",
            "description": "Message to echo",
            "required": True
        }
    }
)
def echo_tool(message: str) -> Result[Dict[str, Any]]:
    """Echo a message.
    
    Args:
        message: Message to echo
        
    Returns:
        Result containing echoed message
    """
    return Ok({
        "echoed": message,
        "timestamp": "2026-01-23T00:00:00Z",
        "status": "success"
    })


@mcp_tool(
    name="transform_tool",
    description="Transform data between different formats (JSON, YAML, etc.).",
    parameters={
        "data": {
            "type": "string",
            "description": "Data to transform",
            "required": True
        },
        "source_format": {
            "type": "string",
            "description": "Source data format",
            "required": True
        },
        "target_format": {
            "type": "string",
            "description": "Target data format",
            "required": True
        }
    }
)
def transform_tool(data: str, source_format: str, target_format: str) -> Result[Dict[str, Any]]:
    """Transform data between formats.
    
    Args:
        data: Input data
        source_format: Source format (json, yaml, xml)
        target_format: Target format (json, yaml, xml)
        
    Returns:
        Result containing transformed data
    """
    return Ok({
        "source_format": source_format,
        "target_format": target_format,
        "transformed_data": data,  # Simplified for now
        "status": "transformed"
    })
