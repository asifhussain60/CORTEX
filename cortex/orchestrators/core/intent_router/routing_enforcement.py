"""
routing_enforcement.py — Intent Router Routing Enforcement

Stub restored for import compatibility. Enforces CORE routing rules
during intent classification.
"""
from __future__ import annotations

from typing import Any


class RoutingEnforcement:
    """Validates and enforces routing decisions against CORE governance rules."""

    def __init__(self) -> None:
        """Initialise RoutingEnforcement."""
        self._violations: list[str] = []

    def enforce(self, intent: str, confidence: float) -> bool:
        """Enforce routing rules for a given intent and confidence score.

        Args:
            intent: The classified intent string.
            confidence: Confidence score (0.0–1.0).

        Returns:
            True if routing is allowed, False if blocked.
        """
        if confidence < 0.0 or confidence > 1.0:
            self._violations.append(f"Invalid confidence: {confidence}")
            return False
        return True

    @property
    def violations(self) -> list[str]:
        """Return accumulated violations."""
        return list(self._violations)
