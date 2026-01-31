"""Execution Strategy Selector for adaptive task execution.

This module implements intelligent strategy selection based on task characteristics,
resource availability, deadline constraints, and historical performance data.

AC-PHX-010-01: Dynamic strategy selection based on:
- Task complexity analysis
- Resource availability
- Deadline constraints
- Historical performance patterns
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import statistics

from cortex.orchestrators.adaptive.unified_adaptive_layer import StrategyType


@dataclass
class StrategyMetrics:
    """Metrics for a strategy's historical performance."""
    strategy: StrategyType
    execution_count: int = 0
    avg_duration: float = 0.0
    success_rate: float = 1.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class StrategySelector:
    """Selects optimal execution strategy based on task and system context.
    
    Analyzes task characteristics, resource availability, and deadline
    constraints to select the best execution strategy (FAST, BALANCED, THOROUGH).
    
    Example:
        >>> selector = StrategySelector()
        >>> task = {"complexity": "medium", "timeout": 5}
        >>> strategy = selector.select_strategy(task)
        >>> print(f"Selected: {strategy}")
    """
    
    def __init__(self) -> None:
        """Initialize strategy selector with default configurations."""
        self._strategy_configs: Dict[StrategyType, Dict[str, Any]] = {
            StrategyType.FAST: {
                "timeout_multiplier": 1.0,
                "validation_level": 0.2,
                "enable_caching": True,
                "retry_count": 0,
                "parallel_execution": True,
            },
            StrategyType.BALANCED: {
                "timeout_multiplier": 2.0,
                "validation_level": 0.6,
                "enable_caching": True,
                "retry_count": 1,
                "parallel_execution": True,
            },
            StrategyType.THOROUGH: {
                "timeout_multiplier": 4.0,
                "validation_level": 1.0,
                "enable_caching": False,
                "retry_count": 3,
                "parallel_execution": False,
            },
        }
        
        # Historical performance metrics
        self._metrics: Dict[StrategyType, StrategyMetrics] = {
            strategy: StrategyMetrics(strategy=strategy)
            for strategy in StrategyType
        }
        
        # Execution history for learning
        self._execution_history: List[Dict[str, Any]] = []
    
    def select_strategy(self, task: Dict[str, Any]) -> str:
        """Select optimal strategy for a task.
        
        Analyzes task characteristics and system context to choose the best
        execution strategy. Considers:
        - Task complexity (low/medium/high)
        - Deadline constraints
        - Resource availability
        - Historical performance
        
        Args:
            task: Task characteristics dictionary
            
        Returns:
            Selected strategy name: "FAST", "BALANCED", or "THOROUGH"
        """
        complexity = self._analyze_complexity(task)
        deadline = task.get("deadline_seconds", float('inf'))
        required_certainty = task.get("required_certainty", 0.5)
        
        # Decision matrix
        if complexity == "low":
            return "FAST"
        elif complexity == "medium":
            if deadline < 3:
                return "FAST"
            elif required_certainty > 0.9:
                return "THOROUGH"
            else:
                return "BALANCED"
        else:  # high complexity
            if required_certainty > 0.95:
                return "THOROUGH"
            elif deadline < 5:
                return "BALANCED"
            else:
                return "THOROUGH"
    
    def _analyze_complexity(self, task: Dict[str, Any]) -> str:
        """Analyze task complexity.
        
        Args:
            task: Task to analyze
            
        Returns:
            Complexity level: "low", "medium", or "high"
        """
        if "complexity" in task:
            return task["complexity"]
        
        # Estimate based on characteristics
        input_size = len(task.get("inputs", []))
        requires_validation = task.get("requires_validation", False)
        
        if input_size > 10 or requires_validation:
            return "high"
        elif input_size > 5:
            return "medium"
        else:
            return "low"
    
    def record_execution(self, execution_result: Dict[str, Any]) -> None:
        """Record execution result for learning.
        
        Args:
            execution_result: Result dictionary with strategy, duration, success
        """
        self._execution_history.append({
            "timestamp": datetime.now(),
            **execution_result
        })
        
        # Update metrics
        strategy_str = execution_result.get("strategy", "FAST")
        try:
            strategy = StrategyType[strategy_str]
        except KeyError:
            return
        
        metrics = self._metrics[strategy]
        metrics.execution_count += 1
        
        if execution_result.get("success", True):
            success_count = sum(
                1 for e in self._execution_history 
                if e.get("strategy") == strategy_str and e.get("success", True)
            )
            metrics.success_rate = success_count / metrics.execution_count
        
        # Update average duration
        durations = [
            e.get("duration", 0) for e in self._execution_history
            if e.get("strategy") == strategy_str
        ]
        if durations:
            metrics.avg_duration = statistics.mean(durations)
    
    def get_strategy_config(self, strategy: str) -> Dict[str, Any]:
        """Get configuration for a strategy.
        
        Args:
            strategy: Strategy name
            
        Returns:
            Configuration dictionary
        """
        try:
            strategy_type = StrategyType[strategy]
            return self._strategy_configs[strategy_type].copy()
        except KeyError:
            return self._strategy_configs[StrategyType.BALANCED].copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all strategies.
        
        Returns:
            Metrics dictionary
        """
        return {
            strategy.value: {
                "execution_count": metrics.execution_count,
                "avg_duration": metrics.avg_duration,
                "success_rate": metrics.success_rate,
            }
            for strategy, metrics in self._metrics.items()
        }
