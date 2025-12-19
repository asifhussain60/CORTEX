# task_injection_manager

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


## Table of Contents

### Classes
- [TaskPriority](#taskpriority)
- [TaskStatus](#taskstatus)
- [TaskInjectionManager](#taskinjectionmanager)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** datetime, enum, logging, queue, threading, time, typing, uuid


## Classes

### TaskPriority

```python
class TaskPriority(Enum)
```

Task priority levels



---

### TaskStatus

```python
class TaskStatus(Enum)
```

Task status lifecycle



---

### TaskInjectionManager

```python
class TaskInjectionManager
```

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


**Methods:**

  #### `inject_task`

  ```python
  inject_task(self, description: str, priority: str, metadata: Optional[Dict[str, Any]]) -> str
  ```

  Inject a new task into the queue.

Args:
    description: Task description
    priority: Task priority ("HIGH", "MEDIUM", "LOW") - default: "MEDIUM"
    metadata: Optional metadata dictionary

Returns:
    task_id for tracking

  **Parameters:**

  - `self`
  - `description` (str): Task description
  - `priority` (str) = `'MEDIUM'`: Task priority ("HIGH", "MEDIUM", "LOW") - default: "MEDIUM"
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Optional metadata dictionary


  **Returns:** str
    task_id for tracking


  #### `get_next_task`

  ```python
  get_next_task(self) -> Optional[Dict[str, Any]]
  ```

  Get next task from queue (priority-ordered, FIFO within priority).

Returns:
    Task dictionary or None if queue is empty

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]
    Task dictionary or None if queue is empty


  #### `mark_complete`

  ```python
  mark_complete(self, task_id: str, result: Optional[str], metadata: Optional[Dict[str, Any]]) -> bool
  ```

  Mark task as completed.

Args:
    task_id: Task ID to mark complete
    result: Optional result description
    metadata: Optional additional metadata

Returns:
    True if marked successfully, False if task not found

  **Parameters:**

  - `self`
  - `task_id` (str): Task ID to mark complete
  - `result` (Optional[str]) = `None`: Optional result description
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Optional additional metadata


  **Returns:** bool
    True if marked successfully, False if task not found


  #### `get_task_status`

  ```python
  get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]
  ```

  Get current status of a task.

Args:
    task_id: Task ID to query

Returns:
    Task status dictionary or None if not found

  **Parameters:**

  - `self`
  - `task_id` (str): Task ID to query


  **Returns:** Optional[Dict[str, Any]]
    Task status dictionary or None if not found


  #### `get_all_tasks`

  ```python
  get_all_tasks(self) -> List[Dict[str, Any]]
  ```

  Get all tasks with their current statuses.

Returns:
    List of task dictionaries

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of task dictionaries


  #### `render_task_list_for_progress`

  ```python
  render_task_list_for_progress(self, renderer: Any) -> str
  ```

  Render injected tasks for ProgressRenderer integration.

Args:
    renderer: ProgressRenderer instance

Returns:
    Formatted string showing injected tasks

  **Parameters:**

  - `self`
  - `renderer` (Any): ProgressRenderer instance


  **Returns:** str
    Formatted string showing injected tasks


  #### `handle_keyboard_injection`

  ```python
  handle_keyboard_injection(self) -> Optional[str]
  ```

  Handle keyboard interrupt for mid-execution task injection.

Prompts user for task description and injects as HIGH priority.

Returns:
    task_id if injected, None if cancelled

  **Parameters:**

  - `self`


  **Returns:** Optional[str]
    task_id if injected, None if cancelled



---
