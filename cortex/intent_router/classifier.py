"""Intent Classifier

Author: CORTEX Framework
"""

from enum import Enum

class IntentCategory(str, Enum):
    """Intent categories."""
    QUERY = "query"
    COMMAND = "command"
    NAVIGATION = "navigation"


from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Intent classification result."""
    intent: str
    confidence: float
    category: IntentCategory = IntentCategory.QUERY


@dataclass
class IntentSignal:
    """Intent signal."""
    signal_type: str
    strength: float



class IntentClassifier:
    """Classify intents."""
    
    def classify(self, text: str) -> IntentCategory:
        """Classify intent."""
        return IntentCategory.QUERY

__all__ = ["IntentCategory", "IntentClassifier"]
