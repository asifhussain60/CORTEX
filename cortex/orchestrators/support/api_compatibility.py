"""
API Compatibility Layer: Bridge Old and New Orchestrator APIs

This module provides adapter functions that bridge the old orchestrator APIs
with the new unified orchestrator APIs, enabling gradual migration without
breaking existing code.

STRATEGY:
1. Old imports continue to work (backward compat)
2. Adapter functions provide compatibility shims
3. Gradual migration: Old code → Adapter → Unified (Phase 3+)
4. No breaking changes during Phase 2-3 (until 2026-03-31)

EXAMPLE:
    # OLD API (DEPRECATED - still works):
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    orchestrator = LENSOrchestrator(repo_path="/path/to/repo")
    result = orchestrator.analyze_file(file_path)
    
    # NEW API (RECOMMENDED):
    from cortex.orchestrators.support.api_compatibility import analyze_file_via_unified
    result = analyze_file_via_unified(file_path, repo_path)
"""

from typing import Any, Dict, Optional

from cortex.orchestrators.support.orchestrator_factories import (
    get_unified_analysis_orchestrator,
    get_unified_onboarding_orchestrator,
    get_unified_quality_orchestrator,
)


# ============================================================================
# LENS Analysis API Compatibility Layer
# ============================================================================

def analyze_file_via_unified(
    file_path: str,
    repo_path: Optional[str] = None,
    analysis_type: str = "complexity",
) -> Dict[str, Any]:
    """
    Analyze a file using unified analysis orchestrator (LENS API compatibility).
    
    Args:
        file_path: Path to file to analyze
        repo_path: Optional repository root (for context)
        analysis_type: Type of analysis (complexity, security, dependencies, performance)
    
    Returns:
        Analysis result compatible with old LENS API
    
    Example:
        >>> result = analyze_file_via_unified("src/main.py")
        >>> print(f"Complexity: {result.get('complexity_score')}")
    """
    orchestrator = get_unified_analysis_orchestrator()
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except (FileNotFoundError, IOError) as e:
        return {"error": str(e), "success": False}
    
    # Perform analysis via unified orchestrator
    try:
        result = orchestrator.analyze(code, analysis_type)
        return {
            "success": True,
            "file_path": file_path,
            "analysis": result,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# Repository Onboarding API Compatibility Layer
# ============================================================================

def onboard_repository_via_unified(
    repo_path: str,
    include_profile: bool = True,
) -> Dict[str, Any]:
    """
    Onboard repository using unified onboarding orchestrator.
    
    Args:
        repo_path: Path to repository
        include_profile: Whether to generate profile
    
    Returns:
        Onboarding result compatible with old API
    
    Example:
        >>> result = onboard_repository_via_unified("/path/to/repo")
        >>> print(f"Success: {result['success']}")
    """
    orchestrator = get_unified_onboarding_orchestrator()
    
    try:
        profile = orchestrator.onboard_repository(repo_path)
        return {
            "success": True,
            "repo_path": repo_path,
            "profile": profile,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# Quality Assurance API Compatibility Layer
# ============================================================================

def check_recommendation_via_unified(
    recommendation: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Check recommendation safety using unified quality orchestrator.
    
    Args:
        recommendation: The recommendation to check
        context: Optional context about the recommendation
    
    Returns:
        Safety check result compatible with old API
    
    Example:
        >>> result = check_recommendation_via_unified("Add async support")
        >>> print(f"Safe: {result['is_safe']}")
    """
    orchestrator = get_unified_quality_orchestrator()
    
    try:
        result = orchestrator.check_recommendation_safety(
            recommendation=recommendation,
            recommendation_type=context.get("type", "enhancement") if context else "enhancement",
            affected_files=context.get("files", []) if context else [],
        )
        return {
            "success": True,
            "is_safe": result.is_safe,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


__all__ = [
    "analyze_file_via_unified",
    "onboard_repository_via_unified",
    "check_recommendation_via_unified",
]
