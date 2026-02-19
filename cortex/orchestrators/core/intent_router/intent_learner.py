"""Intent Learner - Learning and adaptation for intent classification.

Learns from feedback to improve classification accuracy over time.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import List

from cortex.intent_router.classifier import IntentCategory


@dataclass
class FeedbackEntry:
    """Feedback on an intent classification.

    Attributes:
        predicted: Predicted intent category
        actual: Actual intent category (from feedback)
        query: Original user query
        was_correct: Whether prediction was correct
    """
    predicted: IntentCategory
    actual: IntentCategory
    query: str
    was_correct: bool


class IntentLearner:
    """Learn from classification feedback.

    Records feedback on classifications and tracks accuracy over time.

    Attributes:
        feedback_log: List of feedback entries
    """

    def __init__(self):
        """Initialize learner."""
        self.feedback_log: List[FeedbackEntry] = []

    def record_feedback(
        self,
        predicted: IntentCategory,
        actual: IntentCategory,
        query: str
    ) -> None:
        """Record feedback on a classification.

        Args:
            predicted: Predicted intent category
            actual: Actual intent category
            query: Original user query
        """
        was_correct = predicted == actual
        entry = FeedbackEntry(
            predicted=predicted,
            actual=actual,
            query=query,
            was_correct=was_correct
        )
        self.feedback_log.append(entry)

    def get_accuracy(self) -> float:
        """Calculate classification accuracy.

        Returns:
            Accuracy as percentage (0.0 to 1.0)
        """
        if not self.feedback_log:
            return 0.0

        correct = sum(1 for entry in self.feedback_log if entry.was_correct)
        return correct / len(self.feedback_log)


__all__ = ["FeedbackEntry", "IntentLearner"]
