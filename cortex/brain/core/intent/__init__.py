"""Intent module for CORTEX."""

from cortex.core.intent.challenge_generator import (
    Challenge,
    ChallengeCategory,
    ChallengeGenerator,
    Severity,
)

from .comprehension_yaml import (
    CanonicalIntentComposer,
    ChallengeSection,
    ComprehensionYAML,
    IntentSection,
    RecommendationSection,
)
from .intent_canonicalizer import (
    CanonicalizedIntent,
    IntentCanonicalizer,
    IntentScope,
    IntentType,
)
from .intent_reflection_protocol import (
    IntentReflectionEngine,
    ReflectionRequest,
    ReflectionResponse,
    ReflectionStatus,
)
from .lens_context_builder import (
    ContextEdge,
    ContextNode,
    KnowledgeGraph,
    LENSContext,
    LENSContextBuilder,
)
from .lens_response_formatter import (
    FormattedResponse,
    LENSResponseFormatter,
    ResponseFormat,
    SeverityColor,
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
