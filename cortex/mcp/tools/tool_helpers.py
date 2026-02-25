"""
tool_helpers.py — MCP Tool Helper Utilities

Shared utilities for MCP tool implementations. Stub restored
for import compatibility.
"""
from __future__ import annotations

from typing import Any


def format_response(data: Any, status: str = "ok", error: str | None = None) -> dict[str, Any]:
    """Format a standardised MCP tool response dict.

    Args:
        data: The payload to return.
        status: Response status string ('ok' or 'error').
        error: Optional error message.

    Returns:
        Formatted response dictionary.
    """
    return {
        "status": status,
        "data": data,
        "error": error,
    }


def validate_params(params: dict[str, Any], required: list[str]) -> list[str]:
    """Validate that all required params are present.

    Args:
        params: The parameter dictionary from the MCP request.
        required: List of required parameter keys.

    Returns:
        List of missing parameter names (empty if all present).
    """
    return [k for k in required if k not in params]


def safe_get(params: dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely retrieve a value from params with a default.

    Args:
        params: The parameter dictionary.
        key: The key to retrieve.
        default: Fallback value if key is absent.

    Returns:
        The value or the default.
    """
    return params.get(key, default)
