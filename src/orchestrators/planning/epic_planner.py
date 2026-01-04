"""
CORTEX 5.0 Epic Planner - Multi-Plan Coordination Engine

Purpose: Manage hierarchical planning with multiple child plans, dependency validation,
         and aggregate progress tracking for strategic epic-level initiatives.

Version: 5.0.0
Author: Asif Hussain
Created: January 4, 2026

Features:
- Multi-child plan management
- Dependency validation and enforcement
- Aggregate progress calculation
- Child plan registry management
- Epic-level milestone tracking
- HTML viewer generation integration
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class PlanStatus(Enum):
    """Plan execution status."""
    NOT_STARTED = "not_started"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETE = "complete"
    FAILED = "failed"


class DependencyType(Enum):
    """Dependency relationship types."""
    BLOCKS = "blocks"       # Source must complete before target can start
    ENABLES = "enables"     # Source completion enables target
    INFORMS = "informs"     # Source provides context to target


@dataclass
class ChildPlan:
    """Represents a child plan within an epic."""
    order: str  # e.g., "00A", "01", "02"
    id: str  # kebab-case identifier
    name: str
    folder: str
    progress: float = 0.0
    phases_complete: int = 0
    total_phases: int = 0
    duration: str = ""
    status: PlanStatus = PlanStatus.NOT_STARTED
    status_emoji: str = "⏳"
    dependencies: List[str] = field(default_factory=list)
    dependency_rule: str = ""
    viewer_url: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "order": self.order,
            "id": self.id,
            "name": self.name,
            "folder": self.folder,
            "progress": self.progress,
            "phases_complete": self.phases_complete,
            "total_phases": self.total_phases,
            "duration": self.duration,
            "status": self.status.value,
            "status_emoji": self.status_emoji,
            "dependencies": self.dependencies,
            "dependency_rule": self.dependency_rule,
            "viewer_url": self.viewer_url,
            "start_date": self.start_date,
            "end_date": self.end_date
        }


@dataclass
class Milestone:
    """Epic-level milestone."""
    id: str
    name: str
    description: str
    status: str
    target_date: str
    actual_date: Optional[str] = None
    criteria: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "target_date": self.target_date,
            "actual_date": self.actual_date,
            "criteria": self.criteria
        }


@dataclass
class Dependency:
    """Inter-plan dependency relationship."""
    from_plan: str
    to_plan: str
    type: DependencyType
    description: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "from_plan": self.from_plan,
            "to_plan": self.to_plan,
            "type": self.type.value,
            "description": self.description
        }


@dataclass
class EpicProgressTracker:
    """Epic-level progress tracking data."""
    schema_version: str = "1.0"
    plan_type: str = "epic"
    plan_id: str = ""
    plan_name: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    overall_progress: float = 0.0
    total_plans: int = 0
    completed_plans: int = 0
    total_phases: int = 0
    completed_phases: int = 0
    estimated_days: int = 0
    status: PlanStatus = PlanStatus.NOT_STARTED
    child_plans: List[ChildPlan] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "plan_type": self.plan_type,
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "overall_progress": self.overall_progress,
            "total_plans": self.total_plans,
            "completed_plans": self.completed_plans,
            "total_phases": self.total_phases,
            "completed_phases": self.completed_phases,
            "estimated_days": self.estimated_days,
            "status": self.status.value,
            "child_plans": [cp.to_dict() for cp in self.child_plans],
            "milestones": [m.to_dict() for m in self.milestones],
            "dependencies": [d.to_dict() for d in self.dependencies]
        }


class DependencyValidator:
    """Validates inter-plan dependencies and detects issues."""
    
    def __init__(self, child_plans: List[ChildPlan]):
        self.child_plans = {plan.id: plan for plan in child_plans}
    
    def validate_dependencies(self, plan_id: str) -> Tuple[bool, List[str]]:
        """
        Check if all dependencies for a plan are satisfied.
        
        Args:
            plan_id: ID of plan to validate
            
        Returns:
            Tuple of (is_satisfied, list of unsatisfied dependency IDs)
        """
        plan = self.child_plans.get(plan_id)
        if not plan:
            return False, [f"Plan {plan_id} not found"]
        
        unsatisfied = []
        for dep_id in plan.dependencies:
            dep_plan = self.child_plans.get(dep_id)
            if not dep_plan:
                unsatisfied.append(f"{dep_id} (not found)")
                continue
            
            if dep_plan.status != PlanStatus.COMPLETE:
                unsatisfied.append(f"{dep_id} (status: {dep_plan.status.value})")
        
        return len(unsatisfied) == 0, unsatisfied
    
    def get_blocked_plans(self) -> List[str]:
        """Get list of plan IDs blocked by unsatisfied dependencies."""
        blocked = []
        for plan_id, plan in self.child_plans.items():
            if plan.status in [PlanStatus.NOT_STARTED, PlanStatus.BLOCKED]:
                is_satisfied, _ = self.validate_dependencies(plan_id)
                if not is_satisfied:
                    blocked.append(plan_id)
        return blocked
    
    def get_ready_plans(self) -> List[str]:
        """Get list of plan IDs ready to start (dependencies satisfied)."""
        ready = []
        for plan_id, plan in self.child_plans.items():
            if plan.status in [PlanStatus.NOT_STARTED, PlanStatus.BLOCKED]:
                is_satisfied, _ = self.validate_dependencies(plan_id)
                if is_satisfied:
                    ready.append(plan_id)
        return ready
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependency chains.
        
        Returns:
            List of circular dependency chains (each chain is a list of plan IDs)
        """
        def dfs(node: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
            if node in path:
                # Found cycle - return the circular portion
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            
            if node in visited:
                return None
            
            visited.add(node)
            current_path = path + [node]
            
            plan = self.child_plans.get(node)
            if plan:
                for dep in plan.dependencies:
                    cycle = dfs(dep, visited.copy(), current_path)
                    if cycle:
                        return cycle
            
            return None
        
        cycles = []
        global_visited = set()
        
        for plan_id in self.child_plans:
            if plan_id not in global_visited:
                cycle = dfs(plan_id, set(), [])
                if cycle:
                    cycles.append(cycle)
                    global_visited.update(cycle)
        
        return cycles


class ProgressCalculator:
    """Calculates aggregate progress across child plans."""
    
    @staticmethod
    def calculate_overall_progress(child_plans: List[ChildPlan]) -> float:
        """
        Calculate weighted overall progress.
        
        Uses simple average - all plans weighted equally.
        Could be enhanced to weight by duration/complexity.
        """
        if not child_plans:
            return 0.0
        
        total_progress = sum(plan.progress for plan in child_plans)
        return round(total_progress / len(child_plans), 1)
    
    @staticmethod
    def calculate_phase_totals(child_plans: List[ChildPlan]) -> Tuple[int, int]:
        """
        Calculate total and completed phases across all child plans.
        
        Returns:
            Tuple of (total_phases, completed_phases)
        """
        total = sum(plan.total_phases for plan in child_plans)
        completed = sum(plan.phases_complete for plan in child_plans)
        return total, completed
    
    @staticmethod
    def calculate_completion_count(child_plans: List[ChildPlan]) -> int:
        """Count number of completed child plans."""
        return sum(
            1 for plan in child_plans 
            if plan.status == PlanStatus.COMPLETE
        )
    
    @staticmethod
    def determine_epic_status(child_plans: List[ChildPlan]) -> PlanStatus:
        """Determine overall epic status based on child plan states."""
        if not child_plans:
            return PlanStatus.NOT_STARTED
        
        statuses = [plan.status for plan in child_plans]
        
        # If any failed, epic is failed
        if PlanStatus.FAILED in statuses:
            return PlanStatus.FAILED
        
        # If all complete, epic is complete
        if all(s == PlanStatus.COMPLETE for s in statuses):
            return PlanStatus.COMPLETE
        
        # If any in progress, epic is in progress
        if PlanStatus.IN_PROGRESS in statuses:
            return PlanStatus.IN_PROGRESS
        
        # If any paused (and none in progress), epic is paused
        if PlanStatus.PAUSED in statuses:
            return PlanStatus.PAUSED
        
        # If all blocked or not started, check if any can start
        validator = DependencyValidator(child_plans)
        ready_plans = validator.get_ready_plans()
        if ready_plans:
            return PlanStatus.NOT_STARTED  # Ready to start
        
        return PlanStatus.BLOCKED


class EpicPlanner:
    """
    Epic-level planner managing multiple coordinated child plans.
    
    Responsibilities:
    - Child plan registry management
    - Dependency validation and enforcement
    - Aggregate progress tracking
    - Epic-level milestone management
    - Integration with HTML viewer generation
    """
    
    def __init__(self, epic_path: Path):
        """
        Initialize epic planner.
        
        Args:
            epic_path: Path to epic root directory
        """
        self.epic_path = epic_path
        self.tracking_dir = epic_path / "tracking"
        self.tracker_file = self.tracking_dir / "epic-progress-tracker.json"
        self.registry_file = self.tracking_dir / "child-plan-registry.json"
        self.dependency_file = self.tracking_dir / "dependency-graph.json"
        
        # Create tracking directory if needed
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing tracker or create new
        self.tracker = self._load_or_create_tracker()
    
    def _load_or_create_tracker(self) -> EpicProgressTracker:
        """Load existing progress tracker or create new one."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file) as f:
                    data = json.load(f)
                return self._deserialize_tracker(data)
            except Exception as e:
                logger.error(f"Failed to load tracker: {e}")
                return EpicProgressTracker()
        else:
            return EpicProgressTracker()
    
    def _deserialize_tracker(self, data: Dict) -> EpicProgressTracker:
        """Deserialize JSON data to EpicProgressTracker."""
        # Deserialize child plans
        child_plans = []
        for cp_data in data.get("child_plans", []):
            child_plan = ChildPlan(
                order=cp_data["order"],
                id=cp_data["id"],
                name=cp_data["name"],
                folder=cp_data["folder"],
                progress=cp_data.get("progress", 0.0),
                phases_complete=cp_data.get("phases_complete", 0),
                total_phases=cp_data.get("total_phases", 0),
                duration=cp_data.get("duration", ""),
                status=PlanStatus(cp_data.get("status", "not_started")),
                status_emoji=cp_data.get("status_emoji", "⏳"),
                dependencies=cp_data.get("dependencies", []),
                dependency_rule=cp_data.get("dependency_rule", ""),
                viewer_url=cp_data.get("viewer_url", ""),
                start_date=cp_data.get("start_date"),
                end_date=cp_data.get("end_date")
            )
            child_plans.append(child_plan)
        
        # Deserialize milestones
        milestones = []
        for m_data in data.get("milestones", []):
            milestone = Milestone(
                id=m_data["id"],
                name=m_data["name"],
                description=m_data.get("description", ""),
                status=m_data.get("status", "not_started"),
                target_date=m_data.get("target_date", ""),
                actual_date=m_data.get("actual_date"),
                criteria=m_data.get("criteria", "")
            )
            milestones.append(milestone)
        
        # Deserialize dependencies
        dependencies = []
        for d_data in data.get("dependencies", []):
            dependency = Dependency(
                from_plan=d_data["from_plan"],
                to_plan=d_data["to_plan"],
                type=DependencyType(d_data["type"]),
                description=d_data.get("description", "")
            )
            dependencies.append(dependency)
        
        return EpicProgressTracker(
            schema_version=data.get("schema_version", "1.0"),
            plan_type=data.get("plan_type", "epic"),
            plan_id=data.get("plan_id", ""),
            plan_name=data.get("plan_name", ""),
            created_date=data.get("created_date", ""),
            last_updated=data.get("last_updated", ""),
            overall_progress=data.get("overall_progress", 0.0),
            total_plans=data.get("total_plans", 0),
            completed_plans=data.get("completed_plans", 0),
            total_phases=data.get("total_phases", 0),
            completed_phases=data.get("completed_phases", 0),
            estimated_days=data.get("estimated_days", 0),
            status=PlanStatus(data.get("status", "not_started")),
            child_plans=child_plans,
            milestones=milestones,
            dependencies=dependencies
        )
    
    def save_tracker(self) -> None:
        """Save progress tracker to disk."""
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(self.tracker.to_dict(), f, indent=2)
            logger.info(f"Saved epic tracker: {self.tracker_file}")
        except Exception as e:
            logger.error(f"Failed to save tracker: {e}")
            raise
    
    def add_child_plan(self, child_plan: ChildPlan) -> None:
        """
        Add a child plan to the epic.
        
        Args:
            child_plan: ChildPlan instance to add
        """
        # Check for duplicate order
        existing_orders = [cp.order for cp in self.tracker.child_plans]
        if child_plan.order in existing_orders:
            raise ValueError(f"Child plan with order {child_plan.order} already exists")
        
        # Check for duplicate ID
        existing_ids = [cp.id for cp in self.tracker.child_plans]
        if child_plan.id in existing_ids:
            raise ValueError(f"Child plan with ID {child_plan.id} already exists")
        
        self.tracker.child_plans.append(child_plan)
        self.tracker.total_plans = len(self.tracker.child_plans)
        self._recalculate_progress()
        logger.info(f"Added child plan: {child_plan.id} ({child_plan.order})")
    
    def update_child_plan_progress(
        self, 
        plan_id: str, 
        progress: float,
        phases_complete: Optional[int] = None
    ) -> None:
        """
        Update progress for a child plan.
        
        Args:
            plan_id: ID of child plan to update
            progress: New progress percentage (0-100)
            phases_complete: Optional number of completed phases
        """
        plan = self._get_child_plan(plan_id)
        if not plan:
            raise ValueError(f"Child plan {plan_id} not found")
        
        plan.progress = max(0.0, min(100.0, progress))
        
        if phases_complete is not None:
            plan.phases_complete = phases_complete
        
        # Update status based on progress
        if plan.progress == 0:
            plan.status = PlanStatus.NOT_STARTED
            plan.status_emoji = "⏳"
        elif plan.progress == 100:
            plan.status = PlanStatus.COMPLETE
            plan.status_emoji = "✅"
            plan.end_date = datetime.now().isoformat()
        elif plan.status == PlanStatus.NOT_STARTED:
            plan.status = PlanStatus.IN_PROGRESS
            plan.status_emoji = "🔄"
            if not plan.start_date:
                plan.start_date = datetime.now().isoformat()
        
        self._recalculate_progress()
        self._update_blocked_plans()
        logger.info(f"Updated {plan_id} progress: {progress}%")
    
    def _get_child_plan(self, plan_id: str) -> Optional[ChildPlan]:
        """Get child plan by ID."""
        for plan in self.tracker.child_plans:
            if plan.id == plan_id:
                return plan
        return None
    
    def _recalculate_progress(self) -> None:
        """Recalculate aggregate progress metrics."""
        calculator = ProgressCalculator()
        
        # Overall progress
        self.tracker.overall_progress = calculator.calculate_overall_progress(
            self.tracker.child_plans
        )
        
        # Phase totals
        total_phases, completed_phases = calculator.calculate_phase_totals(
            self.tracker.child_plans
        )
        self.tracker.total_phases = total_phases
        self.tracker.completed_phases = completed_phases
        
        # Completion count
        self.tracker.completed_plans = calculator.calculate_completion_count(
            self.tracker.child_plans
        )
        
        # Epic status
        self.tracker.status = calculator.determine_epic_status(
            self.tracker.child_plans
        )
        
        # Update timestamp
        self.tracker.last_updated = datetime.now().isoformat()
    
    def _update_blocked_plans(self) -> None:
        """Update status of plans blocked by dependencies."""
        validator = DependencyValidator(self.tracker.child_plans)
        
        # Get plans that are ready to start
        ready_plan_ids = validator.get_ready_plans()
        
        # Update blocked plans to not_started if dependencies now satisfied
        for plan in self.tracker.child_plans:
            if plan.status == PlanStatus.BLOCKED and plan.id in ready_plan_ids:
                plan.status = PlanStatus.NOT_STARTED
                plan.status_emoji = "⏳"
                logger.info(f"Unblocked plan: {plan.id}")
            elif plan.status == PlanStatus.NOT_STARTED and plan.id not in ready_plan_ids:
                is_satisfied, unsatisfied = validator.validate_dependencies(plan.id)
                if not is_satisfied and plan.dependencies:
                    plan.status = PlanStatus.BLOCKED
                    plan.status_emoji = "🔒"
                    logger.info(f"Blocked plan: {plan.id} (waiting on: {unsatisfied})")
    
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Validate all dependencies in the epic.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        validator = DependencyValidator(self.tracker.child_plans)
        
        errors = []
        
        # Check for circular dependencies
        cycles = validator.detect_circular_dependencies()
        if cycles:
            for cycle in cycles:
                errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
        
        # Check for missing dependencies
        for plan in self.tracker.child_plans:
            for dep_id in plan.dependencies:
                if not self._get_child_plan(dep_id):
                    errors.append(
                        f"Plan {plan.id} depends on non-existent plan: {dep_id}"
                    )
        
        return len(errors) == 0, errors
    
    def get_next_available_plans(self) -> List[ChildPlan]:
        """
        Get child plans that are ready to start.
        
        Returns:
            List of ChildPlan instances with satisfied dependencies
        """
        validator = DependencyValidator(self.tracker.child_plans)
        ready_ids = validator.get_ready_plans()
        
        return [
            plan for plan in self.tracker.child_plans 
            if plan.id in ready_ids
        ]
    
    def mark_plan_complete(self, plan_id: str) -> None:
        """
        Mark a child plan as complete.
        
        Args:
            plan_id: ID of plan to complete
        """
        self.update_child_plan_progress(plan_id, 100.0)
        logger.info(f"Marked plan complete: {plan_id}")


# Export public API
__all__ = [
    "EpicPlanner",
    "ChildPlan",
    "Milestone",
    "Dependency",
    "EpicProgressTracker",
    "DependencyValidator",
    "ProgressCalculator",
    "PlanStatus",
    "DependencyType"
]
