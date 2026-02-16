"""Health Agent Module - Specialized Health Detectors

Provides specialized agents for detecting specific health issues:
- DuplicateDetectionAgent: CORE-035 violations
- StubDetectionAgent: Weak implementations
- StubAutoFixAgent: Automatic stub fixing (Phase 96)
- PathIntegrityAgent: Import path drift
- VersionCleanupAgent: Version artifacts
- TestCoverageAgent: Missing tests
- RegistryConsistencyAgent: Config misplacement

Author: CORTEX Framework
Phase: PHASE-92 + PHASE-96 enhancements
"""

from .base_agent import (
    BaseHealthAgent,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
    HealthCheckResult,
)
from .duplicate_detection_agent import DuplicateDetectionAgent
from .path_integrity_agent import PathIntegrityAgent
from .registry_consistency_agent import RegistryConsistencyAgent
from .stub_detection_agent import StubDetectionAgent
from .stub_autofix_agent import StubAutoFixAgent
from .test_coverage_agent import TestCoverageAgent
from .token_optimization_agent import TokenOptimizationAgent
from .version_cleanup_agent import VersionCleanupAgent

__all__ = [
    "BaseHealthAgent",
    "HealthIssue",
    "HealthIssueCategory",
    "HealthIssueSeverity",
    "HealthCheckResult",
    "DuplicateDetectionAgent",
    "PathIntegrityAgent",
    "RegistryConsistencyAgent",
    "StubDetectionAgent",
    "StubAutoFixAgent",
    "TestCoverageAgent",
    "TokenOptimizationAgent",
    "VersionCleanupAgent",
]
