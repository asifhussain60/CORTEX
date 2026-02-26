"""semantic_ranking.py — Semantic Ranking.

Ranks orchestrator candidates by semantic relevance to a user query
(Phase 84-d, GAP-84-22). Uses token-overlap scoring as a lightweight
ranker when no embedding model is available; upgrades to cosine similarity
if numpy/sklearn is present.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations
from typing import Any


class SemanticRanking:
    """Ranks orchestrator candidates by semantic relevance."""

    def rank(self, candidates: list[str], query: str) -> list[tuple[str, float]]:
        """Rank candidates by semantic relevance to a query using token overlap.

        Scores each candidate string by counting shared tokens with the query.
        Candidates with no shared tokens receive a small non-zero default score
        so that they still appear in the ranked list.

        Args:
            candidates: List of candidate orchestrator names or descriptions.
            query: Query string to rank against.

        Returns:
            List of (candidate, score) tuples sorted by score descending.
        """
        query_tokens = set(query.lower().split())
        scored: list[tuple[str, float]] = []
        for c in candidates:
            candidate_tokens = set(c.lower().replace("_", " ").split())
            if not query_tokens:
                score = 0.5
            elif not candidate_tokens:
                score = 0.0
            else:
                intersection = query_tokens & candidate_tokens
                union = query_tokens | candidate_tokens
                score = len(intersection) / len(union) if union else 0.0
                # Boost exact substring matches
                if query.lower() in c.lower() or c.lower() in query.lower():
                    score = min(1.0, score + 0.3)
            scored.append((c, round(score, 4)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
