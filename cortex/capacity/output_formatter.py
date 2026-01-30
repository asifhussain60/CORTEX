"""
Output Formatter for Capacity Planning (CAP-009).

Generates sprint breakdowns with 10-day cycles (2 weeks, excluding weekends).

Author: Asif Hussain
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Any
import math


@dataclass
class SprintDay:
    """Single day in a sprint."""
    date: date
    day_number: int  # 1-10
    allocated_hours: float = 0.0
    tasks: List[str] = field(default_factory=list)


@dataclass
class SprintBreakdown:
    """Complete sprint breakdown with task distribution."""
    sprint_length_days: int = 10
    days: List[SprintDay] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_allocated_hours: float = 0.0


class OutputFormatter:
    """
    Generate sprint breakdowns and Gantt visualizations.
    
    Sprint Cycle: 10 business days (2 weeks, Mon-Fri only)
    Capacity: 8h/day maximum (realistic sustainable pace)
    Distribution: Tasks allocated based on dependencies and parallelization
    """
    
    SPRINT_DAYS = 10  # 2 weeks of business days
    MAX_HOURS_PER_DAY = 8.0  # Sustainable work capacity
    TARGET_HOURS_PER_DAY = 4.0  # Preferred load balancing target
    
    def generate_sprint_breakdown(
        self,
        start_date: date,
        total_hours: float,
        tasks: List[Dict[str, Any]]
    ) -> SprintBreakdown:
        """
        Generate sprint breakdown with task distribution.
        
        Args:
            start_date: Sprint start date (should be Monday)
            total_hours: Total project hours
            tasks: List of task dicts with {id, hours, dependencies}
        
        Returns:
            SprintBreakdown with 10-day allocation
        """
        breakdown = SprintBreakdown()
        
        # Generate 10 business days (skip weekends)
        current_date = start_date
        day_number = 1
        
        while day_number <= self.SPRINT_DAYS:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                sprint_day = SprintDay(
                    date=current_date,
                    day_number=day_number
                )
                breakdown.days.append(sprint_day)
                day_number += 1
            
            current_date += timedelta(days=1)
        
        # Distribute tasks across days
        self._distribute_tasks(breakdown, tasks)
        
        # Calculate total allocated hours
        breakdown.total_allocated_hours = sum(day.allocated_hours for day in breakdown.days)
        
        # Check for overload (>8h/day average)
        avg_hours_per_day = total_hours / self.SPRINT_DAYS
        if avg_hours_per_day > self.MAX_HOURS_PER_DAY:
            breakdown.warnings.append(
                f"Sprint overload: {avg_hours_per_day:.1f}h/day average exceeds 8h/day sustainable capacity"
            )
        
        return breakdown
    
    def _distribute_tasks(self, breakdown: SprintBreakdown, tasks: List[Dict[str, Any]]) -> None:
        """
        Distribute tasks across sprint days respecting dependencies.
        
        Strategy:
        1. Identify tasks in dependency chains vs truly independent tasks
        2. Chained tasks: complete ASAP (8h/day) to unblock dependents
        3. Truly independent tasks: spread evenly across ALL sprint days
        4. Multiple independent tasks: run in parallel, share daily capacity
        """
        if not tasks:
            return
        
        # Build task completion mapping
        task_completion_day: Dict[str, int] = {}
        
        # Sort tasks by dependencies (topological sort)
        sorted_tasks = self._topological_sort(tasks)
        
        # Identify tasks that are part of dependency chains
        # (either they have dependencies OR other tasks depend on them)
        all_dependencies = set()
        for t in tasks:
            all_dependencies.update(t.get("dependencies", []))
        
        chained_tasks = [
            t for t in sorted_tasks 
            if t.get("dependencies") or t["id"] in all_dependencies
        ]
        independent_tasks = [
            t for t in sorted_tasks 
            if not t.get("dependencies") and t["id"] not in all_dependencies
        ]
        
        # Allocate chained tasks first (sequential execution)
        for task in chained_tasks:
            task_id = task["id"]
            task_hours = task["hours"]
            dependencies = task.get("dependencies", [])
            
            # Start after all dependencies complete
            earliest_start = 1
            for dep_id in dependencies:
                if dep_id in task_completion_day:
                    earliest_start = max(earliest_start, task_completion_day[dep_id] + 1)
            
            # Target 4h/day for better load balancing (not max 8h/day)
            days_needed = math.ceil(task_hours / self.TARGET_HOURS_PER_DAY)
            
            # Ensure we don't exceed sprint length
            if earliest_start + days_needed - 1 > self.SPRINT_DAYS:
                days_needed = self.SPRINT_DAYS - earliest_start + 1
            
            hours_per_day = task_hours / days_needed
            
            # Allocate to days
            for i in range(days_needed):
                day_index = earliest_start - 1 + i
                if day_index < len(breakdown.days):
                    breakdown.days[day_index].tasks.append(task_id)
                    breakdown.days[day_index].allocated_hours += hours_per_day
            
            # Record completion
            completion_day = earliest_start + days_needed - 1
            task_completion_day[task_id] = min(completion_day, self.SPRINT_DAYS)
        
        # Allocate independent tasks (parallel execution across all days)
        if independent_tasks:
            total_independent_hours = sum(t["hours"] for t in independent_tasks)
            hours_per_day = total_independent_hours / self.SPRINT_DAYS
            
            # Distribute each independent task across all 10 days
            for task in independent_tasks:
                task_id = task["id"]
                task_hours = task["hours"]
                
                # This task's share of the daily allocation
                task_hours_per_day = task_hours / self.SPRINT_DAYS
                
                for day_index in range(self.SPRINT_DAYS):
                    if day_index < len(breakdown.days):
                        breakdown.days[day_index].tasks.append(task_id)
                        breakdown.days[day_index].allocated_hours += task_hours_per_day
                
                task_completion_day[task_id] = self.SPRINT_DAYS
    
    def _topological_sort(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort tasks by dependencies (Kahn's algorithm).
        
        Returns tasks in execution order (dependencies first).
        """
        # Build adjacency list
        task_map = {t["id"]: t for t in tasks}
        in_degree = {t["id"]: 0 for t in tasks}
        
        for task in tasks:
            for dep in task.get("dependencies", []):
                if dep in in_degree:
                    in_degree[task["id"]] += 1
        
        # Find tasks with no dependencies
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        sorted_tasks = []
        
        while queue:
            task_id = queue.pop(0)
            sorted_tasks.append(task_map[task_id])
            
            # Reduce in-degree for dependent tasks
            for task in tasks:
                if task_id in task.get("dependencies", []):
                    in_degree[task["id"]] -= 1
                    if in_degree[task["id"]] == 0:
                        queue.append(task["id"])
        
        return sorted_tasks
