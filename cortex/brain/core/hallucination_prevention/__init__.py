# © 2025-2026 Asif Hussain. All rights reserved.
"""
Hallucination Prevention System.

PHASE-11: Behavioral boundaries and detection for AI agents.

Submodules:
- intent_canonicalization: Extended intent canonicalization (HP-001-01)
- behavior_boundaries: Boundary rules enforcement (HP-001-02)
- execution_sandbox: Isolated execution with rollback (HP-002-01)
- hallucination_detection: SSOT corruption detection (HP-002-02)
- vision_mutations: Vision mutation tracking (HP-003-01)
- confidence_scoring: Agent confidence assessment (HP-003-02)
"""

from cortex.brain.core.hallucination_prevention.intent_canonicalization import (
    ExtendedIntentCanonicalizer,
    ExtendedCanonicalIntent,
    ActionType,
)

from cortex.brain.core.hallucination_prevention.behavioral_boundaries import (
    BehavioralBoundaryRules,
    BoundaryViolation,
    ViolationType,
)

from cortex.brain.core.hallucination_prevention.execution_sandbox import (
    ExecutionSandbox,
    SandboxExecution,
    SandboxSnapshot,
    ExecutionMode,
    ExecutionState,
)

from cortex.brain.core.hallucination_prevention.hallucination_detection import (
    HallucinationDetector,
    CorruptionDetectionResult,
    CorruptionType,
    RecoveryStrategy,
    IncidentReport,
)

from cortex.brain.core.hallucination_prevention.vision_mutations import (
    VisionMutationTracker,
    VisionMutation,
    MutationType,
    MutationSnapshot,
)

from cortex.brain.core.hallucination_prevention.confidence_scoring import (
    ConfidenceScorer,
    ConfidenceAssessment,
    ScoringFactor,
    ScoringModel,
    ReviewTrigger,
)

__all__ = [
    "ExtendedIntentCanonicalizer",
    "ExtendedCanonicalIntent",
    "ActionType",
    "BehavioralBoundaryRules",
    "BoundaryViolation",
    "ViolationType",
    "ExecutionSandbox",
    "SandboxExecution",
    "SandboxSnapshot",
    "ExecutionMode",
    "ExecutionState",
    "HallucinationDetector",
    "CorruptionDetectionResult",
    "CorruptionType",
    "RecoveryStrategy",
    "IncidentReport",
    "VisionMutationTracker",
    "VisionMutation",
    "MutationType",
    "MutationSnapshot",
    "ConfidenceScorer",
    "ConfidenceAssessment",
    "ScoringFactor",
    "ScoringModel",
    "ReviewTrigger",
]
