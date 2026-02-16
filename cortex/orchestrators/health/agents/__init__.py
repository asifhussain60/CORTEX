"""Health Agent Module - Specialized Health Detectors

Provides specialized agents for detecting specific health issues:
- DuplicateDetectionAgent: CORE-035 violations
- StubDetectionAgent: Weak implementations
- PathIntegrityAgent: Import path drift
- VersionCleanupAgent: Version artifacts
- TestCoverageAgent: Missing tests
- RegistryConsistencyAgent: Config misplacement

Author: CORTEX Framework
Phase: PHASE-92
"""

from .base_agent import (
    BaseHealthAgent,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
    HealthCheckResult,
)

__all__ = [
    "BaseHealthAgent",
    "HealthIssue",
    "HealthIssueCategory",
    "HealthIssueSeverity",
    "HealthCheckResult",
]
