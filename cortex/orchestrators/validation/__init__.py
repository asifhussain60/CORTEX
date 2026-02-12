"""
Validation Orchestrators Package

Phase 48: Holistic Validation Gate
Provides pre-implementation validation with challenge generation and confidence scoring.

Components:
- HolisticValidationOrchestrator: Main validation coordinator
- PreImplementationChecklist: 12-category systematic review
- ChallengeEngine: Generate 3 alternative approaches
- ConfidenceScorer: Multi-factor confidence scoring (0-1.0)

Author: Asif Hussain
Priority: P0-CRITICAL (HIGHEST ROI)
"""

from cortex.orchestrators.validation.holistic_validation_orchestrator import (
    HolisticValidationOrchestrator,
    ValidationResult,
)
from cortex.orchestrators.validation.pre_implementation_checklist import (
    PreImplementationChecklist,
    ChecklistResult,
    CheckResult,
)

__all__ = [
    "HolisticValidationOrchestrator",
    "ValidationResult",
    "PreImplementationChecklist",
    "ChecklistResult",
    "CheckResult",
]

__version__ = "1.0.0"
__author__ = "Asif Hussain"

# AC_START: AC-PHASE48-S1-IMPL-001
