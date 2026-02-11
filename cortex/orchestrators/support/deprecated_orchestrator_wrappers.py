"""
TRACK 4: Deprecated Orchestrator Migration Wrappers

This module provides backward-compatible wrappers for all deprecated orchestrators
that were consolidated in Wave 7 Track 3.

SUNSET DATE: 2026-03-31
STATUS: All functionality moved to unified orchestrators

Deprecated Orchestrators:
1. RepositoryOnboardingOrchestrator → UnifiedOnboardingOrchestrator
2. SetupOrchestrator → UnifiedOnboardingOrchestrator
3. LENSOrchestrator → UnifiedAnalysisOrchestrator
4. ToolDiscoveryOrchestrator → UnifiedAnalysisOrchestrator
5. RecommendationGate → UnifiedQualityAssuranceOrchestrator
6. ChallengeEngine → UnifiedQualityAssuranceOrchestrator
7. MetaAuditOrchestrator → UnifiedQualityAssuranceOrchestrator
8. EducationalOrchestrator → UnifiedDiscoveryOrchestrator
9. BusinessLanguageOrchestrator → UnifiedDiscoveryOrchestrator

Usage:
    # OLD (DEPRECATED):
    from cortex.orchestrators.support.repository_onboarding_orchestrator import RepositoryOnboardingOrchestrator
    
    # NEW (RECOMMENDED):
    from cortex.orchestrators.support.unified_onboarding_orchestrator import UnifiedOnboardingOrchestrator

Note: Importing from deprecated modules will show warnings but still work until sunset date.
"""

import warnings
from typing import Any


def deprecated_import_wrapper(old_class_name: str, unified_class_name: str, unified_module: str):
    """
    Create a deprecation wrapper that redirects to a unified orchestrator.
    
    Args:
        old_class_name: Name of deprecated class
        unified_class_name: Name of unified replacement class
        unified_module: Module path to unified class
    
    Returns:
        Wrapper class that delegates to unified orchestrator
    """
    from importlib import import_module
    
    unified_cls = getattr(import_module(unified_module), unified_class_name)
    
    class DeprecatedWrapper:
        """Wrapper for deprecated orchestrator."""
        
        def __init__(self, *args, **kwargs):
            """Initialize with deprecation warning."""
            warnings.warn(
                f"{old_class_name} is DEPRECATED and will be removed on 2026-03-31. "
                f"Use {unified_class_name} instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            self._unified = unified_cls(*args, **kwargs)
        
        def __getattr__(self, name: str) -> Any:
            """Delegate all attribute access to unified orchestrator."""
            return getattr(self._unified, name)
        
        def __repr__(self) -> str:
            return f"DeprecatedWrapper({old_class_name} → {unified_class_name})"
    
    # Set better class name for debugging
    DeprecatedWrapper.__name__ = old_class_name
    DeprecatedWrapper.__qualname__ = old_class_name
    
    return DeprecatedWrapper


# Export deprecated wrappers (these will be imported by existing code)
__all__ = [
    "get_deprecated_orchestrator_wrapper",
]


def get_deprecated_orchestrator_wrapper(old_name: str):
    """
    Get a wrapper for a deprecated orchestrator.
    
    This function maintains a registry of deprecated orchestrators and their
    replacements, enabling seamless migration.
    
    Args:
        old_name: Name of deprecated orchestrator class
    
    Returns:
        Wrapper class that delegates to unified orchestrator
    
    Raises:
        KeyError: If orchestrator not found in registry
    """
    deprecation_map = {
        # Onboarding consolidation
        "RepositoryOnboardingOrchestrator": (
            "UnifiedOnboardingOrchestrator",
            "cortex.orchestrators.support.unified_onboarding_orchestrator",
        ),
        "SetupOrchestrator": (
            "UnifiedOnboardingOrchestrator",
            "cortex.orchestrators.support.unified_onboarding_orchestrator",
        ),
        "OnboardingOrchestrator": (
            "UnifiedOnboardingOrchestrator",
            "cortex.orchestrators.support.unified_onboarding_orchestrator",
        ),
        
        # Analysis consolidation
        "LENSOrchestrator": (
            "UnifiedAnalysisOrchestrator",
            "cortex.orchestrators.support.unified_analysis_orchestrator",
        ),
        "ToolDiscoveryOrchestrator": (
            "UnifiedAnalysisOrchestrator",
            "cortex.orchestrators.support.unified_analysis_orchestrator",
        ),
        
        # Quality consolidation
        "RecommendationGate": (
            "UnifiedQualityAssuranceOrchestrator",
            "cortex.orchestrators.support.unified_quality_orchestrator",
        ),
        "ChallengeEngine": (
            "UnifiedQualityAssuranceOrchestrator",
            "cortex.orchestrators.support.unified_quality_orchestrator",
        ),
        "MetaAuditOrchestrator": (
            "UnifiedQualityAssuranceOrchestrator",
            "cortex.orchestrators.support.unified_quality_orchestrator",
        ),
        "CodeReviewOrchestrator": (
            "UnifiedQualityAssuranceOrchestrator",
            "cortex.orchestrators.support.unified_quality_orchestrator",
        ),
        "SecurityReviewEngine": (
            "UnifiedQualityAssuranceOrchestrator",
            "cortex.orchestrators.support.unified_quality_orchestrator",
        ),
        
        # Discovery consolidation
        "EducationalOrchestrator": (
            "UnifiedDiscoveryOrchestrator",
            "cortex.orchestrators.support.unified_discovery_orchestrator",
        ),
        "BusinessLanguageOrchestrator": (
            "UnifiedDiscoveryOrchestrator",
            "cortex.orchestrators.support.unified_discovery_orchestrator",
        ),
    }
    
    if old_name not in deprecation_map:
        raise KeyError(f"Unknown deprecated orchestrator: {old_name}")
    
    unified_name, unified_module = deprecation_map[old_name]
    return deprecated_import_wrapper(old_name, unified_name, unified_module)
