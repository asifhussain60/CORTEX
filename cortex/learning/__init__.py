"""
Learning module for CORTEX - Universal Learning Loop.

Phase 71 S1: Universal Learning Infrastructure
Provides automatic pattern extraction and knowledge integration for all orchestrators.
"""

from cortex.learning.universal_learning_loop import (
    UniversalLearningLoop,
    get_learning_loop,
    LearningCapture,
    PatternType,
)
from cortex.learning.pattern_extractor import (
    PatternExtractor,
    ExtractedPattern,
)
from cortex.learning.knowledge_merger import (
    KnowledgeMerger,
    MergeStrategy,
)
from cortex.learning.confidence_scorer import (
    ConfidenceScorer,
    ConfidenceLevel,
)

__all__ = [
    # Universal Learning Loop
    "UniversalLearningLoop",
    "get_learning_loop",
    "LearningCapture",
    "PatternType",
    # Pattern Extraction
    "PatternExtractor",
    "ExtractedPattern",
    # Knowledge Merging
    "KnowledgeMerger",
    "MergeStrategy",
    # Confidence Scoring
    "ConfidenceScorer",
    "ConfidenceLevel",
]

