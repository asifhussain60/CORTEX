"""Response orchestrators package."""

# ✅ CONS-008: Unified Response Composer (consolidates 5 implementations)
from .unified_response_composer import (
    UnifiedResponseComposer,
    get_unified_response_composer,
    ResponseMode,
    ResponseTone,
    FormattingProfile,
    ResponseType,
    VariableType,
    ChallengeType as UnifiedChallengeType,
    QualityMetricType,
    ResponseComposerConfig,
    ResponseMetadata,
    ResponseSegment,
    TurnResponse,
    ResponseQualityMetrics,
    FormattingOptions,
    VariableSpec,
    ResponseTemplate,
    Challenge as UnifiedChallenge,
    ResponseWithChallenges as UnifiedResponseWithChallenges,
)

# ✅ Legacy imports for backward compatibility
from .turn_response_generator import (
    TurnResponseGenerator,
    ResponseBuilder,
    ResponseFormatter,
)
from .turn_response_with_challenges import (
    TurnResponseWithChallenges,
    ChallengeResponseGenerator,
    ResponseWithChallenges,
    Challenge,
    ChallengeType,
)

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
    # Legacy exports (for backward compatibility)
    "TurnResponseGenerator",
    "ResponseBuilder",
    "ResponseFormatter",
    "TurnResponseWithChallenges",
    "ChallengeResponseGenerator",
    "ResponseWithChallenges",
    "Challenge",
    "ChallengeType",
]
