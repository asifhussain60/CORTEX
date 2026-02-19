"""
OrchestratorLearningMixin - Enable learning for existing orchestrators (Phase 71 S5).

AC-ID: PHASE-71-S5
Purpose: Integrate learning into TDD, Refactoring, Interaction orchestrators

Pattern:
    class YourOrchestrator(OrchestratorLearningMixin, YourBaseMixin):
        pass

    # In _execute_domain_logic():
    # 1. Collect test scores if applicable
    # 2. Call self._capture_learning(...) at end

Learning Integration Points:
- Test value scoring for TDD: High-value tests prioritized
- Refactoring pattern extraction: Patterns learned from refactorings
- Interaction flows: Common user patterns captured

Author: Asif Hussain
Date: 2026-02-10
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.learning.universal_learning_loop import get_learning_loop
from cortex.testing.test_value_scorer import TestMetrics, get_test_value_scorer

logger = logging.getLogger(__name__)


class OrchestratorLearningMixin:
    """
    Mixin for orchestrators to enable learning capture.

    Provides:
    - Non-blocking learning integration
    - Test quality scoring for TDD
    - Pattern extraction helpers
    - Learning metrics tracking

    Usage:
        class MyOrchestrator(OrchestratorLearningMixin, BaseOrchestrator):
            def _execute_domain_logic(self, ...):
                # Your logic

                # Capture learning at end
                self._capture_learning(
                    operation_type="custom_type",
                    patterns=extracted_patterns,
                    test_scores=test_scores  # optional
                )
    """

    def _capture_learning(
        self,
        operation_type: str,
        patterns: Optional[Dict[str, Any]] = None,
        test_scores: Optional[List[Dict[str, Any]]] = None,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Capture learning from orchestrator execution.

        Args:
            operation_type: Type of operation (tdd, refactoring, interaction, etc.)
            patterns: Dictionary of extracted patterns
            test_scores: List of test score metrics
            execution_context: Additional context (user_request, files affected, etc.)
        """
        try:
            learning_loop = get_learning_loop()

            if not learning_loop:
                logger.debug("Learning loop unavailable, skipping capture")
                return

            # Build learning operation
            operation = {
                "type": operation_type,
                "patterns": patterns or {},
                "test_scores": test_scores or [],
                "context": execution_context or {},
            }

            # Capture patterns (non-blocking)
            learning_loop.capture_from_operation(
                orchestrator=self.__class__.__name__,
                operation=operation_type,
                context={},
                result=operation,
            )

            logger.debug(
                f"Learning captured for {operation_type} "
                f"({len(patterns or {})} patterns, {len(test_scores or [])} scores)"
            )

        except Exception as e:
            logger.warning(
                f"Learning capture failed (non-blocking): {e}",
                exc_info=False,
            )

    def _score_test_quality(
        self,
        test_name: str,
        coverage_percent: float,
        edge_cases_covered: int,
        total_edge_cases: int,
        mutations_caught: int,
        total_mutations: int,
        flakiness_percent: float = 0.0,
        false_positives: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Score test quality and track high-value tests.

        Returns test score dict for learning or None if scoring disabled.

        Args:
            test_name: Name of test being scored
            coverage_percent: Code coverage (0-100)
            edge_cases_covered: Number of edge cases covered
            total_edge_cases: Total edge cases in scope
            mutations_caught: Mutations killed by test
            total_mutations: Total mutations in scope
            flakiness_percent: Test flakiness (0-100)
            false_positives: Number of false positive alerts

        Returns:
            Dict with score info, or None
        """
        try:
            scorer = get_test_value_scorer()

            if not scorer:
                logger.debug("Test value scorer unavailable, skipping scoring")
                return None

            metrics = TestMetrics(
                coverage_percent=coverage_percent,
                edge_cases_covered=edge_cases_covered,
                total_edge_cases=total_edge_cases,
                mutations_caught=mutations_caught,
                total_mutations=total_mutations,
                flakiness_percent=flakiness_percent,
                false_positives=false_positives,
            )

            score = scorer.score_test(test_name, metrics)

            logger.debug(f"Test {test_name} scored as {score.tier.value}")

            return score.to_dict()

        except Exception as e:
            logger.warning(
                f"Test quality scoring failed (non-blocking): {e}",
                exc_info=False,
            )
            return None

    def _extract_refactoring_patterns(
        self,
        operation: str,
        files_affected: List[str],
        changes_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract patterns from refactoring operation.

        Args:
            operation: Refactoring operation (rename, extract_method, etc.)
            files_affected: Files changed by refactoring
            changes_summary: Dict of change metrics

        Returns:
            Dict of extracted patterns for learning
        """
        patterns = {
            "operation": operation,
            "file_count": len(files_affected),
            "files": files_affected,
            "complexity_reduction": changes_summary.get("complexity_reduction", 0),
            "lines_changed": changes_summary.get("lines_changed", 0),
            "maintainability_improvement": changes_summary.get("maintainability_improvement", 0),
        }

        return patterns

    def _extract_interaction_patterns(
        self,
        user_intent: str,
        interaction_type: str,
        outcome: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extract patterns from user interaction.

        Args:
            user_intent: What user was trying to do
            interaction_type: Type of interaction (clarification, suggestion, etc.)
            outcome: How the interaction resolved
            metadata: Additional context

        Returns:
            Dict of extracted patterns for learning
        """
        patterns = {
            "user_intent": user_intent,
            "interaction_type": interaction_type,
            "outcome": outcome,
            "metadata": metadata or {},
        }

        return patterns

    def _get_learning_orchestrator_type(self) -> str:
        """
        Get learning orchestrator type for this mixin user.

        Override in subclasses for custom classification.

        Returns:
            Orchestrator type (tdd, refactoring, interaction, coordination, governance)
        """
        class_name = self.__class__.__name__.lower()

        # Determine type based on class name
        if "tdd" in class_name:
            return "tdd"
        elif "refactor" in class_name:
            return "refactoring"
        elif "interaction" in class_name:
            return "interaction"
        elif "governance" in class_name or "enforcement" in class_name:
            return "governance"
        elif "coordination" in class_name or "master" in class_name or "coordinator" in class_name:
            return "coordination"
        else:
            return "generic"


__all__ = [
    "OrchestratorLearningMixin",
]
