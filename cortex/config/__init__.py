"""
CORTEX Configuration Module

Provides:
- Configuration management
- Unified onboarding interface (backward compatible)
- Settings and defaults
"""

# Unified Onboarding - Primary API
from cortex.config.unified_onboarding import (
    Journey,
    JourneyState,
    OnboardingConfig,
    UnifiedOnboarding,
    get_unified_onboarding,
)

__all__ = [
    # Unified Onboarding
    "UnifiedOnboarding",
    "OnboardingConfig",
    "Journey",
    "JourneyState",
    "get_unified_onboarding",
]
