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
from .reference_updater import (
    ReferenceType,
    Reference,
    UpdateResult,
    ReferenceScanner,
    ReferenceUpdater,
)
from .rule_based_planner import (
    CleanupAction,
    CleanupRule,
    CleanupItem,
    CleanupPlan,
    RuleBasedPlanner,
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
    # Reference Updater
    "ReferenceType",
    "Reference",
    "UpdateResult",
    "ReferenceScanner",
    "ReferenceUpdater",
    # Rule-Based Planner
    "CleanupAction",
    "CleanupRule",
    "CleanupItem",
    "CleanupPlan",
    "RuleBasedPlanner",
]
