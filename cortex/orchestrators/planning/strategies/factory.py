"""
Wave 8 Stage 1: Strategy Factory and Composition Utilities (REFACTOR Phase)

Provides factory pattern and composition utilities for easy strategy instantiation and reuse.
Extracted from implementation patterns during GREEN phase.

AC_START: AC-WAVE8-STAGE1-REFACTOR-001
Authority: Wave 8 Execution Activation
Compliance: CORE-035 (Single canonical implementation), CORE-008 (TDD)
"""

from __future__ import annotations

from typing import Dict, Type, Optional, Any
from .base import ExecutionStrategy, ExecutionContext, ExecutionResult
from .phase import PhaseExecutionStrategy
from .wave import WaveOrchestrationStrategy
from .track import TrackParallelizationStrategy


class StrategyFactory:
    """
    Factory for creating execution strategies.
    
    AC_START: AC-WAVE8-STAGE1-REFACTOR-002
    Enables easy instantiation and composition of strategies.
    """

    _strategies: Dict[str, Type[ExecutionStrategy]] = {
        "phase": PhaseExecutionStrategy,
        "wave": WaveOrchestrationStrategy,
        "track": TrackParallelizationStrategy,
    }

    @classmethod
    def create(cls, strategy_type: str, **kwargs) -> ExecutionStrategy:
        """
        Create a strategy instance by type.
        
        Args:
            strategy_type: One of "phase", "wave", or "track"
            **kwargs: Strategy-specific initialization arguments
            
        Returns:
            ExecutionStrategy instance
            
        Raises:
            ValueError: If strategy_type is unknown
        """
        if strategy_type not in cls._strategies:
            raise ValueError(
                f"Unknown strategy type: {strategy_type}. "
                f"Valid types: {list(cls._strategies.keys())}"
            )
        
        strategy_class = cls._strategies[strategy_type]
        return strategy_class()

    @classmethod
    def register(cls, strategy_type: str, strategy_class: Type[ExecutionStrategy]) -> None:
        """
        Register a custom strategy type.
        
        AC_START: AC-WAVE8-STAGE1-REFACTOR-003
        """
        if not issubclass(strategy_class, ExecutionStrategy):
            raise TypeError(
                f"{strategy_class} must be a subclass of ExecutionStrategy"
            )
        cls._strategies[strategy_type] = strategy_class

    @classmethod
    def get_available_types(cls) -> list[str]:
        """Get list of available strategy types."""
        return list(cls._strategies.keys())

    # AC_COMPLETE: AC-WAVE8-STAGE1-REFACTOR-002, AC-WAVE8-STAGE1-REFACTOR-003


class StrategyComposer:
    """
    Composes multiple strategies for hierarchical execution.
    
    AC_START: AC-WAVE8-STAGE1-REFACTOR-004
    Enables Track → Wave → Phase hierarchy composition.
    
    Example:
        >>> composer = StrategyComposer()
        >>> composer.add_strategy("phase", PhaseExecutionStrategy())
        >>> composer.add_strategy("wave", WaveOrchestrationStrategy())
        >>> composer.add_strategy("track", TrackParallelizationStrategy())
        >>> result = composer.execute_hierarchy(context)
    """

    def __init__(self):
        """Initialize composer with empty strategy hierarchy."""
        self._strategies: Dict[str, ExecutionStrategy] = {}
        self._execution_order: list[tuple[int, str]] = []

    def add_strategy(
        self, strategy_type: str, strategy: ExecutionStrategy, order: int = 0
    ) -> StrategyComposer:
        """
        Add strategy to composition.
        
        Args:
            strategy_type: Strategy identifier (e.g., "phase", "wave", "track")
            strategy: ExecutionStrategy instance
            order: Execution order (lower = earlier)
            
        Returns:
            Self for chaining
        """
        self._strategies[strategy_type] = strategy
        self._execution_order.append((order, strategy_type))
        self._execution_order.sort(key=lambda x: x[0])
        return self

    def execute_hierarchy(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute strategies in hierarchy.
        
        AC_START: AC-WAVE8-STAGE1-REFACTOR-005
        Top-level strategy delegates to lower-level strategies.
        """
        if not self._strategies:
            return ExecutionResult(
                success=False,
                error="No strategies registered"
            )

        # Execute in reverse order (top-down: Track→Wave→Phase)
        for _order, strategy_type in reversed(self._execution_order):
            strategy = self._strategies[strategy_type]
            result = strategy.execute(context)
            if not result.success:
                return result

        return ExecutionResult(
            success=True,
            message="Hierarchy execution complete"
        )

    # AC_COMPLETE: AC-WAVE8-STAGE1-REFACTOR-004, AC-WAVE8-STAGE1-REFACTOR-005


class MetricsCollector:
    """
    Collects metrics from all strategies in composition.
    
    AC_START: AC-WAVE8-STAGE1-REFACTOR-006
    Aggregates metrics for observability and optimization.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._metrics: Dict[str, Dict[str, Any]] = {}

    def collect_from_strategy(
        self, strategy_type: str, strategy: ExecutionStrategy
    ) -> None:
        """
        Collect metrics from strategy.
        
        Args:
            strategy_type: Strategy identifier
            strategy: ExecutionStrategy instance
        """
        metrics = strategy.get_metrics()
        log = strategy.get_execution_log()

        self._metrics[strategy_type] = {
            "metrics": metrics,
            "execution_log": log,
            "event_count": len(log),
        }

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all collected strategies.
        
        AC_START: AC-WAVE8-STAGE1-REFACTOR-007
        """
        return {
            "strategies": self._metrics,
            "total_events": sum(
                m.get("event_count", 0) for m in self._metrics.values()
            ),
        }

    # AC_COMPLETE: AC-WAVE8-STAGE1-REFACTOR-006, AC-WAVE8-STAGE1-REFACTOR-007


# AC_COMPLETE: AC-WAVE8-STAGE1-REFACTOR-001
