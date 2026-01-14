"""
TODO Lifecycle Manager - Task 2.4.2 Implementation
GREEN phase: Make tests pass with minimal implementation

Manages automatic task state transitions with dependency resolution,
validation, and comprehensive audit logging.

Author: GitHub Copilot
Phase: feat02-phase4-completion Phase 1
Correlation ID: FEAT02-P4-T2.4.2
"""

import time
import threading
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from collections import defaultdict

from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditLevel, AuditCategory


class TaskState(Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class TransitionResult:
    """Result of a state transition attempt."""
    success: bool
    message: str
    old_state: Optional[TaskState] = None
    new_state: Optional[TaskState] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StateChangeEvent:
    """Event emitted on state changes."""
    task_id: str
    old_state: TaskState
    new_state: TaskState
    timestamp: datetime
    reason: Optional[str] = None


class TodoLifecycleManager:
    """
    Manages TODO task lifecycle with automatic state transitions.
    
    Features:
    - Automatic state transition validation
    - Dependency resolution before transitions
    - Event emission on state changes
    - Comprehensive audit logging
    - Circular dependency prevention
    - Performance metrics tracking
    """
    
    # Valid state transitions (includes BLOCKED from any state)
    VALID_TRANSITIONS = {
        TaskState.PENDING: {TaskState.IN_PROGRESS, TaskState.BLOCKED},
        TaskState.IN_PROGRESS: {TaskState.COMPLETED, TaskState.FAILED, TaskState.BLOCKED},
        TaskState.BLOCKED: {TaskState.PENDING, TaskState.IN_PROGRESS},
        TaskState.COMPLETED: {TaskState.BLOCKED},  # Can block even after completion
        TaskState.FAILED: {TaskState.PENDING, TaskState.BLOCKED}  # Can retry or block
    }
    
    def __init__(self, audit_logger: Optional[EnterpriseAuditLogger] = None):
        """Initialize lifecycle manager."""
        self.audit_logger = audit_logger or EnterpriseAuditLogger()
        self._tasks: Dict[str, TaskState] = {}
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._blocked_tasks: Dict[str, str] = {}  # task_id -> reason
        self._event_handlers: List[Callable] = []
        self._performance_logs: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        
        self._log_audit(
            "lifecycle_manager_initialized",
            "TodoLifecycleManager initialized",
            {}
        )
    
    def can_transition(self, from_state: TaskState, to_state: TaskState) -> bool:
        """Check if state transition is valid."""
        # BLOCKED can be reached from any state
        if to_state == TaskState.BLOCKED:
            return True
        return to_state in self.VALID_TRANSITIONS.get(from_state, set())
    
    def get_state(self, task_id: str) -> TaskState:
        """Get current state of task."""
        with self._lock:
            return self._tasks.get(task_id, TaskState.PENDING)
    
    def create_task(self, task_id: str) -> TaskState:
        """Create a new task in PENDING state."""
        with self._lock:
            if task_id not in self._tasks:
                self._tasks[task_id] = TaskState.PENDING
                self._log_audit(
                    "task_created",
                    f"Task {task_id} created",
                    {"task_id": task_id}
                )
            return self._tasks[task_id]
    
    def start_task(self, task_id: str) -> TransitionResult:
        """Start a task (transition to IN_PROGRESS)."""
        start_time = time.perf_counter()
        
        with self._lock:
            # Raise error if task doesn't exist (explicit creation required)
            if task_id not in self._tasks:
                raise ValueError(f"Task {task_id} not found")
            
            current_state = self._tasks[task_id]
            
            # Check if blocked
            if task_id in self._blocked_tasks:
                result = TransitionResult(
                    success=False,
                    message=f"Task is blocked: {self._blocked_tasks[task_id]}",
                    old_state=current_state
                )
                self._log_performance("start_task", time.perf_counter() - start_time, False)
                return result
            
            # Check dependencies
            if not self._check_dependencies(task_id):
                result = TransitionResult(
                    success=False,
                    message="Task has unmet dependency requirements",
                    old_state=current_state
                )
                self._log_performance("start_task", time.perf_counter() - start_time, False)
                return result
            
            # Validate transition
            if not self.can_transition(current_state, TaskState.IN_PROGRESS):
                result = TransitionResult(
                    success=False,
                    message=f"Cannot transition from {current_state.value} to IN_PROGRESS",
                    old_state=current_state
                )
                self._log_performance("start_task", time.perf_counter() - start_time, False)
                return result
            
            # Perform transition
            self._tasks[task_id] = TaskState.IN_PROGRESS
            
            # Emit event
            event = StateChangeEvent(
                task_id=task_id,
                old_state=current_state,
                new_state=TaskState.IN_PROGRESS,
                timestamp=datetime.now()
            )
            self._emit_event(event)
            
            # Audit log
            self._log_audit(
                "state_transition",
                f"Task {task_id} transitioned to IN_PROGRESS",
                {
                    "task_id": task_id,
                    "old_state": current_state.value,
                    "new_state": TaskState.IN_PROGRESS.value
                }
            )
            
            duration = time.perf_counter() - start_time
            self._log_performance("start_task", duration, True)
            
            return TransitionResult(
                success=True,
                message=f"Task {task_id} started",
                old_state=current_state,
                new_state=TaskState.IN_PROGRESS
            )
    
    def complete_task(self, task_id: str) -> TransitionResult:
        """Complete a task (transition to COMPLETED)."""
        start_time = time.perf_counter()
        
        with self._lock:
            if task_id not in self._tasks:
                raise ValueError(f"Task {task_id} not found")
            
            current_state = self._tasks[task_id]
            
            # Validate transition
            if not self.can_transition(current_state, TaskState.COMPLETED):
                result = TransitionResult(
                    success=False,
                    message=f"Cannot transition from {current_state.value} to COMPLETED",
                    old_state=current_state
                )
                self._log_performance("complete_task", time.perf_counter() - start_time, False)
                return result
            
            # Perform transition
            self._tasks[task_id] = TaskState.COMPLETED
            
            # Emit event
            event = StateChangeEvent(
                task_id=task_id,
                old_state=current_state,
                new_state=TaskState.COMPLETED,
                timestamp=datetime.now()
            )
            self._emit_event(event)
            
            # Audit log
            self._log_audit(
                "state_transition",
                f"Task {task_id} completed",
                {
                    "task_id": task_id,
                    "old_state": current_state.value,
                    "new_state": TaskState.COMPLETED.value
                }
            )
            
            duration = time.perf_counter() - start_time
            self._log_performance("complete_task", duration, True)
            
            return TransitionResult(
                success=True,
                message=f"Task {task_id} completed",
                old_state=current_state,
                new_state=TaskState.COMPLETED
            )
    
    def block_task(self, task_id: str, reason: str) -> TransitionResult:
        """Block a task."""
        with self._lock:
            if task_id not in self._tasks:
                self._tasks[task_id] = TaskState.PENDING
            
            current_state = self._tasks[task_id]
            self._tasks[task_id] = TaskState.BLOCKED
            self._blocked_tasks[task_id] = reason
            
            self._log_audit(
                "task_blocked",
                f"Task {task_id} blocked: {reason}",
                {"task_id": task_id, "reason": reason}
            )
            
            return TransitionResult(
                success=True,
                message=f"Task {task_id} blocked",
                old_state=current_state,
                new_state=TaskState.BLOCKED
            )
    
    def unblock_task(self, task_id: str) -> TransitionResult:
        """Unblock a task."""
        with self._lock:
            if task_id in self._blocked_tasks:
                del self._blocked_tasks[task_id]
                self._tasks[task_id] = TaskState.PENDING
                
                self._log_audit(
                    "task_unblocked",
                    f"Task {task_id} unblocked",
                    {"task_id": task_id}
                )
                
                return TransitionResult(
                    success=True,
                    message=f"Task {task_id} unblocked",
                    new_state=TaskState.PENDING
                )
            
            return TransitionResult(
                success=False,
                message=f"Task {task_id} was not blocked"
            )
    
    def add_dependency(self, task_id: str, depends_on: str):
        """Add a dependency between tasks."""
        with self._lock:
            # Check for circular dependencies
            if self._would_create_cycle(task_id, depends_on):
                raise ValueError(f"Adding dependency would create circular dependency")
            
            self._dependencies[task_id].add(depends_on)
            
            self._log_audit(
                "dependency_added",
                f"Task {task_id} depends on {depends_on}",
                {"task_id": task_id, "depends_on": depends_on}
            )
    
    def get_dependencies(self, task_id: str) -> List[str]:
        """Get dependencies for a task."""
        return list(self._dependencies.get(task_id, set()))
    
    def on_state_change(self, handler: Callable):
        """Register event handler for state changes."""
        self._event_handlers.append(handler)
    
    def get_performance_logs(self) -> List[Dict[str, Any]]:
        """Get performance logs."""
        return self._performance_logs.copy()
    
    def _check_dependencies(self, task_id: str) -> bool:
        """Check if all dependencies are met."""
        deps = self._dependencies.get(task_id, set())
        for dep_id in deps:
            if self._tasks.get(dep_id) != TaskState.COMPLETED:
                return False
        return True
    
    def _would_create_cycle(self, task_id: str, depends_on: str) -> bool:
        """Check if adding dependency would create a cycle."""
        # BFS to detect cycle
        visited = set()
        queue = [depends_on]
        
        while queue:
            current = queue.pop(0)
            if current == task_id:
                return True
            
            if current in visited:
                continue
            
            visited.add(current)
            queue.extend(self._dependencies.get(current, set()))
        
        return False
    
    def _emit_event(self, event: StateChangeEvent):
        """Emit state change event to all handlers."""
        event_dict = {
            "task_id": event.task_id,
            "old_state": event.old_state,
            "new_state": event.new_state,
            "timestamp": event.timestamp.isoformat(),
            "reason": event.reason
        }
        
        for handler in self._event_handlers:
            try:
                handler(event_dict)
            except Exception as e:
                self._log_audit(
                    "event_handler_error",
                    f"Error in event handler: {str(e)}",
                    {"error": str(e)}
                )
    
    def _log_audit(self, operation: str, message: str, context: Dict[str, Any]):
        """Log audit trail with correlation ID."""
        correlation_id = f"FEAT02-P4-LIFECYCLE-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        self.audit_logger.log(
            AuditLevel.INFO,
            AuditCategory.EXECUTION,
            "todo_lifecycle_manager",
            operation,
            message,
            context={
                **context,
                "correlation_id": correlation_id
            }
        )
    
    def _log_performance(self, operation: str, duration: float, success: bool):
        """Log performance metrics."""
        duration_ms = duration * 1000
        
        log_entry = {
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self._performance_logs.append(log_entry)
        
        self._log_audit(
            "performance_metric",
            f"Operation {operation} took {duration_ms:.2f}ms",
            log_entry
        )
