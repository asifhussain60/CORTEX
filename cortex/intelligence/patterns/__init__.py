"""
Pattern detection engine for architectural analysis.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Stage: S1-S5 - Architectural Pattern Detection & Classification
         Phase 60 - Enterprise Custom Pattern Registry & Policy Engine
"""

from .base import (
    BasePatternDetector,
    PatternInfo,
    PatternMatch,
    SignatureMatcher,
    PatternCategory,
)
from .catalog import PatternCatalog
from .classification import ArchitectureClassifier, ArchitectureClassification, ArchitectureType
from .registry import (
    CustomPatternRegistry,
    PatternMetadata,
    DetectionRule,
    DetectionRuleType,
)

__all__ = [
    "BasePatternDetector",
    "PatternInfo",
    "PatternMatch",
    "SignatureMatcher",
    "PatternCategory",
    "PatternCatalog",
    "ArchitectureClassifier",
    "ArchitectureClassification",
    "ArchitectureType",
    "CustomPatternRegistry",
    "PatternMetadata",
    "DetectionRule",
    "DetectionRuleType",
]
