"""
DEPRECATED: RepositoryOnboardingOrchestrator

This module is DEPRECATED and will be removed on 2026-03-31.

MIGRATION: Use UnifiedOnboardingOrchestrator instead

    # OLD (DEPRECATED):
    from cortex.orchestrators.support.repository_onboarding_orchestrator import RepositoryOnboardingOrchestrator
    orchestrator = RepositoryOnboardingOrchestrator()
    profile = orchestrator.profile_repository(repo_path)

    # NEW (CURRENT):
    from cortex.orchestrators.support.unified_onboarding_orchestrator import UnifiedOnboardingOrchestrator
    orchestrator = UnifiedOnboardingOrchestrator()
    profile = orchestrator.onboard_repository(repo_path)

This wrapper maintains backward compatibility by delegating to UnifiedOnboardingOrchestrator.
"""

import warnings
from typing import Any, Dict, Optional

from cortex.orchestrators.support.unified_onboarding_orchestrator import (
    UnifiedOnboardingOrchestrator,
)


class RepositoryOnboardingOrchestrator:
    """
    DEPRECATED: Use UnifiedOnboardingOrchestrator instead.
    
    This class is a compatibility wrapper that delegates to UnifiedOnboardingOrchestrator.
    It will be removed on 2026-03-31.
    """

    def __init__(self):
        """Initialize with deprecation warning."""
        warnings.warn(
            "RepositoryOnboardingOrchestrator is DEPRECATED and will be removed on 2026-03-31. "
            "Use UnifiedOnboardingOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._unified = UnifiedOnboardingOrchestrator()

    def profile_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        DEPRECATED: Use UnifiedOnboardingOrchestrator.onboard_repository() instead.
        
        Profile a repository.
        """
        return self._unified.onboard_repository(repo_path)

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to unified orchestrator."""
        return getattr(self._unified, name)
