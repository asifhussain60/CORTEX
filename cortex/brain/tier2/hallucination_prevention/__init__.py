"""
Hallucination Prevention System (PHASE-11)

Behavioral boundaries for AI agents through:
- Intent canonicalization
- Boundary enforcement
- Execution sandboxing
- Detection and recovery
- Mutation tracking
- Confidence scoring
"""

from .canonicalization_engine import (
    CanonicalIntentEngine,
    IntentCanonicalForm,
    ACIDExtraction,
    PhaseClassification,
    ActionTypeClassifier,
)

__all__ = [
    "CanonicalIntentEngine",
    "IntentCanonicalForm",
    "ACIDExtraction",
    "PhaseClassification",
    "ActionTypeClassifier",
]
