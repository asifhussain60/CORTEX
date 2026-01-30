"""
Historical Learning System for Capacity Planning (CAP-011-013).

Tracks estimates vs actuals, calculates MAPE, and enables model improvement.

Author: Asif Hussain
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class EstimateRecord:
    """Historical estimate for a task."""
    task_id: str
    pert_estimate: float
    story_point_estimate: float
    cpm_estimate: float
    consensus_estimate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ActualRecord:
    """Actual completion data for a task."""
    task_id: str
    actual_hours: float
    team_info: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


class LearningOrchestrator:
    """
    Tracks estimate accuracy and enables continuous learning.
    
    Features:
    - Estimate audit trail: Record PERT, SP, CPM, consensus
    - Actual hours capture: Track real completion time
    - MAPE calculation: Mean Absolute Percentage Error
    - Model weight adjustment: Improve consensus over time
    
    Target: <15% MAPE for reliable production planning
    """
    
    def __init__(self):
        self._estimates: Dict[str, EstimateRecord] = {}
        self._actuals: Dict[str, ActualRecord] = {}
    
    def record_estimate(
        self,
        task_id: str,
        pert_estimate: float,
        story_point_estimate: float,
        cpm_estimate: float,
        consensus_estimate: float
    ) -> None:
        """
        Record estimates for a task.
        
        Args:
            task_id: Unique task identifier
            pert_estimate: PERT (O+4*ML+P)/6 estimate
            story_point_estimate: Story points converted to hours
            cpm_estimate: Critical path method estimate
            consensus_estimate: Weighted consensus (40-40-20)
        """
        record = EstimateRecord(
            task_id=task_id,
            pert_estimate=pert_estimate,
            story_point_estimate=story_point_estimate,
            cpm_estimate=cpm_estimate,
            consensus_estimate=consensus_estimate
        )
        self._estimates[task_id] = record
    
    def get_estimate(self, task_id: str) -> Optional[EstimateRecord]:
        """Retrieve estimate record for a task."""
        return self._estimates.get(task_id)
    
    def record_actual(
        self,
        task_id: str,
        actual_hours: float,
        team_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record actual completion hours for a task.
        
        Args:
            task_id: Unique task identifier
            actual_hours: Hours actually spent
            team_info: Optional team composition details
        """
        record = ActualRecord(
            task_id=task_id,
            actual_hours=actual_hours,
            team_info=team_info
        )
        self._actuals[task_id] = record
    
    def get_actual(self, task_id: str) -> Optional[ActualRecord]:
        """Retrieve actual record for a task."""
        return self._actuals.get(task_id)
    
    def calculate_mape(self) -> float:
        """
        Calculate Mean Absolute Percentage Error across completed tasks.
        
        Formula: MAPE = (1/n) * Σ(|actual - estimate| / actual) * 100
        
        Returns:
            MAPE percentage (0-100+)
            0% = perfect estimates
            <15% = production-ready accuracy
        """
        completed_tasks = []
        
        # Find tasks with both estimate and actual
        for task_id in self._estimates.keys():
            if task_id in self._actuals:
                estimate = self._estimates[task_id].consensus_estimate
                actual = self._actuals[task_id].actual_hours
                
                # Calculate absolute percentage error
                ape = abs(actual - estimate) / actual * 100
                completed_tasks.append(ape)
        
        if not completed_tasks:
            return 0.0
        
        # Mean APE
        mape = sum(completed_tasks) / len(completed_tasks)
        return mape
