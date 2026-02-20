"""
cortex.ci_cd — CI/CD Re-exports.

The canonical implementation lives at cortex.infrastructure.ci_cd.
This module provides a convenience import path.

Authority: CORE-035 (Single Canonical Implementation)
"""

from cortex.infrastructure.ci_cd.production_release import (
    ProductionReleaseManager,
    ReleaseResult,
)

__all__ = [
    "ProductionReleaseManager",
    "ReleaseResult",
]
