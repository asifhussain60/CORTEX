"""
Health Score Calculator - Dashboard Overview Tab

Calculates overall health scores from category metrics.
Determines status levels (healthy/warning/critical).

Author: Asif Hussain
Created: 2025-12-06
"""

from typing import Dict


class HealthScoreCalculator:
    """
    Calculates health scores using weighted averages.
    
    Weights:
        - Code Quality: 30%
        - Security: 30%
        - Tests: 25%
        - Documentation: 15%
    """
    
    WEIGHTS = {
        "code_quality": 0.30,
        "security": 0.30,
        "tests": 0.25,
        "documentation": 0.15
    }
    
    def calculate_overall_health(self, category_scores: Dict[str, float]) -> float:
        """
        Calculate weighted overall health score.
        
        Args:
            category_scores: Dictionary of category names to scores
            
        Returns:
            Overall health score (0-100)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for category, weight in self.WEIGHTS.items():
            if category in category_scores:
                total_score += category_scores[category] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return round(total_score / total_weight * (1.0 / total_weight), 1)
    
    def determine_status(self, score: float) -> str:
        """
        Determine status based on score.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            Status: "healthy", "warning", or "critical"
        """
        if score >= 80:
            return "healthy"
        elif score >= 50:
            return "warning"
        else:
            return "critical"
