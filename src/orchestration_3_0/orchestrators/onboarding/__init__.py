"""
Onboarding Orchestrator - Project, user, and team onboarding for CORTEX 4.0.

Provides guided onboarding for projects, users, and teams with progress tracking.
"""

from .onboarding_orchestrator import (
    OnboardingOrchestrator,
    create_onboarding_orchestrator,
    ProjectOnboardingResult,
    UserOnboardingResult,
    TeamOnboardingResult
)

__all__ = [
    'OnboardingOrchestrator',
    'create_onboarding_orchestrator',
    'ProjectOnboardingResult',
    'UserOnboardingResult',
    'TeamOnboardingResult'
]
