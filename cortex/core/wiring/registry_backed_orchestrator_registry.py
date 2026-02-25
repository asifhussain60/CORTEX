"""registry_backed_orchestrator_registry.py — Registry-Backed Orchestrator Registry stub."""
from __future__ import annotations
from typing import Any


class RegistryBackedOrchestratorRegistry:
    """Registry backed by YAML wiring specifications."""

    def __init__(self) -> None:
        """Initialise with empty registry."""
        self._entries: dict[str, Any] = {}

    def register(self, name: str, cls: Any) -> None:
        """Register an orchestrator class.

        Args:
            name: Orchestrator name.
            cls: Orchestrator class.
        """
        self._entries[name] = cls

    def get(self, name: str) -> Any | None:
        """Retrieve an orchestrator class by name.

        Args:
            name: Orchestrator name.

        Returns:
            Orchestrator class or None.
        """
        return self._entries.get(name)
