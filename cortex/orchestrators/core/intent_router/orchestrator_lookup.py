"""
orchestrator_lookup.py — Intent Router Orchestrator Lookup

Stub restored for import compatibility. Resolves orchestrator
class references from intent strings.
"""
from __future__ import annotations

from typing import Any


class OrchestratorLookup:
    """Resolves an intent string to the target orchestrator class."""

    def __init__(self) -> None:
        """Initialise OrchestratorLookup with an empty registry."""
        self._registry: dict[str, Any] = {}

    def register(self, intent: str, orchestrator_cls: Any) -> None:
        """Register an orchestrator class for an intent.

        Args:
            intent: The intent key (e.g. 'IMPLEMENT', 'FIX').
            orchestrator_cls: The orchestrator class to route to.
        """
        self._registry[intent.upper()] = orchestrator_cls

    def resolve(self, intent: str) -> Any | None:
        """Resolve an intent to its orchestrator class.

        Args:
            intent: The intent string to look up.

        Returns:
            The orchestrator class, or None if not registered.
        """
        return self._registry.get(intent.upper())

    def registered_intents(self) -> list[str]:
        """Return all registered intent keys."""
        return list(self._registry.keys())
