"""
CORTEX Estimation Agents Package

Purpose: Sprint estimation agents for SWAGGER Entry Point Module (CORTEX 3.3.0)
Components:
- ScopeInferenceEngine: Extract scope from Planning DoR Q3/Q6
- ScopeValidator: Generate scope previews for user confirmation
- ClarificationOrchestrator: Targeted questions for low-confidence scopes
- SwaggerCrawler: Boundary-aware codebase analysis
- SwaggerEstimator: Three-point PERT estimation with confidence scoring
"""

__all__ = [
    'ScopeInferenceEngine',
    'ScopeValidator',
    'ClarificationOrchestrator',
    'SwaggerCrawler',
    'SwaggerEstimator',
    'ScopeEntities',
    'ScopeBoundary',
]
