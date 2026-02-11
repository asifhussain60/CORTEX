"""
Learning Extraction Engine for CORTEX.

Extracts patterns, insights, and learnings from conversation
sessions for continuous improvement.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 3 specification
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    SentenceTransformer = None  # type: ignore
    cosine_similarity = None  # type: ignore
    np = None  # type: ignore

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of learning insights."""
    FEATURE_REQUEST = "FEATURE_REQUEST"
    BUG_PATTERN = "BUG_PATTERN"
    DESIGN_DECISION = "DESIGN_DECISION"
    REFACTOR_OPPORTUNITY = "REFACTOR_OPPORTUNITY"
    BEST_PRACTICE = "BEST_PRACTICE"


class PatternType(Enum):
    """Types of recognized patterns."""
    IMPLEMENTATION = "IMPLEMENTATION"
    DEBUGGING = "DEBUGGING"
    TESTING = "TESTING"
    REFACTORING = "REFACTORING"
    DOCUMENTATION = "DOCUMENTATION"


@dataclass
class LearningInsight:
    """
    Learning insight from conversation.

    Attributes:
        insight_type: Type of insight
        description: Insight description
        confidence: Confidence score (0-1)
        evidence: Supporting evidence from conversation
        metadata: Optional additional metadata
    """
    insight_type: InsightType
    description: str
    confidence: float
    evidence: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecognizedPattern:
    """
    Recognized conversation pattern.

    Attributes:
        pattern_type: Type of pattern
        description: Pattern description
        occurrences: Number of occurrences
        confidence: Confidence score (0-1)
        examples: Example excerpts
    """
    pattern_type: PatternType
    description: str
    occurrences: int
    confidence: float
    examples: List[str] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """
    Learning extraction result.

    Attributes:
        insights: Extracted insights
        patterns: Recognized patterns
        total_processed: Total turns processed
    """
    insights: List[LearningInsight]
    patterns: List[RecognizedPattern]
    total_processed: int


@dataclass
class ExtractionConfig:
    """
    Extraction configuration.

    Attributes:
        min_confidence: Minimum confidence threshold
        extract_patterns: Whether to extract patterns
        extract_insights: Whether to extract insights
    """
    min_confidence: float = 0.7
    extract_patterns: bool = True
    extract_insights: bool = True


class LearningExtractor:
    """
    Learning extraction engine.

    Extracts insights and patterns from conversations for
    continuous improvement.
    """

    # Pattern keywords for detection
    PATTERN_KEYWORDS = {
        PatternType.IMPLEMENTATION: [
            "implement", "create", "build", "develop", "code", "write",
            "red", "green", "refactor", "tdd",
        ],
        PatternType.DEBUGGING: [
            "debug", "error", "bug", "fix", "issue", "problem",
            "investigate", "trace", "root cause",
        ],
        PatternType.TESTING: [
            "test", "verify", "validate", "assert", "check",
            "unit test", "integration test", "coverage",
        ],
        PatternType.REFACTORING: [
            "refactor", "improve", "optimize", "clean up", "simplify",
            "restructure", "reorganize",
        ],
        PatternType.DOCUMENTATION: [
            "document", "docs", "readme", "comment", "docstring",
            "explain", "describe",
        ],
    }

    # Insight keywords for detection
    INSIGHT_KEYWORDS = {
        InsightType.FEATURE_REQUEST: [
            "feature", "add", "new", "would like", "can we", "should we",
            "request", "need", "want",
        ],
        InsightType.BUG_PATTERN: [
            "bug", "error", "crash", "fail", "broken", "issue",
            "wrong", "incorrect", "mistake",
        ],
        InsightType.DESIGN_DECISION: [
            "architecture", "design", "pattern", "approach", "strategy",
            "chose", "decided", "because", "reason",
        ],
        InsightType.REFACTOR_OPPORTUNITY: [
            "could improve", "should refactor", "technical debt",
            "code smell", "duplication", "complexity",
        ],
        InsightType.BEST_PRACTICE: [
            "best practice", "recommended", "standard", "convention",
            "guideline", "should", "prefer",
        ],
    }

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        config: Optional[ExtractionConfig] = None,
    ):
        """
        Initialize learning extractor.

        Args:
            model_name: SentenceTransformer model name
            config: Extraction configuration

        Raises:
            ImportError: If dependencies not installed
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Required dependencies not installed. "
                "Install with: pip install sentence-transformers scikit-learn"
            )

        self.model = SentenceTransformer(model_name)
        self.config = config or ExtractionConfig()

        logger.info(f"LearningExtractor initialized with model: {model_name}")

    def extract(self, conversation: List[str]) -> ExtractionResult:
        """
        Extract learnings from conversation.

        Args:
            conversation: List of conversation turns

        Returns:
            ExtractionResult: Extraction result
        """
        if not conversation:
            return ExtractionResult(
                insights=[],
                patterns=[],
                total_processed=0,
            )

        insights = []
        patterns = []

        if self.config.extract_insights:
            insights = self.extract_insights(conversation)

        if self.config.extract_patterns:
            patterns = self.recognize_patterns(conversation)

        return ExtractionResult(
            insights=insights,
            patterns=patterns,
            total_processed=len(conversation),
        )

    def extract_insights(self, conversation: List[str]) -> List[LearningInsight]:
        """
        Extract insights from conversation.

        Args:
            conversation: List of conversation turns

        Returns:
            List[LearningInsight]: Extracted insights
        """
        if not conversation:
            return []

        insights = []

        # Combine conversation for full context
        full_text = " ".join(conversation).lower()

        # Check each insight type
        for insight_type, keywords in self.INSIGHT_KEYWORDS.items():
            matches = []
            for keyword in keywords:
                if keyword in full_text:
                    matches.append(keyword)

            if matches:
                # Calculate confidence based on keyword frequency
                confidence = min(1.0, len(matches) / len(keywords) * 2)

                if confidence >= self.config.min_confidence:
                    # Find evidence turns
                    evidence = self._find_evidence(conversation, matches)

                    insight = LearningInsight(
                        insight_type=insight_type,
                        description=f"{insight_type.value.replace('_', ' ').title()} detected",
                        confidence=confidence,
                        evidence=evidence[:3],  # Limit to top 3
                        metadata={"matched_keywords": matches[:5]},
                    )
                    insights.append(insight)

        return insights

    def recognize_patterns(self, conversation: List[str]) -> List[RecognizedPattern]:
        """
        Recognize patterns in conversation.

        Args:
            conversation: List of conversation turns

        Returns:
            List[RecognizedPattern]: Recognized patterns
        """
        if not conversation:
            return []

        patterns = []

        # Check each pattern type
        for pattern_type, keywords in self.PATTERN_KEYWORDS.items():
            occurrences = 0
            examples = []

            for turn in conversation:
                turn_lower = turn.lower()
                for keyword in keywords:
                    if keyword in turn_lower:
                        occurrences += 1
                        if len(examples) < 3:
                            examples.append(turn[:100])  # First 100 chars
                        break  # Count each turn only once

            if occurrences > 0:
                # Calculate confidence based on occurrence frequency
                confidence = min(1.0, occurrences / len(conversation) + 0.5)

                if confidence >= self.config.min_confidence:
                    pattern = RecognizedPattern(
                        pattern_type=pattern_type,
                        description=f"{pattern_type.value.title()} workflow pattern",
                        occurrences=occurrences,
                        confidence=confidence,
                        examples=examples,
                    )
                    patterns.append(pattern)

        return patterns

    def _find_evidence(self, conversation: List[str], keywords: List[str]) -> List[str]:
        """
        Find evidence turns containing keywords.

        Args:
            conversation: List of conversation turns
            keywords: Keywords to search for

        Returns:
            List[str]: Evidence turns
        """
        evidence = []

        for turn in conversation:
            turn_lower = turn.lower()
            for keyword in keywords:
                if keyword in turn_lower:
                    evidence.append(turn)
                    break  # Add each turn only once

        return evidence
