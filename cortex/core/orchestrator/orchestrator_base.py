"""Orchestrator Base - Base class for all orchestrators.

Provides common functionality and interface for orchestrator implementations.

Author: CORTEX Framework
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime


class OrchestratorBase(ABC):
    """Abstract base class for orchestrators."""

    def __init__(self, name: str, version: str = "1.0.0") -> None:
        """Initialize orchestrator base.

        Args:
            name: Orchestrator name.
            version: Orchestrator version.
        """
        self.name = name
        self.version = version
        self.created_at = datetime.now()
        self._state: Dict[str, Any] = {}

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the orchestrator.

        Returns:
            True if initialization successful, False otherwise.
        """
        pass

    @abstractmethod
    def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute an operation.

        Args:
            operation: Operation name.
            **kwargs: Operation parameters.

        Returns:
            Result dictionary.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        pass

    def get_name(self) -> str:
        """Get orchestrator name.

        Returns:
            Orchestrator name.
        """
        return self.name

    def get_version(self) -> str:
        """Get orchestrator version.

        Returns:
            Orchestrator version.
        """
        return self.version

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value.

        Args:
            key: State key.
            default: Default value if key not found.

        Returns:
            State value or default.
        """
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set state value.

        Args:
            key: State key.
            value: Value to set.
        """
        self._state[key] = value

    def clear_state(self) -> None:
        """Clear all state."""
        self._state.clear()

    def get_mcp_tools(self) -> Dict[str, Any]:
        """Get available MCP tools for this orchestrator.
        
        AC-MCP-EXPOSURE-001: Default implementation returns all 15 tools.
        
        Subclasses can override to customize tool exposure based on their
        specific domain and capabilities.
        
        Returns:
            Dict with tool categories and names. Follows format:
            {
                "status": "ok",
                "orchestrator": orchestrator_name,
                "tools": {
                    "governance": [tool_names...],
                    "orchestration": [tool_names...],
                    "knowledge": [tool_names...],
                    "utility": [tool_names...]
                },
                "total_tools": 15
            }
        """
        from cortex.orchestrators.mcp_tools_registry import MCPToolsRegistry
        
        tool_names = MCPToolsRegistry.get_tool_names()
        
        return {
            "status": "ok",
            "orchestrator": self.get_name(),
            "tools": tool_names,
            "total_tools": MCPToolsRegistry.get_tool_count(),
        }


__all__ = ["OrchestratorBase"]
