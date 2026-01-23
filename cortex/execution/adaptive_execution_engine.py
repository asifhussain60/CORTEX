"""
Adaptive Execution Engine - Learning-based execution strategy selection.

This module provides the core adaptive execution engine that learns from
execution patterns and automatically selects the best execution strategy.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
import statistics


class ExecutionStrategy(Enum):
    """Execution strategy options."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ASYNC = "async"


@dataclass
class ExecutionContext:
    """Context information for a single execution."""
    task_id: str
    strategy: ExecutionStrategy
    duration: float
    success: bool
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdaptiveExecutionEngine:
    """
    Adaptive execution engine that learns from execution patterns.
    
    This engine tracks execution history and adapts strategy selection
    based on observed performance patterns and success rates.
    """

    def __init__(self) -> None:
        """Initialize the adaptive execution engine."""
        self.execution_history: List[ExecutionContext] = []
        self.current_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
        self.strategy_scores: Dict[ExecutionStrategy, float] = {
            ExecutionStrategy.SEQUENTIAL: 0.5,
            ExecutionStrategy.PARALLEL: 0.3,
            ExecutionStrategy.ASYNC: 0.2,
        }

    def record_execution(self, context: ExecutionContext) -> None:
        """
        Record an execution in the history.
        
        Args:
            context: ExecutionContext containing execution details.
        """
        self.execution_history.append(context)
        self._update_strategy_scores()

    def _update_strategy_scores(self) -> None:
        """
        Update strategy scores based on recent execution history.
        
        Uses success rate and average duration to score each strategy.
        """
        if not self.execution_history:
            return

        for strategy in ExecutionStrategy:
            relevant_executions = [
                ex for ex in self.execution_history
                if ex.strategy == strategy
            ]
            
            if not relevant_executions:
                continue

            success_count = sum(1 for ex in relevant_executions if ex.success)
            success_rate = success_count / len(relevant_executions)
            avg_duration = statistics.mean(
                ex.duration for ex in relevant_executions
            )

            # Score based on success rate (70%) and speed (30%)
            speed_score = 1.0 - min(avg_duration / 10.0, 1.0)
            self.strategy_scores[strategy] = (success_rate * 0.7) + (speed_score * 0.3)

    def recommend_strategy(self) -> ExecutionStrategy:
        """
        Recommend the best execution strategy based on history.
        
        Returns:
            ExecutionStrategy with highest score.
        """
        if not self.execution_history:
            return ExecutionStrategy.SEQUENTIAL

        best_strategy: ExecutionStrategy = max(
            self.strategy_scores.items(),
            key=lambda x: x[1]
        )[0]
        self.current_strategy = best_strategy
        return best_strategy

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics from history.
        
        Returns:
            Dictionary containing execution statistics.
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "avg_duration": 0.0,
            }

        total = len(self.execution_history)
        successful = sum(1 for ex in self.execution_history if ex.success)
        failed = total - successful
        avg_duration = statistics.mean(
            ex.duration for ex in self.execution_history
        )

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "avg_duration": avg_duration,
            "success_rate": successful / total if total > 0 else 0.0,
            "strategy_scores": dict(self.strategy_scores),
        }

    def reset_history(self) -> None:
        """Clear execution history and reset strategy scores."""
        self.execution_history.clear()
        self.strategy_scores = {
            ExecutionStrategy.SEQUENTIAL: 0.5,
            ExecutionStrategy.PARALLEL: 0.3,
            ExecutionStrategy.ASYNC: 0.2,
        }
        self.current_strategy = ExecutionStrategy.SEQUENTIAL
