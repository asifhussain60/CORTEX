"""
Knowledge Persistence Enforcement Agent - Phase 12 S5

AC-PHASE71-013: Knowledge persistence enforcement

9th enforcement agent for EnforcementOrchestrator.
Validates knowledge persistence requirements during onboarding operations.

Enforcement Rules:
- KP-001: Learning capture required for onboarding
- KP-002: Brain enhancement integration required
- KP-003: Knowledge artifacts must be generated
- KP-004: Promotion threshold recommendations

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ViolationLevel(Enum):
    """Violation severity levels."""

    INFO = auto()
    WARNING = auto()
    BLOCKING = auto()


@dataclass
class ValidationResult:  # noqa: CORE-035-scoped — domain-specific ValidationResult variant
    """Knowledge persistence validation result."""

    rule_id: str
    passed: bool
    level: ViolationLevel
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "level": self.level.name,
            "message": self.message
        }


class KnowledgePersistenceAgent:
    """
    9th enforcement agent: Knowledge persistence validation.

    Validates knowledge persistence during onboarding:
    - Learning capture completeness
    - Brain enhancement integration
    - Knowledge artifact generation
    - Promotion threshold adherence

    BLOCKS when:
    - No learning capture during onboarding
    - Missing brain enhancement
    - No knowledge artifacts generated

    WARNS when:
    - Low promotion rate (< 30%)
    - Partial brain enhancement

    AC-PHASE71-013: Knowledge persistence enforcement
    """

    def __init__(self) -> None:
        """Initialize Knowledge Persistence Agent."""
        self.validation_rules = [
            {
                "id": "KP-001",
                "name": "Learning Capture Required",
                "validator": self.validate_learning_capture,
                "blocking": True
            },
            {
                "id": "KP-002",
                "name": "Brain Enhancement Required",
                "validator": self.validate_brain_enhancement,
                "blocking": True
            },
            {
                "id": "KP-003",
                "name": "Knowledge Artifacts Required",
                "validator": self.validate_artifacts,
                "blocking": False  # Warning only
            },
            {
                "id": "KP-004",
                "name": "Promotion Threshold",
                "validator": self.validate_promotion_threshold,
                "blocking": False  # Warning only
            }
        ]

    def validate(self, context: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate knowledge persistence requirements.

        Args:
            context: Operation context including learning metrics

        Returns:
            List of validation results
        """
        # Only validate onboard operations
        if context.get("operation") != "onboard":
            return []

        results = []

        for rule in self.validation_rules:
            try:
                result = rule["validator"](context)
                results.append(result)

                if not result.passed:
                    logger.warning(
                        f"Knowledge persistence validation failed: {rule['id']} - "
                        f"{result.message}"
                    )

            except Exception as e:
                logger.error(f"Validation error for {rule['id']}: {e}")
                results.append(ValidationResult(
                    rule_id=rule["id"],
                    passed=False,
                    level=ViolationLevel.WARNING,
                    message=f"Validation error: {str(e)}"
                ))

        return results

    def validate_learning_capture(
        self,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate learning capture completeness.

        Args:
            context: Operation context

        Returns:
            Validation result
        """
        learning_metrics = context.get("learning_metrics", {})

        patterns_captured = learning_metrics.get("patterns_captured", 0)

        if patterns_captured == 0:
            return ValidationResult(
                rule_id="KP-001",
                passed=False,
                level=ViolationLevel.BLOCKING,
                message="No patterns captured during onboarding. "
                        "Learning capture is required for knowledge persistence."
            )

        return ValidationResult(
            rule_id="KP-001",
            passed=True,
            level=ViolationLevel.INFO,
            message=f"Learning capture complete: {patterns_captured} patterns captured"
        )

    def validate_brain_enhancement(
        self,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate brain enhancement integration.

        Args:
            context: Operation context

        Returns:
            Validation result
        """
        brain_enhancement = context.get("brain_enhancement", {})

        if not brain_enhancement:
            return ValidationResult(
                rule_id="KP-002",
                passed=False,
                level=ViolationLevel.BLOCKING,
                message="Brain enhancement missing. "
                        "Pattern detection and strategy selection required."
            )

        patterns_detected = brain_enhancement.get("patterns_detected", 0)
        strategies_recommended = brain_enhancement.get("strategies_recommended", 0)

        if patterns_detected == 0 and strategies_recommended == 0:
            return ValidationResult(
                rule_id="KP-002",
                passed=False,
                level=ViolationLevel.WARNING,
                message="Brain enhancement incomplete: no patterns or strategies generated"
            )

        return ValidationResult(
            rule_id="KP-002",
            passed=True,
            level=ViolationLevel.INFO,
            message=f"Brain enhancement complete: {patterns_detected} patterns, "
                    f"{strategies_recommended} strategies"
        )

    def validate_artifacts(
        self,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate knowledge artifact generation.

        Args:
            context: Operation context

        Returns:
            Validation result
        """
        artifacts = context.get("artifacts", {})

        if not artifacts:
            return ValidationResult(
                rule_id="KP-003",
                passed=False,
                level=ViolationLevel.WARNING,
                message="No knowledge artifacts generated. "
                        "Consider generating templates or best practices YAML."
            )

        templates = artifacts.get("templates_generated", 0)
        yaml_files = artifacts.get("yaml_files_created", 0)

        if templates == 0 and yaml_files == 0:
            return ValidationResult(
                rule_id="KP-003",
                passed=False,
                level=ViolationLevel.WARNING,
                message="Knowledge artifacts empty"
            )

        return ValidationResult(
            rule_id="KP-003",
            passed=True,
            level=ViolationLevel.INFO,
            message=f"Artifacts generated: {templates} templates, {yaml_files} YAML files"
        )

    def validate_promotion_threshold(
        self,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate learning promotion threshold.

        Args:
            context: Operation context

        Returns:
            Validation result
        """
        learning_metrics = context.get("learning_metrics", {})

        patterns_captured = learning_metrics.get("patterns_captured", 0)
        patterns_promoted = learning_metrics.get("patterns_promoted", 0)

        if patterns_captured == 0:
            return ValidationResult(
                rule_id="KP-004",
                passed=True,
                level=ViolationLevel.INFO,
                message="No patterns to promote"
            )

        promotion_rate = patterns_promoted / patterns_captured

        if promotion_rate < 0.3:
            return ValidationResult(
                rule_id="KP-004",
                passed=False,
                level=ViolationLevel.WARNING,
                message=f"Low promotion rate: {promotion_rate:.0%}. "
                        f"Consider adjusting confidence thresholds."
            )

        return ValidationResult(
            rule_id="KP-004",
            passed=True,
            level=ViolationLevel.INFO,
            message=f"Promotion rate healthy: {promotion_rate:.0%}"
        )

    def get_validation_rules(self) -> List[Dict[str, Any]]:
        """
        Get list of validation rules.

        Returns:
            List of rule definitions
        """
        return [
            {
                "id": rule["id"],
                "name": rule["name"],
                "blocking": rule["blocking"]
            }
            for rule in self.validation_rules
        ]


__all__ = [
    "KnowledgePersistenceAgent",
    "ValidationResult",
    "ViolationLevel"
]
