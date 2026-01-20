"""Intent Learner - Machine learning for intent recognition improvement.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class LearningExample:
    """A training example for intent learning."""
    
    input_text: str
    predicted_intent: str
    actual_intent: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """Metrics for the learning model."""
    
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    total_examples: int = 0
    correct_predictions: int = 0


class IntentLearner:
    """Learns and improves intent recognition through feedback."""
    
    def __init__(self, learning_rate: float = 0.01):
        """Initialize intent learner.
        
        Args:
            learning_rate: Learning rate for model updates
        """
        self.learning_rate = learning_rate
        self.training_examples: List[LearningExample] = []
        self.intent_patterns: Dict[str, List[str]] = {}
        self.metrics = ModelMetrics()
    
    def add_example(
        self,
        input_text: str,
        predicted_intent: str,
        actual_intent: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a training example.
        
        Args:
            input_text: The input text
            predicted_intent: What was predicted
            actual_intent: What it actually was
            confidence: Prediction confidence
            metadata: Optional metadata
        """
        example = LearningExample(
            input_text=input_text,
            predicted_intent=predicted_intent,
            actual_intent=actual_intent,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        self.training_examples.append(example)
        
        # Update intent patterns
        if actual_intent not in self.intent_patterns:
            self.intent_patterns[actual_intent] = []
        self.intent_patterns[actual_intent].append(input_text)
        
        logger.debug(f"Added learning example: {predicted_intent} -> {actual_intent}")
    
    def train(self) -> ModelMetrics:
        """Train the model on accumulated examples.
        
        Returns:
            Updated model metrics
        """
        if not self.training_examples:
            logger.warning("No training examples available")
            return self.metrics
        
        # Calculate metrics
        total = len(self.training_examples)
        correct = sum(
            1 for ex in self.training_examples 
            if ex.predicted_intent == ex.actual_intent
        )
        
        self.metrics.total_examples = total
        self.metrics.correct_predictions = correct
        self.metrics.accuracy = correct / total if total > 0 else 0.0
        
        # Simplified precision/recall calculation
        self.metrics.precision = self.metrics.accuracy
        self.metrics.recall = self.metrics.accuracy
        self.metrics.f1_score = (
            2 * (self.metrics.precision * self.metrics.recall) / 
            (self.metrics.precision + self.metrics.recall)
            if (self.metrics.precision + self.metrics.recall) > 0 else 0.0
        )
        
        logger.info(f"Training complete: accuracy={self.metrics.accuracy:.2%}")
        return self.metrics
    
    def predict(self, input_text: str) -> Tuple[str, float]:
        """Predict intent for input text.
        
        Args:
            input_text: Text to classify
            
        Returns:
            Tuple of (predicted_intent, confidence)
        """
        if not self.intent_patterns:
            return ("unknown", 0.0)
        
        # Simple pattern matching for now
        best_match = None
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                # Calculate simple similarity score
                score = self._calculate_similarity(input_text, pattern)
                if score > best_score:
                    best_score = score
                    best_match = intent
        
        return (best_match or "unknown", best_score)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_metrics(self) -> ModelMetrics:
        """Get current model metrics.
        
        Returns:
            ModelMetrics object
        """
        return self.metrics
    
    def get_intent_distribution(self) -> Dict[str, int]:
        """Get distribution of intents in training data.
        
        Returns:
            Dictionary mapping intent to count
        """
        distribution = {}
        for example in self.training_examples:
            intent = example.actual_intent
            distribution[intent] = distribution.get(intent, 0) + 1
        
        return distribution
    
    def clear_examples(self) -> None:
        """Clear all training examples."""
        self.training_examples.clear()
        logger.info("Cleared training examples")


__all__ = ["IntentLearner", "LearningExample", "ModelMetrics"]
