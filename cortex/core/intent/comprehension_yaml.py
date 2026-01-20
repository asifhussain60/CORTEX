"""Comprehension YAML - YAML schema for comprehension results.

Manages YAML schema and serialization for comprehension data.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum


class ComprehensionLevel(Enum):
    """Comprehension levels."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class ComprehensionResult:
    """Comprehension assessment result.

    Attributes:
        level: Comprehension level achieved.
        confidence: Confidence in assessment (0-1).
        topics_covered: Topics that were understood.
        gaps: Knowledge gaps identified.
        recommendations: Recommendations for improvement.
    """

    level: ComprehensionLevel
    confidence: float = 1.0
    topics_covered: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ComprehensionYAML:
    """Manages YAML comprehension schema."""

    def __init__(self) -> None:
        """Initialize comprehension YAML manager."""
        self.schema_version = "1.0"
        self.results: List[ComprehensionResult] = []

    def create_result(
        self,
        level: ComprehensionLevel,
        confidence: float = 1.0,
        topics_covered: Optional[List[str]] = None,
        gaps: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> ComprehensionResult:
        """Create a comprehension result.

        Args:
            level: Comprehension level.
            confidence: Confidence score.
            topics_covered: Topics covered.
            gaps: Knowledge gaps.
            recommendations: Improvement recommendations.

        Returns:
            ComprehensionResult.
        """
        result = ComprehensionResult(
            level=level,
            confidence=confidence,
            topics_covered=topics_covered or [],
            gaps=gaps or [],
            recommendations=recommendations or [],
        )
        self.results.append(result)
        return result

    def to_dict(self, result: ComprehensionResult) -> Dict[str, Any]:
        """Convert result to dictionary.

        Args:
            result: ComprehensionResult.

        Returns:
            Dictionary representation.
        """
        return {
            "schema_version": self.schema_version,
            "level": result.level.value,
            "confidence": result.confidence,
            "topics_covered": result.topics_covered,
            "gaps": result.gaps,
            "recommendations": result.recommendations,
        }

    def get_average_confidence(self) -> float:
        """Get average confidence across all results.

        Returns:
            Average confidence (0-1).
        """
        if not self.results:
            return 0.0
        return sum(r.confidence for r in self.results) / len(self.results)

    def get_results_by_level(self, level: ComprehensionLevel) -> List[ComprehensionResult]:
        """Get results by comprehension level.

        Args:
            level: Comprehension level.

        Returns:
            List of ComprehensionResult.
        """
        return [r for r in self.results if r.level == level]


# Alias for backward compatibility
ComprehensionSchema = ComprehensionYAML

__all__ = [
    "ComprehensionYAML",
    "ComprehensionSchema",
    "ComprehensionResult",
    "ComprehensionLevel",
]
