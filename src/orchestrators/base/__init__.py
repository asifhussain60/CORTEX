"""
CORTEX 4.0 Base Orchestrator Framework

Provides base classes for all CORTEX orchestrators with standardized:
- Initialization and configuration
- Phase management and transitions
- Error handling and recovery
- Brain tier integration
- Template rendering
- Logging and metrics

All CORTEX 4.0 orchestrators must inherit from BaseOrchestrator.
"""

from .base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
    ValidationResult,
    ErrorResult
)
from .phase_manager import (
    PhaseManager,
    PhaseResult,
    PhaseStatus,
    PhaseTransition,
    RecoveryStrategy
)
from .error_handler import (
    OrchestratorErrorHandler,
    OrchestratorError,
    PhaseError,
    ConfigurationError,
    ErrorSeverity,
    ErrorCategory,
    Error,
    ErrorContext
)

__all__ = [
    # Base classes
    "BaseOrchestrator",
    "PhaseManager",
    "OrchestratorErrorHandler",
    
    # Result types
    "OrchestratorResult",
    "OrchestratorStatus",
    "PhaseResult",
    "PhaseStatus",
    "ValidationResult",
    "ErrorResult",
    "PhaseTransition",
    "RecoveryStrategy",
    
    # Error types
    "OrchestratorError",
    "PhaseError",
    "ConfigurationError",
    "ErrorSeverity",
    "ErrorCategory",
    "Error",
    "ErrorContext",
]

__version__ = "4.0.0"
