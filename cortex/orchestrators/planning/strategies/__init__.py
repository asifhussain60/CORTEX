"""
Wave 8 Stage 1: Planning Orchestrator Strategies

Pluggable strategies for plan execution, extracted from EnhancedPlanningOrchestrator.
Enables composition and reusable orchestration patterns.

Authority: Wave 8 Execution Activation
Compliance: CORE-035 (Single canonical implementation)
"""

from .base import (
    ExecutionStrategy,
    ExecutionContext,
    ExecutionResult,
    ValidationResult,
)
from .phase import PhaseExecutionStrategy, PhaseState
from .wave import WaveOrchestrationStrategy, WavePhaseInfo
from .track import TrackParallelizationStrategy, ResourceAllocation
from .factory import StrategyFactory, StrategyComposer, MetricsCollector

__all__ = [
    # Base classes
    "ExecutionStrategy",
    "ExecutionContext",
    "ExecutionResult",
    "ValidationResult",
    # Phase strategy
    "PhaseExecutionStrategy",
    "PhaseState",
    # Wave strategy
    "WaveOrchestrationStrategy",
    "WavePhaseInfo",
    # Track strategy
    "TrackParallelizationStrategy",
    "ResourceAllocation",
    # Factory and composition
    "StrategyFactory",
    "StrategyComposer",
    "MetricsCollector",
]
