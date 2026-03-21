"""SynthesisEngine — knowledge synthesis from multiple sources (KN-005-01).

AC_START: AC-66-B-001-SYNTHESIS-ENGINE-20260224T000000Z
AC_COMPLETE: AC-66-B-001-SYNTHESIS-ENGINE-20260224T000000Z | marker pair declared for static audit coverage
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeSynthesisResult:
    """Result of cross-source knowledge synthesis (tier3 internal — Phase 107 rename).

    Renamed from SynthesisResult → KnowledgeSynthesisResult to resolve CORE-035
    name collision with the canonical cortex.intelligence.models.SynthesisResult.
    This class has a different structure (query/sources/confidence) vs. the
    canonical intelligence SynthesisResult (merged_rules/citations/violations/guidance).

    Authority: GAP-107-02 (Phase 107 Sub-Phase A)
    """

    query: str
    sources: List[Dict[str, Any]]
    synthesized_content: str
    confidence: float
    conflicts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# Backward-compat alias — remove after Sub-Phase B sweep
SynthesisResult = KnowledgeSynthesisResult  # type: ignore[misc]  # noqa: N818


class SynthesisEngine:
    """Synthesizes knowledge from multiple sources into coherent answers."""

    def synthesize(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        strategy: str = "merge",
    ) -> KnowledgeSynthesisResult:
        """Synthesize knowledge from *sources* to answer *query*."""
        if not sources:
            return KnowledgeSynthesisResult(
                query=query,
                sources=[],
                synthesized_content="No sources available.",
                confidence=0.0,
            )
        contents = [str(s.get("content", s.get("description", ""))) for s in sources]
        if strategy == "merge":
            content = "\n\n".join(c for c in contents if c)
        elif strategy == "first":
            content = contents[0] if contents else ""
        else:
            content = "\n".join(f"- {c}" for c in contents if c)
        confidence = min(1.0, 0.5 + len(sources) * 0.1)
        return KnowledgeSynthesisResult(
            query=query,
            sources=sources,
            synthesized_content=content,
            confidence=confidence,
        )

    def detect_conflicts(
        self,
        sources: List[Dict[str, Any]],
        sweep_id: Optional[str] = None,
    ) -> List[str]:
        """Detect conflicting information across sources and populate SweepCatalogue.

        Compares ``content`` fields across sources for contradictory signals.
        When conflicts are found and ``sweep_id`` is provided, each conflict is
        submitted to :class:`~cortex.orchestrators.support.sweep_catalogue_orchestrator.SweepCatalogueOrchestrator`
        via :meth:`_submit_to_sweep_catalogue`.

        Args:
            sources: List of knowledge source dicts, each with at least an
                     ``id`` and ``content`` key.
            sweep_id: Optional sweep identifier for SweepCatalogue submission
                      (GAP-66-007).  When ``None``, conflicts are returned but
                      not persisted.

        Returns:
            List of conflict description strings.  Empty when no conflicts
            detected.
        """
        if len(sources) < 2:
            return []

        conflicts: List[str] = []
        contents = [(s.get("id", str(i)), str(s.get("content", ""))) for i, s in enumerate(sources)]

        # Simple conflict heuristic: look for negation or contradictory signals
        _NEGATION_MARKERS = ("not", "deprecated", "instead", "replaced", "conflicts", "incorrect")
        seen_ids: set = set()
        for i, (id_a, content_a) in enumerate(contents):
            for j, (id_b, content_b) in enumerate(contents):
                if i >= j:
                    continue
                pair_key = f"{id_a}:{id_b}"
                if pair_key in seen_ids:
                    continue
                seen_ids.add(pair_key)
                # Extract meaningful nouns (simplistic: split on whitespace)
                words_a = set(content_a.lower().split())
                words_b = set(content_b.lower().split())
                common = words_a & words_b
                # If they share topic words and one contains a negation marker → conflict
                if common and any(m in words_a or m in words_b for m in _NEGATION_MARKERS):
                    conflict_desc = (
                        f"Conflict between '{id_a}' and '{id_b}': "
                        f"shared topic words {list(common)[:5]!r} with opposing signals."
                    )
                    conflicts.append(conflict_desc)

        if conflicts and sweep_id:
            self._submit_to_sweep_catalogue(sweep_id=sweep_id, conflicts=conflicts)

        return conflicts

    def _submit_to_sweep_catalogue(
        self,
        sweep_id: str,
        conflicts: List[str],
    ) -> None:
        """Submit detected conflicts to SweepCatalogueOrchestrator.

        Creates one :meth:`~cortex.orchestrators.support.sweep_catalogue_orchestrator.SweepCatalogueOrchestrator.add_issue`
        entry per conflict, associating each with the provided sweep.

        Args:
            sweep_id: Sweep identifier to attach issues to.
            conflicts: List of conflict description strings from
                       :meth:`detect_conflicts`.
        """
        try:
            from cortex.orchestrators.support.sweep_catalogue_orchestrator import (
                SweepCatalogueOrchestrator,
            )
            catalogue = SweepCatalogueOrchestrator()
            for conflict in conflicts:
                catalogue.add_issue(
                    sweep_id=sweep_id,
                    file="SynthesisEngine",
                    description=conflict,
                )
        except Exception:  # noqa: BLE001
            # Graceful degradation — never block synthesis on catalogue errors
            pass

    def merge(
        self,
        primary: Dict[str, Any],
        secondary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge two knowledge entries."""
        merged = {**secondary, **primary}
        tags = list(set(primary.get("tags", []) + secondary.get("tags", [])))
        if tags:
            merged["tags"] = tags
        return merged
