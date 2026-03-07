"""ContentLibraryOrchestrator — Response-layer content pool coordinator.

Bridges the ContentLibraryEngine (intelligence layer) with the response
composition pipeline. Invoked by MasterOrchestrator at Stage 4 (response
enrichment) to select the next quote, principle, or AI spark for the current
response turn.

Phase: 130 (GAP-130-03)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cortex.intelligence.content_library_engine import (
    ContentLibraryEngine,
    get_content_library_engine,
)

logger = logging.getLogger(__name__)


class ContentLibraryOrchestrator:
    """Coordinates content pool selection for response composition.

    This orchestrator is the single entry point for all content selection
    at response assembly time.  It delegates to :class:`ContentLibraryEngine`
    for pool management and epoch-shuffled anti-repetition.

    Lifecycle:
        - Instantiated once per session by MasterOrchestrator Stage 4.
        - :meth:`orchestrate` is called per response turn to obtain the
          appropriate content item for the chosen pool.

    Usage::

        orch = ContentLibraryOrchestrator()
        result = orch.orchestrate(pool="quotes")
        # {"text": "...", "author": "...", "book": "...", "theme": "..."}

        # Mutual exclusion across pools
        result = orch.orchestrate_across(["principles", "ai_sparks"])
        # {"pool": "principles", "title": "...", "body": "..."}

    Phase: 130 — GAP-130-03
    """

    def __init__(
        self,
        engine: Optional[ContentLibraryEngine] = None,
    ) -> None:
        """Initialize instance.

        Args:
            engine: Optional :class:`ContentLibraryEngine` to use. Defaults
                to the module-level singleton from :func:`get_content_library_engine`.
        """
        self._engine: ContentLibraryEngine = engine or get_content_library_engine()
        logger.debug("ContentLibraryOrchestrator initialised")

    # ── Public API ────────────────────────────────────────────────────────────

    def orchestrate(self, pool: str = "quotes") -> Dict[str, Any]:
        """Select the next content item from the specified pool.

        Delegates to :meth:`ContentLibraryEngine.select`.

        Args:
            pool: Pool name — one of ``"quotes"``, ``"principles"``,
                  or ``"ai_sparks"``.

        Returns:
            A dict with the item's fields appropriate for template rendering.
        """
        try:
            return self._engine.select(pool)
        except Exception as exc:
            logger.warning("ContentLibraryOrchestrator.orchestrate() failed for pool '%s': %s", pool, exc)
            return {"error": str(exc), "pool": pool}

    def orchestrate_across(self, pools: List[str]) -> Dict[str, Any]:
        """Select one item from the given pools, enforcing mutual exclusion.

        Delegates to :meth:`ContentLibraryEngine.select_across`.

        Args:
            pools: Pool names to choose from.

        Returns:
            A dict with the item's fields plus a ``"pool"`` key.
        """
        try:
            return self._engine.select_across(pools)
        except Exception as exc:
            logger.warning("ContentLibraryOrchestrator.orchestrate_across() failed: %s", exc)
            return {"error": str(exc), "pool": pools[0] if pools else "unknown"}

    def stats(self) -> Dict[str, Any]:
        """Return per-pool statistics from the engine.

        Returns:
            Dict mapping pool names to their current epoch and history stats.
        """
        return self._engine.stats()
