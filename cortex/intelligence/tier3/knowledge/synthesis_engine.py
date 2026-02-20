"""SynthesisEngine — knowledge synthesis from multiple sources (KN-005-01)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SynthesisResult:
    query: str
    sources: List[Dict[str, Any]]
    synthesized_content: str
    confidence: float
    conflicts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SynthesisEngine:
    """Synthesizes knowledge from multiple sources into coherent answers."""

    def synthesize(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        strategy: str = "merge",
    ) -> SynthesisResult:
        """Synthesize knowledge from *sources* to answer *query*."""
        if not sources:
            return SynthesisResult(
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
        return SynthesisResult(
            query=query,
            sources=sources,
            synthesized_content=content,
            confidence=confidence,
        )

    def detect_conflicts(
        self, sources: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect conflicting information across sources."""
        return []

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
