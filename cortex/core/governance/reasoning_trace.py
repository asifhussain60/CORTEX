"""Reasoning trace capture and analysis."""

from typing import List, Dict, Any
from datetime import datetime


class ReasoningStep:
    """Single reasoning step in trace."""
    
    def __init__(self, step_id: str, description: str, confidence: float):
        self.step_id = step_id
        self.description = description
        self.confidence = confidence  # 0.0 to 1.0
        self.timestamp = datetime.now()


class ReasoningTrace:
    """Capture and trace reasoning process."""
    
    def __init__(self):
        self.steps: List[ReasoningStep] = []
        self.execution_time_ms: float = 0.0
    
    def add_step(self, step_id: str, description: str, confidence: float = 1.0) -> None:
        """Add reasoning step."""
        step = ReasoningStep(step_id, description, confidence)
        self.steps.append(step)
    
    def get_trace(self) -> List[Dict[str, Any]]:
        """Get complete reasoning trace."""
        return [
            {
                "step_id": step.step_id,
                "description": step.description,
                "confidence": step.confidence,
                "timestamp": step.timestamp
            }
            for step in self.steps
        ]
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze reasoning trace."""
        if not self.steps:
            return {"total_steps": 0, "average_confidence": 0.0}
        
        avg_confidence = sum(s.confidence for s in self.steps) / len(self.steps)
        
        return {
            "total_steps": len(self.steps),
            "average_confidence": avg_confidence,
            "min_confidence": min(s.confidence for s in self.steps),
            "max_confidence": max(s.confidence for s in self.steps)
        }
