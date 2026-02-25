"""
Tier 3 Scratch: Ephemeral working memory for CORTEX orchestrators.

GAP-57-08 (Phase 57-f): Exposes scratch_space path connector pointing to
.cortex-runtime/scratch/ for transient working-memory use.

Authority: AC-PHASE57-F-001
"""
from __future__ import annotations

from pathlib import Path

# Canonical scratch space path (ephemeral — not committed, cleaned on restart)
SCRATCH_PATH: Path = Path(".cortex-runtime") / "scratch"
scratch_space: Path = SCRATCH_PATH


def ensure_scratch_space() -> Path:
    """Create scratch space directory if it does not exist.

    Returns:
        Absolute Path to the scratch directory.

    Authority: AC-PHASE57-F-001
    """
    SCRATCH_PATH.mkdir(parents=True, exist_ok=True)
    return SCRATCH_PATH


try:
    from cortex.intelligence.tier3.knowledge import (
        ExpertRegistry,
        Expert,
        AICurator,
        CurationResult,
        KnowledgeIndexer,
        IndexEntry,
        SynthesisEngine,
        SynthesisResult,
    )

    __all__ = [
        "ExpertRegistry",
        "Expert",
        "AICurator",
        "CurationResult",
        "KnowledgeIndexer",
        "IndexEntry",
        "SynthesisEngine",
        "SynthesisResult",
        "scratch_space",
        "SCRATCH_PATH",
        "ensure_scratch_space",
    ]
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "Optional cortex dependency unavailable: cortex.intelligence.tier3.knowledge"
        " — feature degraded"
    )
    __all__ = ["scratch_space", "SCRATCH_PATH", "ensure_scratch_space"]
