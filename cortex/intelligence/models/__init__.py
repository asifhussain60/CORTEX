"""
cortex.intelligence.models — Canonical Intelligence Models Package.

Single public API for all intelligence base classes and dataclasses.
Authority: Phase 107 Sub-Phase A (GAP-107-01 + GAP-107-02)

Public exports
--------------
BaseIntelligenceEngine  — merged ABC (from models.base_engine)
AnalysisContext         — input context dataclass
AnalysisResult          — output result dataclass
EngineMetrics           — metrics dataclass
SynthesisResult         — knowledge synthesis result (canonical)
UnifiedIntelligenceContext — unified cross-source context

Usage::

    from cortex.intelligence.models import (
        BaseIntelligenceEngine,
        AnalysisContext,
        AnalysisResult,
        EngineMetrics,
        SynthesisResult,
        UnifiedIntelligenceContext,
    )
"""

from __future__ import annotations

from cortex.intelligence.models.base_engine import (
    AnalysisContext,
    AnalysisResult,
    BaseIntelligenceEngine,
    EngineMetrics,
)
from cortex.intelligence.models.context import (
    CORTEXKnowledge,
    CompanyKnowledge,
    LENSIntelligence,
    SynthesisResult,
    UnifiedIntelligenceContext,
)

__all__ = [
    "BaseIntelligenceEngine",
    "AnalysisContext",
    "AnalysisResult",
    "EngineMetrics",
    "SynthesisResult",
    "UnifiedIntelligenceContext",
    # Supporting types (re-exported for convenience)
    "LENSIntelligence",
    "CompanyKnowledge",
    "CORTEXKnowledge",
]
