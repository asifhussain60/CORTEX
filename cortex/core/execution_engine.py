"""Unified execution hub for intent-routed operations.

Phase-m2-c introduces this component as a canonical dispatch layer.
"""

from __future__ import annotations

from typing import Any, Callable, Optional


class ExecutionEngine:
    """Dispatch classified routes to registered handlers."""

    def __init__(self, handlers: Optional[dict[str, Callable[[dict[str, Any]], dict[str, Any]]]] = None) -> None:
        """Initialise engine.

        Args:
            handlers: Optional initial route handlers.
        """
        self._handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = handlers or {}

    def register_handler(self, route: str, handler: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        """Register a route handler.

        Args:
            route: Route key.
            handler: Handler callable.
        """
        self._handlers[route] = handler

    def execute(self, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute payload for a route.

        Args:
            route: Route key resolved by intent gateway.
            payload: Request payload.

        Returns:
            Handler response enriched with route metadata.

        Raises:
            KeyError: If no handler exists for the route.
        """
        handler = self._handlers.get(route)
        if handler is None:
            raise KeyError(f"No handler registered for route: {route}")

        response = handler(payload)
        return {
            "route": route,
            "status": "executed",
            "result": response,
        }

    def health_check(self) -> dict[str, Any]:
        """Return health status for wiring-contract checks."""
        return {
            "status": "healthy",
            "component": "ExecutionEngine",
            "registered_routes": len(self._handlers),
        }
