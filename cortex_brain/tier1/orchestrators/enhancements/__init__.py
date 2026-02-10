"""
Enhancement module initialization and registry.

AC-ID: AC-VAC-ENH-INIT | Phase: Enhancement Integration
Purpose: Export all vacuum orchestrator enhancements
"""

from .file_categorizer import (
    FileCategory,
    ClassificationSignals,
    FileClassifier,
)
from .conflict_detector import (
    ConflictType,
    Conflict,
    ConflictReport,
    ConflictDetector,
)

__all__ = [
    # File Categorizer
    "FileCategory",
    "ClassificationSignals",
    "FileClassifier",
    # Conflict Detector
    "ConflictType",
    "Conflict",
    "ConflictReport",
    "ConflictDetector",
]
