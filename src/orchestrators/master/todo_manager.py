"""
TodoManager - Real-time task tracking with governance-aware task creation.

AC-TODO-001: Core task tracking (PENDING → IN_PROGRESS → COMPLETE/FAILED/BLOCKED)
AC-TODO-002: Task creation from governance evaluation output

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Task:
    """Task definition."""
    id: str
    name: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    ac_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "dependencies": self.dependencies,
            "ac_id": self.ac_id
        }


@dataclass
class GovernanceEvaluationResult:
    """Result from governance evaluation (input to task creation)."""
    request_valid: bool
    violations: List[str]
    required_actions: List[str]
    governance_rules_applied: List[str]
    tier_precedence: Dict[str, int]


class TodoManager:
    """
    Real-time task tracking manager.
    
    Features:
    - Create tasks from governance evaluation (AC-TODO-002)
    - Track task lifecycle (PENDING → IN_PROGRESS → COMPLETE/FAILED/BLOCKED)
    - Support task dependencies and blocking
    - Provide task statistics and queries
    """
    
    def __init__(self):
        """Initialize todo manager."""
        self.logger = logging.getLogger("cortex.orchestrators.master.todo_manager")
        self.tasks: Dict[str, Task] = {}
        self.task_order: List[str] = []  # Track creation order
    
    # AC-TODO-001: Core task tracking
    
    def create_task(
        self,
        name: str,
        description: Optional[str] = None,
        priority: 'TaskPriority' = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        ac_id: Optional[str] = None
    ) -> Task:
        """Create new task with full lifecycle support."""
        if priority is None:
            priority = TaskPriority.MEDIUM
        
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            id=task_id,
            name=name,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            dependencies=dependencies or [],
            ac_id=ac_id
        )
        
        self.tasks[task_id] = task
        self.task_order.append(task_id)
        
        self.logger.debug(
            f"Created task {task_id}",
            extra={
                "task_id": task_id,
                "name": name,
                "priority": priority.name,
                "ac_id": ac_id
            }
        )
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].updated_at = datetime.now()
            self.logger.debug(
                f"Updated task status",
                extra={"task_id": task_id, "status": status.value}
            )
    
    def update_task(self, task_id: str, status: TaskStatus) -> None:
        """Update task status (legacy method)."""
        self.update_task_status(task_id, status)
    
    def start_task(self, task_id: str) -> None:
        """Mark task as in progress."""
        self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
    
    def complete_task(self, task_id: str) -> None:
        """Mark task as complete."""
        self.update_task_status(task_id, TaskStatus.COMPLETE)
    
    def fail_task(self, task_id: str, reason: Optional[str] = None) -> None:
        """Mark task as failed."""
        self.update_task_status(task_id, TaskStatus.FAILED)
        if reason:
            task = self.get_task(task_id)
            if task:
                task.metadata["failure_reason"] = reason
    
    def block_task(self, task_id: str, reason: Optional[str] = None) -> None:
        """Mark task as blocked."""
        self.update_task_status(task_id, TaskStatus.BLOCKED)
        if reason:
            task = self.get_task(task_id)
            if task:
                task.metadata["block_reason"] = reason
    
    # AC-TODO-002: Task creation from governance evaluation
    
    def create_tasks_from_governance_evaluation(
        self,
        evaluation: GovernanceEvaluationResult,
        request_id: str,
        user_intent: str,
        priority_mapping: Optional[Dict[str, TaskPriority]] = None
    ) -> List[Task]:
        """
        Create tasks from governance evaluation result.
        
        This is the core of AC-TODO-002: converts governance evaluation
        (violations and required_actions) into actionable tasks.
        
        Args:
            evaluation: GovernanceEvaluationResult with violations and actions
            request_id: Correlation ID for audit trail
            user_intent: User's original request
            priority_mapping: Optional mapping of action names to priorities
            
        Returns:
            List of created tasks
        """
        created_tasks = []
        priority_mapping = priority_mapping or self._default_priority_mapping()
        
        self.logger.info(
            f"Creating tasks from governance evaluation",
            extra={
                "request_id": request_id,
                "required_actions": len(evaluation.required_actions),
                "violations": len(evaluation.violations)
            }
        )
        
        # Create task for each required action
        for idx, action in enumerate(evaluation.required_actions):
            priority = priority_mapping.get(action, TaskPriority.MEDIUM)
            
            task = self.create_task(
                name=action,
                description=f"Action required: {action}",
                priority=priority,
                metadata={
                    "request_id": request_id,
                    "user_intent": user_intent,
                    "action_index": idx,
                    "governance_rules": evaluation.governance_rules_applied,
                    "tier_precedence": evaluation.tier_precedence
                }
            )
            created_tasks.append(task)
        
        # Create tasks for violations (if any)
        if evaluation.violations:
            for violation in evaluation.violations:
                task = self.create_task(
                    name=f"ADDRESS_VIOLATION: {violation[:50]}",
                    description=f"Governance violation: {violation}",
                    priority=TaskPriority.CRITICAL,
                    metadata={
                        "request_id": request_id,
                        "violation": violation,
                        "type": "governance_violation"
                    }
                )
                created_tasks.append(task)
        
        self.logger.info(
            f"Created {len(created_tasks)} tasks from governance evaluation",
            extra={
                "request_id": request_id,
                "total_tasks": len(created_tasks)
            }
        )
        
        return created_tasks
    
    def _default_priority_mapping(self) -> Dict[str, TaskPriority]:
        """Get default priority mapping for common actions."""
        return {
            "LOAD_CONTEXT": TaskPriority.HIGH,
            "GENERATE_PLAN": TaskPriority.HIGH,
            "CREATE_FILE": TaskPriority.HIGH,
            "WRITE_TESTS": TaskPriority.HIGH,
            "RUN_TESTS": TaskPriority.MEDIUM,
            "UPDATE_TRACKER": TaskPriority.MEDIUM,
            "SYNC_DASHBOARD": TaskPriority.LOW,
            "VALIDATE_AC_IDS": TaskPriority.MEDIUM,
            "ROUTE_REQUEST": TaskPriority.HIGH,
            "EXECUTE": TaskPriority.MEDIUM,
            "GENERATE_COVERAGE": TaskPriority.LOW,
            "RUN_VALIDATION": TaskPriority.MEDIUM,
            "VERIFY_EVIDENCE": TaskPriority.MEDIUM,
            "CONNECT_ADO": TaskPriority.HIGH,
            "LOAD_WORKITEMS": TaskPriority.MEDIUM,
            "CREATE_WORKITEMS": TaskPriority.HIGH,
            "UPDATE_WORKITEMS": TaskPriority.MEDIUM,
        }
    
    # Task queries and statistics
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def get_in_progress_tasks(self) -> List[Task]:
        """Get all in-progress tasks."""
        return self.get_tasks_by_status(TaskStatus.IN_PROGRESS)
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return self.get_tasks_by_status(TaskStatus.COMPLETE)
    
    def get_failed_tasks(self) -> List[Task]:
        """Get all failed tasks."""
        return self.get_tasks_by_status(TaskStatus.FAILED)
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get all blocked tasks."""
        return self.get_tasks_by_status(TaskStatus.BLOCKED)
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get all tasks with specific priority."""
        return [t for t in self.tasks.values() if t.priority == priority]
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get overall task statistics."""
        total = len(self.tasks)
        by_status = {
            "pending": len(self.get_pending_tasks()),
            "in_progress": len(self.get_in_progress_tasks()),
            "complete": len(self.get_completed_tasks()),
            "failed": len(self.get_failed_tasks()),
            "blocked": len(self.get_blocked_tasks())
        }
        
        completion_rate = (
            (by_status["complete"] / total * 100) if total > 0 else 0
        )
        
        return {
            "total_tasks": total,
            "by_status": by_status,
            "completion_rate": round(completion_rate, 2),
            "completion_percentage": round(completion_rate, 2)
        }
    
    def get_blocked_task_reasons(self) -> Dict[str, str]:
        """Get reasons for all blocked tasks."""
        reasons = {}
        for task in self.get_blocked_tasks():
            reasons[task.id] = task.metadata.get("block_reason", "Unknown")
        return reasons
    
    def list_all_tasks(self) -> List[Task]:
        """Get all tasks in creation order."""
        return [self.tasks[task_id] for task_id in self.task_order]
    
    def export_tasks_as_json(self) -> List[Dict[str, Any]]:
        """Export all tasks as JSON-serializable list."""
        return [task.to_dict() for task in self.list_all_tasks()]
    
    def clear_tasks(self) -> None:
        """Clear all tasks (for testing)."""
        self.tasks.clear()
        self.task_order.clear()
        self.logger.debug("Cleared all tasks")
