"""tool_registry.py — MCP Tool Registry stub."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ToolCategory(str, Enum):
    """MCP tool categories."""
    GOVERNANCE = "governance"
    INTELLIGENCE = "intelligence"
    AUDIT = "audit"
    REFACTOR = "refactor"
    UTILITY = "utility"


@dataclass
class ToolMetadata:
    """Metadata for a registered MCP tool."""
    name: str
    category: ToolCategory
    description: str = ""
    operations: list[str] = field(default_factory=list)


class ToolRegistry:
    """Registry for MCP tool metadata and resolution."""

    def __init__(self) -> None:
        """Initialise with empty tool registry."""
        self._tools: dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata) -> None:
        """Register a tool.

        Args:
            metadata: Tool metadata to register.
        """
        self._tools[metadata.name] = metadata

    def get(self, name: str) -> ToolMetadata | None:
        """Get tool metadata by name.

        Args:
            name: Tool name to look up.

        Returns:
            ToolMetadata or None if not found.
        """
        return self._tools.get(name)

    def all_tools(self) -> list[ToolMetadata]:
        """Return all registered tools."""
        return list(self._tools.values())
