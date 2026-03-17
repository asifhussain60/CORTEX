"""
CORTEX Intelligence Layer.

Unified intelligence package consolidating:
- cortex.intelligence: Tier-based adaptive intelligence (perception, reasoning, action)
- cortex.lens: Multi-language code analysis and LENS architecture
- cortex.intelligence: Deep computation engines (AST, git, relationships, patterns)

Authority: Phase 3 - Package Consolidation
"""

__license__ = 'Proprietary'
__description__ = 'Unified Intelligence and Analysis Layer'
__all__ = []

# Core intelligence engines
try:
    from cortex.intelligence.base import (
        AnalysisContext,
        AnalysisResult,
        BaseIntelligenceEngine,
    )
    __all__ = [
        "BaseIntelligenceEngine",
        "AnalysisContext",
        "AnalysisResult",
    ]
except ImportError:
    import logging as _logging; _logging.getLogger(__name__).warning("Optional cortex dependency unavailable: cortex.intelligence.base — feature degraded")

# Tier-based intelligence (formerly cortex.intelligence)
def __getattr__(name: str):
    """Lazy load intelligence tier modules."""
    if name in ('tier0', 'tier1', 'tier2', 'state', 'releases', 'memory', 'perception', 'reasoning', 'action', 'domain', 'domain_brain', 'governance', 'observability', 'onboarded_repos', 'quality', 'audit', 'intelligence', 'wiring'):
        try:
            import importlib
            return importlib.import_module(f'cortex.intelligence.{name}')
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex.intelligence' has no attribute '{name}'")


# GAP-80-07: Canonical synthesize() facade — single knowledge API entry point
try:
    from cortex.intelligence.provider import synthesize  # noqa: F401
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "Optional cortex dependency unavailable: cortex.intelligence.provider.synthesize "
        "— feature degraded"
    )


# Hallucination prevention compatibility exports
try:
    from cortex.intelligence.memory.tier2_adaptive import (  # noqa: F401
        BehavioralBoundaryRules,
        BoundaryViolation,
        ViolationType,
    )
except ImportError:
    BehavioralBoundaryRules = None
    BoundaryViolation = None
    ViolationType = None

try:
    from cortex.intelligence.execution_sandbox import (  # noqa: F401
        ExecutionSandbox,
        SandboxExecution,
        SandboxSnapshot,
        ExecutionMode,
        ExecutionState,
    )
except ImportError:
    ExecutionSandbox = None
    SandboxExecution = None
    SandboxSnapshot = None
    ExecutionMode = None
    ExecutionState = None

try:
    from cortex.intelligence.memory.tier2_adaptive.hallucination_prevention.confidence_scoring import (  # noqa: F401
        ConfidenceScorer,
        ConfidenceAssessment,
    )
except ImportError:
    ConfidenceScorer = None
    ConfidenceAssessment = None

try:
    from cortex.models.canonical_enums import ActionType  # noqa: F401
except ImportError:
    ActionType = None


class ExtendedCanonicalIntent:
    """Compatibility intent model for legacy hallucination prevention contracts."""

    def __init__(self, action_type: object, canonical_text: str) -> None:
        self.action_type = action_type
        self.canonical_text = canonical_text


class ExtendedIntentCanonicalizer:
    """Compatibility canonicalizer for legacy import contracts."""

    def canonicalize(self, text: str) -> "ExtendedCanonicalIntent":
        resolved_action = ActionType.QUERY if ActionType and hasattr(ActionType, "QUERY") else "QUERY"
        return ExtendedCanonicalIntent(action_type=resolved_action, canonical_text=text.strip())


__all__.extend([
    "BehavioralBoundaryRules",
    "BoundaryViolation",
    "ViolationType",
    "ExecutionSandbox",
    "SandboxExecution",
    "SandboxSnapshot",
    "ExecutionMode",
    "ExecutionState",
    "ExtendedIntentCanonicalizer",
    "ExtendedCanonicalIntent",
    "ActionType",
    "ConfidenceScorer",
    "ConfidenceAssessment",
])
