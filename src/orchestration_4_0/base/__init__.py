"""
Base orchestrator framework for CORTEX 4.0.

Provides:
- BaseOrchestrator: Template method pattern for all orchestrators
- PhaseManager: Phase transition and validation
- ErrorHandler: Standardized error recovery
"""

from .base_orchestrator import BaseOrchestrator
from .phase_manager import PhaseManager, Phase, PhaseTransition
from .error_handler import ErrorHandler, OrchestratorError

__all__ = [
    "BaseOrchestrator",
    "PhaseManager",
    "Phase",
    "PhaseTransition",
    "ErrorHandler",
    "OrchestratorError",
]
