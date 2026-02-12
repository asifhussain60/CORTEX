"""Onboarding orchestrators package for CORTEX.

Wave 7 Track 4: Consolidated to single OnboardingOrchestrator.
Legacy components purged 2026-02-12.
"""

from cortex.orchestrators.onboarding.orchestrator import OnboardingOrchestrator

__all__ = [
    "OnboardingOrchestrator",
]
