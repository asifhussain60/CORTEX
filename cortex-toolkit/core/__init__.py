"""
CORTEX Toolkit Core Module

Central orchestration layer for toolkit operations.
"""
from .toolkit_manager import (
    ToolkitManager,
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    CreationCheck,
    ToolSpec,
)
from .gate_keeper import (
    GateKeeper,
    ValidationCheck,
    SanitizeResult,
    SecurityViolation,
)
from .capability_matrix import (
    CapabilityMatrix,
    ToolCapabilities,
    ToolMatch,
)
from .request_analyzer import (
    RequestAnalyzer,
    ToolRequest,
    AnalysisResult,
    RecommendationType,
)
from .checkpoint import (
    Checkpoint,
    CheckpointState,
)
from .recovery_manager import (
    RecoveryManager,
    ExecutionContext as RecoveryContext,
    RollbackResult,
    RecoveryError,
    CheckpointNotFoundError,
)
from .dependency_manager import (
    DependencyManager,
    DependencyCheck,
    DependencyGraph,
    CircularDependencyError,
    UnmetDependencyError,
)
from .manifest_schema import (
    ManifestSchema,
    ValidationResult as SchemaValidationResult,
    PRIVILEGE_LEVELS,
    VALID_CAPABILITIES,
    DESTRUCTIVE_PATTERNS,
)
from .security_guard import (
    SecurityGuard,
    SanitizeResult as SecuritySanitizeResult,
    SecurityViolation as SecurityGuardViolation,
    PrivilegeCheckResult,
    Severity,
    PrivilegeLevel,
)
from .audit_logger import (
    AuditLogger,
    ExecutionEvent as AuditExecutionEvent,
    SecurityEvent,
)
from .exceptions import (
    ToolkitError,
    ToolNotFoundError,
    PlatformNotSupportedError,
    DependencyError,
    SecurityViolationError,
    ValidationError,
    ExecutionError,
    RateLimitError,
    DuplicationWarning,
    CheckpointError,
    ValidationResult,
)

__all__ = [
    # Manager
    "ToolkitManager",
    "ExecutionContext",
    "ExecutionResult",
    "ExecutionStatus",
    "CreationCheck",
    "ToolSpec",
    # GateKeeper
    "GateKeeper",
    "ValidationCheck",
    "SanitizeResult",
    "SecurityViolation",
    # Capability Matrix
    "CapabilityMatrix",
    "ToolCapabilities",
    "ToolMatch",
    # Request Analyzer
    "RequestAnalyzer",
    "ToolRequest",
    "AnalysisResult",
    "RecommendationType",
    # Checkpoint & Recovery
    "Checkpoint",
    "CheckpointState",
    "RecoveryManager",
    "RecoveryContext",
    "RollbackResult",
    "RecoveryError",
    "CheckpointNotFoundError",
    # Dependency Manager
    "DependencyManager",
    "DependencyCheck",
    "DependencyGraph",
    "CircularDependencyError",
    "UnmetDependencyError",
    # Manifest Schema (Phase 5)
    "ManifestSchema",
    "SchemaValidationResult",
    "PRIVILEGE_LEVELS",
    "VALID_CAPABILITIES",
    "DESTRUCTIVE_PATTERNS",
    # Security Guard (Phase 6)
    "SecurityGuard",
    "SecuritySanitizeResult",
    "SecurityGuardViolation",
    "PrivilegeCheckResult",
    "Severity",
    "PrivilegeLevel",
    # Audit Logger (Phase 6)
    "AuditLogger",
    "AuditExecutionEvent",
    "SecurityEvent",
    # Exceptions
    "ToolkitError",
    "ToolNotFoundError",
    "PlatformNotSupportedError",
    "DependencyError",
    "SecurityViolationError",
    "ValidationError",
    "ExecutionError",
    "RateLimitError",
    "DuplicationWarning",
    "CheckpointError",
    "ValidationResult",
]
