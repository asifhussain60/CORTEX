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


# ============================================================================
# ACTION & EXECUTION ENUMS
# ============================================================================

class ActionType(Enum):
    """Type of action being taken."""
    IMPLEMENT = "implement"
    FIX = "fix"
    REFACTOR = "refactor"
    ANALYZE = "analyze"
    TEST = "test"
    DOCUMENT = "document"
    REVIEW = "review"
    DEPLOY = "deploy"


class ExecutionMode(Enum):
    """Orchestrator execution mode."""
    SYNC = "sync"
    ASYNC = "async"
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"


# ============================================================================
# ALERT & MONITORING ENUMS
# ============================================================================

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertPriority(Enum):
    """Alert priority for processing."""
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    DEFERRED = 5


class AlertState(Enum):
    """State of an alert."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


# ============================================================================
# AUDIT & GOVERNANCE ENUMS
# ============================================================================

class AuditEventType(Enum):
    """Type of audit event."""
    AC_START = "ac_start"
    AC_EXECUTE = "ac_execute"
    AC_COMPLETE = "ac_complete"
    GOVERNANCE_CHECK = "governance_check"
    POLICY_VIOLATION = "policy_violation"
    STATE_CHANGE = "state_change"
    ERROR = "error"
    WARNING = "warning"


class AuditAction(Enum):
    """Action recorded in audit trail."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"


class AuditOperationType(Enum):
    """Type of operation being audited."""
    FILE_OPERATION = "file_operation"
    DATABASE_OPERATION = "database_operation"
    NETWORK_OPERATION = "network_operation"
    GOVERNANCE_OPERATION = "governance_operation"
    ORCHESTRATOR_OPERATION = "orchestrator_operation"


class ApprovalStatus(Enum):
    """Status of approval."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class CheckpointStatus(Enum):
    """Status of a checkpoint."""
    CREATED = "created"
    VERIFIED = "verified"
    RESTORED = "restored"
    FAILED = "failed"
    ARCHIVED = "archived"


# ============================================================================
# CHALLENGE & INTENT ENUMS
# ============================================================================

class ChallengeType(Enum):
    """Type of challenge posed to user."""
    CLARIFICATION = "clarification"
    VERIFICATION = "verification"
    ALTERNATIVE = "alternative"
    CONCERN = "concern"
    SUGGESTION = "suggestion"


class ChallengeCategory(Enum):
    """Category of challenge."""
    INTENT = "intent"
    IMPLEMENTATION = "implementation"
    RISK = "risk"
    EFFICIENCY = "efficiency"
    GOVERNANCE = "governance"


class IntentType(Enum):
    """Classification of user intent."""
    IMPLEMENT = "implement"
    FIX = "fix"
    REFACTOR = "refactor"
    ANALYZE = "analyze"
    TEST = "test"
    DOCUMENT = "document"
    PLAN = "plan"
    DEPLOY = "deploy"
    OTHER = "other"


class RoutingType(Enum):
    """Type of routing decision."""
    PRIMARY = "primary"
    FALLBACK = "fallback"
    COMPOSITE = "composite"
    CONDITIONAL = "conditional"


# ============================================================================
# CHANGE & VERSION ENUMS
# ============================================================================

class ChangeType(Enum):
    """Type of change being tracked."""
    ADDITION = "addition"
    MODIFICATION = "modification"
    DELETION = "deletion"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"


class BrainTier(Enum):
    """Tier level in the CORTEX brain architecture."""
    TIER_0 = "tier_0"
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


# ============================================================================
# CIRCUIT BREAKER & RESILIENCE ENUMS
# ============================================================================

class CircuitBreakerState(Enum):
    """State of a circuit breaker."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


# ============================================================================
# COHERENCE & VALIDATION ENUMS
# ============================================================================

class CoherenceType(Enum):
    """Type of coherence check."""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    LOGICAL = "logical"
    CONSISTENCY = "consistency"


class ValidationLevel(Enum):
    """Level of validation to perform."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"


# ============================================================================
# CONTINUATION & DECISION ENUMS
# ============================================================================

class ContinuationReason(Enum):
    """Reason for continuation decision."""
    INCOMPLETE = "incomplete"
    MULTI_TURN = "multi_turn"
    APPROVAL_GATE = "approval_gate"
    RESOURCE_CONSTRAINT = "resource_constraint"
    USER_REQUEST = "user_request"


class DecisionStatus(Enum):
    """Status of a decision."""
    PENDING = "pending"
    DECIDED = "decided"
    APPEALED = "appealed"
    OVERRIDDEN = "overridden"


# ============================================================================
# GOVERNANCE & TIER ENUMS
# ============================================================================

class TierType(Enum):
    """Type of governance tier."""
    TIER_0 = "tier_0"  # Immutable governance
    TIER_1 = "tier_1"  # Acceptance criteria
    TIER_2 = "tier_2"  # Response templates
    TIER_3 = "tier_3"  # Knowledge & practices


class GovernanceStatus(Enum):
    """Status of governance compliance."""
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"
    DEFERRED = "deferred"


class RuleType(Enum):
    """Type of governance rule."""
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    DEPRECATED = "deprecated"


# ============================================================================
# KNOWLEDGE & ANALYSIS ENUMS
# ============================================================================

class KnowledgeSource(Enum):
    """Source of knowledge."""
    DOCUMENTATION = "documentation"
    GIT_HISTORY = "git_history"
    CODE_ANALYSIS = "code_analysis"
    USER_INPUT = "user_input"
    SYSTEM_GENERATED = "system_generated"


class AnalysisLevel(Enum):
    """Level of analysis depth."""
    SURFACE = "surface"
    STANDARD = "standard"
    DEEP = "deep"
    COMPREHENSIVE = "comprehensive"


# ============================================================================
# OPERATION & STATE ENUMS
# ============================================================================

class OperationStatus(Enum):
    """Status of an operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StateTransition(Enum):
    """Type of state transition."""
    INITIALIZATION = "initialization"
    NORMAL = "normal"
    ROLLBACK = "rollback"
    RECOVERY = "recovery"
    FINALIZATION = "finalization"


class PhaseStatus(Enum):
    """Status of a phase in execution."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# PATTERN & MATCHING ENUMS
# ============================================================================

class PatternType(Enum):
    """Type of pattern being detected."""
    DUPLICATION = "duplication"
    BRITTLENESS = "brittleness"
    HALLUCINATION = "hallucination"
    REGRESSION = "regression"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"


class MatchConfidence(Enum):
    """Confidence level of a pattern match."""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


# ============================================================================
# RESPONSE & COMMUNICATION ENUMS
# ============================================================================

class ResponseType(Enum):
    """Type of response."""
    DIRECT = "direct"
    INTERROGATIVE = "interrogative"
    INFORMATIVE = "informative"
    SUGGESTIVE = "suggestive"
    CHALLENGING = "challenging"


class MessageLevel(Enum):
    """Level of message detail."""
    SUMMARY = "summary"
    STANDARD = "standard"
    DETAILED = "detailed"
    EXHAUSTIVE = "exhaustive"


# ============================================================================
# TESTING & QUALITY ENUMS
# ============================================================================

class TestType(Enum):
    """Type of test."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestStatus(Enum):
    """Status of a test."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"


class QualityGate(Enum):
    """Quality gate status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


# ============================================================================
# WIRING & REGISTRY ENUMS
# ============================================================================

class WiringState(Enum):
    """State of orchestrator wiring."""
    UNINITIALIZED = "uninitialized"
    LOADING = "loading"
    REGISTERING = "registering"
    WIRED = "wired"
    FAILED = "failed"


class ComponentHealth(Enum):
    """Health status of a component."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# ============================================================================
# WORKFLOW & EXECUTION ENUMS
# ============================================================================

class WorkflowStage(Enum):
    """Stage in a workflow."""
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    COMPLETION = "completion"


class ExecutionStrategy(Enum):
    """Strategy for executing work."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    HYBRID = "hybrid"


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
