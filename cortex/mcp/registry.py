"""MCP Tool Registry - Centralized registry for MCP tools.

Manages registration, retrieval, and lifecycle of MCP tools across the
CORTEX framework. Provides a single source of truth for available tools
with category-based organization and discovery mechanisms.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Callable
from threading import Lock
from dataclasses import dataclass, field
from datetime import datetime
import importlib
import inspect
from pathlib import Path


@dataclass
class ToolRegistryEntry:
    """Registry entry for an MCP tool.

    Attributes:
        tool_id: Unique tool identifier.
        tool_name: Human-readable tool name.
        description: Tool description.
        parameters: Tool parameters schema.
        metadata: Additional tool metadata.
        created_at: Tool registration timestamp.
    """

    tool_id: str
    tool_name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


class MCPToolRegistry:
    """Centralized registry for MCP tools.

    Manages registration and retrieval of MCP tools with thread-safe
    operations and metadata tracking.
    """

    def __init__(self) -> None:
        """Initialize the MCP tool registry."""
        self._tools: Dict[str, ToolRegistryEntry] = {}
        self._lock = Lock()

    def register_tool(
        self,
        tool_id: str,
        tool_name: str,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolRegistryEntry:
        """Register a new MCP tool.

        Args:
            tool_id: Unique tool identifier.
            tool_name: Human-readable tool name.
            description: Tool description.
            parameters: Tool parameters schema.
            metadata: Additional tool metadata.

        Returns:
            ToolRegistryEntry: The registered tool entry.

        Raises:
            ValueError: If tool_id is already registered.
        """
        with self._lock:
            if tool_id in self._tools:
                raise ValueError(f"Tool {tool_id} is already registered")

            entry = ToolRegistryEntry(
                tool_id=tool_id,
                tool_name=tool_name,
                description=description,
                parameters=parameters or {},
                metadata=metadata or {},
                created_at=str(__import__("datetime").datetime.now()),
            )
            self._tools[tool_id] = entry
            return entry

    def get_tool(self, tool_id: str) -> Optional[ToolRegistryEntry]:
        """Retrieve a registered tool by ID.

        Args:
            tool_id: The tool identifier.

        Returns:
            ToolRegistryEntry if found, None otherwise.
        """
        with self._lock:
            return self._tools.get(tool_id)

    def list_tools(self) -> List[ToolRegistryEntry]:
        """List all registered tools.

        Returns:
            List of ToolRegistryEntry objects.
        """
        with self._lock:
            return list(self._tools.values())

    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister a tool by ID.

        Args:
            tool_id: The tool identifier.

        Returns:
            True if tool was removed, False if not found.
        """
        with self._lock:
            if tool_id in self._tools:
                del self._tools[tool_id]
                return True
            return False

    def clear(self) -> None:
        """Clear all registered tools."""
        with self._lock:
            self._tools.clear()

    def tool_exists(self, tool_id: str) -> bool:
        """Check if a tool is registered.

        Args:
            tool_id: The tool identifier.

        Returns:
            True if tool is registered, False otherwise.
        """
        with self._lock:
            return tool_id in self._tools

    def get_tool_count(self) -> int:
        """Get the total number of registered tools.

        Returns:
            Number of registered tools.
        """
        with self._lock:
            return len(self._tools)


# Global registry instance
_mcp_tool_registry: Optional[MCPToolRegistry] = None
_registry_lock = Lock()


def get_mcp_tool_registry() -> MCPToolRegistry:
    """Get the global MCP tool registry instance.

    Returns:
        MCPToolRegistry: The global registry instance.
    """
    global _mcp_tool_registry
    if _mcp_tool_registry is None:
        with _registry_lock:
            if _mcp_tool_registry is None:
                _mcp_tool_registry = MCPToolRegistry()
    return _mcp_tool_registry


class OrchestratorRegistry:
    """Registry for orchestrator tools and metadata.

    Manages orchestrator discovery, registration, and lifecycle management.
    """

    def __init__(self) -> None:
        """Initialize orchestrator registry."""
        self.orchestrators: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def register_orchestrator(
        self, orchestrator_id: str, name: str, config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Register an orchestrator.

        Args:
            orchestrator_id: Unique orchestrator identifier.
            name: Human-readable orchestrator name.
            config: Orchestrator configuration.

        Returns:
            Registered orchestrator info.

        Raises:
            ValueError: If orchestrator_id already registered.
        """
        with self._lock:
            if orchestrator_id in self.orchestrators:
                raise ValueError(f"Orchestrator {orchestrator_id} already registered")

            entry = {
                "orchestrator_id": orchestrator_id,
                "name": name,
                "config": config or {},
                "registered_at": str(__import__("datetime").datetime.now()),
            }
            self.orchestrators[orchestrator_id] = entry
            return entry

    def get_orchestrator(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an orchestrator.

        Args:
            orchestrator_id: Orchestrator identifier.

        Returns:
            Orchestrator info if found, None otherwise.
        """
        with self._lock:
            return self.orchestrators.get(orchestrator_id)

    def list_orchestrators(self) -> List[Dict[str, Any]]:
        """List all registered orchestrators.

        Returns:
            List of orchestrator entries.
        """
        with self._lock:
            return list(self.orchestrators.values())

    def unregister_orchestrator(self, orchestrator_id: str) -> bool:
        """Unregister an orchestrator.

        Args:
            orchestrator_id: Orchestrator identifier.

        Returns:
            True if unregistered, False if not found.
        """
        with self._lock:
            if orchestrator_id in self.orchestrators:
                del self.orchestrators[orchestrator_id]
                return True
            return False


# Global orchestrator registry instance
_orchestrator_registry: Optional[OrchestratorRegistry] = None
_orch_registry_lock = Lock()


def get_orchestrator_registry() -> OrchestratorRegistry:
    """Get the global orchestrator registry instance.

    Returns:
        OrchestratorRegistry: The global registry instance.
    """
    global _orchestrator_registry
    if _orchestrator_registry is None:
        with _orch_registry_lock:
            if _orchestrator_registry is None:
                _orchestrator_registry = OrchestratorRegistry()
    return _orchestrator_registry


# Alias for backward compatibility
ToolRegistry = MCPToolRegistry


__all__ = [
    "ToolRegistryEntry",
    "MCPToolRegistry",
    "ToolRegistry",
    "OrchestratorRegistry",
    "get_mcp_tool_registry",
    "get_orchestrator_registry",
]
