"""BDOM-001: Cost Tracking & Budget Enforcement"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from enum import Enum

class CostStatus(Enum):
    UNDER_BUDGET = "under_budget"
    WARNING = "warning"
    OVER_BUDGET = "over_budget"

@dataclass
class CostTracker:
    budget: float
    current_cost: float = 0.0
    operations: Dict[str, float] = field(default_factory=dict)
    
    def add_cost(self, op_id: str, amount: float) -> None:
        self.operations[op_id] = amount
        self.current_cost += amount
    
    def get_status(self) -> CostStatus:
        percent = (self.current_cost / self.budget * 100) if self.budget > 0 else 0
        if percent >= 100:
            return CostStatus.OVER_BUDGET
        elif percent >= 80:
            return CostStatus.WARNING
        return CostStatus.UNDER_BUDGET
    
    def get_remaining_budget(self) -> float:
        return max(0, self.budget - self.current_cost)
