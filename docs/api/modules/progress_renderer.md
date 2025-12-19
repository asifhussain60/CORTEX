# progress_renderer

Progress Renderer for Copilot Chat

Renders visual progress bars and phase transitions for autonomous execution.
Designed for real-time visibility during long-running orchestrator operations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0

Features:
- Emoji-rich progress bars (🔄 ✅ ⏱️ 📋)
- Task-level progress updates (<10ms overhead)
- Phase transition markers
- Git checkpoint status display
- Terminal width adaptation

Usage:
    from src.operations.utilities.progress_renderer import ProgressRenderer
    
    renderer = ProgressRenderer()
    
    # After each task completion
    progress_msg = renderer.render_task_progress(
        current=5,
        total=10,
        phase_name="Development",
        current_phase=2,
        total_phases=4,
        task_name="Implement authentication",
        elapsed_time="2m 15s"
    )
    print(progress_msg)
    
    # Between phases
    transition_msg = renderer.render_phase_transition(
        from_phase="Foundation",
        to_phase="Development",
        completed_tasks=5,
        duration="3m 10s",
        checkpoint_created=True,
        checkpoint_name="cortex-checkpoint-phase-1-foundation-20251213-143022"
    )
    print(transition_msg)


## Table of Contents

### Classes
- [ProgressRenderer](#progressrenderer)

### Functions
- [format_elapsed_time](#format_elapsed_time)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** logging, shutil, typing


## Classes

### ProgressRenderer

```python
class ProgressRenderer
```

Renders visual progress bars for Copilot Chat autonomous execution.

Provides real-time feedback during long-running operations with:
- Task-level progress bars
- Phase transition markers
- Git checkpoint status
- Emoji-rich formatting

Performance: <10ms per render


**Methods:**

  #### `render_task_progress`

  ```python
  render_task_progress(self, current: int, total: int, phase_name: str, current_phase: int, total_phases: int, task_name: str, elapsed_time: str, bar_width: Optional[int]) -> str
  ```

  Render task-level progress update.

Args:
    current: Current task number (1-based)
    total: Total tasks
    phase_name: Name of current phase
    current_phase: Current phase number (1-based)
    total_phases: Total phases
    task_name: Current task name
    elapsed_time: Elapsed time string (e.g., "2m 15s")
    bar_width: Optional override for bar width

Returns:
    Formatted progress string for Copilot Chat

Example Output:
    🔄 Phase 2 of 4: Development
    [████████░░] 80% (8/10 tasks) | ⏱️ 2m 15s | 📋 Current: Implement authentication

  **Parameters:**

  - `self`
  - `current` (int): Current task number (1-based)
  - `total` (int): Total tasks
  - `phase_name` (str): Name of current phase
  - `current_phase` (int): Current phase number (1-based)
  - `total_phases` (int): Total phases
  - `task_name` (str): Current task name
  - `elapsed_time` (str): Elapsed time string (e.g., "2m 15s")
  - `bar_width` (Optional[int]) = `None`: Optional override for bar width


  **Returns:** str
    Formatted progress string for Copilot Chat Example Output: 🔄 Phase 2 of 4: Development [████████░░] 80% (8/10 tasks) | ⏱️ 2m 15s | 📋 Current: Implement authentication


  #### `render_phase_transition`

  ```python
  render_phase_transition(self, from_phase: str, to_phase: str, completed_tasks: int, duration: str, checkpoint_created: bool, checkpoint_name: str) -> str
  ```

  Render phase completion and transition to next phase.

Args:
    from_phase: Name of completed phase
    to_phase: Name of next phase
    completed_tasks: Number of tasks completed in phase
    duration: Phase duration string (e.g., "3m 10s")
    checkpoint_created: Whether git checkpoint was created
    checkpoint_name: Name of checkpoint (if created)

Returns:
    Formatted transition string for Copilot Chat

Example Output:
    ✅ Phase 1: Foundation Complete! (5 tasks, 3m 10s)
    ✅ Git checkpoint created: cortex-checkpoint-phase-1-foundation-20251213-143022
    🔄 Starting Phase 2: Development...

  **Parameters:**

  - `self`
  - `from_phase` (str): Name of completed phase
  - `to_phase` (str): Name of next phase
  - `completed_tasks` (int): Number of tasks completed in phase
  - `duration` (str): Phase duration string (e.g., "3m 10s")
  - `checkpoint_created` (bool) = `False`: Whether git checkpoint was created
  - `checkpoint_name` (str) = `''`: Name of checkpoint (if created)


  **Returns:** str
    Formatted transition string for Copilot Chat Example Output: ✅ Phase 1: Foundation Complete! (5 tasks, 3m 10s) ✅ Git checkpoint created: cortex-checkpoint-phase-1-foundation-20251213-143022 🔄 Starting Phase 2: Development...


  #### `render_checkpoint_status`

  ```python
  render_checkpoint_status(self, success: bool, checkpoint_name: str, error_message: str) -> str
  ```

  Render git checkpoint creation status.

Args:
    success: Whether checkpoint was created successfully
    checkpoint_name: Name of checkpoint (if successful)
    error_message: Error message (if failed)

Returns:
    Formatted checkpoint status string

Example Output (Success):
    ✅ Git checkpoint created: cortex-checkpoint-phase-1-foundation-20251213-143022

Example Output (Failure):
    ⚠️ Git checkpoint failed: No changes to commit

  **Parameters:**

  - `self`
  - `success` (bool): Whether checkpoint was created successfully
  - `checkpoint_name` (str) = `''`: Name of checkpoint (if successful)
  - `error_message` (str) = `''`: Error message (if failed)


  **Returns:** str
    Formatted checkpoint status string Example Output (Success): ✅ Git checkpoint created: cortex-checkpoint-phase-1-foundation-20251213-143022 Example Output (Failure): ⚠️ Git checkpoint failed: No changes to commit


  #### `render_completion_summary`

  ```python
  render_completion_summary(self, total_phases: int, total_tasks: int, total_duration: str, checkpoints_created: int) -> str
  ```

  Render final completion summary.

Args:
    total_phases: Total phases executed
    total_tasks: Total tasks completed
    total_duration: Total execution time (e.g., "15m 30s")
    checkpoints_created: Number of git checkpoints created

Returns:
    Formatted completion summary

Example Output:
    🎉 Autonomous Execution Complete!
    ✅ Phases: 4/4
    ✅ Tasks: 47/47
    ⏱️ Duration: 15m 30s
    📍 Checkpoints: 4

  **Parameters:**

  - `self`
  - `total_phases` (int): Total phases executed
  - `total_tasks` (int): Total tasks completed
  - `total_duration` (str): Total execution time (e.g., "15m 30s")
  - `checkpoints_created` (int): Number of git checkpoints created


  **Returns:** str
    Formatted completion summary Example Output: 🎉 Autonomous Execution Complete! ✅ Phases: 4/4 ✅ Tasks: 47/47 ⏱️ Duration: 15m 30s 📍 Checkpoints: 4



---

## Functions

### format_elapsed_time

```python
format_elapsed_time(seconds: float) -> str
```

Format elapsed time for display.

Args:
    seconds: Elapsed time in seconds

Returns:
    Formatted time string (e.g., "2m 15s", "1h 5m", "45s")

Examples:
    format_elapsed_time(45) -> "45s"
    format_elapsed_time(135) -> "2m 15s"
    format_elapsed_time(3725) -> "1h 2m"


**Parameters:**

- `seconds` (float): Elapsed time in seconds


**Returns:** str
  Formatted time string (e.g., "2m 15s", "1h 5m", "45s")


---
