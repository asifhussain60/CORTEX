"""
cortex.ci_cd.production_release — Re-export from canonical location.

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
