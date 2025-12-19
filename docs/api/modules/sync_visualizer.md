# sync_visualizer

Sync Operation Visual Feedback System

Provides real-time visualization for sync/commit operations with network diagram
and file flow representation.

Author: Asif Hussain
Created: 2025-11-28
Version: 1.0.0


## Table of Contents

### Classes
- [SyncVisualizer](#syncvisualizer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, pathlib, typing


## Classes

### SyncVisualizer

```python
class SyncVisualizer
```

Visual feedback for sync/commit operations.

Features:
- Network diagram showing local ↔ remote synchronization
- File flow visualization (added/modified/deleted)
- Operation status indicators (pull, merge, push)
- Conflict detection and resolution visualization
- Real-time progress updates via WebSocket


**Methods:**

  #### `track_file_change`

  ```python
  track_file_change(self, file_path: str, change_type: str, size_bytes: int, status: str) -> None
  ```

  Track a file change during sync operation.

Args:
    file_path: Path to the file
    change_type: 'added', 'modified', or 'deleted'
    size_bytes: File size in bytes
    status: Current status ('pending', 'syncing', 'complete', 'failed')

  **Parameters:**

  - `self`
  - `file_path` (str): Path to the file
  - `change_type` (str): 'added', 'modified', or 'deleted'
  - `size_bytes` (int): File size in bytes
  - `status` (str) = `'pending'`: Current status ('pending', 'syncing', 'complete', 'failed')


  **Returns:** None


  #### `track_operation`

  ```python
  track_operation(self, operation_name: str, status: str, duration_ms: float, message: str) -> None
  ```

  Track a sync operation step (pull, merge, push).

Args:
    operation_name: Name of operation ('pull', 'merge', 'push', 'commit')
    status: Operation status ('pending', 'running', 'complete', 'failed')
    duration_ms: Operation duration in milliseconds
    message: Status message or error description

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of operation ('pull', 'merge', 'push', 'commit')
  - `status` (str): Operation status ('pending', 'running', 'complete', 'failed')
  - `duration_ms` (float) = `0.0`: Operation duration in milliseconds
  - `message` (str) = `''`: Status message or error description


  **Returns:** None


  #### `track_conflict`

  ```python
  track_conflict(self, file_path: str, conflict_type: str, resolution: Optional[str]) -> None
  ```

  Track a merge conflict.

Args:
    file_path: Path to conflicted file
    conflict_type: Type of conflict ('content', 'rename', 'delete')
    resolution: How conflict was resolved (None if unresolved)

  **Parameters:**

  - `self`
  - `file_path` (str): Path to conflicted file
  - `conflict_type` (str): Type of conflict ('content', 'rename', 'delete')
  - `resolution` (Optional[str]) = `None`: How conflict was resolved (None if unresolved)


  **Returns:** None


  #### `generate_network_diagram_data`

  ```python
  generate_network_diagram_data(self) -> Dict[str, Any]
  ```

  Generate data for D3.js network diagram.

Returns:
    Dict with nodes and links for network visualization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with nodes and links for network visualization


  #### `generate_file_flow_data`

  ```python
  generate_file_flow_data(self) -> Dict[str, Any]
  ```

  Generate data for file flow visualization.

Returns:
    Dict with file changes grouped by type

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with file changes grouped by type


  #### `generate_operations_timeline`

  ```python
  generate_operations_timeline(self) -> List[Dict[str, Any]]
  ```

  Generate timeline data for operation steps.

Returns:
    List of operations with timestamps and durations

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of operations with timestamps and durations


  #### `generate_conflicts_summary`

  ```python
  generate_conflicts_summary(self) -> Dict[str, Any]
  ```

  Generate conflict resolution summary.

Returns:
    Dict with conflict data and resolution status

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with conflict data and resolution status


  #### `generate_websocket_message`

  ```python
  generate_websocket_message(self, event_type: str) -> Dict[str, Any]
  ```

  Generate WebSocket message for real-time updates.

Args:
    event_type: Type of event ('file_change', 'operation_update', 'conflict_detected')

Returns:
    WebSocket message dict

  **Parameters:**

  - `self`
  - `event_type` (str): Type of event ('file_change', 'operation_update', 'conflict_detected')


  **Returns:** Dict[str, Any]
    WebSocket message dict


  #### `generate_html_dashboard`

  ```python
  generate_html_dashboard(self, output_path: Path) -> str
  ```

  Generate HTML dashboard with sync visualization.

Args:
    output_path: Path to save HTML file

Returns:
    Path to generated HTML file

  **Parameters:**

  - `self`
  - `output_path` (Path): Path to save HTML file


  **Returns:** str
    Path to generated HTML file



---
