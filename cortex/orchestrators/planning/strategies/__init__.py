"""
Wave 8 Stage 1: Planning Orchestrator Strategies

Pluggable strategies for plan execution, extracted from EnhancedPlanningOrchestrator.
Enables composition and reusable orchestration patterns.

Authority: Wave 8 Execution Activation
Compliance: CORE-035 (Single canonical implementation)
"""

from cortex.orchestrators.planning.strategies.strategy_base import (
    ExecutionStrategy,
    ExecutionContext,
    ExecutionResult,
    ValidationResult,
    ExecutionStatus,
)
from cortex.orchestrators.planning.strategies.phase import (
    PhaseExecutionStrategy,
    PhaseExecutionConfig,
)
from cortex.orchestrators.planning.strategies.wave import (
    WaveOrchestrationStrategy,
    WaveOrchestrationConfig,
)
from cortex.orchestrators.planning.strategies.track import (
    TrackParallelizationStrategy,
    TrackParallelizationConfig,
)

__all__ = [
    # Base classes
    "ExecutionStrategy",
    "ExecutionContext",
    "ExecutionResult",
    "ValidationResult",
    "ExecutionStatus",
    # Strategy implementations
    "PhaseExecutionStrategy",
    "PhaseExecutionConfig",
    "WaveOrchestrationStrategy",
    "WaveOrchestrationConfig",
    "TrackParallelizationStrategy",
    "TrackParallelizationConfig",
]

