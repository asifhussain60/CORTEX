"""
Health Score Calculator

Calculates overall health scores from category scores using weighted averaging.
Determines health status classification (healthy/warning/critical).
"""

from typing import Dict, Optional


class HealthScoreCalculator:
    """Calculator for project health scores and status determination."""
    
    # Default category weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "code_quality": 0.30,
        "security": 0.30,
        "tests": 0.25,
        "documentation": 0.15
    }
    
    # Status thresholds
    HEALTHY_THRESHOLD = 80
    WARNING_THRESHOLD = 50
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize health score calculator.
        
        Args:
            weights: Optional custom category weights (must sum to 1.0)
                    If None, uses DEFAULT_WEIGHTS
        
        Raises:
            ValueError: If weights don't sum to 1.0
        """
        self.weights = weights if weights is not None else self.DEFAULT_WEIGHTS.copy()
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point error
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
    
    def calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """
        Calculate weighted average overall health score.
        
        Args:
            category_scores: Dictionary of category names to scores (0-100)
        
        Returns:
            Overall health score (0-100)
        
        Raises:
            KeyError: If required category is missing from scores
        """
        total_score = 0.0
        
        for category, weight in self.weights.items():
            score = category_scores[category]  # Will raise KeyError if missing
            total_score += score * weight
        
        return round(total_score, 2)
    
    def determine_status(self, score: float) -> str:
        """
        Determine health status from score.
        
        Args:
            score: Health score (0-100)
        
        Returns:
            Status string: "healthy", "warning", or "critical"
        """
        if score >= self.HEALTHY_THRESHOLD:
            return "healthy"
        elif score >= self.WARNING_THRESHOLD:
            return "warning"
        else:
            return "critical"
