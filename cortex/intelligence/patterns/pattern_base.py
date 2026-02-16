"""
Base classes and interfaces for pattern detection.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Stage: S1 - Pattern Recognition Foundation
AC Marker: AC-PHASE57-S1-002
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class PatternCategory(str, Enum):
    """Pattern categories from Gang of Four."""

    CREATIONAL = "Creational"
    STRUCTURAL = "Structural"
    BEHAVIORAL = "Behavioral"
    CONCURRENCY = "Concurrency"
    ENTERPRISE = "Enterprise"
    ARCHITECTURAL = "Architectural"


@dataclass
class PatternInfo:
    """
    Metadata about a design pattern.

    Attributes:
        name: Pattern name (e.g., "Singleton", "Factory")
        category: PatternCategory enum
        signatures: List of method/class signatures that indicate this pattern
        description: Human-readable pattern description
        confidence: Default confidence score (0.0-1.0) for this pattern
        aliases: Alternative names for the pattern
    """

    name: str
    category: Union[PatternCategory, str]
    signatures: List[str]
    description: str
    confidence: float = 0.75
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate confidence bounds."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.signatures:
            raise ValueError("signatures list cannot be empty")


@dataclass
class PatternMatch:
    """
    Result of pattern detection in code.

    Attributes:
        pattern_name: Name of detected pattern
        confidence: Confidence score (0.0-1.0)
        location: File path and line number
        evidence: Dict of evidence supporting this match
    """

    pattern_name: str
    confidence: float
    location: str
    evidence: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate confidence bounds."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


class SignatureMatcher:
    """
    Algorithm for matching method signatures against patterns.

    Implements fuzzy matching to find patterns even when not all signatures
    are present (partial matches).
    """

    def match(
        self,
        pattern_signatures: List[str],
        code_methods: Dict[str, Dict[str, Any]],
    ) -> float:
        """
        Calculate confidence score for pattern match.

        Args:
            pattern_signatures: Expected method signatures for pattern
            code_methods: Dict of methods found in code
                         Keys: method names, Values: method metadata

        Returns:
            Confidence score (0.0-1.0)

        Example:
            >>> matcher = SignatureMatcher()
            >>> confidence = matcher.match(
            ...     pattern_signatures=["getInstance()"],
            ...     code_methods={"getInstance": {"static": True}}
            ... )
            >>> confidence > 0.85
            True
        """
        if not pattern_signatures or not code_methods:
            return 0.0

        matched_count = 0

        for sig in pattern_signatures:
            # Extract method name from signature (before parentheses)
            method_name = sig.split("(")[0].strip()

            if method_name in code_methods:
                matched_count += 1

        # Calculate confidence: (matched / total) with bonus for exact match
        confidence = matched_count / len(pattern_signatures)

        # If all signatures matched, high confidence
        if matched_count == len(pattern_signatures):
            return min(1.0, confidence + 0.1)

        # If no signatures matched, low confidence
        if matched_count == 0:
            return 0.0

        # Partial match: scale between 0.5 and 0.85
        return 0.5 + (confidence * 0.35)


class BasePatternDetector(ABC):
    """
    Abstract base class for all pattern detectors.

    Subclasses implement specific pattern detection algorithms.

    Example:
        ```python
        class SingletonDetector(BasePatternDetector):
            @property
            def pattern_info(self) -> PatternInfo:
                return PatternInfo(
                    name="Singleton",
                    category=PatternCategory.CREATIONAL,
                    signatures=["getInstance()"],
                    description="Restrict instantiation to single object"
                )

            def detect(self, ast_node, context) -> List[PatternMatch]:
                # Implementation
                ...
        ```
    """

    @property
    @abstractmethod
    def pattern_info(self) -> PatternInfo:
        """
        Return metadata about this pattern.

        Returns:
            PatternInfo object with pattern details
        """
        pass

    @abstractmethod
    def detect(self, ast_node: Any, context: Optional[Dict[str, Any]] = None) -> List[PatternMatch]:
        """
        Detect this pattern in an AST node.

        Args:
            ast_node: AST node to analyze
            context: Optional execution context

        Returns:
            List of PatternMatch objects found
        """
        pass

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<{self.__class__.__name__} for {self.pattern_info.name}>"
