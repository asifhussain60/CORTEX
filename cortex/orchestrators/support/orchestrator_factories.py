"""
TRACK 4: Orchestrator Factory Functions (Compatibility Layer)

This module provides unified factory functions that handle the migration from
deprecated orchestrators to their unified replacements.

All code should use these factories instead of direct imports.

DEPRECATION POLICY:
- Old factory functions (e.g., get_repository_onboarding_orchestrator) will emit warnings
- New factory functions (e.g., get_unified_onboarding_orchestrator) are recommended
- Both work until sunset date (2026-03-31)

Example:
    # OLD (DEPRECATED):
    from cortex.orchestrators.support.repository_onboarding_orchestrator import get_repository_onboarding_orchestrator
    orchestrator = get_repository_onboarding_orchestrator()
    
    # NEW (RECOMMENDED):
    from cortex.orchestrators.support.orchestrator_factories import get_unified_onboarding_orchestrator
    orchestrator = get_unified_onboarding_orchestrator()
"""

import warnings
from typing import Optional

from cortex.orchestrators.support.unified_analysis_orchestrator import (
    UnifiedAnalysisOrchestrator,
)
from cortex.orchestrators.support.unified_discovery_orchestrator import (
    UnifiedDiscoveryOrchestrator,
)
from cortex.orchestrators.support.unified_onboarding_orchestrator import (
    UnifiedOnboardingOrchestrator,
)
from cortex.orchestrators.support.unified_quality_orchestrator import (
    UnifiedQualityAssuranceOrchestrator,
)


# ============================================================================
# New Unified Factory Functions (RECOMMENDED)
# ============================================================================

def get_unified_onboarding_orchestrator() -> UnifiedOnboardingOrchestrator:
    """
    Get unified onboarding orchestrator.
    
    Consolidates:
    - RepositoryOnboardingOrchestrator
    - SetupOrchestrator
    - OnboardingOrchestrator
    
    Returns:
        UnifiedOnboardingOrchestrator instance
    
    Example:
        >>> orchestrator = get_unified_onboarding_orchestrator()
        >>> profile = orchestrator.onboard_repository("/path/to/repo")
    """
    return UnifiedOnboardingOrchestrator()


def get_unified_analysis_orchestrator() -> UnifiedAnalysisOrchestrator:
    """
    Get unified analysis orchestrator.
    
    Consolidates:
    - LENSOrchestrator
    - ToolDiscoveryOrchestrator
    
    Returns:
        UnifiedAnalysisOrchestrator instance
    
    Example:
        >>> orchestrator = get_unified_analysis_orchestrator()
        >>> result = orchestrator.analyze(code, "complexity")
    """
    return UnifiedAnalysisOrchestrator()


def get_unified_quality_orchestrator() -> UnifiedQualityAssuranceOrchestrator:
    """
    Get unified quality assurance orchestrator.
    
    Consolidates:
    - RecommendationGate
    - ChallengeEngine
    - MetaAuditOrchestrator
    - CodeReviewOrchestrator
    - SecurityReviewEngine
    
    Returns:
        UnifiedQualityAssuranceOrchestrator instance
    
    Example:
        >>> orchestrator = get_unified_quality_orchestrator()
        >>> result = orchestrator.check_recommendation_safety(recommendation)
    """
    return UnifiedQualityAssuranceOrchestrator()


def get_unified_discovery_orchestrator() -> UnifiedDiscoveryOrchestrator:
    """
    Get unified discovery orchestrator.
    
    Consolidates:
    - EducationalOrchestrator
    - BusinessLanguageOrchestrator
    
    Returns:
        UnifiedDiscoveryOrchestrator instance
    
    Example:
        >>> orchestrator = get_unified_discovery_orchestrator()
        >>> results = orchestrator.discover_resources(query="async")
    """
    return UnifiedDiscoveryOrchestrator()


# ============================================================================
# Deprecated Factory Functions (BACKWARD COMPATIBILITY ONLY)
# ============================================================================

def get_repository_onboarding_orchestrator() -> UnifiedOnboardingOrchestrator:
    """
    DEPRECATED: Use get_unified_onboarding_orchestrator() instead.
    
    Get repository onboarding orchestrator.
    
    This function is deprecated and will be removed on 2026-03-31.
    It now delegates to UnifiedOnboardingOrchestrator.
    
    Returns:
        UnifiedOnboardingOrchestrator instance (wrapped for compatibility)
    """
    warnings.warn(
        "get_repository_onboarding_orchestrator() is DEPRECATED and will be removed on 2026-03-31. "
        "Use get_unified_onboarding_orchestrator() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return UnifiedOnboardingOrchestrator()


def get_lens_orchestrator() -> UnifiedAnalysisOrchestrator:
    """
    DEPRECATED: Use get_unified_analysis_orchestrator() instead.
    
    Get LENS analysis orchestrator.
    
    This function is deprecated and will be removed on 2026-03-31.
    It now delegates to UnifiedAnalysisOrchestrator.
    
    Returns:
        UnifiedAnalysisOrchestrator instance (wrapped for compatibility)
    """
    warnings.warn(
        "get_lens_orchestrator() is DEPRECATED and will be removed on 2026-03-31. "
        "Use get_unified_analysis_orchestrator() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return UnifiedAnalysisOrchestrator()


def get_recommendation_gate() -> UnifiedQualityAssuranceOrchestrator:
    """
    DEPRECATED: Use get_unified_quality_orchestrator() instead.
    
    Get recommendation safety gate.
    
    This function is deprecated and will be removed on 2026-03-31.
    It now delegates to UnifiedQualityAssuranceOrchestrator.
    
    Returns:
        UnifiedQualityAssuranceOrchestrator instance (wrapped for compatibility)
    """
    warnings.warn(
        "get_recommendation_gate() is DEPRECATED and will be removed on 2026-03-31. "
        "Use get_unified_quality_orchestrator() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return UnifiedQualityAssuranceOrchestrator()


def get_educational_orchestrator() -> UnifiedDiscoveryOrchestrator:
    """
    DEPRECATED: Use get_unified_discovery_orchestrator() instead.
    
    Get educational discovery orchestrator.
    
    This function is deprecated and will be removed on 2026-03-31.
    It now delegates to UnifiedDiscoveryOrchestrator.
    
    Returns:
        UnifiedDiscoveryOrchestrator instance (wrapped for compatibility)
    """
    warnings.warn(
        "get_educational_orchestrator() is DEPRECATED and will be removed on 2026-03-31. "
        "Use get_unified_discovery_orchestrator() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return UnifiedDiscoveryOrchestrator()


__all__ = [
    # New unified factories (RECOMMENDED)
    "get_unified_onboarding_orchestrator",
    "get_unified_analysis_orchestrator",
    "get_unified_quality_orchestrator",
    "get_unified_discovery_orchestrator",
    # Deprecated factories (for backward compatibility only)
    "get_repository_onboarding_orchestrator",
    "get_lens_orchestrator",
    "get_recommendation_gate",
    "get_educational_orchestrator",
]
