"""
Orchestrator Wiring Module

Provides access to the orchestrator registry for MCP server integration.
This module bridges the gap between the wiring system and MCP tool discovery.

AC-AUDIT-FIX-001: Create missing orchestrator_wiring module
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_wiring_registry() -> Any:
    """
    Get the orchestrator wiring registry.

    Returns the registry object that tracks all wired orchestrators.
    Used by MCP server to discover tools from orchestrators.

    Returns:
        WiringRegistry instance, or a mock if not available
    """
    try:
        # Try to import and get the actual registry
        # AC-PRODUCTION-READINESS-001: Fix import path
        from cortex.wiring.registry.git_backed_registry import GitBackedRegistry

        # Create new instance and load wiring
        registry = GitBackedRegistry()
        registry.load()
        return registry
    except (ImportError, AttributeError) as e:
        logger.warning(f"GitBackedRegistry not available: {e}, returning mock registry")
        return MockWiringRegistry()


class MockWiringRegistry:
    """
    Mock wiring registry for graceful degradation.

    Used when the actual wiring registry is not available.
    Prevents MCP server from crashing during tool discovery.
    """

    def __init__(self):
        """Initialize mock registry."""
        self.wired_orchestrators: Dict[str, Any] = {}
        logger.info("Using MockWiringRegistry (actual registry not available)")

    def get_orchestrator(self, name: str) -> Optional[Any]:
        """
        Get an orchestrator by name.

        Args:
            name: Orchestrator name

        Returns:
            None (mock implementation)
        """
        return None

    def list_orchestrators(self) -> Dict[str, Any]:
        """
        List all registered orchestrators.

        Returns:
            Empty dict (mock implementation)
        """
        return {}


__all__ = [
    "get_wiring_registry",
    "MockWiringRegistry",
]
