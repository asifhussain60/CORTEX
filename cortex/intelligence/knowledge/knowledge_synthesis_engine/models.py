"""
KSE data models — KnowledgeSource, SynthesizedInstruction.

Phase 103-g: extracted from knowledge_synthesis_engine.py (1,567L) god-object.
CORE-035 — domain-scoped dataclass; distinct from canonical_enums.KnowledgeSource(Enum)
"""
# CORE-035-scoped — domain-scoped KnowledgeSource dataclass, distinct from canonical_enums Enum
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KnowledgeSource:
    """Attribution for a knowledge source."""

    layer: str  # "CORTEX" or "Company"
    domain: str  # e.g., "TESTING-VALIDATION", "PRODUCT-ENGINEERING"
    priority: Optional[str] = None
    yaml_files: List[str] = field(default_factory=list)


@dataclass
class SynthesizedInstruction:
    """Final synthesized instruction set with source attribution."""

    instruction: str
    sources: List[KnowledgeSource]
    synthesis_confidence: float  # 0.0-1.0
    composition_rules_applied: List[str] = field(default_factory=list)
