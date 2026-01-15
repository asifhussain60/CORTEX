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

from src.core.hallucination_prevention.intent_canonicalization import (
    ExtendedIntentCanonicalizer,
    ExtendedCanonicalIntent,
    ActionType,
)

from src.core.hallucination_prevention.behavioral_boundaries import (
    BehavioralBoundaryRules,
    BoundaryViolation,
    ViolationType,
)

from src.core.hallucination_prevention.execution_sandbox import (
    ExecutionSandbox,
    SandboxExecution,
    SandboxSnapshot,
    ExecutionMode,
    ExecutionState,
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
]
