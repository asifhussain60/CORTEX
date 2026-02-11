"""
CORTEX Intelligence Layer.

Deep computation engines for code analysis:
- AST analysis (syntax and structure)
- Git intelligence (history, blame, patterns)
- Relationship traversal (dependencies, call graphs)
- Pattern detection (anti-patterns, best practices)
- Semantic analysis (code similarity, embeddings)
- Comment intelligence (quality, coverage)

Authority: Phase 56 - LENS/Intelligence Hybrid Architecture
"""

from cortex.intelligence.base import (
    AnalysisContext,
    AnalysisResult,
    BaseIntelligenceEngine,
)

__all__ = [
    "BaseIntelligenceEngine",
    "AnalysisContext",
    "AnalysisResult",
]
