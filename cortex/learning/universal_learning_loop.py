"""
Universal Learning Loop - Phase 71 S1

AC-PHASE71-001: Unified learning infrastructure for all orchestrators
AC-PHASE71-002: Pattern extraction from operation results
AC-PHASE71-003: Incremental knowledge repository updates

Purpose: Every orchestrator operation feeds into learning loop to capture
patterns, refine knowledge, and improve future recommendations.

Author: GitHub Copilot
Date: 2026-02-10
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Type of learned pattern."""

    TECHNICAL = auto()      # Code patterns, test patterns, refactoring
    BUSINESS = auto()       # Domain knowledge, business rules
    GOVERNANCE = auto()     # Rule violations, compliance patterns
    INTERACTION = auto()    # User preferences, conversation patterns
    PERFORMANCE = auto()    # Optimization patterns, efficiency gains


@dataclass
class LearningCapture:
    """Captured learning from orchestrator operation."""

    orchestrator: str                 # Which orchestrator generated this
    operation: str                    # What operation was performed
    pattern_type: PatternType        # Type of pattern
    pattern_description: str         # Human-readable description
    pattern_data: Dict[str, Any]     # Structured pattern data
    confidence: float                # Initial confidence (0.0-1.0)
    frequency: int = 1               # Number of occurrences
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "orchestrator": self.orchestrator,
            "operation": self.operation,
            "pattern_type": self.pattern_type.name,
            "pattern_description": self.pattern_description,
            "pattern_data": self.pattern_data,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


class UniversalLearningLoop:
    """
    Universal learning loop for all CORTEX orchestrators.

    Provides unified interface for:
    1. Capturing patterns from operation results
    2. Scoring confidence based on frequency
    3. Merging patterns to knowledge repositories
    4. Tracking learning metrics

    AC-PHASE71-001: Unified learning infrastructure
    """

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        enable_logging: bool = True
    ):
        """
        Initialize universal learning loop.

        Args:
            workspace_root: Root of CORTEX workspace
            enable_logging: Enable detailed logging
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.enable_logging = enable_logging

        # Learning cache (in-memory before persistence)
        self._learning_cache: Dict[str, List[LearningCapture]] = {}

        # Initialize sub-components
        from cortex.learning.confidence_scorer import ConfidenceScorer
        from cortex.learning.knowledge_merger import KnowledgeMerger
        from cortex.learning.pattern_extractor import PatternExtractor

        self._pattern_extractor = PatternExtractor()
        self._knowledge_merger = KnowledgeMerger(self.workspace_root)
        self._confidence_scorer = ConfidenceScorer()

        # Metrics
        self._total_learnings = 0
        self._learnings_by_orchestrator: Dict[str, int] = {}

        if self.enable_logging:
            logger.info("UniversalLearningLoop initialized")

    def capture_from_operation(
        self,
        orchestrator: str,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[LearningCapture]:
        """
        Capture learnings from orchestrator operation.

        AC-PHASE71-002: Pattern extraction from operation results

        Args:
            orchestrator: Name of orchestrator (e.g., "TDDOrchestrator")
            operation: Operation performed (e.g., "refactor", "challenge")
            context: Operation context (input parameters, state)
            result: Operation result (output, metrics)

        Returns:
            List of learning captures extracted from operation
        """
        try:
            # Extract patterns using PatternExtractor
            patterns = self._pattern_extractor.extract_patterns(
                orchestrator=orchestrator,
                operation=operation,
                context=context,
                result=result
            )

            # Convert to LearningCapture objects
            learnings: List[LearningCapture] = []
            for pattern in patterns:
                learning = LearningCapture(
                    orchestrator=orchestrator,
                    operation=operation,
                    pattern_type=pattern.pattern_type,
                    pattern_description=pattern.description,
                    pattern_data=pattern.data,
                    confidence=pattern.confidence,
                    context=context
                )
                learnings.append(learning)

            # Cache learnings
            cache_key = f"{orchestrator}:{operation}"
            if cache_key not in self._learning_cache:
                self._learning_cache[cache_key] = []
            self._learning_cache[cache_key].extend(learnings)

            # Update metrics
            self._total_learnings += len(learnings)
            self._learnings_by_orchestrator[orchestrator] = (
                self._learnings_by_orchestrator.get(orchestrator, 0) + len(learnings)
            )

            if self.enable_logging and learnings:
                logger.info(
                    f"Captured {len(learnings)} learnings from {orchestrator}.{operation}"
                )

            return learnings

        except Exception as e:
            logger.error(f"Failed to capture learnings: {e}", exc_info=True)
            return []

    def merge_to_knowledge(
        self,
        learnings: List[LearningCapture],
        threshold: float = 0.7
    ) -> Result[Dict[str, Any]]:
        """
        Merge learnings to knowledge repositories.

        AC-PHASE71-003: Incremental knowledge repository updates

        Args:
            learnings: List of learning captures to merge
            threshold: Confidence threshold for promotion (default 0.7)

        Returns:
            Result with merge summary
        """
        try:
            # Score confidence (frequency-based)
            scored_learnings = self._confidence_scorer.score_learnings(learnings)

            # Filter by threshold
            promotable = [
                learning for learning in scored_learnings
                if learning.confidence >= threshold
            ]

            if not promotable:
                return Ok({
                    "status": "no_promotions",
                    "total_learnings": len(learnings),
                    "threshold": threshold,
                    "message": "No learnings met confidence threshold"
                })

            # Merge to knowledge repositories
            merge_result = self._knowledge_merger.merge_learnings(promotable)

            if merge_result.is_err():
                return merge_result

            merge_data = merge_result.unwrap()

            return Ok({
                "status": "merged",
                "total_learnings": len(learnings),
                "promoted": len(promotable),
                "threshold": threshold,
                "files_updated": merge_data.get("files_updated", []),
                "message": f"Promoted {len(promotable)} learnings to knowledge repositories"
            })

        except Exception as e:
            logger.error(f"Failed to merge learnings: {e}", exc_info=True)
            return Err(f"Merge failed: {str(e)}")

    def get_learning_metrics(self) -> Dict[str, Any]:
        """
        Get learning metrics summary.

        Returns:
            Dictionary with learning statistics
        """
        return {
            "total_learnings": self._total_learnings,
            "by_orchestrator": self._learnings_by_orchestrator.copy(),
            "cached_learnings": sum(len(v) for v in self._learning_cache.values()),
            "cache_keys": list(self._learning_cache.keys()),
        }

    def clear_cache(self) -> None:
        """Clear learning cache."""
        self._learning_cache.clear()
        logger.info("Learning cache cleared")


# Singleton accessor
_learning_loop_instance: Optional[UniversalLearningLoop] = None


def get_learning_loop(
    workspace_root: Optional[Path] = None
) -> UniversalLearningLoop:
    """
    Get singleton UniversalLearningLoop instance.

    Args:
        workspace_root: Root of CORTEX workspace

    Returns:
        Singleton UniversalLearningLoop instance
    """
    global _learning_loop_instance

    if _learning_loop_instance is None:
        _learning_loop_instance = UniversalLearningLoop(workspace_root)

    return _learning_loop_instance
