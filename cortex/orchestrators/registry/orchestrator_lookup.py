"""orchestrator_lookup.py — Orchestrator Lookup Registry."""
from __future__ import annotations
from typing import Any


class OrchestratorLookup:
    """Resolves intent strings to orchestrator classes."""

    def __init__(self) -> None:
        """Initialise with empty registry."""
        self._registry: dict[str, Any] = {}

    def register(self, intent: str, orchestrator_cls: Any) -> None:
        """Register an orchestrator for an intent.

        Args:
            intent: Intent key (e.g. IMPLEMENT, FIX).
            orchestrator_cls: The orchestrator class to map.
        """
        self._registry[intent.upper()] = orchestrator_cls

    def resolve(self, intent: str) -> Any | None:
        """Resolve an intent to its orchestrator class.

        Args:
            intent: Intent string to look up.

        Returns:
            Orchestrator class or None.
        """
        return self._registry.get(intent.upper())

    def registered_intents(self) -> list[str]:
        """Return all registered intent keys."""
        return list(self._registry.keys())
