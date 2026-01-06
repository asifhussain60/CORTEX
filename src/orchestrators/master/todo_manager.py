"""
Master Orchestrator Task Manager

Integrates with GitHub Copilot's manage_todo_list tool for real-time task tracking
across all autonomous orchestrator executions.

This module provides a unified interface for orchestrators to manage tasks, ensuring
consistent task tracking patterns and enabling visual progress updates in Copilot Chat.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0 (CORTEX v5.0 Epic Phase P02.1)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from dataclasses import dataclass, asdict


# Task status types matching GitHub Copilot's manage_todo_list
TaskStatus = Literal["not-started", "in-progress", "completed"]


@dataclass
class Task:
    """
    Represents a single task in the Master Orchestrator's task registry.
    
    Schema matches GitHub Copilot's manage_todo_list tool for seamless integration.
    """
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: int = 2  # 1=High, 2=Medium, 3=Low
    dependencies: List[int] = None
    created_at: str = None
    updated_at: str = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.dependencies is None:
            self.dependencies = []
        
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        data = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in data.items() if v is not None}
    
    def to_copilot_format(self) -> Dict[str, Any]:
        """
        Convert task to GitHub Copilot's manage_todo_list format.
        
        Returns:
            Dictionary with id, title, description, status keys
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status
        }


class TodoManager:
    """
    Manages tasks for Master Orchestrator with GitHub Copilot integration.
    
    Features:
    - CRUD operations (Create, Read, Update, Delete)
    - Priority-based sorting
    - Dependency tracking
    - Real-time JSON persistence
    - GitHub Copilot manage_todo_list format compatibility
    
    Usage:
        manager = TodoManager(plan_dir="path/to/plan")
        
        # Create tasks
        manager.create_task("Setup environment", "Install dependencies and configure")
        manager.create_task("Run tests", "Execute test suite", dependencies=[1])
        
        # Update status
        manager.start_task(1)
        manager.complete_task(1)
        
        # Get tasks for Copilot
        copilot_tasks = manager.get_copilot_format()
    """
    
    def __init__(
        self,
        plan_dir: Optional[Path] = None,
        registry_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize TodoManager.
        
        Args:
            plan_dir: Plan directory (creates tracking/ subdirectory)
            registry_path: Direct path to task-registry.json (overrides plan_dir)
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Determine registry path
        if registry_path:
            self.registry_path = Path(registry_path)
        elif plan_dir:
            tracking_dir = Path(plan_dir) / "tracking"
            tracking_dir.mkdir(parents=True, exist_ok=True)
            self.registry_path = tracking_dir / "task-registry.json"
        else:
            raise ValueError("Either plan_dir or registry_path must be provided")
        
        # Load existing tasks or initialize empty registry
        self.tasks: Dict[int, Task] = {}
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load tasks from JSON registry file."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task = Task(**task_data)
                        self.tasks[task.id] = task
                self.logger.info(f"Loaded {len(self.tasks)} tasks from {self.registry_path}")
            except Exception as e:
                self.logger.error(f"Failed to load tasks: {e}")
                self.tasks = {}
        else:
            self.logger.info("No existing task registry found, starting fresh")
    
    def _save_tasks(self) -> None:
        """Save tasks to JSON registry file."""
        try:
            # Ensure directory exists
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data
            data = {
                "version": "1.0.0",
                "updated_at": datetime.now().isoformat(),
                "task_count": len(self.tasks),
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }
            
            # Write atomically (write to temp, then rename)
            temp_path = self.registry_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.registry_path)
            
            self.logger.debug(f"Saved {len(self.tasks)} tasks to {self.registry_path}")
        except Exception as e:
            self.logger.error(f"Failed to save tasks: {e}")
    
    def create_task(
        self,
        title: str,
        description: str,
        priority: int = 2,
        dependencies: Optional[List[int]] = None,
        status: TaskStatus = "not-started"
    ) -> int:
        """
        Create a new task.
        
        Args:
            title: Task title (short, action-oriented)
            description: Detailed description with context
            priority: 1=High, 2=Medium, 3=Low
            dependencies: List of task IDs that must complete first
            status: Initial status (default: not-started)
        
        Returns:
            Task ID
        """
        # Generate next task ID
        task_id = max(self.tasks.keys(), default=0) + 1
        
        # Create task
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        self._save_tasks()
        
        self.logger.info(f"Created task {task_id}: {title}")
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
        
        Returns:
            True if successful, False if task not found
        """
        task = self.tasks.get(task_id)
        if not task:
            self.logger.warning(f"Task {task_id} not found")
            return False
        
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now().isoformat()
        
        if status == "completed" and not task.completed_at:
            task.completed_at = datetime.now().isoformat()
        
        self._save_tasks()
        self.logger.info(f"Task {task_id} status: {old_status} → {status}")
        return True
    
    def start_task(self, task_id: int) -> bool:
        """Mark task as in-progress."""
        return self.update_task_status(task_id, "in-progress")
    
    def complete_task(self, task_id: int) -> bool:
        """Mark task as completed."""
        return self.update_task_status(task_id, "completed")
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[int] = None,
        sort_by: str = "id"
    ) -> List[Task]:
        """
        List tasks with optional filtering and sorting.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            sort_by: Sort key (id, priority, title, created_at, updated_at)
        
        Returns:
            List of tasks matching criteria
        """
        tasks = list(self.tasks.values())
        
        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        # Sort
        sort_keys = {
            "id": lambda t: t.id,
            "priority": lambda t: (t.priority, t.id),  # Secondary sort by ID
            "title": lambda t: t.title.lower(),
            "created_at": lambda t: t.created_at,
            "updated_at": lambda t: t.updated_at
        }
        
        if sort_by in sort_keys:
            tasks.sort(key=sort_keys[sort_by])
        
        return tasks
    
    def get_copilot_format(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in GitHub Copilot's manage_todo_list format.
        
        Returns:
            List of task dictionaries with id, title, description, status
        """
        return [task.to_copilot_format() for task in self.list_tasks(sort_by="id")]
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get progress summary statistics.
        
        Returns:
            Dictionary with task counts and progress percentage
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        in_progress = sum(1 for t in self.tasks.values() if t.status == "in-progress")
        not_started = sum(1 for t in self.tasks.values() if t.status == "not-started")
        
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "progress_percentage": round(progress_pct, 1)
        }
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            self.logger.info(f"Deleted task {task_id}")
            return True
        return False
    
    def clear_completed(self) -> int:
        """
        Remove all completed tasks.
        
        Returns:
            Number of tasks removed
        """
        completed_ids = [tid for tid, task in self.tasks.items() if task.status == "completed"]
        for tid in completed_ids:
            del self.tasks[tid]
        
        if completed_ids:
            self._save_tasks()
            self.logger.info(f"Cleared {len(completed_ids)} completed tasks")
        
        return len(completed_ids)


# Convenience function for quick integration
def create_todo_manager(plan_dir: Path) -> TodoManager:
    """
    Factory function to create TodoManager for a plan.
    
    Args:
        plan_dir: Plan directory path
    
    Returns:
        TodoManager instance
    """
    return TodoManager(plan_dir=plan_dir)


__all__ = ["TodoManager", "Task", "TaskStatus", "create_todo_manager"]
