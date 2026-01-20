"""Test for BDOM-001: Cost Tracking"""
import pytest
from src.core.governance.cost_tracking import CostTracker, CostStatus

class TestCostTracking:
    def test_create_tracker(self):
        tracker = CostTracker(budget=100.0)
        assert tracker.budget == 100.0
        assert tracker.current_cost == 0.0
    
    def test_add_cost(self):
        tracker = CostTracker(budget=100.0)
        tracker.add_cost("op1", 25.0)
        assert tracker.current_cost == 25.0
    
    def test_status_under_budget(self):
        tracker = CostTracker(budget=100.0)
        tracker.add_cost("op1", 50.0)
        assert tracker.get_status() == CostStatus.UNDER_BUDGET
    
    def test_status_warning(self):
        tracker = CostTracker(budget=100.0)
        tracker.add_cost("op1", 85.0)
        assert tracker.get_status() == CostStatus.WARNING
    
    def test_status_over_budget(self):
        tracker = CostTracker(budget=100.0)
        tracker.add_cost("op1", 110.0)
        assert tracker.get_status() == CostStatus.OVER_BUDGET
    
    def test_remaining_budget(self):
        tracker = CostTracker(budget=100.0)
        tracker.add_cost("op1", 30.0)
        assert tracker.get_remaining_budget() == 70.0
