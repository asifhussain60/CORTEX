"""Response orchestrators package."""

# ✅ CONS-008: Unified Response Composer (consolidates 5 implementations)
from .unified_response_composer import (
    Challenge as UnifiedChallenge,
)
from .unified_response_composer import (
    ChallengeType as UnifiedChallengeType,
)
from .unified_response_composer import (
    FormattingOptions,
    FormattingProfile,
    QualityMetricType,
    ResponseComposerConfig,
    ResponseMetadata,
    ResponseMode,
    ResponseQualityMetrics,
    ResponseSegment,
    ResponseTemplate,
    ResponseTone,
    ResponseType,
    TurnResponse,
    UnifiedResponseComposer,
    VariableSpec,
    VariableType,
    get_unified_response_composer,
)
from .unified_response_composer import (
    ResponseWithChallenges as UnifiedResponseWithChallenges,
)

# Note: Legacy imports removed after CONS-008 consolidation
# - turn_response_generator.py → UnifiedResponseComposer
# - turn_response_with_challenges.py → UnifiedResponseComposer
# All functionality available via UnifiedResponseComposer

__all__ = [
    # Unified Response Composer (CONS-008)
    "UnifiedResponseComposer",
    "get_unified_response_composer",
    "ResponseMode",
    "ResponseTone",
    "FormattingProfile",
    "ResponseType",
    "VariableType",
    "UnifiedChallengeType",
    "QualityMetricType",
    "ResponseComposerConfig",
    "ResponseMetadata",
    "ResponseSegment",
    "TurnResponse",
    "ResponseQualityMetrics",
    "FormattingOptions",
    "VariableSpec",
    "ResponseTemplate",
    "UnifiedChallenge",
    "UnifiedResponseWithChallenges",
]
