"""
Intelligence Orchestrator - AI-powered operations for CORTEX 4.0.

Provides feature completion, runtime clarification, and multi-language refactoring.
"""

from .intelligence_orchestrator import (
    IntelligenceOrchestrator,
    create_intelligence_orchestrator,
    FeatureCompletionResult,
    ClarificationResult,
    RefactoringResult
)

__all__ = [
    'IntelligenceOrchestrator',
    'create_intelligence_orchestrator',
    'FeatureCompletionResult',
    'ClarificationResult',
    'RefactoringResult'
]
