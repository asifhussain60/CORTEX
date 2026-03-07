"""ContentLibraryEngine + EpochShuffler — Unified response content pool management.

Manages three distinct content pools (quotes, principles, ai_sparks) with
epoch-based anti-repetition guarantees via the EpochShuffler strategy.

Key guarantees:
  - Within a single epoch of N items, each item appears exactly once
    (Fisher-Yates shuffle applied at epoch boundary).
  - select_across() enforces mutual exclusion — exactly ONE pool renders
    per response (resolves P2 rendering violation from Phase 130 gap audit).
  - All pools are seeded from their canonical YAML SSOT files.

Phase: 130 (GAP-130-03 — ContentLibraryEngine + EpochShuffler)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

# ─── Canonical registry paths ─────────────────────────────────────────────────
_REGISTRY_ROOT = Path(__file__).parent.parent.parent / "cortex-registry"
_PRINCIPLES_YAML = _REGISTRY_ROOT / "knowledge" / "sdlc" / "high-value-principles.yaml"
_QUOTES_YAML = _REGISTRY_ROOT / "templates" / "response" / "atoms" / "atom-quote.yaml"
_AI_SPARK_YAML = _REGISTRY_ROOT / "templates" / "response" / "atoms" / "atom-ai-spark.yaml"


# ─────────────────────────────────────────────────────────────────────────────
# EpochShuffler
# ─────────────────────────────────────────────────────────────────────────────

class EpochShuffler:
    """Fisher-Yates epoch shuffler — anti-repetition guarantee within each epoch.

    Maintains a shuffled copy of *items*.  Every call to :meth:`next` returns
    the next item in the shuffled sequence.  When the sequence is exhausted a
    new epoch begins: the pool is re-shuffled and a fresh pass starts.

    A *ring buffer* of recent draws is maintained so callers can inspect which
    items were returned most recently.

    Args:
        items: The pool of items to shuffle and draw from.  Must be non-empty.
        ring_buffer_size: How many recent draws to retain in :attr:`history`.
            Defaults to ``min(10, len(items))``.
        seed: Optional RNG seed for reproducible testing.

    Example::

        shuffler = EpochShuffler(["a", "b", "c"])
        seen = [shuffler.next() for _ in range(3)]  # epoch 0 — each appears once
        # shuffler.epoch_number == 1  (new epoch starts automatically)

    Phase: 130 — GAP-130-03
    """

    def __init__(
        self,
        items: Sequence[Any],
        ring_buffer_size: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize instance."""
        if not items:
            raise ValueError("EpochShuffler requires a non-empty item pool")
        self._pool: List[Any] = list(items)
        self._rng = random.Random(seed)
        self._ring_size: int = ring_buffer_size if ring_buffer_size is not None else min(10, len(items))
        self._history: List[Any] = []
        self._epoch: int = 0
        self._current_sequence: List[Any] = []
        self._cursor: int = 0
        self._start_new_epoch()

    # ── Public API ────────────────────────────────────────────────────────────

    def next(self) -> Any:
        """Return the next item from the current epoch.

        When the current epoch is exhausted, a new epoch begins automatically
        with a freshly shuffled sequence.  ``epoch_number`` increments as
        soon as the last item of an epoch is returned (eager — not lazy).

        Returns:
            The next item from the shuffled pool.
        """
        if self._cursor >= len(self._current_sequence):
            self._start_new_epoch()

        item = self._current_sequence[self._cursor]
        self._cursor += 1
        self._record(item)

        # Eagerly mark epoch complete so epoch_number reflects exhaustion
        if self._cursor >= len(self._current_sequence):
            self._epoch += 1

        return item

    def reset(self) -> None:
        """Reset the shuffler to epoch 0 and clear history.

        Useful for testing or when the pool content changes.
        """
        self._epoch = 0
        self._history = []
        self._start_new_epoch()

    @property
    def epoch_number(self) -> int:
        """Current epoch number (0-indexed, increments after each full pass)."""
        return self._epoch

    @property
    def history(self) -> List[Any]:
        """The most recent ``ring_buffer_size`` items returned by :meth:`next`.

        Returns a copy — callers cannot mutate the internal ring buffer.
        """
        return list(self._history)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _start_new_epoch(self) -> None:
        """Shuffle the pool and reset the cursor for a new epoch."""
        self._current_sequence = list(self._pool)
        self._rng.shuffle(self._current_sequence)
        self._cursor = 0

    def _record(self, item: Any) -> None:
        """Add *item* to the ring buffer, evicting oldest if full."""
        self._history.append(item)
        if len(self._history) > self._ring_size:
            self._history = self._history[-self._ring_size:]


# ─────────────────────────────────────────────────────────────────────────────
# ContentLibraryEngine
# ─────────────────────────────────────────────────────────────────────────────

class ContentLibraryEngine:
    """Unified manager for the three CORTEX response content pools.

    Pools managed:
      - **quotes** — 120-entry book quote pool from ``atom-quote.yaml``
      - **principles** — 90-entry SDLC principle pool from ``high-value-principles.yaml``
      - **ai_sparks** — AI adoption insight pool from ``atom-ai-spark.yaml``

    Each pool is backed by an :class:`EpochShuffler` for anti-repetition.

    :meth:`select_across` enforces mutual exclusion — only ONE pool renders
    per response, resolving the Proceed Gate principle rendering violation
    identified in GAP-130-02.

    Usage::

        engine = ContentLibraryEngine()
        quote = engine.select("quotes")        # {"text": ..., "author": ..., "book": ...}
        principle = engine.select("principles")  # {"title": ..., "body": ..., "domain": ...}
        spark = engine.select("ai_sparks")     # {"body": ..., "author": ..., "source": ...}

        # Mutual exclusion — picks ONE pool per call
        chosen = engine.select_across(["principles", "ai_sparks"])
        # {"pool": "principles", "title": ..., "body": ...}

    Phase: 130 — GAP-130-03
    Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
    """

    # Pool name constants
    POOL_QUOTES = "quotes"
    POOL_PRINCIPLES = "principles"
    POOL_AI_SPARKS = "ai_sparks"

    def __init__(self) -> None:
        """Initialize instance — seeds all three pools from YAML SSOTs."""
        self.quotes: EpochShuffler = EpochShuffler(self._load_quotes())
        self.principles: EpochShuffler = EpochShuffler(self._load_principles())
        self.ai_sparks: EpochShuffler = EpochShuffler(self._load_ai_sparks())

        self._pools: Dict[str, EpochShuffler] = {
            self.POOL_QUOTES: self.quotes,
            self.POOL_PRINCIPLES: self.principles,
            self.POOL_AI_SPARKS: self.ai_sparks,
        }

        # Tracks which pool was last used for select_across() alternation
        self._last_pool_used: Optional[str] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def select(self, pool: str) -> Dict[str, Any]:
        """Draw the next item from the named pool.

        Args:
            pool: One of ``"quotes"``, ``"principles"``, or ``"ai_sparks"``.

        Returns:
            A dict containing the item's fields.

        Raises:
            ValueError: If *pool* is not recognised.
        """
        if pool not in self._pools:
            raise ValueError(
                f"Unknown pool '{pool}'. Valid pools: {sorted(self._pools)}"
            )
        return self._pools[pool].next()

    def select_across(self, pools: List[str]) -> Dict[str, Any]:
        """Draw from one of the named pools — enforcing mutual exclusion.

        On each call, picks the pool that was NOT used last (alternating) to
        prevent two consecutive responses from using the same atom type.
        The selected pool's name is included in the returned dict under
        the ``"pool"`` key.

        Args:
            pools: List of pool names to choose among (e.g. ``["principles", "ai_sparks"]``).

        Returns:
            A dict with the item's fields plus a ``"pool"`` key indicating
            which pool was selected.

        Raises:
            ValueError: If *pools* is empty or contains unknown pool names.
        """
        if not pools:
            raise ValueError("select_across() requires at least one pool name")
        for p in pools:
            if p not in self._pools:
                raise ValueError(f"Unknown pool '{p}' in select_across() call")

        # Prefer the pool that was NOT used last (simple round-robin alternation)
        preferred: List[str] = [p for p in pools if p != self._last_pool_used]
        chosen_pool = preferred[0] if preferred else pools[0]

        item = self._pools[chosen_pool].next()
        self._last_pool_used = chosen_pool
        item["pool"] = chosen_pool
        return item

    def history(self, pool: str) -> List[Any]:
        """Return the recent-draw history for a pool.

        Args:
            pool: Pool name.

        Returns:
            List of the most recent items drawn from *pool*.
        """
        if pool not in self._pools:
            raise ValueError(f"Unknown pool '{pool}'")
        return self._pools[pool].history

    def reset(self, pool: str) -> None:
        """Reset a pool's EpochShuffler to epoch 0, clearing history.

        Args:
            pool: Pool name to reset.
        """
        if pool not in self._pools:
            raise ValueError(f"Unknown pool '{pool}'")
        self._pools[pool].reset()

    def stats(self) -> Dict[str, Any]:
        """Return per-pool statistics.

        Returns:
            A dict mapping each pool name to its current stats dict.
        """
        result: Dict[str, Any] = {}
        for name, shuffler in self._pools.items():
            result[name] = {
                "epoch": shuffler.epoch_number,
                "history_size": len(shuffler.history),
                "pool_size": len(shuffler._pool),
            }
        return result

    # ── YAML data loaders ─────────────────────────────────────────────────────

    def _load_principles(self) -> List[Dict[str, Any]]:
        """Load principles from high-value-principles.yaml.

        Returns:
            List of principle dicts (keys: title, body, domain, tags, intent_types).
            Falls back to an embedded minimal pool if YAML cannot be read.
        """
        try:
            import yaml  # type: ignore[import]
            raw = yaml.safe_load(_PRINCIPLES_YAML.read_text(encoding="utf-8"))
            items = raw.get("principles", [])
            if items:
                return [
                    {
                        "title": p.get("title", ""),
                        "body": p.get("body", ""),
                        "domain": p.get("domain", ""),
                        "tags": p.get("tags", []),
                    }
                    for p in items
                ]
        except Exception as exc:  # pragma: no cover
            logger.warning("ContentLibraryEngine: could not load principles YAML: %s", exc)

        # Fallback pool — always at least 3 principles so the engine is never empty
        return [
            {"title": "Red–Green–Refactor", "body": "Write failing test, make it pass, then improve.", "domain": "tdd", "tags": ["tdd"]},
            {"title": "Boy Scout Rule", "body": "Always leave the code a little better than you found it.", "domain": "refactoring", "tags": ["refactoring"]},
            {"title": "YAGNI", "body": "You Aren't Gonna Need It — build only what is required now.", "domain": "code_quality", "tags": ["design"]},
        ]

    def _load_quotes(self) -> List[Dict[str, Any]]:
        """Load quotes from atom-quote.yaml.

        Returns:
            List of quote dicts (keys: text, author, book, theme).
            Falls back to a minimal inline pool on failure.
        """
        try:
            import yaml  # type: ignore[import]
            raw = yaml.safe_load(_QUOTES_YAML.read_text(encoding="utf-8"))
            # atom-quote.yaml stores quotes under a 'quotes' key nested per theme
            quotes_section = raw.get("quotes", {})
            items: List[Dict[str, Any]] = []
            if isinstance(quotes_section, dict):
                for theme, theme_quotes in quotes_section.items():
                    if isinstance(theme_quotes, list):
                        for q in theme_quotes:
                            if isinstance(q, dict):
                                items.append({
                                    "text": q.get("text", q.get("quote", "")),
                                    "quote": q.get("text", q.get("quote", "")),
                                    "author": q.get("author", ""),
                                    "book": q.get("source", q.get("book", "")),
                                    "theme": theme,
                                })
            if items:
                return items
        except Exception as exc:  # pragma: no cover
            logger.warning("ContentLibraryEngine: could not load quotes YAML: %s", exc)

        # Fallback pool
        return [
            {"text": "Make it work, make it right, make it fast.", "quote": "Make it work, make it right, make it fast.", "author": "Kent Beck", "book": "TDD by Example", "theme": "quality"},
            {"text": "Programs must be written for people to read.", "quote": "Programs must be written for people to read.", "author": "Harold Abelson", "book": "SICP", "theme": "universal"},
            {"text": "The art of programming is the art of organising complexity.", "quote": "The art of programming is the art of organising complexity.", "author": "E.W. Dijkstra", "book": "Selected Writings", "theme": "universal"},
        ]

    def _load_ai_sparks(self) -> List[Dict[str, Any]]:
        """Load AI spark entries from atom-ai-spark.yaml.

        Returns:
            List of ai_spark dicts (keys: body, author, source).
            Falls back to a minimal inline pool on failure.
        """
        try:
            import yaml  # type: ignore[import]
            raw = yaml.safe_load(_AI_SPARK_YAML.read_text(encoding="utf-8"))
            spark_pool = raw.get("spark_pool", raw.get("sparks", []))
            if isinstance(spark_pool, list) and spark_pool:
                return [
                    {
                        "body": s.get("body", s.get("text", "")),
                        "author": s.get("author", ""),
                        "source": s.get("source", ""),
                    }
                    for s in spark_pool
                    if isinstance(s, dict)
                ]
        except Exception as exc:  # pragma: no cover
            logger.warning("ContentLibraryEngine: could not load ai_sparks YAML: %s", exc)

        # Fallback pool
        return [
            {"body": "AI won't replace engineers. Engineers who use AI will replace engineers who don't.", "author": "Jensen Huang", "source": "NVIDIA GTC 2024"},
            {"body": "The most powerful tool we have as developers is automation.", "author": "Scott Hanselman", "source": "CodeNewbie Podcast"},
            {"body": "Intelligence is the ability to adapt to change.", "author": "Stephen Hawking", "source": "A Brief History of Time"},
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

_engine: Optional[ContentLibraryEngine] = None


def get_content_library_engine() -> ContentLibraryEngine:
    """Return the module-level ContentLibraryEngine singleton.

    Creates on first access (lazy initialization).

    Returns:
        Shared :class:`ContentLibraryEngine` instance.
    """
    global _engine
    if _engine is None:
        _engine = ContentLibraryEngine()
    return _engine
