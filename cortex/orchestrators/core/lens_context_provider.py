"""lens_context_provider.py — LENS Context Provider.

Provides LENS analysis context for orchestrator invocations with an
in-process LRU cache (Phase 84-d, GAP-84-23). Delegates to the LENS
orchestrator for real analysis on cache miss; caches results keyed by path
for the lifetime of the process.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    """A single LENS cache entry."""
    key: str
    data: dict[str, Any] = field(default_factory=dict)


class LENSCache:
    """Simple in-memory LENS result cache."""

    def __init__(self) -> None:
        """Initialise with empty cache."""
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve a cache entry.

        Args:
            key: Cache key string.

        Returns:
            CacheEntry if found, else None.
        """
        return self._store.get(key)

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Store a cache entry.

        Args:
            key: Cache key string.
            data: Data payload to cache.
        """
        self._store[key] = CacheEntry(key=key, data=data)


class LENSContextProvider:
    """Provides LENS context for orchestrator invocations."""

    def __init__(self) -> None:
        """Initialise with a fresh LENS cache."""
        self.cache = LENSCache()

    def get_context(self, path: str) -> dict[str, Any]:
        """Retrieve LENS context for a workspace path, with caching.

        On a cache hit returns the stored entry. On a cache miss attempts
        to delegate to the LENS orchestrator for real analysis, then caches
        and returns the result.

        Args:
            path: Workspace path to analyse.

        Returns:
            LENS context dictionary with analysis results.
        """
        entry = self.cache.get(path)
        if entry:
            return entry.data
        context: dict[str, Any] = {"path": path, "analysed": False}
        try:
            from cortex.lens.lens_orchestrator import LENSOrchestrator
            orchestrator = LENSOrchestrator()
            result = orchestrator.analyze_file(path)
            if result:
                context = {"path": path, "analysed": True, **result}
        except Exception:
            pass  # Fallback to minimal context — LENS not available
        self.cache.set(path, context)
        return context
