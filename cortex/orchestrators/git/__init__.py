"""Git orchestrator package.

Public exports:
    PreCommitEnforcementOrchestrator — Stage 1: CORE rule enforcement (replaces .githooks + GHA)
    EnforcementOrchestrator — deprecated alias for PreCommitEnforcementOrchestrator
    SanitizationOrchestrator — Stage 2: proprietary/PII/secret deep scan + morph
    GitPublishOrchestrator — Stage 3: local commit; push is opt-in (auto_push=False)
    GitOrchestrator — Full 3-stage pipeline coordinator (canonical entry point)
"""

from cortex.orchestrators.git.enforcement_orchestrator import (
    CheckResult,
    EnforcementOrchestrator,          # deprecated alias — kept for backward compat
    EnforcementReport,
    PreCommitEnforcementOrchestrator,  # canonical name (CORE-035)
)
from cortex.orchestrators.git.git_orchestrator import (
    GitOrchestrator,
    GitOrchestratorError,
    GitOrchestratorResult,
)
from cortex.orchestrators.git.git_publish_orchestrator import (
    GitPublishOrchestrator,
    PublishError,
    PublishResult,
)
from cortex.orchestrators.git.sanitization_orchestrator import (
    AuditTrail,
    FileScannerEngine,
    IntegrityValidator,
    MorphingEngine,
    PatternRegistry,
    SanitizationError,
    SanitizationOrchestrator,
)

__all__ = [
    # Enforcement (canonical)
    "CheckResult",
    "PreCommitEnforcementOrchestrator",
    "EnforcementOrchestrator",   # deprecated alias
    "EnforcementReport",
    # Pipeline coordinator
    "GitOrchestrator",
    "GitOrchestratorError",
    "GitOrchestratorResult",
    # Publish
    "GitPublishOrchestrator",
    "PublishError",
    "PublishResult",
    # Sanitization
    "AuditTrail",
    "FileScannerEngine",
    "IntegrityValidator",
    "MorphingEngine",
    "PatternRegistry",
    "SanitizationError",
    "SanitizationOrchestrator",
]
