"""
Canonical Enum Definitions - Single Source of Truth (SSOT)

AC-ID: AC-PERMANENT-FIX-017
Purpose: Eliminate CORE-035 violations by consolidating 275+ duplicate enum definitions

This module serves as the SINGLE CANONICAL LOCATION for all enums used across CORTEX.
All other files must import enums from this module, never define duplicates.

Governance Rules:
- CORE-035: Single Canonical Implementation
- CORE-011: Type hints mandatory (all enums use Enum)
- CORE-030: Implementation Truth (this is the truth; other copies are errors)

Migration Strategy:
1. Search codebase for enum definitions
2. Replace with imports from this module
3. Delete original enum definitions
4. Validate circular import prevention
"""

from enum import Enum
from cortex.models.canonical_enums import (
    ActionType,
    AlertPriority,
    AlertSeverity,
    AlertState,
    AnalysisLevel,
    ApprovalStatus,
    AuditAction,
    AuditEventType,
    AuditOperationType,
    BrainTier,
    ChallengeCategory,
    ChallengeType,
    ChangeType,
    CheckpointStatus,
    CircuitBreakerState,
    CoherenceType,
    ComponentHealth,
    ContinuationReason,
    DecisionStatus,
    ExecutionMode,
    ExecutionStrategy,
    GovernanceStatus,
    IntentType,
    KnowledgeSource,
    MatchConfidence,
    MessageLevel,
    OperationStatus,
    PatternType,
    PhaseStatus,
    QualityGate,
    ResponseType,
    RoutingType,
    RuleType,
    StateTransition,
    TestStatus,
    TestType,
    TierType,
    ValidationLevel,
    WiringState,
    WorkflowStage
)


# ============================================================================
# ACTION & EXECUTION ENUMS
# ============================================================================





# ============================================================================
# ALERT & MONITORING ENUMS
# ============================================================================







# ============================================================================
# AUDIT & GOVERNANCE ENUMS
# ============================================================================











# ============================================================================
# CHALLENGE & INTENT ENUMS
# ============================================================================









# ============================================================================
# CHANGE & VERSION ENUMS
# ============================================================================





# ============================================================================
# CIRCUIT BREAKER & RESILIENCE ENUMS
# ============================================================================



# ============================================================================
# COHERENCE & VALIDATION ENUMS
# ============================================================================





# ============================================================================
# CONTINUATION & DECISION ENUMS
# ============================================================================





# ============================================================================
# GOVERNANCE & TIER ENUMS
# ============================================================================







# ============================================================================
# KNOWLEDGE & ANALYSIS ENUMS
# ============================================================================





# ============================================================================
# OPERATION & STATE ENUMS
# ============================================================================







# ============================================================================
# PATTERN & MATCHING ENUMS
# ============================================================================





# ============================================================================
# RESPONSE & COMMUNICATION ENUMS
# ============================================================================





# ============================================================================
# TESTING & QUALITY ENUMS
# ============================================================================







# ============================================================================
# WIRING & REGISTRY ENUMS
# ============================================================================





# ============================================================================
# WORKFLOW & EXECUTION ENUMS
# ============================================================================





# ============================================================================
# Module-level exports for star imports
# ============================================================================

__all__ = [
    # Action & Execution
    "ActionType",
    "ExecutionMode",
    # Alert & Monitoring
    "AlertSeverity",
    "AlertPriority",
    "AlertState",
    # Audit & Governance
    "AuditEventType",
    "AuditAction",
    "AuditOperationType",
    "ApprovalStatus",
    "CheckpointStatus",
    # Challenge & Intent
    "ChallengeType",
    "ChallengeCategory",
    "IntentType",
    "RoutingType",
    # Change & Version
    "ChangeType",
    "BrainTier",
    # Circuit Breaker & Resilience
    "CircuitBreakerState",
    # Coherence & Validation
    "CoherenceType",
    "ValidationLevel",
    # Continuation & Decision
    "ContinuationReason",
    "DecisionStatus",
    # Governance & Tier
    "TierType",
    "GovernanceStatus",
    "RuleType",
    # Knowledge & Analysis
    "KnowledgeSource",
    "AnalysisLevel",
    # Operation & State
    "OperationStatus",
    "StateTransition",
    "PhaseStatus",
    # Pattern & Matching
    "PatternType",
    "MatchConfidence",
    # Response & Communication
    "ResponseType",
    "MessageLevel",
    # Testing & Quality
    "TestType",
    "TestStatus",
    "QualityGate",
    # Wiring & Registry
    "WiringState",
    "ComponentHealth",
    # Workflow & Execution
    "WorkflowStage",
    "ExecutionStrategy",
]
