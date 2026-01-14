# ==============================================================================
# CORTEX 6.0 - TODO Orchestrator with DAG-based Dependency Management
# ==============================================================================
# Author: Asif Hussain
# Version: 6.0.0
# Purpose: Orchestrate TODO items with dependency tracking
# TDD: Tests in tests/unit/test_todo_orchestrator.py
# ==============================================================================

"""
TODO Orchestrator for CORTEX 6.0.

This module provides enterprise-grade TODO management with DAG-based dependency
tracking. It integrates with StateManager for persistence and AuditLogger for
comprehensive audit trails.

Key Features:
- DAG-based dependency management
- State machine-enforced status transitions
- Checkpoint and recovery
- Parallel task identification
- Rollback support
- Audit logging integration

Architecture:
    TodoOrchestrator manages:
    - todos: Dict[str, Todo] - All TODO items
    - dag: DAG - Dependency graph
    - state_manager: StateManager - Persistence layer
    - audit_logger: EnterpriseAuditLogger - Audit trail

State Machine:
    NOT_STARTED → BLOCKED/READY
    BLOCKED → READY
    READY → IN_PROGRESS
    IN_PROGRESS → COMPLETED/FAILED
    FAILED → ROLLED_BACK/READY
    COMPLETED → (terminal)
    
Performance Guarantees:
    - create_todo: O(1)
    - read_todo: O(1)
    - update_todo: O(1)
    - delete_todo: O(degree)
    - list_todos: O(n) where n = matching todos
    - get_ready_tasks: O(V)
    - get_parallel_tasks: O(V+E)

Usage:
    >>> from src.orchestrators.core.todo_orchestrator import TodoOrchestrator
    >>> orchestrator = TodoOrchestrator(state_manager, audit_logger)
    >>> todo_id = orchestrator.create_todo(
    ...     title="Implement feature",
    ...     description="Add new feature to system",
    ...     priority=Priority.P0_CRITICAL
    ... )
    >>> orchestrator.transition_status(todo_id, TodoStatus.IN_PROGRESS)
    >>> orchestrator.create_checkpoint()
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from src.orchestrators.core.dag import (
    DAG,
    DAGNode,
    DAGEdge,
    NodeStatus,
    EdgeType,
    Priority,
    DAGError,
    DAGValidationError,
    CyclicDependencyError,
    NodeNotFoundError,
)
from src.orchestrators.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditCategory, AuditLevel

logger = logging.getLogger(__name__)


# ==============================================================================
# ENUMS
# ==============================================================================


class TodoStatus(str, Enum):
    """Status of a TODO item (maps to DAG NodeStatus)."""
    NOT_STARTED = "not_started"
    BLOCKED = "blocked"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"
    
    @property
    def is_terminal(self) -> bool:
        """Check if status is terminal."""
        return self in {TodoStatus.COMPLETED, TodoStatus.CANCELLED}
    
    @property
    def is_active(self) -> bool:
        """Check if status indicates active work."""
        return self == TodoStatus.IN_PROGRESS
    
    def to_node_status(self) -> NodeStatus:
        """Convert to DAG NodeStatus."""
        mapping = {
            TodoStatus.NOT_STARTED: NodeStatus.NOT_STARTED,
            TodoStatus.BLOCKED: NodeStatus.BLOCKED,
            TodoStatus.READY: NodeStatus.NOT_STARTED,  # Ready is a computed state
            TodoStatus.IN_PROGRESS: NodeStatus.IN_PROGRESS,
            TodoStatus.COMPLETED: NodeStatus.COMPLETED,
            TodoStatus.FAILED: NodeStatus.FAILED,
            TodoStatus.ROLLED_BACK: NodeStatus.FAILED,
            TodoStatus.CANCELLED: NodeStatus.CANCELLED,
        }
        return mapping[self]


# ==============================================================================
# EXCEPTIONS
# ==============================================================================


class TodoError(Exception):
    """Base exception for TODO orchestrator errors."""
    pass


class TodoNotFoundError(TodoError):
    """TODO item not found."""
    pass


class InvalidStatusTransitionError(TodoError):
    """Invalid status transition attempted."""
    pass


class TodoValidationError(TodoError):
    """TODO validation failed."""
    pass


class CheckpointError(TodoError):
    """Checkpoint operation failed."""
    pass


# ==============================================================================
# DATA CLASSES
# ==============================================================================


@dataclass
class Todo:
    """
    TODO item with dependency tracking.
    
    Attributes:
        id: Unique identifier
        title: Brief title
        description: Detailed description
        status: Current status
        priority: Task priority
        tags: Set of tags for categorization
        created_at: Creation timestamp
        updated_at: Last update timestamp
        started_at: When work started
        completed_at: When work completed
        dependencies: List of TODO IDs this depends on
        dependents: List of TODO IDs that depend on this
        data: Additional metadata
        checkpoint_data: Checkpoint-specific data
    """
    id: str
    title: str
    description: str = ""
    status: TodoStatus = TodoStatus.NOT_STARTED
    priority: Priority = Priority.P2_MEDIUM
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        # Convert sets to lists for JSON serialization
        result["tags"] = list(self.tags)
        # Convert datetime to ISO format
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        result["started_at"] = self.started_at.isoformat() if self.started_at else None
        result["completed_at"] = self.completed_at.isoformat() if self.completed_at else None
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Todo:
        """Create from dictionary."""
        # Convert lists back to sets
        if "tags" in data:
            data["tags"] = set(data["tags"])
        # Convert ISO format back to datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TodoStatus(data["status"])
        if "priority" in data and isinstance(data["priority"], str):
            data["priority"] = Priority(data["priority"])
        return cls(**data)


@dataclass
class Checkpoint:
    """
    Checkpoint for TODO orchestrator state.
    
    Attributes:
        id: Unique checkpoint identifier
        timestamp: When checkpoint was created
        todos: Snapshot of all TODO items
        dag_state: Serialized DAG state
        metadata: Additional checkpoint metadata
    """
    id: str
    timestamp: datetime
    todos: Dict[str, Todo]
    dag_state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "todos": {k: v.to_dict() for k, v in self.todos.items()},
            "dag_state": self.dag_state,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Checkpoint:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            todos={k: Todo.from_dict(v) for k, v in data["todos"].items()},
            dag_state=data["dag_state"],
            metadata=data.get("metadata", {}),
        )


# ==============================================================================
# TODO ORCHESTRATOR
# ==============================================================================


class TodoOrchestrator:
    """
    TODO Orchestrator with DAG-based dependency management.
    
    Manages TODO items with:
    - Dependency tracking via DAG
    - State machine-enforced transitions
    - Checkpoint and recovery
    - Parallel task identification
    - Rollback support
    - Comprehensive audit logging
    """
    
    # Valid status transitions (state machine)
    VALID_TRANSITIONS = {
        # READY is a computed state that maps to NodeStatus.NOT_STARTED
        # Allow moving from NOT_STARTED to READY or IN_PROGRESS
        TodoStatus.NOT_STARTED: {TodoStatus.BLOCKED, TodoStatus.READY, TodoStatus.IN_PROGRESS, TodoStatus.CANCELLED},
        # From BLOCKED, allow becoming READY (maps to NOT_STARTED) or CANCELLED
        # Do NOT allow direct BLOCKED -> IN_PROGRESS (DAG disallows)
        TodoStatus.BLOCKED: {TodoStatus.READY, TodoStatus.CANCELLED},
        # From READY, allow progression to IN_PROGRESS or becoming BLOCKED
        TodoStatus.READY: {TodoStatus.IN_PROGRESS, TodoStatus.BLOCKED},
        # From IN_PROGRESS, allow completion, failure, or cancellation (DAG allows)
        TodoStatus.IN_PROGRESS: {TodoStatus.COMPLETED, TodoStatus.FAILED, TodoStatus.CANCELLED},
        # From FAILED, only allow resetting to READY (maps to NOT_STARTED) for retry
        TodoStatus.FAILED: {TodoStatus.READY},
        # Terminal states
        TodoStatus.COMPLETED: set(),
        # ROLLED_BACK is represented as FAILED at the DAG level; allow moving to READY
        TodoStatus.ROLLED_BACK: {TodoStatus.READY},
        TodoStatus.CANCELLED: set(),
    }
    
    def __init__(
        self,
        state_manager: StateManager,
        audit_logger: Optional[EnterpriseAuditLogger] = None,
        name: str = "cortex-todo-orchestrator",
        auto_checkpoint_interval: Optional[int] = None,
        workspace_root: Optional[Path] = None,
        governance_merger: Optional[Any] = None,
    ):
        """
        Initialize TODO Orchestrator.
        
        Args:
            state_manager: StateManager instance for persistence
            audit_logger: Optional audit logger (creates new if None)
            name: Name for this orchestrator instance
            auto_checkpoint_interval: Auto-checkpoint every N operations (None = disabled)
            workspace_root: Root directory of workspace (for feat04 integration)
            governance_merger: Optional GovernanceMerger for rule enforcement
        """
        self.name = name
        self.state_manager = state_manager
        self.audit_logger = audit_logger or EnterpriseAuditLogger()
        self.workspace_root = workspace_root or Path.cwd()
        self.governance_merger = governance_merger
        
        # Core state
        self.todos: Dict[str, Todo] = {}
        self.dag = DAG(name=f"{name}-dag")
        
        # Checkpoint management
        self.checkpoints: List[Checkpoint] = []
        self.auto_checkpoint_interval = auto_checkpoint_interval
        self._operation_count = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            "total_created": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_checkpoints": 0,
            "total_recoveries": 0,
        }
        
        logger.info(f"TodoOrchestrator '{name}' initialized")
    
    # ==========================================================================
    # TODO CRUD OPERATIONS
    # ==========================================================================
    
    def create_todo(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.P2_MEDIUM,
        tags: Optional[Set[str]] = None,
        dependencies: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        todo_id: Optional[str] = None,
    ) -> str:
        """
        Create a new TODO item.
        
        Args:
            title: Brief title
            description: Detailed description
            priority: Task priority
            tags: Optional set of tags
            dependencies: Optional list of TODO IDs this depends on
            data: Optional additional metadata
            todo_id: Optional explicit ID (generates UUID if None)
            
        Returns:
            Created TODO ID
            
        Raises:
            TodoValidationError: If validation fails
            CyclicDependencyError: If dependencies create a cycle
        """
        with self._lock:
            # Generate ID
            if todo_id is None:
                todo_id = f"todo-{uuid.uuid4().hex[:12]}"
            
            # Validate title
            if not title or not title.strip():
                raise TodoValidationError("Title cannot be empty")
            
            # Create TODO
            todo = Todo(
                id=todo_id,
                title=title.strip(),
                description=description.strip(),
                priority=priority,
                tags=tags or set(),
                dependencies=dependencies or [],
                data=data or {},
            )
            
            # Add to DAG
            self.dag.add_node(
                todo_id,
                name=title,
                priority=priority,
                tags=tags or set(),
                data={"todo": todo.to_dict()},
            )
            
            # Add dependency edges
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self.todos:
                        raise TodoValidationError(f"Dependency '{dep_id}' not found")
                    self.dag.add_edge(dep_id, todo_id)
            
            # Store TODO
            self.todos[todo_id] = todo
            
            # Update statistics
            self._stats["total_created"] += 1
            self._operation_count += 1
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="create_todo",
                message=f"Created TODO '{title}'",
                context={"todo_id": todo_id, "priority": priority.value},
            )
            
            # Auto-checkpoint
            self._auto_checkpoint_if_needed()
            
            return todo_id
    
    def read_todo(self, todo_id: str) -> Todo:
        """
        Read a TODO item.
        
        Args:
            todo_id: TODO identifier
            
        Returns:
            Todo object
            
        Raises:
            TodoNotFoundError: If TODO not found
        """
        with self._lock:
            if todo_id not in self.todos:
                raise TodoNotFoundError(f"TODO '{todo_id}' not found")
            return self.todos[todo_id]
    
    def update_todo(
        self,
        todo_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        tags: Optional[Set[str]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Todo:
        """
        Update a TODO item.
        
        Args:
            todo_id: TODO identifier
            title: Optional new title
            description: Optional new description
            priority: Optional new priority
            tags: Optional new tags (replaces existing)
            data: Optional data updates (merges with existing)
            
        Returns:
            Updated Todo object
            
        Raises:
            TodoNotFoundError: If TODO not found
        """
        with self._lock:
            todo = self.read_todo(todo_id)
            
            # Update fields
            if title is not None:
                todo.title = title.strip()
            if description is not None:
                todo.description = description.strip()
            if priority is not None:
                todo.priority = priority
            if tags is not None:
                todo.tags = tags
            if data is not None:
                todo.data.update(data)
            
            todo.updated_at = datetime.now()
            
            # Update DAG node
            self.dag.update_node(
                todo_id,
                name=todo.title,
                priority=todo.priority,
                tags=todo.tags,
                data={"todo": todo.to_dict()},
            )
            
            # Update statistics
            self._operation_count += 1
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="update_todo",
                message=f"Updated TODO '{todo.title}'",
                context={"todo_id": todo_id},
            )
            
            # Auto-checkpoint
            self._auto_checkpoint_if_needed()
            
            return todo
    
    def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a TODO item.
        
        Args:
            todo_id: TODO identifier
            
        Returns:
            True if deleted
            
        Raises:
            TodoNotFoundError: If TODO not found
            TodoValidationError: If TODO has active dependents
        """
        with self._lock:
            todo = self.read_todo(todo_id)
            
            # Check for active dependents
            dependents = self.dag.get_dependents(todo_id)
            active_dependents = [
                dep_id for dep_id in dependents
                if not self.todos[dep_id].status.is_terminal
            ]
            if active_dependents:
                raise TodoValidationError(
                    f"Cannot delete TODO with active dependents: {active_dependents}"
                )
            
            # Remove from DAG
            self.dag.remove_node(todo_id)
            
            # Remove from storage
            del self.todos[todo_id]
            
            # Update statistics
            self._operation_count += 1
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="delete_todo",
                message=f"Deleted TODO '{todo.title}'",
                context={"todo_id": todo_id},
            )
            
            # Auto-checkpoint
            self._auto_checkpoint_if_needed()
            
            return True
    
    def list_todos(
        self,
        status: Optional[TodoStatus] = None,
        priority: Optional[Priority] = None,
        tags: Optional[Set[str]] = None,
    ) -> List[Todo]:
        """
        List TODO items with optional filters.
        
        Args:
            status: Optional status filter
            priority: Optional priority filter
            tags: Optional tag filter (TODO must have ALL tags)
            
        Returns:
            List of matching Todo objects
        """
        with self._lock:
            results = []
            for todo in self.todos.values():
                # Apply filters
                if status is not None and todo.status != status:
                    continue
                if priority is not None and todo.priority != priority:
                    continue
                if tags is not None and not tags.issubset(todo.tags):
                    continue
                results.append(todo)
            return results
    
    # ==========================================================================
    # STATUS TRANSITIONS
    # ==========================================================================
    
    def transition_status(self, todo_id: str, new_status: TodoStatus) -> Todo:
        """
        Transition TODO to new status.
        
        Args:
            todo_id: TODO identifier
            new_status: Target status
            
        Returns:
            Updated Todo object
            
        Raises:
            TodoNotFoundError: If TODO not found
            InvalidStatusTransitionError: If transition is invalid
        """
        with self._lock:
            todo = self.read_todo(todo_id)
            old_status = todo.status
            
            # Validate transition
            if not self._validate_transition(old_status, new_status):
                raise InvalidStatusTransitionError(
                    f"Invalid transition: {old_status.value} → {new_status.value}"
                )
            
            # Update status
            todo.status = new_status
            todo.updated_at = datetime.now()
            
            # Update timestamps
            if new_status == TodoStatus.IN_PROGRESS and todo.started_at is None:
                todo.started_at = datetime.now()
            elif new_status == TodoStatus.COMPLETED:
                todo.completed_at = datetime.now()
                self._stats["total_completed"] += 1
            elif new_status == TodoStatus.FAILED:
                self._stats["total_failed"] += 1
            
            # Update DAG node status
            self.dag.set_node_status(
                todo_id,
                status=new_status.to_node_status()
            )
            
            # Also update node data to keep TODO in sync
            self.dag.update_node(
                todo_id,
                data={"todo": todo.to_dict()},
            )
            
            # Update dependent statuses
            self._update_dependent_statuses(todo_id)
            
            # Update statistics
            self._operation_count += 1
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.STATE_MANAGEMENT,
                component="todo_orchestrator",
                operation="transition_status",
                message=f"TODO '{todo.title}' transitioned: {old_status.value} → {new_status.value}",
                context={
                    "todo_id": todo_id,
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                },
            )
            
            # Auto-checkpoint
            self._auto_checkpoint_if_needed()
            
            return todo
    
    def _validate_transition(self, from_status: TodoStatus, to_status: TodoStatus) -> bool:
        """Validate if status transition is allowed."""
        return to_status in self.VALID_TRANSITIONS.get(from_status, set())
    
    def _update_dependent_statuses(self, todo_id: str) -> None:
        """Update statuses of dependent TODOs after status change."""
        todo = self.todos[todo_id]
        dependents = self.dag.get_dependents(todo_id)
        
        for dep_id in dependents:
            dep_todo = self.todos[dep_id]
            
            # Skip terminal states
            if dep_todo.status.is_terminal:
                continue
            
            # Check if dependent should be unblocked
            if dep_todo.status == TodoStatus.BLOCKED:
                if self._is_ready(dep_id):
                    self.transition_status(dep_id, TodoStatus.READY)
            
            # Check if dependent should be blocked
            elif dep_todo.status in {TodoStatus.NOT_STARTED, TodoStatus.READY}:
                if not self._is_ready(dep_id):
                    self.transition_status(dep_id, TodoStatus.BLOCKED)
    
    def _is_ready(self, todo_id: str) -> bool:
        """Check if TODO is ready to execute (all dependencies completed)."""
        dependencies = self.dag.get_dependencies(todo_id)
        return all(
            self.todos[dep_id].status == TodoStatus.COMPLETED
            for dep_id in dependencies
        )
    
    # ==========================================================================
    # PARALLEL TASK IDENTIFICATION
    # ==========================================================================
    
    def get_ready_tasks(self) -> List[Todo]:
        """
        Get all TODO items that are ready to execute.
        
        A TODO is ready if:
        - Status is READY or NOT_STARTED
        - All dependencies are completed
        
        Returns:
            List of ready Todo objects, sorted by priority
        """
        with self._lock:
            ready_node_ids = self.dag.get_ready_tasks()
            ready_todos = [
                self.todos[node_id]
                for node_id in ready_node_ids
                if node_id in self.todos
            ]
            # Sort by priority (P0 first)
            ready_todos.sort(key=lambda t: t.priority.value)
            return ready_todos
    
    def get_parallel_tasks(self) -> List[List[Todo]]:
        """
        Get groups of TODO items that can execute in parallel.
        
        Returns:
            List of TODO groups, where TODOs in each group can run in parallel
        """
        with self._lock:
            parallel_node_groups = self.dag.get_parallel_groups()
            parallel_todo_groups = [
                [self.todos[node_id] for node_id in group if node_id in self.todos]
                for group in parallel_node_groups
            ]
            return parallel_todo_groups

    def _calculate_critical_path(self) -> List[Todo]:
        """
        Calculate the critical path (longest dependency chain) of TODOs.
        
        Returns:
            List of Todo objects in critical path order (roots → leaf)
        """
        with self._lock:
            node_path = self.dag.get_critical_path()
            return [self.todos[node_id] for node_id in node_path if node_id in self.todos]
    
    # ==========================================================================
    # EXECUTION QUEUE (Phase 4, task-2.4.2)
    # ==========================================================================
    
    def get_next_tasks(self) -> List[Todo]:
        """Get the next tasks ready for execution, prioritized.
        
        Returns tasks in priority order:
        1. READY tasks first
        2. Critical path tasks prioritized
        3. High priority tasks first
        
        Returns:
            List of Todo objects ready for execution, sorted by priority
        """
        with self._lock:
            ready_tasks = self.get_ready_tasks()
            
            # Get critical path task IDs for prioritization
            # Only apply critical path logic if there are actual dependencies
            critical_path = self._calculate_critical_path()
            has_dependencies = len(critical_path) > 1  # Single node = no dependencies
            critical_ids = {t.id for t in critical_path} if has_dependencies else set()
            
            # Sort by: critical path first (if exists), then priority, then creation time
            def sort_key(todo: Todo) -> Tuple[int, int, datetime]:
                is_critical = 0 if todo.id in critical_ids else 1
                priority_value = todo.priority.value
                return (is_critical, priority_value, todo.created_at)
            
            sorted_tasks = sorted(ready_tasks, key=sort_key)
            
            # Log operation
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="get_next_tasks",
                message=f"Retrieved {len(sorted_tasks)} tasks for execution",
                context={"task_count": len(sorted_tasks)},
            )
            
            return sorted_tasks
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as in progress and return execution context.
        
        Args:
            task_id: TODO ID to execute
            
        Returns:
            Dictionary with task info and execution context
            
        Raises:
            ValueError: If task is not ready for execution
        """
        with self._lock:
            todo = self.read_todo(task_id)
            
            # Verify task is ready
            if todo.status != TodoStatus.READY:
                raise ValueError(f"Task {task_id} is not ready (status: {todo.status})")
            
            # Transition to IN_PROGRESS
            self.transition_status(task_id, TodoStatus.IN_PROGRESS)
            
            # Log execution start
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="execute_task",
                message=f"Started execution of task: {todo.title}",
                context={"task_id": task_id, "title": todo.title},
            )
            
            return {
                "task_id": task_id,
                "title": todo.title,
                "description": todo.description,
                "priority": todo.priority.value,
                "started_at": datetime.utcnow().isoformat(),
            }
    
    def mark_complete(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> Todo:
        """Mark a task as completed.
        
        Args:
            task_id: TODO ID to complete
            result: Optional result data
            
        Returns:
            Updated Todo object
        """
        with self._lock:
            # Transition to COMPLETED
            todo = self.transition_status(task_id, TodoStatus.COMPLETED)
            
            # Store result if provided
            if result:
                todo.data = todo.data or {}
                todo.data["result"] = result
                self.todos[task_id] = todo
            
            # Log completion
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="mark_complete",
                message=f"Completed task: {todo.title}",
                context={"task_id": task_id, "title": todo.title},
            )
            
            return todo
    
    def mark_failed(self, task_id: str, error: str) -> Todo:
        """Mark a task as failed.
        
        Args:
            task_id: TODO ID that failed
            error: Error message/description
            
        Returns:
            Updated Todo object
        """
        with self._lock:
            # Transition to FAILED
            todo = self.transition_status(task_id, TodoStatus.FAILED)
            
            # Store error info
            todo.data = todo.data or {}
            todo.data["error"] = error
            todo.data["failed_at"] = datetime.utcnow().isoformat()
            self.todos[task_id] = todo
            
            # Log failure
            self.audit_logger.log(
                level=AuditLevel.ERROR,
                category=AuditCategory.EXECUTION,
                component="todo_orchestrator",
                operation="mark_failed",
                message=f"Task failed: {todo.title}",
                context={"task_id": task_id, "title": todo.title, "error": error},
            )
            
            return todo
    
    # ==========================================================================
    # PROGRESS TRACKING (Phase 4, task-2.4.3)
    # ==========================================================================
    
    def get_progress(self) -> Dict[str, Any]:
        """Get overall TODO progress report.
        
        Returns:
            Dictionary with progress metrics
        """
        with self._lock:
            all_todos = list(self.todos.values())
            total = len(all_todos)
            
            if total == 0:
                return {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "blocked_tasks": 0,
                    "ready_tasks": 0,
                    "in_progress_tasks": 0,
                    "percentage": 0.0,
                    "estimated_remaining_time": 0,
                }
            
            completed = sum(1 for t in all_todos if t.status == TodoStatus.COMPLETED)
            failed = sum(1 for t in all_todos if t.status == TodoStatus.FAILED)
            blocked = sum(1 for t in all_todos if t.status == TodoStatus.BLOCKED)
            ready = sum(1 for t in all_todos if t.status == TodoStatus.READY)
            in_progress = sum(1 for t in all_todos if t.status == TodoStatus.IN_PROGRESS)
            
            percentage = (completed / total) * 100 if total > 0 else 0.0
            
            # Estimate remaining time based on TODO data
            remaining_tasks = total - completed - failed
            avg_time = 60  # Default 60 minutes per task
            estimated_remaining = remaining_tasks * avg_time
            
            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "failed_tasks": failed,
                "blocked_tasks": blocked,
                "ready_tasks": ready,
                "in_progress_tasks": in_progress,
                "percentage": round(percentage, 2),
                "estimated_remaining_time": estimated_remaining,
            }
    
    def get_feature_progress(self, feature_id: str) -> Dict[str, Any]:
        """Get progress for a specific feature.
        
        Args:
            feature_id: Feature ID to get progress for
            
        Returns:
            Dictionary with feature progress metrics
        """
        with self._lock:
            # Filter TODOs by feature_id in data
            feature_todos = [
                t for t in self.todos.values()
                if t.data and t.data.get("feature_id") == feature_id
            ]
            
            if not feature_todos:
                return {
                    "feature_id": feature_id,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "percentage": 0.0,
                }
            
            total = len(feature_todos)
            completed = sum(1 for t in feature_todos if t.status == TodoStatus.COMPLETED)
            percentage = (completed / total) * 100 if total > 0 else 0.0
            
            return {
                "feature_id": feature_id,
                "total_tasks": total,
                "completed_tasks": completed,
                "failed_tasks": sum(1 for t in feature_todos if t.status == TodoStatus.FAILED),
                "blocked_tasks": sum(1 for t in feature_todos if t.status == TodoStatus.BLOCKED),
                "ready_tasks": sum(1 for t in feature_todos if t.status == TodoStatus.READY),
                "percentage": round(percentage, 2),
            }
    
    def get_phase_progress(self, feature_id: str, phase_id: int) -> Dict[str, Any]:
        """Get progress for a specific phase within a feature.
        
        Args:
            feature_id: Feature ID
            phase_id: Phase number
            
        Returns:
            Dictionary with phase progress metrics
        """
        with self._lock:
            # Filter TODOs by feature_id and phase_id in data
            phase_todos = [
                t for t in self.todos.values()
                if t.data 
                and t.data.get("feature_id") == feature_id
                and t.data.get("phase_id") == phase_id
            ]
            
            if not phase_todos:
                return {
                    "feature_id": feature_id,
                    "phase_id": phase_id,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "percentage": 0.0,
                }
            
            total = len(phase_todos)
            completed = sum(1 for t in phase_todos if t.status == TodoStatus.COMPLETED)
            percentage = (completed / total) * 100 if total > 0 else 0.0
            
            return {
                "feature_id": feature_id,
                "phase_id": phase_id,
                "total_tasks": total,
                "completed_tasks": completed,
                "percentage": round(percentage, 2),
            }
    
    # ==========================================================================
    # CHECKPOINT & RECOVERY
    # ==========================================================================
    
    def create_checkpoint(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a checkpoint of current state.
        
        Args:
            metadata: Optional checkpoint metadata
            
        Returns:
            Checkpoint ID
        """
        with self._lock:
            checkpoint = Checkpoint(
                id=f"checkpoint-{uuid.uuid4().hex[:12]}",
                timestamp=datetime.now(),
                todos={k: v for k, v in self.todos.items()},  # Shallow copy
                dag_state=self.dag.to_dict(),
                metadata=metadata or {},
            )
            
            self.checkpoints.append(checkpoint)
            self._stats["total_checkpoints"] += 1
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.STATE_MANAGEMENT,
                component="todo_orchestrator",
                operation="create_checkpoint",
                message=f"Created checkpoint '{checkpoint.id}'",
                context={"checkpoint_id": checkpoint.id, "todo_count": len(self.todos)},
            )
            
            return checkpoint.id
    
    def load_checkpoint(self, checkpoint_id: str) -> None:
        """
        Load state from a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Raises:
            CheckpointError: If checkpoint not found
        """
        with self._lock:
            # Find checkpoint
            checkpoint = None
            for cp in self.checkpoints:
                if cp.id == checkpoint_id:
                    checkpoint = cp
                    break
            
            if checkpoint is None:
                raise CheckpointError(f"Checkpoint '{checkpoint_id}' not found")
            
            # Restore state
            self.todos = {k: v for k, v in checkpoint.todos.items()}  # Shallow copy
            self.dag = DAG.from_dict(checkpoint.dag_state)
            
            self._stats["total_recoveries"] += 1
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.STATE_MANAGEMENT,
                component="todo_orchestrator",
                operation="load_checkpoint",
                message=f"Loaded checkpoint '{checkpoint_id}'",
                context={"checkpoint_id": checkpoint_id, "todo_count": len(self.todos)},
            )
    
    def _auto_checkpoint_if_needed(self) -> None:
        """Create checkpoint if auto-checkpoint interval reached."""
        if self.auto_checkpoint_interval is None:
            return
        
        if self._operation_count % self.auto_checkpoint_interval == 0:
            self.create_checkpoint(metadata={"auto": True})
    
    # ==========================================================================
    # PERSISTENCE
    # ==========================================================================
    
    def persist(self) -> None:
        """Persist current state to StateManager."""
        with self._lock:
            state_data = {
                "todos": {k: v.to_dict() for k, v in self.todos.items()},
                "dag_state": self.dag.to_dict(),
                "stats": self._stats,
            }
            
            state_key = f"{self.name}-state"
            
            # Try to read existing state to determine if we need create or update
            existing_state = self.state_manager.read_state(state_key)
            
            if existing_state is None:
                # Create new state
                self.state_manager.create_state(
                    key=state_key,
                    value=state_data,
                    metadata={"orchestrator": self.name}
                )
            else:
                # Update existing state with optimistic locking
                self.state_manager.update_state(
                    key=state_key,
                    value=state_data,
                    expected_version=existing_state["version"],
                    metadata={"orchestrator": self.name, "updated_at": datetime.utcnow().isoformat()}
                )
            
            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.STATE_MANAGEMENT,
                component="todo_orchestrator",
                operation="persist",
                message=f"Persisted orchestrator state",
                context={"todo_count": len(self.todos)},
            )
    
    def load(self) -> None:
        """Load state from StateManager."""
        with self._lock:
            state_key = f"{self.name}-state"
            state_result = self.state_manager.read_state(state_key)
            
            if state_result:
                state_data = state_result["value"]
                
                # Restore TODOs
                self.todos = {
                    k: Todo.from_dict(v)
                    for k, v in state_data.get("todos", {}).items()
                }
                
                # Restore DAG
                dag_state = state_data.get("dag_state")
                if dag_state:
                    self.dag = DAG.from_dict(dag_state)
                
                # Restore statistics
                self._stats.update(state_data.get("stats", {}))
                
                # Audit log
                self.audit_logger.log(
                    level=AuditLevel.INFO,
                    category=AuditCategory.STATE_MANAGEMENT,
                    component="todo_orchestrator",
                    operation="load",
                    message=f"Loaded orchestrator state (version {state_result['version']})",
                    context={
                        "todo_count": len(self.todos),
                        "version": state_result["version"]
                    },
                )
    
    # ==========================================================================
    # STATISTICS
    # ==========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        with self._lock:
            return {
                **self._stats,
                "total_todos": len(self.todos),
                "ready_todos": len(self.get_ready_tasks()),
                "in_progress": len([t for t in self.todos.values() if t.status == TodoStatus.IN_PROGRESS]),
                "blocked": len([t for t in self.todos.values() if t.status == TodoStatus.BLOCKED]),
            }

    # ==========================================================================
    # YAML LOADING (Phase 4, task-2.4.1)
    # ==========================================================================
    
    def load_from_yaml(self, yaml_path: str) -> List[Todo]:
        """Load TODOs from a YAML feature file.
        
        Args:
            yaml_path: Path to the YAML feature file
            
        Returns:
            List of created Todo objects
            
        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        # Load YAML file
        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Parse feature YAML
        tasks = self._parse_feature_yaml(data)
        
        # Build DAG from tasks
        task_mapping = self._build_dag_from_tasks(tasks)
        
        # Create TODO objects
        todos = []
        for task_id, todo_id in task_mapping.items():
            todo = self.read_todo(todo_id)
            todos.append(todo)
        
        # Log operation
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="todo_orchestrator",
            operation="load_from_yaml",
            message=f"Loaded {len(todos)} TODOs from YAML",
            context={"yaml_path": yaml_path, "todo_count": len(todos)},
        )
        
        return todos
    
    def _parse_feature_yaml(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse feature YAML data into task list.
        
        Args:
            data: Parsed YAML data
            
        Returns:
            List of task dictionaries with id, name, priority, dependencies
        """
        tasks = []
        feature = data.get("feature", {})
        phases = feature.get("phases", [])
        
        for phase in phases:
            phase_tasks = phase.get("tasks", [])
            for task in phase_tasks:
                tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "priority": task.get("priority", "P2_MEDIUM"),
                    "estimated_minutes": task.get("estimated_minutes", 60),
                    "dependencies": task.get("dependencies", []),
                    "description": task.get("description", ""),
                })
        
        return tasks
    
    def _build_dag_from_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, str]:
        """Build DAG and create TODOs from task list.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Mapping of task IDs to TODO IDs
        """
        task_mapping = {}
        
        # First pass: Create all TODOs (without dependencies)
        for task in tasks:
            task_id = task["id"]
            priority_str = task["priority"]
            
            # Convert priority string to Priority enum
            try:
                priority = Priority[priority_str]
            except KeyError:
                priority = Priority.P2_MEDIUM
            
            # Create TODO
            todo_id = self.create_todo(
                title=task["name"],
                description=task.get("description", ""),
                priority=priority,
                data={
                    "task_id": task_id,
                    "estimated_minutes": task.get("estimated_minutes", 60),
                },
            )
            task_mapping[task_id] = todo_id
        
        # Second pass: Add dependencies
        for task in tasks:
            task_id = task["id"]
            todo_id = task_mapping[task_id]
            dependencies = task.get("dependencies", [])
            
            # Resolve dependencies
            resolved_deps = self._resolve_dependencies(dependencies, task_mapping)
            
            # Add edges to DAG
            for dep_id in resolved_deps:
                self.dag.add_edge(dep_id, todo_id)
            
            # Update TODO status based on dependencies
            todo = self.read_todo(todo_id)
            if resolved_deps:
                todo.status = TodoStatus.BLOCKED
                self.dag.set_node_status(todo_id, NodeStatus.BLOCKED)
            else:
                # No dependencies - mark as READY
                todo.status = TodoStatus.READY
                self.dag.set_node_status(todo_id, NodeStatus.NOT_STARTED)
            self.todos[todo_id] = todo
        
        return task_mapping
    
    def _resolve_dependencies(
        self, 
        task_deps: List[str], 
        task_mapping: Dict[str, str]
    ) -> List[str]:
        """Resolve task IDs to TODO IDs.
        
        Args:
            task_deps: List of task IDs
            task_mapping: Mapping of task IDs to TODO IDs
            
            
        Returns:
            List of TODO IDs
        """
        resolved = []
        for task_id in task_deps:
            if task_id in task_mapping:
                resolved.append(task_mapping[task_id])
        return resolved
    
    # ==========================================================================
    # FEAT04 PHASE 2: INTEGRATION METHODS
    # ==========================================================================
    
    def create_todos_from_plan(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create TODOs from a plan specification.
        
        This is a simplified implementation for feat04 Phase 2 integration.
        Full implementation with governance integration TBD in CORTEX 6.1.
        
        Args:
            plan_data: Plan specification with phases and tasks
            
        Returns:
            List of created TODO dictionaries
        """
        todos = []
        
        phases = plan_data.get("phases", [])
        for phase in phases:
            phase_id = phase.get("id")
            phase_name = phase.get("name", f"Phase {phase_id}")
            tasks = phase.get("tasks", [])
            
            for task in tasks:
                task_id = task.get("id")
                task_name = task.get("name", f"Task {task_id}")
                dependencies = task.get("dependencies", [])
                
                # Create TODO
                todo_id = self.create_todo(
                    title=f"[{phase_name}] {task_name}",
                    description=task.get("description", ""),
                    priority=Priority.P2_MEDIUM,
                    tags={f"phase-{phase_id}", "from-plan"},
                    metadata={"task_id": task_id, "phase_id": phase_id}
                )
                
                # Store task_id -> todo_id mapping for dependencies
                if not hasattr(self, '_task_id_mapping'):
                    self._task_id_mapping = {}
                self._task_id_mapping[task_id] = todo_id
                
                todos.append({
                    "todo_id": todo_id,
                    "task_id": task_id,
                    "phase_id": phase_id,
                    "status": "NOT_STARTED"
                })
        
        # Add dependencies after all TODOs created
        for phase in phases:
            for task in phase.get("tasks", []):
                task_id = task.get("id")
                dependencies = task.get("dependencies", [])
                
                if task_id in self._task_id_mapping and dependencies:
                    todo_id = self._task_id_mapping[task_id]
                    
                    for dep_task_id in dependencies:
                        if dep_task_id in self._task_id_mapping:
                            dep_todo_id = self._task_id_mapping[dep_task_id]
                            self.add_dependency(todo_id, dep_todo_id)
        
        return todos
    
    def mark_task_completed(self, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier (can be TODO ID or task_id from plan)
            result: Completion result data
            
        Returns:
            Result dictionary with success status
        """
        # Resolve task_id to todo_id if needed
        todo_id = task_id
        if hasattr(self, '_task_id_mapping') and task_id in self._task_id_mapping:
            todo_id = self._task_id_mapping[task_id]
        
        # Check if TODO exists
        if todo_id not in self.todos:
            raise ValueError(f"Task {task_id} not found")
        
        # Transition to completed
        self.transition_status(todo_id, TodoStatus.COMPLETED)
        
        # Store result in metadata
        todo = self.todos[todo_id]
        todo.metadata["completion_result"] = result
        
        return {
            "success": True,
            "task_id": task_id,
            "todo_id": todo_id,
            "status": "COMPLETED",
            "result": result
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a task.
        
        Args:
            task_id: Task identifier (can be TODO ID or task_id from plan)
            
        Returns:
            Status dictionary
        """
        # Resolve task_id to todo_id if needed
        todo_id = task_id
        if hasattr(self, '_task_id_mapping') and task_id in self._task_id_mapping:
            todo_id = self._task_id_mapping[task_id]
        
        # Check if TODO exists
        if todo_id not in self.todos:
            raise ValueError(f"Task {task_id} not found")
        
        todo = self.todos[todo_id]
        
        return {
            "task_id": task_id,
            "todo_id": todo_id,
            "status": todo.status.value,
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority.value,
            "created_at": todo.created_at.isoformat(),
            "updated_at": todo.updated_at.isoformat(),
            "metadata": todo.metadata
        }

