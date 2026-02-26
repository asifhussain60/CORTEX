"""
OPJ Promoter — Phase 71-F ES-005: Auto-promotion of high-confidence OPJ
patterns to the T1 knowledge tier.

Patterns with confidence >= PROMOTION_THRESHOLD (default 0.80) are eligible
for automatic promotion so that CORTEX accumulates institutional knowledge
from successful operational patterns.

AC-ID: AC-OPJ-PHASE71F-PROMOTER
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-028 (snake_case), CORE-035 (canonical singleton)
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Sequence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROMOTION_THRESHOLD: float = 0.80
"""Minimum confidence score for automatic T1 promotion."""

T1_KNOWLEDGE_TIER: str = "T1"
"""Target knowledge tier for promoted patterns."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_opj_patterns() -> List[Any]:
    """Load all OPJ patterns from the OPJReader registry.

    This function is the single integration point between the promoter and the
    persistence layer.  It is module-level so that tests can patch it cleanly
    via ``cortex.intelligence.learning.opj_promoter._load_opj_patterns``.

    Returns:
        List of OPJ pattern / entry objects (may be empty if registry is
        absent or unreadable).
    """
    try:
        from cortex.intelligence.learning.opj_reader import OPJReader  # noqa: PLC0415
        reader = OPJReader()
        return list(reader.read_all())
    except Exception:
        logger.debug("OPJ registry unavailable — no patterns loaded for promotion.")
        return []


# ---------------------------------------------------------------------------
# Core promotion function (ES-005)
# ---------------------------------------------------------------------------


def promote_high_confidence_patterns(
    patterns: Optional[Sequence[Any]] = None,
    threshold: float = PROMOTION_THRESHOLD,
    dry_run: bool = False,
) -> List[str]:
    """Promote OPJ patterns with confidence >= threshold to the T1 knowledge tier.

    When *patterns* is ``None`` the function loads all patterns from the OPJ
    registry via :func:`_load_opj_patterns` (patchable in tests).

    Args:
        patterns: Optional sequence of OPJ pattern objects.  Each object must
            expose a ``confidence`` attribute (float) and an ``id`` attribute
            (str).  When ``None`` patterns are loaded from the live registry.
        threshold: Minimum confidence score required for promotion.
            Defaults to :data:`PROMOTION_THRESHOLD` (0.80).
        dry_run: When True, return eligible pattern IDs without mutating them.

    Returns:
        List of ``id`` strings for patterns that were (or are eligible to be)
        promoted.

    Example::

        from cortex.intelligence.learning.opj_promoter import promote_high_confidence_patterns
        promoted_ids = promote_high_confidence_patterns(threshold=0.80)
        print(f"{len(promoted_ids)} patterns promoted to T1.")
    """
    if patterns is None:
        patterns = _load_opj_patterns()

    promoted_ids: List[str] = []

    for pattern in patterns:
        confidence = getattr(pattern, "confidence", 0.0)
        if confidence >= threshold:
            if not dry_run:
                try:
                    pattern.promoted = True
                    pattern.tier = T1_KNOWLEDGE_TIER
                except AttributeError:
                    pass  # read-only model — still counted as eligible
            pattern_id = str(getattr(pattern, "id", "unknown"))
            promoted_ids.append(pattern_id)
            logger.debug(
                "OPJ pattern promoted to %s: id=%s confidence=%.2f",
                T1_KNOWLEDGE_TIER,
                pattern_id,
                confidence,
            )

    logger.info(
        "OPJ promotion complete: %d/%d patterns meet threshold %.2f%s",
        len(promoted_ids),
        len(list(patterns)),
        threshold,
        " (dry_run)" if dry_run else "",
    )

    return promoted_ids


# ---------------------------------------------------------------------------
# Convenience alias
# ---------------------------------------------------------------------------

promote = promote_high_confidence_patterns
"""Alias for :func:`promote_high_confidence_patterns`."""
