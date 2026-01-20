"""Cost tracking and budgeting module."""

from enum import Enum
from typing import Dict, Any, List
from datetime import datetime


class CostStatus(Enum):
    """Cost tracking status."""
    WITHIN_BUDGET = "within_budget"
    NEAR_LIMIT = "near_limit"
    EXCEEDED = "exceeded"


class CostTracker:
    """Track and manage operational costs."""
    
    def __init__(self, budget_limit: float = 1000.0):
        self.budget_limit = budget_limit
        self.current_cost = 0.0
        self.cost_history: List[Dict[str, Any]] = []
    
    def log_cost(self, amount: float, operation_id: str) -> CostStatus:
        """Log a cost and check budget status."""
        self.current_cost += amount
        
        self.cost_history.append({
            "operation_id": operation_id,
            "amount": amount,
            "total": self.current_cost,
            "timestamp": datetime.now()
        })
        
        return self.get_status()
    
    def get_status(self) -> CostStatus:
        """Get current cost status."""
        if self.current_cost > self.budget_limit:
            return CostStatus.EXCEEDED
        elif self.current_cost > self.budget_limit * 0.8:
            return CostStatus.NEAR_LIMIT
        return CostStatus.WITHIN_BUDGET
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return max(0.0, self.budget_limit - self.current_cost)
