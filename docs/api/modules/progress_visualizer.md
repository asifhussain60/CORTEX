# progress_visualizer

Progress Visualizer - Visual representations of operation progress.

Generates progress bars, phase timelines, and completion charts
for multi-phase operations.


## Table of Contents

### Classes
- [ProgressVisualizer](#progressvisualizer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, typing


## Classes

### ProgressVisualizer

```python
class ProgressVisualizer
```

Generate progress visualizations.


**Methods:**

  #### `generate_progress_bar`

  ```python
  generate_progress_bar(self, current: int, total: int, width: int) -> str
  ```

  Generate ASCII progress bar.

Args:
    current: Current progress value
    total: Total progress value
    width: Bar width in characters
    
Returns:
    ASCII progress bar string

  **Parameters:**

  - `self`
  - `current` (int): Current progress value
  - `total` (int): Total progress value
  - `width` (int) = `50`: Bar width in characters


  **Returns:** str
    ASCII progress bar string


  #### `generate_phase_timeline`

  ```python
  generate_phase_timeline(self, phases: List[Dict[str, Any]]) -> str
  ```

  Generate Gantt-style phase timeline.

Args:
    phases: List of phase dicts with name, id, status, start, end
    
Returns:
    Mermaid Gantt chart

  **Parameters:**

  - `self`
  - `phases` (List[Dict[str, Any]]): List of phase dicts with name, id, status, start, end


  **Returns:** str
    Mermaid Gantt chart


  #### `generate_metrics_chart`

  ```python
  generate_metrics_chart(self, metrics: Dict[str, Any]) -> str
  ```

  Generate metrics visualization.

Args:
    metrics: Dict of metric names to numeric values
    
Returns:
    ASCII bar chart

  **Parameters:**

  - `self`
  - `metrics` (Dict[str, Any]): Dict of metric names to numeric values


  **Returns:** str
    ASCII bar chart


  #### `generate_completion_summary`

  ```python
  generate_completion_summary(self, total_phases: int, completed_phases: int, in_progress_phases: int, pending_phases: int) -> str
  ```

  Generate visual completion summary.

Args:
    total_phases: Total number of phases
    completed_phases: Number of completed phases
    in_progress_phases: Number of in-progress phases
    pending_phases: Number of pending phases
    
Returns:
    Visual summary with progress bar and status breakdown

  **Parameters:**

  - `self`
  - `total_phases` (int): Total number of phases
  - `completed_phases` (int): Number of completed phases
  - `in_progress_phases` (int): Number of in-progress phases
  - `pending_phases` (int): Number of pending phases


  **Returns:** str
    Visual summary with progress bar and status breakdown



---
