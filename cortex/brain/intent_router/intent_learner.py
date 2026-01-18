"""AC-PHX-007-08: Intent Learning Loop"""
from typing import Dict, List, Tuple
from cortex.brain.intent_router.classifier import IntentCategory

class IntentLearner:
    """Learning loop for improving classifications."""
    
    def __init__(self) -> None:
        self.feedback_log: List[Tuple[str, IntentCategory, bool]] = []
        self.accuracy_history: List[float] = []
    
    def record_feedback(
        self,
        text: str,
        predicted: IntentCategory,
        correct: bool
    ) -> None:
        """Record user feedback."""
        self.feedback_log.append((text, predicted, correct))
    
    def get_accuracy(self) -> float:
        """Calculate accuracy from feedback."""
        if not self.feedback_log:
            return 0.0
        correct = sum(1 for _, _, c in self.feedback_log if c)
        return correct / len(self.feedback_log)
