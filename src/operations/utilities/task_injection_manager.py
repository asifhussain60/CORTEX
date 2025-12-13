"""
Task Injection Manager - Feature 12 (Context-Aware Task Injection)

**Purpose:** Enable mid-execution task injection during orchestrator workflows without interrupting execution.

**Features:**
- Priority-based task queue (HIGH → MEDIUM → LOW)
- Thread-safe concurrent injection
- FIFO ordering within same priority
- Status tracking (pending/in-progress/completed)
- ProgressRenderer integration
- Keyboard interrupt handling (Ctrl+T simulation)
- <10ms injection overhead

**Usage:**
    from src.operations.utilities import TaskInjectionManager
    
    manager = TaskInjectionManager()
    
    # Inject high-priority task
    task_id = manager.inject_task(
        description="Add missing error handling",
        priority="HIGH"
    )
    
    # Get next task (priority-ordered)
    task = manager.get_next_task()
    
    # Mark complete
    manager.mark_complete(task_id, result="Success")

**Author:** Asif Hussain
**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 12
"""

import uuid
import queue
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskStatus(Enum):
    """Task status lifecycle"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskInjectionManager:
    """
    Thread-safe task injection manager for orchestrator workflows.
    
    **Features:**
    - Priority queue with FIFO ordering within same priority
    - Thread-safe operations (queue.PriorityQueue)
    - Status tracking throughout task lifecycle
    - ProgressRenderer integration for visual feedback
    - Keyboard interrupt handling for mid-execution injection
    
    **Performance:**
    - inject_task: <10ms
    - get_next_task: <10ms
    """
    
    def __init__(self):
        """Initialize task injection manager."""
        # Priority queue: (priority_value, timestamp, task_id, task_data)
        self._task_queue = queue.PriorityQueue()
        
        # Task tracking dictionary: {task_id: task_metadata}
        self._tasks: Dict[str, Dict[str, Any]] = {}
        
        # Thread lock for task metadata access
        self._tasks_lock = threading.Lock()
    
    def inject_task(
        self,
        description: str,
        priority: str = "MEDIUM",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Inject a new task into the queue.
        
        Args:
            description: Task description
            priority: Task priority ("HIGH", "MEDIUM", "LOW") - default: "MEDIUM"
            metadata: Optional metadata dictionary
        
        Returns:
            task_id for tracking
        """
        start_time = time.time()
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Map priority string to enum value
        priority_enum = TaskPriority[priority.upper()]
        
        # Create task data
        task_data = {
            "task_id": task_id,
            "description": description,
            "priority": priority.upper(),
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "metadata": metadata or {}
        }
        
        # Store in tracking dictionary
        with self._tasks_lock:
            self._tasks[task_id] = task_data
        
        # Add to priority queue (priority_value, timestamp, task_id)
        # Lower priority_value = higher priority (HIGH=1, MEDIUM=2, LOW=3)
        # Timestamp ensures FIFO within same priority
        self._task_queue.put((
            priority_enum.value,
            time.time(),
            task_id,
            task_data
        ))
        
        # Performance tracking
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > 10:
            logger.warning(f"inject_task exceeded 10ms: {elapsed_ms:.2f}ms")
        
        return task_id
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Get next task from queue (priority-ordered, FIFO within priority).
        
        Returns:
            Task dictionary or None if queue is empty
        """
        start_time = time.time()
        
        try:
            # Non-blocking get with 0.1 second timeout
            priority_value, timestamp, task_id, task_data = self._task_queue.get(timeout=0.1)
            
            # Update status to in_progress
            with self._tasks_lock:
                if task_id in self._tasks:
                    self._tasks[task_id]["status"] = TaskStatus.IN_PROGRESS.value
                    self._tasks[task_id]["started_at"] = datetime.now().isoformat()
                    task_data = self._tasks[task_id].copy()
            
            # Performance tracking
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > 10:
                logger.warning(f"get_next_task exceeded 10ms: {elapsed_ms:.2f}ms")
            
            return task_data
        
        except queue.Empty:
            return None
    
    def mark_complete(
        self,
        task_id: str,
        result: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark task as completed.
        
        Args:
            task_id: Task ID to mark complete
            result: Optional result description
            metadata: Optional additional metadata
        
        Returns:
            True if marked successfully, False if task not found
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                return False
            
            self._tasks[task_id]["status"] = TaskStatus.COMPLETED.value
            self._tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self._tasks[task_id]["result"] = result
            
            if metadata:
                self._tasks[task_id]["metadata"].update(metadata)
        
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a task.
        
        Args:
            task_id: Task ID to query
        
        Returns:
            Task status dictionary or None if not found
        """
        with self._tasks_lock:
            if task_id not in self._tasks:
                return None
            
            return self._tasks[task_id].copy()
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks with their current statuses.
        
        Returns:
            List of task dictionaries
        """
        with self._tasks_lock:
            return [task.copy() for task in self._tasks.values()]
    
    def render_task_list_for_progress(self, renderer: Any) -> str:
        """
        Render injected tasks for ProgressRenderer integration.
        
        Args:
            renderer: ProgressRenderer instance
        
        Returns:
            Formatted string showing injected tasks
        """
        with self._tasks_lock:
            tasks = list(self._tasks.values())
        
        if not tasks:
            return ""
        
        # Sort by priority and timestamp
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        tasks.sort(key=lambda t: (
            priority_order.get(t["priority"], 1),
            t["created_at"]
        ))
        
        lines = ["\n💉 Injected Tasks:"]
        
        for task in tasks:
            status_icon = {
                "pending": "⏸️",
                "in_progress": "🔄",
                "completed": "✅"
            }.get(task["status"], "❓")
            
            priority_icon = {
                "HIGH": "🔴",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }.get(task["priority"], "⚪")
            
            lines.append(
                f"  {status_icon} {priority_icon} {task['description'][:50]}"
            )
        
        return "\n".join(lines)
    
    def handle_keyboard_injection(self) -> Optional[str]:
        """
        Handle keyboard interrupt for mid-execution task injection.
        
        Prompts user for task description and injects as HIGH priority.
        
        Returns:
            task_id if injected, None if cancelled
        """
        try:
            description = input("\n💉 Inject task (or press Enter to cancel): ")
            
            if not description or not description.strip():
                print("   Cancelled.")
                return None
            
            task_id = self.inject_task(description.strip(), priority="HIGH")
            print(f"   ✅ Task injected: {task_id[:8]}")
            
            return task_id
        
        except (KeyboardInterrupt, EOFError):
            print("\n   Cancelled.")
            return None
