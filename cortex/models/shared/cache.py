"""
cortex/models/shared/cache.py — Canonical CacheEntry.

Phase 114-a GAP-114-01: Single authoritative CacheEntry used across CORTEX.
Consolidates 9 separate CacheEntry class definitions.

All new code should import from here:
  from cortex.models.shared.cache import CacheEntry, CacheStats

Governance: CORE-035 (single canonical), CORE-011 (type hints), CORE-012 (docstrings)
Authority: phase-114-a, SWEEP-114-LAYERING-RESET
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CacheEntry:
    """Canonical cache entry with value, TTL, and access metadata.

    Single source-of-truth CacheEntry. Fields are a superset of all
    former CacheEntry definitions so existing callers can migrate
    without losing data.

    Attributes:
        value: The cached value.
        timestamp: Unix timestamp when the entry was created.
        ttl: Time-to-live in seconds (0 = never expire).
        access_count: Number of times this entry has been accessed.
        last_access: Unix timestamp of most recent access.
        key: Optional cache key for self-referential lookup.
        metadata: Arbitrary extra metadata.
    """

    value: Any
    timestamp: float = field(default_factory=time.time)
    ttl: float = 0.0
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    key: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Return True if the entry has exceeded its TTL."""
        if self.ttl <= 0:
            return False
        return (time.time() - self.timestamp) > self.ttl

    def touch(self) -> None:
        """Update last_access and increment access_count."""
        self.last_access = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Canonical cache statistics.

    Attributes:
        hits: Number of cache hits.
        misses: Number of cache misses.
        evictions: Number of evicted entries.
        size: Current number of entries.
        max_size: Maximum number of entries allowed.
    """

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 1000

    def hit_rate(self) -> float:
        """Return cache hit rate as a float between 0.0 and 1.0."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


__all__ = ["CacheEntry", "CacheStats"]
