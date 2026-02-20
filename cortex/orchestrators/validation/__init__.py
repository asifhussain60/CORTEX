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
from cortex.orchestrators.validation.challenge_engine import (
    ChallengeEngine,
    Challenge,
)
from cortex.orchestrators.validation.confidence_scorer import (
    ConfidenceScorer,
    ConfidenceResult,
    ConfidenceFactor,
)
from cortex.orchestrators.validation.change_coherence_engine import ChangeCoherenceEngine
from cortex.orchestrators.validation.coherence_models import (
    CoherenceStatus,
    PreEditContext,
    CoherenceReport,
)
from cortex.orchestrators.validation.coherence_validator import (
    CoherenceValidator,
    ValidationConfig,
)
from cortex.orchestrators.validation.duplicate_scanner import DuplicateScanner
from cortex.orchestrators.validation.structure_analyzer import StructureAnalyzer

__all__ = [
    "HolisticValidationOrchestrator",
    "ValidationResult",
    "PreImplementationChecklist",
    "ChecklistResult",
    "CheckResult",
    "ChallengeEngine",
    "Challenge",
    "ConfidenceScorer",
    "ConfidenceResult",
    "ConfidenceFactor",
    "ChangeCoherenceEngine",
    "CoherenceStatus",
    "PreEditContext",
    "CoherenceReport",
    "CoherenceValidator",
    "ValidationConfig",
    "DuplicateScanner",
    "StructureAnalyzer",
]


# AC_START: AC-PHASE48-S1-IMPL-001
