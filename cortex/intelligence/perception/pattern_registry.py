"""
Pattern Registry - Phase 12 S3 (Brain Perception Layer)

AC-PHASE71-009: Pattern registration and detection in perception layer

Brain perception layer that:
- Registers learned patterns with detection signatures
- Detects patterns in new repositories via similarity matching
- Scores confidence for pattern matches
- Supports fuzzy matching and partial signature detection

Used by learning loop to enhance pattern recognition over time.

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
# noqa: CORE-035 — domain-scoped; class name is contextually appropriate here

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RegisteredPattern:
    """Pattern registered in perception layer."""

    id: str
    name: str
    signature: Dict[str, Any]      # Detection rules
    context: Dict[str, str]        # When applicable
    strategies: List[str]          # Recommended approaches
    risk_factors: List[str]        # Known challenges
    success_rate: float            # Historical effectiveness

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "signature": self.signature,
            "context": self.context,
            "strategies": self.strategies,
            "risk_factors": self.risk_factors,
            "success_rate": self.success_rate,
        }


@dataclass
class PatternMatch:
    """Result of pattern detection."""

    pattern_id: str
    confidence: float
    matched_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_id": self.pattern_id,
            "confidence": self.confidence,
            "matched_fields": self.matched_fields,
            "missing_fields": self.missing_fields,
        }


class PatternRegistry:
    """
    Brain perception layer pattern registry.

    Registers learned patterns and detects them in new repositories
    using signature-based matching with confidence scoring.

    AC-PHASE71-009: Pattern registration and detection
    """

    def __init__(self) -> None:
        """Initialize pattern registry."""
        self._patterns: Dict[str, RegisteredPattern] = {}
        self._pattern_count = 0

    def register_pattern(self, pattern: RegisteredPattern) -> None:
        """
        Register a pattern in the registry.

        Args:
            pattern: RegisteredPattern to register
        """
        # If ID already exists, replace (update)
        if pattern.id in self._patterns:
            logger.debug(f"Updating existing pattern: {pattern.id}")
        else:
            self._pattern_count += 1
            logger.debug(f"Registering new pattern: {pattern.id}")

        self._patterns[pattern.id] = pattern

    def get_pattern(self, pattern_id: str) -> Optional[RegisteredPattern]:
        """
        Get pattern by ID.

        Args:
            pattern_id: ID of pattern to retrieve

        Returns:
            RegisteredPattern if found, None otherwise
        """
        return self._patterns.get(pattern_id)

    def get_all_patterns(self) -> List[RegisteredPattern]:
        """
        Get all registered patterns.

        Returns:
            List of all RegisteredPattern objects
        """
        return list(self._patterns.values())

    def detect_patterns(
        self,
        repository_analysis: Dict[str, Any],
        fuzzy: bool = False
    ) -> List[PatternMatch]:
        """
        Detect patterns in repository analysis.

        Args:
            repository_analysis: Analysis data from repository
            fuzzy: Enable fuzzy string matching

        Returns:
            List of PatternMatch objects sorted by confidence
        """
        matches: List[PatternMatch] = []

        for pattern in self._patterns.values():
            match = self._match_pattern(
                pattern,
                repository_analysis,
                fuzzy=fuzzy
            )

            if match and match.confidence > 0.1:  # Threshold for inclusion
                matches.append(match)

        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)

        logger.debug(f"Detected {len(matches)} pattern matches")
        return matches

    def _match_pattern(
        self,
        pattern: RegisteredPattern,
        repo_data: Dict[str, Any],
        fuzzy: bool = False
    ) -> Optional[PatternMatch]:
        """
        Match a single pattern against repository data.

        Args:
            pattern: RegisteredPattern to match
            repo_data: Repository analysis data
            fuzzy: Enable fuzzy matching

        Returns:
            PatternMatch if pattern matches, None otherwise
        """
        matched_fields: List[str] = []
        missing_fields: List[str] = []
        total_fields = len(pattern.signature)

        if total_fields == 0:
            return None

        for field, expected_value in pattern.signature.items():
            if field not in repo_data:
                missing_fields.append(field)
                continue

            actual_value = repo_data[field]

            # Check if field matches
            if self._values_match(expected_value, actual_value, fuzzy=fuzzy):
                matched_fields.append(field)
            else:
                missing_fields.append(field)

        # Calculate confidence
        if not matched_fields:
            return None

        base_confidence = len(matched_fields) / total_fields

        # Adjust based on pattern's historical success rate
        confidence = (base_confidence * 0.7) + (pattern.success_rate * 0.3)

        return PatternMatch(
            pattern_id=pattern.id,
            confidence=min(confidence, 1.0),
            matched_fields=matched_fields,
            missing_fields=missing_fields
        )

    def _values_match(
        self,
        expected: Any,
        actual: Any,
        fuzzy: bool = False
    ) -> bool:
        """
        Check if expected and actual values match.

        Args:
            expected: Expected value from signature
            actual: Actual value from repository
            fuzzy: Enable fuzzy matching

        Returns:
            True if values match
        """
        # Exact match
        if expected == actual:
            return True

        # Fuzzy string matching
        if fuzzy and isinstance(expected, str) and isinstance(actual, str):
            if expected.lower() == actual.lower():
                return True

        # List containment
        if isinstance(expected, list) and isinstance(actual, list):
            # Check if most expected items are in actual
            if not expected:
                return True
            matches = sum(1 for item in expected if item in actual)
            return matches / len(expected) >= 0.7  # 70% threshold

        # Numeric range matching
        if isinstance(expected, dict) and "min" in expected and "max" in expected:
            if isinstance(actual, (int, float)):
                return expected["min"] <= actual <= expected["max"]

        # Type matching
        if isinstance(expected, type):
            return isinstance(actual, expected)

        return False


# Singleton accessor
_registry_instance: Optional[PatternRegistry] = None


def get_pattern_registry() -> PatternRegistry:
    """
    Get singleton PatternRegistry instance.

    Returns:
        Singleton PatternRegistry instance
    """
    global _registry_instance

    if _registry_instance is None:
        _registry_instance = PatternRegistry()

    return _registry_instance
