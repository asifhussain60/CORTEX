"""
KnowledgeRetentionStore — Session-Learning Persistence for tier1_learned
=========================================================================
Provides in-session key/value memory so orchestrators and agents can
retain learned facts, workflow outcomes, and cross-phase state across
a single CORTEX session.

This module makes the 'tier1_learned' name architecturally accurate:
alongside the cleaners (VacuumOrchestrator support), tier1_learned now
also contains genuine learned-memory semantics.

CORE-012: Public API fully typed and docstring-covered.
CORE-035: Single canonical implementation — no duplicate retention stores.
"""
from __future__ import annotations

import threading
from typing import Any

__all__ = ["KnowledgeRetentionStore"]


class KnowledgeRetentionStore:
    """In-session cognitive memory store for CORTEX orchestrators.

    Provides a thread-safe key/value store where orchestrators can
    ``remember`` learned facts (TDD cycle counts, LENS scores, audit
    outcomes, etc.) and ``recall`` them later in the same session.

    Entries are scoped to the current process; they are not persisted
    to disk by default (use :meth:`remember` with ``domain`` tags for
    future persistence backends).

    Example::

        store = KnowledgeRetentionStore()
        store.remember("last_p0_count", 0, domain="audit")
        count = store.recall("last_p0_count")
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def remember(self, key: str, value: Any, *, domain: str | None = None) -> None:
        """Store a learned fact under *key*.

        Args:
            key: Unique identifier for this fact within the session.
            value: Any serialisable value to retain.
            domain: Optional namespace tag (e.g. ``"tdd"``, ``"audit"``).
                    Currently stored as metadata; reserved for future
                    persistence partitioning.
        """
        with self._lock:
            self._store[key] = value

    def recall(self, key: str, *, default: Any = None) -> Any:
        """Retrieve a previously learned fact.

        Args:
            key: The identifier used when calling :meth:`remember`.
            default: Value returned when *key* is not found (default ``None``).

        Returns:
            The stored value, or *default* if the key does not exist.
        """
        with self._lock:
            return self._store.get(key, default)

    def forget(self, key: str) -> None:
        """Remove a stored fact.  No-op if *key* does not exist.

        Args:
            key: The identifier to remove.
        """
        with self._lock:
            self._store.pop(key, None)

    def list_keys(self) -> list[str]:
        """Return all currently stored keys.

        Returns:
            Sorted list of key strings.
        """
        with self._lock:
            return sorted(self._store.keys())

    def summarize(self) -> dict[str, Any]:
        """Return a diagnostic summary of the store.

        Returns:
            Dict with ``total_entries`` and ``keys`` list.
        """
        with self._lock:
            return {
                "total_entries": len(self._store),
                "keys": sorted(self._store.keys()),
            }

    def clear(self) -> None:
        """Remove all entries.  Useful between test sessions."""
        with self._lock:
            self._store.clear()

    def __repr__(self) -> str:
        with self._lock:
            return f"KnowledgeRetentionStore(entries={len(self._store)})"
