"""
Feedback Loop - Continuous improvement system for execution strategies.

This module implements the feedback mechanism that allows the adaptive
execution system to improve strategies based on actual outcomes.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cortex.execution.adaptive_execution_engine import ExecutionStrategy


@dataclass
class StrategySuggestion:
    """Suggestion for strategy improvement."""
    recommended_strategy: ExecutionStrategy
    confidence: float
    reason: str


class FeedbackLoop:
    """
    Feedback loop for continuous improvement of execution strategies.

    Records execution outcomes and uses them to suggest and validate
    strategy improvements.
    """

    def __init__(self) -> None:
        """Initialize the feedback loop."""
        self.feedback_history: List[Dict[str, Any]] = []
        self.strategy_outcomes: Dict[ExecutionStrategy, List[Dict[str, Any]]] = {
            ExecutionStrategy.SEQUENTIAL: [],
            ExecutionStrategy.PARALLEL: [],
            ExecutionStrategy.ASYNC: [],
        }

    def record_outcome(self, outcome: Dict[str, Any]) -> None:
        """
        Record an execution outcome.

        Args:
            outcome: Dictionary containing execution outcome details.
        """
        self.feedback_history.append(outcome)
        strategy = outcome.get("strategy")
        if strategy in self.strategy_outcomes:
            self.strategy_outcomes[strategy].append(outcome)

    def get_cumulative_improvement(self) -> float:
        """
        Calculate cumulative improvement over time.

        Returns:
            Cumulative improvement value (0.0 to 1.0+).
        """
        if not self.feedback_history:
            return 0.0

        total_improvement = sum(
            outcome.get("improvement", 0.0)
            for outcome in self.feedback_history
        )
        return total_improvement / max(len(self.feedback_history), 1)

    def get_strategy_suggestion(self) -> Optional[StrategySuggestion]:
        """
        Get strategy suggestion based on feedback.

        Returns:
            StrategySuggestion if enough data is available, None otherwise.
        """
        if len(self.feedback_history) < 5:
            return None

        # Calculate success rate per strategy
        strategy_scores: Dict[ExecutionStrategy, float] = {}
        for strategy, outcomes in self.strategy_outcomes.items():
            if not outcomes:
                continue

            successes = sum(
                1 for outcome in outcomes if outcome.get("success", False)
            )
            success_rate = successes / len(outcomes)
            avg_improvement = sum(
                outcome.get("improvement", 0.0) for outcome in outcomes
            ) / len(outcomes)

            strategy_scores[strategy] = (success_rate * 0.7) + (avg_improvement * 0.3)

        if not strategy_scores:
            return None

        best_strategy: ExecutionStrategy = max(
            strategy_scores.items(),
            key=lambda x: x[1]
        )[0]
        confidence = strategy_scores[best_strategy]

        # If all strategies have negative scores, recommend sequential
        if confidence < 0 and all(s < 0 for s in strategy_scores.values()):
            best_strategy = ExecutionStrategy.SEQUENTIAL
            confidence = 0.1

        reasons = {
            ExecutionStrategy.SEQUENTIAL: "High error rate detected; sequential execution recommended for reliability",
            ExecutionStrategy.PARALLEL: "Low error rate and good performance; parallel execution is safe",
            ExecutionStrategy.ASYNC: "Long operation duration detected; async execution recommended",
        }

        return StrategySuggestion(
            recommended_strategy=best_strategy,
            confidence=max(min(confidence, 1.0), 0.0),
            reason=reasons[best_strategy],
        )

    def apply_feedback(self, strategy: ExecutionStrategy, improved: bool) -> None:
        """
        Record feedback on whether a strategy change was beneficial.

        Args:
            strategy: The strategy that was evaluated.
            improved: Whether the strategy resulted in improvement.
        """
        outcome = {
            "strategy": strategy,
            "improved": improved,
            "feedback_timestamp": None,
        }
        self.feedback_history.append(outcome)

    def reset_feedback(self) -> None:
        """Reset all feedback and history."""
        self.feedback_history.clear()
        for strategy in self.strategy_outcomes:
            self.strategy_outcomes[strategy].clear()
