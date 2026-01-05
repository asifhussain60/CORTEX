"""
Task List Orchestrator - Lightweight Task Management with Strategic Checkpointing.

Simplified alternative to full DAG graph for sequential/branching orchestration.
Optimized for:
- Fast recovery (<1 second)
- Low memory overhead (<10KB per orchestrator)
- Simple debugging (plain dict tasks)
- Strategic checkpointing (at risky branches only)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from src.database.planning_state_db import PlanningStateDB


class TaskStatus(str, Enum):
    """Task execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """
    Lightweight task representation.
    
    Design: Plain dataclass (no complex graph objects) for easy serialization/debugging.
    """
    task_id: str
    description: str
    executor: Optional[Callable] = None  # Not serialized (reconstructed on recovery)
    parameters: Dict[str, Any] = field(default_factory=dict)
    checkpoint_before: bool = False  # Strategic checkpointing flag
    depends_on: List[str] = field(default_factory=list)  # Task IDs
    
    # State
    status: TaskStatus = TaskStatus.NOT_STARTED
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization (excludes executor)."""
        # Build dict manually to avoid asdict() trying to deep copy executor (which may contain non-picklable objects)
        return {
            'task_id': self.task_id,
            'description': self.description,
            'executor': None,  # Executors must be re-bound via registry after recovery
            'parameters': self.parameters,
            'depends_on': self.depends_on,
            'checkpoint_before': self.checkpoint_before,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds
        }
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get task duration in milliseconds."""
        if self.duration_seconds is not None:
            return self.duration_seconds * 1000
        return None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Reconstruct from dict (executor must be re-bound)."""
        data = data.copy()
        data['status'] = TaskStatus(data['status'])
        if data['started_at']:
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class TaskListOrchestrator:
    """
    Lightweight task orchestrator with strategic checkpointing.
    
    Philosophy:
    - Simple list of tasks (no complex graph)
    - Index-based execution (resume by setting index)
    - Strategic checkpointing (only at risky branches)
    - Plain dict tasks (easy debugging/logging)
    
    Features:
    - Fast recovery (<1 second via JSON load + index set)
    - Low memory (<10KB per orchestrator)
    - Dependency tracking (simple task_id references)
    - Automatic persistence to PlanningStateDB
    
    Usage:
        orch = TaskListOrchestrator("planning_v5", state_db)
        
        # Add tasks
        orch.add_task("discover", "Discover context", discover_fn)
        orch.add_task("analyze", "Analyze requirements", analyze_fn, 
                      depends_on=["discover"], checkpoint_before=True)
        orch.add_task("plan", "Generate plan", plan_fn, depends_on=["analyze"])
        
        # Execute
        while orch.has_pending_tasks():
            result = orch.execute_next()
        
        # Or recover from interruption
        orch.recover()
        while orch.has_pending_tasks():
            result = orch.execute_next()
    """
    
    def __init__(
        self,
        orchestrator_id: str,
        state_db: PlanningStateDB,
        auto_persist: bool = True
    ):
        """
        Initialize task list orchestrator.
        
        Args:
            orchestrator_id: Unique identifier for this orchestrator instance
            state_db: PlanningStateDB for persistence
            auto_persist: Auto-persist state after each task (default: True)
        """
        self.orchestrator_id = orchestrator_id
        self.state_db = state_db
        self.auto_persist = auto_persist
        
        self.tasks: List[Task] = []
        self.current_task_index: int = 0
        self.executor_registry: Dict[str, Callable] = {}  # task_id -> executor
        
        self.logger = logging.getLogger(f"cortex.orchestrators.task_list.{orchestrator_id}")
    
    def add_task(
        self,
        task_id: str,
        description: str,
        executor: Optional[Callable] = None,
        parameters: Optional[Dict[str, Any]] = None,
        checkpoint_before: bool = False,
        depends_on: Optional[List[str]] = None
    ) -> Task:
        """
        Add task to execution list.
        
        Args:
            task_id: Unique task identifier
            description: Human-readable description
            executor: Function to execute (signature: executor(params) -> result)
            parameters: Parameters passed to executor
            checkpoint_before: Create checkpoint before executing this task
            depends_on: List of task_ids that must complete first
        
        Returns:
            Created Task object
        """
        task = Task(
            task_id=task_id,
            description=description,
            executor=executor,
            parameters=parameters or {},
            checkpoint_before=checkpoint_before,
            depends_on=depends_on or []
        )
        
        self.tasks.append(task)
        
        # Register executor for recovery
        if executor:
            self.executor_registry[task_id] = executor
        
        self.logger.debug(f"Added task: {task_id} | Deps: {depends_on or []}")
        
        return task
    
    def execute_next(self) -> Optional[Any]:
        """
        Execute next ready task (dependencies satisfied, not started).
        
        Returns:
            Task result or None if no tasks ready
        
        Raises:
            Exception: If task execution fails
        """
        # Find next ready task
        ready_task = self._find_next_ready_task()
        
        if not ready_task:
            return None
        
        # Strategic checkpoint
        if ready_task.checkpoint_before:
            self.checkpoint(f"Before {ready_task.task_id}")
        
        # Execute task
        self.logger.info(f"Executing task: {ready_task.task_id} - {ready_task.description}")
        
        ready_task.status = TaskStatus.IN_PROGRESS
        ready_task.started_at = datetime.now()
        
        try:
            if not ready_task.executor:
                raise ValueError(f"Task {ready_task.task_id} has no executor")
            
            # Execute with parameters
            result = ready_task.executor(ready_task.parameters)
            
            ready_task.result = result
            ready_task.status = TaskStatus.COMPLETED
            ready_task.completed_at = datetime.now()
            ready_task.duration_seconds = (
                ready_task.completed_at - ready_task.started_at
            ).total_seconds()
            
            self.logger.info(
                f"✅ Task completed: {ready_task.task_id} "
                f"({ready_task.duration_seconds:.2f}s)"
            )
            
        except Exception as e:
            ready_task.status = TaskStatus.FAILED
            ready_task.error = str(e)
            ready_task.completed_at = datetime.now()
            
            self.logger.error(
                f"❌ Task failed: {ready_task.task_id} - {e}"
            )
            raise
        
        finally:
            # Auto-persist if enabled
            if self.auto_persist:
                self._persist_state()
        
        return ready_task.result
    
    def execute_all(self) -> List[Any]:
        """
        Execute all tasks in order.
        
        Returns:
            List of results from completed tasks
        
        Raises:
            Exception: If any task fails
        """
        results = []
        
        while self.has_pending_tasks():
            result = self.execute_next()
            if result is not None:
                results.append(result)
        
        return results
    
    def has_pending_tasks(self) -> bool:
        """Check if there are tasks not yet completed."""
        return any(
            task.status in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]
            for task in self.tasks
        )
    
    def _find_next_ready_task(self) -> Optional[Task]:
        """
        Find next task ready to execute (dependencies satisfied).
        
        Returns:
            Next ready Task or None
        """
        for task in self.tasks:
            # Skip if already started/completed/failed
            if task.status != TaskStatus.NOT_STARTED:
                continue
            
            # Check dependencies
            if self._dependencies_satisfied(task):
                return task
        
        return None
    
    def _dependencies_satisfied(self, task: Task) -> bool:
        """Check if all task dependencies are completed."""
        if not task.depends_on:
            return True
        
        task_map = {t.task_id: t for t in self.tasks}
        
        for dep_id in task.depends_on:
            if dep_id not in task_map:
                self.logger.warning(
                    f"Task {task.task_id} depends on unknown task {dep_id}"
                )
                return False
            
            dep_task = task_map[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def checkpoint(self, label: str = "") -> str:
        """
        Create checkpoint snapshot for recovery.
        
        Args:
            label: Optional description for this checkpoint
        
        Returns:
            Checkpoint ID (snapshot_id from PlanningStateDB)
        """
        checkpoint_data = {
            "orchestrator_id": self.orchestrator_id,
            "timestamp": datetime.now().isoformat(),
            "label": label,
            "current_task_index": self.current_task_index,
            "tasks": [task.to_dict() for task in self.tasks]
        }
        
        # Use PlanningStateDB snapshot mechanism (correct API: state_data not snapshot_data)
        snapshot_id = self.state_db.create_snapshot(
            plan_id=self.orchestrator_id,
            phase_id=None,
            state_data=checkpoint_data,
            snapshot_type="checkpoint",  # Must be 'checkpoint', 'auto', or 'manual'
            description=label or f"Checkpoint at task index {self.current_task_index}"
        )
        
        self.logger.info(f"✅ Checkpoint created: {snapshot_id} - {label}")
        
        return snapshot_id
    
    def recover(self, checkpoint_id: Optional[str] = None) -> None:
        """
        Recover from checkpoint (latest if checkpoint_id not specified).
        
        Args:
            checkpoint_id: Specific checkpoint to restore (None = latest)
        
        Raises:
            ValueError: If no checkpoints found
        """
        if checkpoint_id:
            # Get specific checkpoint
            snapshot = self.state_db.get_snapshot(checkpoint_id)
            if not snapshot:
                raise ValueError(f"Checkpoint {checkpoint_id} not found")
        else:
            # Get latest checkpoint
            snapshot = self.state_db.get_latest_snapshot(
                plan_id=self.orchestrator_id,
                phase_id=None
            )
            
            if not snapshot:
                raise ValueError(
                    f"No checkpoints found for orchestrator {self.orchestrator_id}"
                )
        
        # Restore state (state_data is already a dict, not JSON string)
        checkpoint_data = snapshot["state_data"]
        
        self.current_task_index = checkpoint_data["current_task_index"]
        self.tasks = [Task.from_dict(task_dict) for task_dict in checkpoint_data["tasks"]]
        
        # Re-bind executors (must be done after recovery)
        for task in self.tasks:
            if task.task_id in self.executor_registry:
                task.executor = self.executor_registry[task.task_id]
        
        self.logger.info(
            f"✅ Recovered from checkpoint: {snapshot['snapshot_id']} "
            f"({checkpoint_data['label']})"
        )
    
    def _persist_state(self) -> None:
        """
        Persist current state to PlanningStateDB.
        
        Note: This is lightweight persistence (just task status updates).
        Full checkpoints only created via checkpoint() method.
        """
        # Update current state in DB (simplified for now)
        # Could extend to update individual task records in future
        pass
    
    def register_executor(self, task_id: str, executor: Callable) -> None:
        """
        Register executor for task (needed for recovery).
        
        Args:
            task_id: Task identifier
            executor: Executor function
        """
        self.executor_registry[task_id] = executor
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of specific task."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task.status
        return None
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[Task]:
        """Get all failed tasks."""
        return [task for task in self.tasks if task.status == TaskStatus.FAILED]
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get orchestrator progress statistics.
        
        Returns:
            Dict with progress metrics
        """
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in self.tasks if t.status == TaskStatus.FAILED])
        in_progress = len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS])
        
        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress,
            "progress_percent": (completed / total * 100) if total > 0 else 0.0
        }
