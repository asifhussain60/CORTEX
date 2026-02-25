"""audit_trail.py — Audit Trail stub."""
from __future__ import annotations
from typing import Any
import datetime


class AuditTrail:
    """Records audit events to the runtime trace store."""

    def __init__(self) -> None:
        """Initialise with empty event log."""
        self._events: list[dict[str, Any]] = []

    def record(self, event: str, metadata: dict[str, Any] | None = None) -> None:
        """Record an audit event.

        Args:
            event: Event name or description.
            metadata: Optional event metadata.
        """
        self._events.append({
            "event": event,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        })

    def events(self) -> list[dict[str, Any]]:
        """Return all recorded events."""
        return list(self._events)
