"""Intent module for CORTEX."""

from .intent_canonicalizer import IntentCanonicalizer, CanonicalizedIntent, IntentScope, IntentType
from cortex.core.intent.challenge_generator import ChallengeGenerator, Challenge, ChallengeCategory, Severity
from .comprehension_yaml import (
    CanonicalIntentComposer,
    ComprehensionYAML,
    IntentSection,
    ChallengeSection,
    RecommendationSection,
)
from .intent_reflection_protocol import (
    IntentReflectionEngine,
    ReflectionRequest,
    ReflectionResponse,
    ReflectionStatus,
)
from .lens_context_builder import (
    LENSContextBuilder,
    LENSContext,
    KnowledgeGraph,
    ContextNode,
    ContextEdge,
)
from .lens_response_formatter import (
    LENSResponseFormatter,
    ResponseFormat,
    SeverityColor,
    FormattedResponse,
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
    # Intent reflection protocol
    "IntentReflectionEngine",
    "ReflectionRequest",
    "ReflectionResponse",
    "ReflectionStatus",
    # LENS context builder
    "LENSContextBuilder",
    "LENSContext",
    "KnowledgeGraph",
    "ContextNode",
    "ContextEdge",
    # LENS response formatter
    "LENSResponseFormatter",
    "ResponseFormat",
    "SeverityColor",
    "FormattedResponse",
]
