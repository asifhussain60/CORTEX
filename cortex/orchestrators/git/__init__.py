"""Git orchestrator package.

Public exports:
    EnforcementOrchestrator — Stage 1: CORE rule enforcement (replaces .githooks + GHA)
    SanitizationOrchestrator — Stage 2: proprietary/PII/secret deep scan + morph
    GitPublishOrchestrator — Stage 3: async git add → commit → push
    GitOrchestrator — Full 3-stage pipeline coordinator (canonical entry point)
"""

from cortex.orchestrators.git.enforcement_orchestrator import (
    CheckResult,
    EnforcementOrchestrator,
    EnforcementReport,
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
    # Enforcement
    "CheckResult",
    "EnforcementOrchestrator",
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
