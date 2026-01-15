# © 2025-2026 Asif Hussain. All rights reserved.
"""Intent module for CORTEX."""

from .intent_canonicalizer import IntentCanonicalizer, CanonicalizedIntent, IntentScope, IntentType
from .challenge_generator import ChallengeGenerator, Challenge, ChallengeCategory, Severity
from .comprehension_yaml import (
    CanonicalIntentComposer,
    ComprehensionYAML,
    IntentSection,
    ChallengeSection,
    RecommendationSection,
)

__all__ = [
    # Intent canonicalizer
    "IntentCanonicalizer",
    "CanonicalizedIntent",
    "IntentScope",
    "IntentType",
    # Challenge generator
    "ChallengeGenerator",
    "Challenge",
    "ChallengeCategory",
    "Severity",
    # Comprehension YAML
    "CanonicalIntentComposer",
    "ComprehensionYAML",
    "IntentSection",
    "ChallengeSection",
    "RecommendationSection",
]
