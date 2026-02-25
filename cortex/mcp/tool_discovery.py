"""tool_discovery.py — MCP Tool Discovery stub."""
from __future__ import annotations
from typing import Any


class ToolDiscovery:
    """Discovers available MCP tools at runtime."""

    def discover(self) -> list[str]:
        """Return names of all discoverable MCP tools.

        Returns:
            List of tool name strings.
        """
        return []


# Alias expected by auto_initialization_suite.py
ToolDiscoveryEngine = ToolDiscovery
