"""
TodoManager - Task Tracking and Persistence
===========================================
Creates trackable tasks from MasterOrchestrator's required_actions and persists
execution state to progress-tracker.json with full audit trail.

Phase: 2
AC-IDs: AC-TODO-001, AC-TODO-002, AC-TODO-003, AC-TODO-004
TDD Phase: RED→GREEN

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-13
"""

import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Literal
from pathlib import Path
from datetime import datetime, timezone

from src.orchestrators.audit_logger import get_audit_logger, AuditCategory
from src.orchestrators.state_manager import StateManager


# AC-TODO-001: Create Trackable Tasks
@dataclass
class Task:
    """Represents a trackable task from required_actions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ac_id: str = ""
    title: str = ""
    description: str = ""
    status: Literal["not-started", "in-progress", "blocked", "completed"] = "not-started"
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    blocked_reason: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # List of AC-IDs or Task IDs
    evidence_bundle: Optional[Dict[str, Any]] = None


class TodoManager:
    """
    TodoManager - Task Tracking System
    
    Capabilities:
    - AC-TODO-001: Create trackable tasks from required_actions
    - AC-TODO-002: Persist to progress-tracker.json
    - AC-TODO-003: Status tracking (not-started, in-progress, blocked, completed)
    - AC-TODO-004: Dependency order enforcement
    """
    
    def __init__(self, state_manager: StateManager, workspace_root: Optional[Path] = None):
        """
        Initialize TodoManager
        
        Args:
            state_manager: StateManager instance for persistence
            workspace_root: Optional workspace root (defaults to Path.cwd())
        """
        self.state_manager = state_manager
        self.workspace_root = workspace_root or Path.cwd()
        self.logger = get_audit_logger()
        
        # Track active tasks in memory
        self.tasks: Dict[str, Task] = {}
        
        # Progress tracker file path
        self.tracker_file = self.workspace_root / "cortex-brain" / "tier1" / "tracking" / "progress-tracker.json"
        
        self._initialize()
    
    def _initialize(self):
        """Initialize TodoManager from existing state"""
        self.logger.log(
            level="INFO",
            category=AuditCategory.ORCHESTRATOR,
            message="TodoManager initialized",
            details={
                "tracker_file": str(self.tracker_file),
                "state_manager": type(self.state_manager).__name__
            }
        )
    
    # AC-TODO-001: Create Trackable Tasks
    def create_tasks_from_actions(self, ac_id: str, required_actions: List[Dict[str, Any]], 
                                  priority: str = "MEDIUM") -> List[Task]:
        """
        Create trackable tasks from MasterOrchestrator's required_actions
        
        Args:
            ac_id: Parent AC-ID triggering the actions
            required_actions: List of action dicts from governance
            priority: Task priority level
        
        Returns:
            List of created Task objects
        
        Raises:
            ValueError: If required_actions format is invalid
        """
        if not required_actions or not isinstance(required_actions, list):
            raise ValueError("required_actions must be a non-empty list")
        
        created_tasks = []
        
        for action in required_actions:
            if not isinstance(action, dict):
                raise ValueError(f"Action must be dict, got {type(action)}")
            
            task = Task(
                ac_id=ac_id,
                title=action.get("name", f"Action from {ac_id}"),
                description=action.get("description", ""),
                priority=action.get("priority", priority),
                dependencies=action.get("dependencies", [])
            )
            
            self.tasks[task.id] = task
            created_tasks.append(task)
            
            self.logger.log(
                level="INFO",
                category=AuditCategory.ORCHESTRATOR,
                ac_id=ac_id,
                message="Task created",
                details={
                    "task_id": task.id,
                    "title": task.title,
                    "priority": task.priority
                }
            )
        
        return created_tasks
    
    # AC-TODO-002: Persist to Tracker
    def persist_to_tracker(self, ac_id: str) -> bool:
        """
        Persist current task state to progress-tracker.json
        
        Args:
            ac_id: AC-ID being tracked
        
        Returns:
            True if successfully persisted, False otherwise
        """
        try:
            if not self.tracker_file.exists():
                self.logger.log(
                    level="WARNING",
                    category=AuditCategory.ORCHESTRATOR,
                    ac_id=ac_id,
                    message="progress-tracker.json not found",
                    details={"tracker_file": str(self.tracker_file)}
                )
                return False
            
            # Read existing tracker
            tracker_data = json.loads(self.tracker_file.read_text())
            
            # Update current_phase with task status summary
            current_phase = tracker_data.get("current_phase", {})
            current_phase["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Count task statuses
            task_counts = {
                "not_started": len([t for t in self.tasks.values() if t.status == "not-started"]),
                "in_progress": len([t for t in self.tasks.values() if t.status == "in-progress"]),
                "blocked": len([t for t in self.tasks.values() if t.status == "blocked"]),
                "completed": len([t for t in self.tasks.values() if t.status == "completed"])
            }
            
            current_phase["tasks"] = {
                "total": len(self.tasks),
                "counts": task_counts,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            tracker_data["current_phase"] = current_phase
            
            # Atomic write with backup
            backup_file = self.tracker_file.with_suffix(".json.bak")
            if self.tracker_file.exists():
                backup_file.write_text(self.tracker_file.read_text())
            
            self.tracker_file.write_text(json.dumps(tracker_data, indent=2))
            
            self.logger.log(
                level="INFO",
                category=AuditCategory.ORCHESTRATOR,
                ac_id=ac_id,
                message="Task state persisted to tracker",
                details={
                    "total_tasks": len(self.tasks),
                    "counts": task_counts
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log(
                level="ERROR",
                category=AuditCategory.ORCHESTRATOR,
                ac_id=ac_id,
                message="Failed to persist to tracker",
                details={
                    "error": str(e),
                    "tracker_file": str(self.tracker_file)
                }
            )
            return False
    
    # AC-TODO-003: Status Tracking
    def update_task_status(self, task_id: str, status: Literal["not-started", "in-progress", "blocked", "completed"],
                          blocked_reason: Optional[str] = None) -> bool:
        """
        Update task status with timestamp tracking
        
        Args:
            task_id: ID of task to update
            status: New status value
            blocked_reason: Reason if status is "blocked"
        
        Returns:
            True if updated successfully
        """
        if task_id not in self.tasks:
            self.logger.log(
                level="ERROR",
                category=AuditCategory.ORCHESTRATOR,
                message="Task not found",
                details={"task_id": task_id}
            )
            return False
        
        task = self.tasks[task_id]
        old_status = task.status
        
        # Update timestamps
        if status == "in-progress" and task.started_at is None:
            task.started_at = datetime.now(timezone.utc).isoformat()
        elif status == "completed":
            task.completed_at = datetime.now(timezone.utc).isoformat()
        
        # Set blocked reason if needed
        if status == "blocked":
            task.blocked_reason = blocked_reason
        
        task.status = status
        
        self.logger.log(
            level="INFO",
            category=AuditCategory.ORCHESTRATOR,
            ac_id=task.ac_id,
            message="Task status updated",
            details={
                "task_id": task_id,
                "old_status": old_status,
                "new_status": status,
                "blocked_reason": blocked_reason
            }
        )
        
        return True
    
    # AC-TODO-004: Dependency Enforcement
    def get_executable_tasks(self) -> List[Task]:
        """
        Get tasks that are ready to execute (no unmet dependencies)
        
        Returns:
            List of Task objects ready to execute in order
        """
        completed_ac_ids = set()  # AC-IDs marked as completed
        
        # Build graph of unmet dependencies
        executable = []
        for task_id, task in self.tasks.items():
            if task.status != "not-started":
                continue  # Skip non-waiting tasks
            
            # Check if all dependencies are met
            unmet_deps = []
            for dep in task.dependencies:
                if dep not in completed_ac_ids:
                    unmet_deps.append(dep)
            
            if not unmet_deps:
                executable.append(task)
        
        self.logger.log(
            level="INFO",
            category=AuditCategory.ORCHESTRATOR,
            message="Executable tasks identified",
            details={
                "total_waiting": len([t for t in self.tasks.values() if t.status == "not-started"]),
                "executable": len(executable)
            }
        )
        
        return sorted(executable, key=lambda t: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[t.priority])
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get all currently blocked tasks"""
        blocked = [t for t in self.tasks.values() if t.status == "blocked"]
        return blocked
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_ac_id(self, ac_id: str) -> List[Task]:
        """Get all tasks for a given AC-ID"""
        return [t for t in self.tasks.values() if t.ac_id == ac_id]
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all task statuses"""
        statuses = {
            "not_started": 0,
            "in_progress": 0,
            "blocked": 0,
            "completed": 0
        }
        
        for task in self.tasks.values():
            statuses[task.status.replace("-", "_")] += 1
        
        return {
            "total": len(self.tasks),
            "statuses": statuses,
            "summary": {
                "percent_complete": round(100 * statuses["completed"] / len(self.tasks), 2) if self.tasks else 0,
                "blocked_count": statuses["blocked"],
                "in_progress_count": statuses["in_progress"]
            }
        }
