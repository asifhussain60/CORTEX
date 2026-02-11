"""
Creational pattern detectors.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Stage: S2 - Design Pattern Detectors
AC Marker: AC-PHASE57-S2-002
"""

from typing import Any, Dict, List, Optional

from cortex.intelligence.patterns.base import (
    BasePatternDetector,
    PatternCategory,
    PatternInfo,
    PatternMatch,
)


class SingletonDetector(BasePatternDetector):
    """Detector for Singleton design pattern."""

    @property
    def pattern_info(self) -> PatternInfo:
        """Return Singleton pattern metadata."""
        return PatternInfo(
            name="Singleton",
            category=PatternCategory.CREATIONAL,
            signatures=["getInstance()", "getinstance()"],
            description="Ensure a class has only one instance",
            confidence=0.85,
        )

    def detect(
        self, ast_node: Any, context: Optional[Dict[str, Any]] = None
    ) -> List[PatternMatch]:
        """
        Detect Singleton pattern in AST.

        Args:
            ast_node: AST node to analyze
            context: Optional execution context

        Returns:
            List of PatternMatch instances
        """
        # Minimal implementation for TDD GREEN phase
        return []


class FactoryDetector(BasePatternDetector):
    """Detector for Factory design pattern."""

    @property
    def pattern_info(self) -> PatternInfo:
        """Return Factory pattern metadata."""
        return PatternInfo(
            name="Factory",
            category=PatternCategory.CREATIONAL,
            signatures=["create()", "make()", "new()"],
            description="Define an interface for creating objects",
            confidence=0.80,
        )

    def detect(
        self, ast_node: Any, context: Optional[Dict[str, Any]] = None
    ) -> List[PatternMatch]:
        """Detect Factory pattern in AST."""
        return []


class BuilderDetector(BasePatternDetector):
    """Detector for Builder design pattern."""

    @property
    def pattern_info(self) -> PatternInfo:
        """Return Builder pattern metadata."""
        return PatternInfo(
            name="Builder",
            category=PatternCategory.CREATIONAL,
            signatures=["build()", "with", "fluent"],
            description="Separate construction from representation",
            confidence=0.78,
        )

    def detect(
        self, ast_node: Any, context: Optional[Dict[str, Any]] = None
    ) -> List[PatternMatch]:
        """Detect Builder pattern in AST."""
        return []
