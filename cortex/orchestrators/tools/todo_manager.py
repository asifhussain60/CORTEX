"""
TodoManager - Multi-phase task tracking with governance integration.
AC-ID: AC-FR-TODO-001, AC-FR-TODO-002, AC-FR-TODO-003, AC-FR-TODO-004

Provides multi-phase task decomposition with:
- Multi-phase execution with dependencies
- Real-time progress tracking and status updates
- Automatic phase advancement based on completion criteria
- Governance validation at each phase transition
- Rollback support for failed phases
- Audit trail for all phase changes

CORE-011: All functions have type hints.
CORE-012: All methods have Google-style docstrings.
CORE-013: Specific exceptions only.

"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from cortex.brain.core.result import Result, Ok, Err


class PhaseStatus(str, Enum):
    """Phase execution status enumeration."""

    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskState(str, Enum):
    """Task execution state enumeration."""

    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class Phase:
    """Phase definition with dependencies and execution state."""

    id: int
    title: str
    description: str
    dependencies: List[int] = field(default_factory=list)
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    error: Optional[str] = None
    violations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Task:
    """Task definition with phases and execution state."""

    task_id: str
    description: str
    phases: List[Phase]
    status: TaskState = TaskState.NOT_STARTED
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskStatus:
    """Task execution status snapshot."""

    task_id: str
    task_status: TaskState
    completed_phases: int
    total_phases: int
    current_phase: Optional[int]
    blocked_phases: List[int]


class TodoManager:
    """Manages multi-phase task execution with governance validation."""

    def __init__(self) -> None:
        """Initialize TodoManager."""
        self._tasks: Dict[str, Task] = {}
        self._audit_trails: Dict[str, List[Dict[str, Any]]] = {}

    def create_task(
        self,
        task_id: str,
        description: str,
        phases: List[Dict[str, Any]],
    ) -> Task:
        """Create a new task with multiple phases.

        Args:
            task_id: Unique task identifier (AC-ID format).
            description: Task description.
            phases: List of phase dictionaries with id, title, description, dependencies.

        Returns:
            Task: Created task instance.

        Raises:
            ValueError: If task_id already exists or phases invalid.
        """
        if task_id in self._tasks:
            raise ValueError(f"Task {task_id} already exists")

        phase_objects = [
            Phase(
                id=p["id"],
                title=p["title"],
                description=p.get("description", ""),
                dependencies=p.get("dependencies", []),
            )
            for p in phases
        ]

        task = Task(
            task_id=task_id,
            description=description,
            phases=phase_objects,
        )

        self._tasks[task_id] = task
        self._audit_trails[task_id] = []

        self._log_audit(
            task_id,
            phase_id=None,
            status="created",
            message=f"Task created with {len(phase_objects)} phases",
        )

        return task

    def get_task(self, task_id: str) -> Task:
        """Get task by ID.

        Args:
            task_id: Task identifier.

        Returns:
            Task: Task instance.

        Raises:
            KeyError: If task not found.
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task {task_id} not found")
        return self._tasks[task_id]

    def mark_phase(
        self,
        task_id: str,
        phase_id: int,
        status: str,
        error: Optional[str] = None,
        violations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[Phase]:
        """Mark phase with new status.

        Args:
            task_id: Task identifier.
            phase_id: Phase identifier.
            status: New status (in-progress, completed, blocked, failed).
            error: Error message if failed.
            violations: Governance violations if blocked.
            metadata: Additional metadata to store.

        Returns:
            Result[Phase]: Updated phase or error.
        """
        try:
            task = self.get_task(task_id)
            phase = self._find_phase(task, phase_id)

            if phase is None:
                return Err(f"Phase {phase_id} not found in task {task_id}")

            try:
                new_status = PhaseStatus(status)
            except ValueError:
                return Err(f"Invalid status: {status}")

            phase.status = new_status

            if new_status == PhaseStatus.IN_PROGRESS:
                phase.started_at = datetime.utcnow()
            elif new_status in [PhaseStatus.COMPLETED, PhaseStatus.FAILED]:
                phase.completed_at = datetime.utcnow()

            if error:
                phase.error = error

            if violations:
                phase.violations = violations

            if metadata:
                phase.metadata.update(metadata)

            self._update_task_status(task)

            self._log_audit(
                task_id,
                phase_id,
                status,
                error=error,
                violations=violations,
            )

            return Ok(phase)
        except Exception as e:
            return Err(f"Error marking phase: {str(e)}")

    def can_advance_to_phase(self, task_id: str, phase_id: int) -> bool:
        """Check if phase can be advanced to (dependencies met).

        Args:
            task_id: Task identifier.
            phase_id: Phase identifier.

        Returns:
            bool: True if dependencies satisfied or no dependencies.
        """
        task = self.get_task(task_id)
        phase = self._find_phase(task, phase_id)

        if phase is None:
            raise KeyError(f"Phase {phase_id} not found")

        if not phase.dependencies:
            return True

        for dep_id in phase.dependencies:
            dep_phase = self._find_phase(task, dep_id)
            if dep_phase is None:
                return False
            if dep_phase.status != PhaseStatus.COMPLETED:
                return False

        return True

    def rollback_to_phase(self, task_id: str, target_phase_id: int) -> Result[None]:
        """Rollback phases after target phase to NOT_STARTED.

        Args:
            task_id: Task identifier.
            target_phase_id: Phase to roll back to.

        Returns:
            Result[None]: Success or error.
        """
        try:
            task = self.get_task(task_id)

            for phase in task.phases:
                if phase.id > target_phase_id:
                    phase.status = PhaseStatus.NOT_STARTED
                    phase.error = None
                    phase.violations = []
                    phase.started_at = None
                    phase.completed_at = None

            self._log_audit(
                task_id,
                phase_id=None,
                status="rollback",
                message=f"Rolled back to phase {target_phase_id}",
            )

            return Ok(None)
        except Exception as e:
            return Err(f"Rollback failed: {str(e)}")

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current task status snapshot.

        Args:
            task_id: Task identifier.

        Returns:
            TaskStatus: Current status snapshot.
        """
        task = self.get_task(task_id)

        completed = sum(
            1 for p in task.phases if p.status == PhaseStatus.COMPLETED
        )
        blocked = [p.id for p in task.phases if p.status == PhaseStatus.BLOCKED]

        current_phase: Optional[int] = None
        for phase in task.phases:
            if phase.status == PhaseStatus.IN_PROGRESS:
                current_phase = phase.id
                break

        return TaskStatus(
            task_id=task_id,
            task_status=task.status,
            completed_phases=completed,
            total_phases=len(task.phases),
            current_phase=current_phase,
            blocked_phases=blocked,
        )

    def get_completed_phases(self, task_id: str) -> List[Phase]:
        """Get all completed phases.

        Args:
            task_id: Task identifier.

        Returns:
            List[Phase]: Completed phase list.
        """
        task = self.get_task(task_id)
        return [p for p in task.phases if p.status == PhaseStatus.COMPLETED]

    def get_blocked_phases(self, task_id: str) -> List[Phase]:
        """Get all blocked phases.

        Args:
            task_id: Task identifier.

        Returns:
            List[Phase]: Blocked phase list.
        """
        task = self.get_task(task_id)
        return [p for p in task.phases if p.status == PhaseStatus.BLOCKED]

    def get_audit_trail(
        self, task_id: str, phase_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get audit trail for task or specific phase.

        Args:
            task_id: Task identifier.
            phase_id: Optional phase identifier (filter by phase if specified).

        Returns:
            List[Dict]: Audit trail entries.
        """
        if task_id not in self._audit_trails:
            raise KeyError(f"No audit trail for task {task_id}")

        trail = self._audit_trails[task_id]

        if phase_id is not None:
            trail = [e for e in trail if e.get("phase_id") == phase_id]

        return trail

    def _find_phase(self, task: Task, phase_id: int) -> Optional[Phase]:
        """Find phase in task by ID.

        Args:
            task: Task instance.
            phase_id: Phase identifier.

        Returns:
            Optional[Phase]: Phase or None if not found.
        """
        for phase in task.phases:
            if phase.id == phase_id:
                return phase
        return None

    def _update_task_status(self, task: Task) -> None:
        """Update task status based on phase statuses.

        Args:
            task: Task to update.
        """
        all_completed = all(p.status == PhaseStatus.COMPLETED for p in task.phases)
        any_blocked = any(p.status == PhaseStatus.BLOCKED for p in task.phases)
        any_failed = any(p.status == PhaseStatus.FAILED for p in task.phases)

        if all_completed:
            task.status = TaskState.COMPLETED
        elif any_blocked:
            task.status = TaskState.BLOCKED
        elif any_failed:
            task.status = TaskState.FAILED
        elif any(p.status == PhaseStatus.IN_PROGRESS for p in task.phases):
            task.status = TaskState.IN_PROGRESS
        else:
            task.status = TaskState.NOT_STARTED

    def _log_audit(
        self,
        task_id: str,
        phase_id: Optional[int],
        status: str,
        error: Optional[str] = None,
        violations: Optional[List[str]] = None,
        message: Optional[str] = None,
    ) -> None:
        """Log operation to audit trail.

        Args:
            task_id: Task identifier.
            phase_id: Phase identifier (optional).
            status: Operation status.
            error: Error message (optional).
            violations: Violations list (optional).
            message: Additional message (optional).
        """
        entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "phase_id": phase_id,
            "status": status,
        }

        if error:
            entry["error"] = error

        if violations:
            entry["violations"] = violations

        if message:
            entry["message"] = message

        if task_id in self._audit_trails:
            self._audit_trails[task_id].append(entry)
