"""
Pattern Extractor - Phase 71 S1

AC-PHASE71-004: Pattern extraction from orchestrator operation results

Extracts reusable patterns from:
- Test execution results (TDDOrchestrator)
- Refactoring operations (RefactoringOrchestrator)
- User interactions (InteractionOrchestrator)
- Governance violations (EnforcementOrchestrator)
- And more...

Author: GitHub Copilot
Date: 2026-02-10
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Type of pattern extracted."""

    TECHNICAL = auto()
    BUSINESS = auto()
    GOVERNANCE = auto()
    INTERACTION = auto()
    PERFORMANCE = auto()


@dataclass
class ExtractedPattern:
    """Pattern extracted from operation."""

    pattern_type: PatternType
    description: str
    data: Dict[str, Any]
    confidence: float
    source_orchestrator: str
    source_operation: str


class PatternExtractor:
    """
    Extracts reusable patterns from orchestrator operation results.

    AC-PHASE71-004: Pattern extraction logic
    """

    def __init__(self):
        """Initialize pattern extractor."""
        # Orchestrator-specific extractors
        self._extractors = {
            "TDDOrchestrator": self._extract_tdd_patterns,
            "RefactoringOrchestrator": self._extract_refactoring_patterns,
            "InteractionOrchestrator": self._extract_interaction_patterns,
            "EnforcementOrchestrator": self._extract_governance_patterns,
            "MasterOrchestrator": self._extract_coordination_patterns,
        }

    def extract_patterns(
        self,
        orchestrator: str,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """
        Extract patterns from operation result.

        Args:
            orchestrator: Orchestrator name
            operation: Operation performed
            context: Operation context
            result: Operation result

        Returns:
            List of extracted patterns
        """
        # Get orchestrator-specific extractor
        extractor = self._extractors.get(orchestrator, self._extract_generic_patterns)

        try:
            patterns = extractor(operation, context, result)
            logger.debug(f"Extracted {len(patterns)} patterns from {orchestrator}.{operation}")
            return patterns
        except Exception as e:
            logger.warning(f"Pattern extraction failed: {e}")
            return []

    def _extract_tdd_patterns(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """Extract patterns from TDDOrchestrator operations."""
        patterns: List[ExtractedPattern] = []

        # Extract test patterns
        if "test_patterns" in result or "guidance_patterns" in result:
            test_patterns = result.get("test_patterns") or result.get("guidance_patterns", [])
            if test_patterns:
                patterns.append(ExtractedPattern(
                    pattern_type=PatternType.TECHNICAL,
                    description=f"Test patterns from {operation} phase",
                    data={"patterns": test_patterns, "phase": operation},
                    confidence=0.6,  # Initial confidence
                    source_orchestrator="TDDOrchestrator",
                    source_operation=operation
                ))

        # Extract refactoring operations
        if operation == "refactor" and "refactoring_result" in result:
            refactoring_data = result["refactoring_result"]
            if isinstance(refactoring_data, dict):
                patterns.append(ExtractedPattern(
                    pattern_type=PatternType.TECHNICAL,
                    description="Refactoring operation successful",
                    data={"operation": "refactor", "result": refactoring_data},
                    confidence=0.7,
                    source_orchestrator="TDDOrchestrator",
                    source_operation=operation
                ))

        return patterns

    def _extract_refactoring_patterns(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """Extract patterns from RefactoringOrchestrator operations."""
        patterns: List[ExtractedPattern] = []

        # Extract code smell patterns
        if "code_smells" in result:
            smells = result["code_smells"]
            if smells:
                patterns.append(ExtractedPattern(
                    pattern_type=PatternType.TECHNICAL,
                    description=f"Code smells detected: {len(smells)}",
                    data={"smells": smells, "file": context.get("file_path")},
                    confidence=0.8,
                    source_orchestrator="RefactoringOrchestrator",
                    source_operation=operation
                ))

        # Extract successful refactoring operations
        if result.get("success"):
            patterns.append(ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description=f"Successful {operation} refactoring",
                data={"operation": operation, "transformations": result.get("transformations", [])},
                confidence=0.9,
                source_orchestrator="RefactoringOrchestrator",
                source_operation=operation
            ))

        return patterns

    def _extract_interaction_patterns(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """Extract patterns from InteractionOrchestrator operations."""
        patterns: List[ExtractedPattern] = []

        # Extract user choice patterns (if challenge was presented)
        if "challenge" in result and "user_choice" in context:
            patterns.append(ExtractedPattern(
                pattern_type=PatternType.INTERACTION,
                description="User choice on challenge",
                data={
                    "challenge": result["challenge"],
                    "choice": context["user_choice"],
                    "alternatives": result.get("alternatives", [])
                },
                confidence=1.0,  # User choices are high confidence
                source_orchestrator="InteractionOrchestrator",
                source_operation=operation
            ))

        # Extract user corrections
        if context.get("correction_detected"):
            patterns.append(ExtractedPattern(
                pattern_type=PatternType.INTERACTION,
                description="User correction captured",
                data={"correction": context["correction_data"]},
                confidence=1.0,
                source_orchestrator="InteractionOrchestrator",
                source_operation=operation
            ))

        return patterns

    def _extract_governance_patterns(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """Extract patterns from EnforcementOrchestrator operations."""
        patterns: List[ExtractedPattern] = []

        # Extract violation patterns
        if "violations" in result:
            violations = result["violations"]
            if violations:
                patterns.append(ExtractedPattern(
                    pattern_type=PatternType.GOVERNANCE,
                    description=f"Governance violations: {len(violations)}",
                    data={"violations": violations, "rules": result.get("rules_checked", [])},
                    confidence=0.8,
                    source_orchestrator="EnforcementOrchestrator",
                    source_operation=operation
                ))

        return patterns

    def _extract_coordination_patterns(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """Extract patterns from MasterOrchestrator operations."""
        patterns: List[ExtractedPattern] = []

        # Extract orchestrator routing patterns
        if "orchestrator_selected" in result:
            patterns.append(ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description=f"Orchestrator routing: {result['orchestrator_selected']}",
                data={"intent": context.get("intent"), "orchestrator": result["orchestrator_selected"]},
                confidence=0.7,
                source_orchestrator="MasterOrchestrator",
                source_operation=operation
            ))

        return patterns

    def _extract_generic_patterns(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[ExtractedPattern]:
        """Generic pattern extraction for unrecognized orchestrators."""
        # Basic pattern: operation success/failure
        if "success" in result or "status" in result:
            return [ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description=f"Operation {operation} completed",
                data={"operation": operation, "result": result},
                confidence=0.5,
                source_orchestrator="Unknown",
                source_operation=operation
            )]
        return []
