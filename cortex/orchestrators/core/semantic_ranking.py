"""semantic_ranking.py — Semantic Ranking stub."""
from __future__ import annotations
from typing import Any


class SemanticRanking:
    """Ranks orchestrator candidates by semantic relevance."""

    def rank(self, candidates: list[str], query: str) -> list[tuple[str, float]]:
        """Rank candidates by relevance to a query.

        Args:
            candidates: List of candidate names.
            query: Query string to rank against.

        Returns:
            List of (candidate, score) tuples sorted by score descending.
        """
        return [(c, 1.0) for c in candidates]
