"""Capacity Planning Orchestrators - Phase 12 Implementation.

CAP-3: Skill Allocator - Task classification and team composition
CAP-4: Output Formatter - Sprint breakdowns and Gantt visualization
CAP-5: Learning Orchestrator - Accuracy tracking and model tuning
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class TaskComplexityLevel(Enum):
    """Task complexity levels for skill matching."""
    TRIVIAL = 1          # Doc changes, config updates
    SIMPLE = 2           # Single file, straightforward logic
    MEDIUM = 3           # Multi-file, moderate dependencies
    COMPLEX = 4          # Significant refactoring, many impacts
    VERY_COMPLEX = 5     # System-wide, high uncertainty


class SkillRequirement(Enum):
    """Skill requirements for tasks."""
    JUNIOR_READY = 1     # Any skill level
    MENTORED = 2         # Needs mid-level+ oversight
    MID_LEVEL = 3        # Requires mid-level minimum
    SENIOR = 4           # Requires senior minimum
    ARCHITECT = 5        # Requires architect


@dataclass
class TaskClassification:
    """Task classification for skill allocation.
    
    Attributes:
        task_id: Task identifier
        complexity_level: Task complexity
        skill_requirement: Minimum skill needed
        estimated_hours: Estimated effort
        parallelizable: Can be split among team members
    """
    task_id: str
    complexity_level: TaskComplexityLevel
    skill_requirement: SkillRequirement
    estimated_hours: float
    parallelizable: bool = False


@dataclass
class AllocationPlan:
    """Team allocation plan for tasks.
    
    Attributes:
        tasks: List of task allocations
        total_hours: Total project hours
        team_composition: Team member details
        risk_mitigation: Risk mitigation strategies
    """
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    total_hours: float = 0.0
    team_composition: Dict[str, Any] = field(default_factory=dict)
    risk_mitigation: List[str] = field(default_factory=list)


class SkillAllocator:
    """Phase 12 CAP-3: Skill Allocator.
    
    Classifies tasks and allocates to appropriate team members.
    Applies Brooks' Law: Adding people to late projects makes them later.
    
    Task Classification:
    - Complexity: 1-5 scale
    - Skill requirement: Based on complexity + domain
    - Parallelizability: Can split work
    
    Team Allocation:
    - Match skill to requirement
    - Balance workload
    - Account for ramp-up time
    - Apply Brooks' Law constraints
    
    AC-CAP-3-01: Classify tasks by complexity (1-5)
    AC-CAP-3-02: Match tasks to team skill levels
    AC-CAP-3-03: Account for parallelization limits (Brooks' Law)
    AC-CAP-3-04: Generate allocation plan
    """
    
    @staticmethod
    def classify_task(
        task_id: str,
        description: str,
        estimated_hours: float,
        file_count: int
    ) -> TaskClassification:
        """Classify task by complexity.
        
        Args:
            task_id: Task identifier
            description: Task description
            estimated_hours: Estimated hours
            file_count: Number of files affected
            
        Returns:
            TaskClassification
        """
        # Determine complexity level
        if estimated_hours < 2 and file_count <= 1:
            complexity = TaskComplexityLevel.TRIVIAL
            skill_req = SkillRequirement.JUNIOR_READY
        elif estimated_hours < 8 and file_count <= 3:
            complexity = TaskComplexityLevel.SIMPLE
            skill_req = SkillRequirement.JUNIOR_READY
        elif estimated_hours < 20 and file_count <= 10:
            complexity = TaskComplexityLevel.MEDIUM
            skill_req = SkillRequirement.MID_LEVEL
        elif estimated_hours < 40 and file_count <= 30:
            complexity = TaskComplexityLevel.COMPLEX
            skill_req = SkillRequirement.SENIOR
        else:
            complexity = TaskComplexityLevel.VERY_COMPLEX
            skill_req = SkillRequirement.ARCHITECT
        
        # Parallelizable if multiple files and medium+ complexity
        parallelizable = file_count > 3 and complexity.value >= 3
        
        return TaskClassification(
            task_id=task_id,
            complexity_level=complexity,
            skill_requirement=skill_req,
            estimated_hours=estimated_hours,
            parallelizable=parallelizable,
        )
    
    @staticmethod
    def apply_brooks_law(
        team_size: int,
        task_count: int,
        available_hours: float,
        required_hours: float
    ) -> Tuple[bool, float]:
        """Apply Brooks' Law to assess feasibility.
        
        Brooks' Law: Adding people to late project makes it later.
        Communication overhead: n*(n-1)/2 channels where n = team size.
        
        Args:
            team_size: Number of team members
            task_count: Number of parallel tasks
            available_hours: Total person-hours available
            required_hours: Total hours needed
            
        Returns:
            (feasible, communication_overhead_hours)
        """
        if task_count == 0:
            return (False, 0.0)
        
        # Communication channels
        channels = team_size * (team_size - 1) / 2 if team_size > 1 else 0
        
        # Estimate communication overhead: 5% per channel per day (assuming 5-day sprint)
        communication_overhead = channels * (required_hours / task_count) * 0.05
        
        # Feasibility check
        total_with_overhead = required_hours + communication_overhead
        feasible = available_hours >= total_with_overhead
        
        return (feasible, communication_overhead)
    
    def generate_allocation_plan(
        self,
        tasks: List[TaskClassification],
        team_members: Dict[str, Dict[str, Any]]
    ) -> AllocationPlan:
        """Generate team allocation plan.
        
        Phase 12 AC-CAP-3-04: Generate allocation plan
        
        Args:
            tasks: List of task classifications
            team_members: Dict of {member_id: {skill_level, availability}}
            
        Returns:
            AllocationPlan
        """
        plan = AllocationPlan()
        
        # Sort tasks by complexity (descending)
        sorted_tasks = sorted(tasks, key=lambda t: t.complexity_level.value, reverse=True)
        
        # Allocate tasks to team members
        member_workload = {mid: 0.0 for mid in team_members}
        
        for task in sorted_tasks:
            # Find best-matched team member with lowest workload
            best_member = None
            min_workload = float('inf')
            
            for member_id, member_info in team_members.items():
                skill_level = member_info.get("skill_level", 1)
                availability = member_info.get("availability_hours", 0)
                
                # Skip if not enough availability
                if member_workload[member_id] + task.estimated_hours > availability:
                    continue
                
                # Skip if skill level insufficient
                if skill_level < task.skill_requirement.value:
                    continue
                
                # Prefer member with lowest workload
                if member_workload[member_id] < min_workload:
                    best_member = member_id
                    min_workload = member_workload[member_id]
            
            if best_member:
                member_workload[best_member] += task.estimated_hours
                plan.tasks.append({
                    "task_id": task.task_id,
                    "assigned_to": best_member,
                    "hours": task.estimated_hours,
                    "complexity": task.complexity_level.value,
                })
        
        plan.total_hours = sum(task.estimated_hours for task in tasks)
        plan.team_composition = {
            mid: {
                "allocated_hours": member_workload[mid],
                "utilization": member_workload[mid] / team_members[mid].get("availability_hours", 1),
            }
            for mid in team_members
        }
        
        return plan


class OutputFormatter:
    """Phase 12 CAP-4: Output Formatter.
    
    Generates delivery formats:
    - Sprint breakdown with daily estimates
    - Gantt chart representation
    - Risk mitigation timeline
    - Team communication artifacts
    
    AC-CAP-4-01: Generate sprint breakdowns
    AC-CAP-4-02: Produce Gantt chart data
    AC-CAP-4-03: Include risk timeline
    AC-CAP-4-04: Create communication artifacts
    """
    
    @staticmethod
    def generate_sprint_breakdown(
        plan: AllocationPlan,
        sprint_days: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate sprint breakdown with daily estimates.
        
        Phase 12 AC-CAP-4-01: Generate sprint breakdowns
        
        Args:
            plan: Allocation plan
            sprint_days: Days per sprint
            
        Returns:
            List of daily sprint tasks
        """
        sprint_breakdown = []
        
        daily_hours = plan.total_hours / sprint_days if sprint_days > 0 else 0
        
        for day in range(1, sprint_days + 1):
            sprint_breakdown.append({
                "day": day,
                "estimated_hours": daily_hours,
                "tasks_to_complete": len(plan.tasks) // sprint_days,
                "focus_areas": "Development" if day % 2 == 0 else "Testing & Review",
            })
        
        return sprint_breakdown
    
    @staticmethod
    def generate_gantt_chart(plan: AllocationPlan) -> Dict[str, Any]:
        """Generate Gantt chart data.
        
        Phase 12 AC-CAP-4-02: Produce Gantt chart data
        
        Args:
            plan: Allocation plan
            
        Returns:
            Gantt chart data structure
        """
        # Calculate timeline
        current_date = datetime.utcnow()
        end_date = current_date + timedelta(hours=plan.total_hours)
        
        return {
            "project": "Capacity Plan",
            "start_date": current_date.isoformat(),
            "end_date": end_date.isoformat(),
            "tasks": plan.tasks,
            "team": list(plan.team_composition.keys()),
            "duration_days": (end_date - current_date).days,
        }
    
    @staticmethod
    def generate_communication_summary(plan: AllocationPlan) -> Dict[str, Any]:
        """Generate summary for stakeholder communication.
        
        Phase 12 AC-CAP-4-04: Create communication artifacts
        
        Args:
            plan: Allocation plan
            
        Returns:
            Communication summary
        """
        return {
            "total_effort": f"{plan.total_hours:.1f} hours",
            "team_size": len(plan.team_composition),
            "task_count": len(plan.tasks),
            "average_utilization": sum(
                tc["utilization"] for tc in plan.team_composition.values()
            ) / len(plan.team_composition) if plan.team_composition else 0,
        }


@dataclass
class LearningRecord:
    """Record of estimation vs actual for learning.
    
    Attributes:
        task_id: Task identifier
        estimated_hours: Estimated hours
        actual_hours: Actual hours spent
        task_type: Type of task
        team_member: Team member who worked on it
        recorded_date: Date recorded
    """
    task_id: str
    estimated_hours: float
    actual_hours: float
    task_type: str = ""
    team_member: str = ""
    recorded_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class LearningOrchestrator:
    """Phase 12 CAP-5: Learning Orchestrator.
    
    Tracks estimation accuracy and tunes models.
    Calculates MAPE (Mean Absolute Percentage Error).
    Updates model parameters based on historical data.
    
    Metrics:
    - MAPE <20%: Good estimates
    - MAPE 20-50%: Acceptable estimates
    - MAPE >50%: Poor estimates, model needs tuning
    
    AC-CAP-5-01: Record actual effort vs estimates
    AC-CAP-5-02: Calculate MAPE metrics
    AC-CAP-5-03: Identify estimation biases
    AC-CAP-5-04: Recommend model adjustments
    """
    
    def __init__(self):
        """Initialize LearningOrchestrator."""
        self.learning_records: List[LearningRecord] = []
    
    def record_actual_effort(self, record: LearningRecord) -> None:
        """Record actual effort for task.
        
        Phase 12 AC-CAP-5-01: Record actual effort
        
        Args:
            record: Learning record
        """
        self.learning_records.append(record)
        logger.info(f"Recorded effort for {record.task_id}: {record.actual_hours}h actual vs {record.estimated_hours}h estimated")
    
    def calculate_mape(self) -> float:
        """Calculate Mean Absolute Percentage Error.
        
        Phase 12 AC-CAP-5-02: Calculate MAPE metrics
        
        Formula: MAPE = mean(|actual - estimated| / actual) * 100
        
        Returns:
            MAPE percentage
        """
        if not self.learning_records:
            return 0.0
        
        errors = []
        for record in self.learning_records:
            if record.actual_hours > 0:
                error = abs(record.actual_hours - record.estimated_hours) / record.actual_hours
                errors.append(error)
        
        if not errors:
            return 0.0
        
        mape = (sum(errors) / len(errors)) * 100
        return mape
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get learning metrics.
        
        Returns:
            Metrics dictionary
        """
        mape = self.calculate_mape()
        
        return {
            "records_collected": len(self.learning_records),
            "mape": f"{mape:.2f}%",
            "accuracy_level": (
                "Good" if mape < 20 else
                "Acceptable" if mape < 50 else
                "Poor"
            ),
        }


if __name__ == "__main__":
    logger.info("Capacity Planning Orchestrators - Phase 12 CAP-3,4,5")
