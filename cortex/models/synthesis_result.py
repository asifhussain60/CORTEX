"""
Canonical SynthesisResult — cortex.models.synthesis_result (GAP-80-04).

Single authoritative definition of SynthesisResult used across CORTEX.
Consolidates: unified_intelligence_context.SynthesisResult (primary),
conversation_synthesizer.SynthesisResult, context_synthesizer.SynthesisResult,
and tier3/knowledge/synthesis_engine.SynthesisResult.

Callers in cortex/intelligence/knowledge/ and cortex/core/ should import
from this module instead of defining their own SynthesisResult.

CORE-011: type hints  CORE-012: docstrings  CORE-035: single canonical definition
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SynthesisResult:  # noqa: CORE-035-scoped — domain-specific synthesis result structure
    """Canonical synthesis result representing merged intelligence output.

    This is the single source-of-truth SynthesisResult for CORTEX.
    Fields are a superset of all former SynthesisResult definitions so
    existing callers can migrate without losing data.

    Attributes:
        guidance: List of proactive guidance strings for the engineer.
        confidence: Confidence score in the synthesis (0.0–1.0).
        merged_rules: Precedence-resolved ruleset (from KnowledgeSynthesisEngine).
        citations: Rule IDs cited in the synthesis decision.
        violations: Rules that were violated (if any).
        context: Optional synthesized context text (from ContextSynthesizer).
        metadata: Arbitrary metadata dict for extra synthesis information.
        sources: Source documents contributing to this synthesis.
        query: The original query that triggered this synthesis.
        recommendations: Additional recommendations beyond guidance.
    """

    guidance: List[str] = field(default_factory=list)
    confidence: float = 1.0
    merged_rules: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    query: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
