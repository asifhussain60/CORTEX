# alignment_state

Alignment State Management

Handles serialization, deserialization, and validation of alignment state.
Supports incremental alignment with file change tracking and auto-discovery.

Features:
- Enhanced state structure with file checksums
- Change detection and diff computation
- Schema validation and migration
- Backward compatibility with legacy format
- Auto-wiring validation

Version: 1.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [FileChecksum](#filechecksum)
- [FeatureScore](#featurescore)
- [ChangesSummary](#changessummary)
- [PerformanceMetrics](#performancemetrics)
- [AlignmentState](#alignmentstate)
- [AlignmentStateManager](#alignmentstatemanager)


## Overview

- **Classes:** 6
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, hashlib, json, pathlib, shutil, typing


## Classes

### FileChecksum

```python
class FileChecksum
```

**Decorators:** `dataclass`

File checksum and metadata.


**Attributes:**

- `sha256`: str
- `last_modified`: str
- `last_checked`: str
- `size_bytes`: int


**Methods:**

  #### `from_file`

  *Decorators:* `classmethod`

  ```python
  from_file(cls, file_path: Path) -> 'FileChecksum'
  ```

  Compute checksum from file.

  **Parameters:**

  - `cls`
  - `file_path` (Path)


  **Returns:** 'FileChecksum'



---

### FeatureScore

```python
class FeatureScore
```

**Decorators:** `dataclass`

Feature integration score with validation metadata.


**Attributes:**

- `score`: int
- `module_path`: str
- `file_hash`: str
- `last_validated`: str
- `validation_count`: int
- `discovered`: bool
- `imported`: bool
- `instantiated`: bool
- `documented`: bool
- `tested`: bool
- `wired`: bool
- `optimized`: bool
- `api_documented`: bool


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'FeatureScore'
  ```

  Create from dictionary.

  **Parameters:**

  - `cls`
  - `data` (Dict[str, Any])


  **Returns:** 'FeatureScore'



---

### ChangesSummary

```python
class ChangesSummary
```

**Decorators:** `dataclass`

Summary of changes detected since last alignment.


**Attributes:**

- `files_added`: List[str]
- `files_modified`: List[str]
- `files_deleted`: List[str]
- `features_impacted`: List[str]


**Methods:**

  #### `has_changes`

  ```python
  has_changes(self) -> bool
  ```

  Check if any changes detected.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### PerformanceMetrics

```python
class PerformanceMetrics
```

**Decorators:** `dataclass`

Performance metrics for alignment run.


**Attributes:**

- `last_run_duration_seconds`: float
- `features_checked`: int
- `features_skipped`: int
- `cache_hit_rate`: float


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### AlignmentState

```python
class AlignmentState
```

**Decorators:** `dataclass`

Complete alignment state with incremental tracking.


**Attributes:**

- `version`: str
- `last_alignment`: str
- `last_full_scan`: str
- `scan_mode`: str
- `context_type`: str
- `file_checksums`: Dict[str, Dict[str, Any]]
- `feature_scores`: Dict[str, Dict[str, Any]]
- `changes_detected`: Dict[str, Any]
- `performance_metrics`: Dict[str, Any]
- `overall_health`: int
- `alignment_history`: List[Dict[str, Any]]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for JSON serialization.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'AlignmentState'
  ```

  Create from dictionary.

  **Parameters:**

  - `cls`
  - `data` (Dict[str, Any])


  **Returns:** 'AlignmentState'


  #### `should_run_full_scan`

  ```python
  should_run_full_scan(self) -> bool
  ```

  Determine if full scan is required.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `is_stale`

  ```python
  is_stale(self, hours: int) -> bool
  ```

  Check if state is stale.

  **Parameters:**

  - `self`
  - `hours` (int) = `48`


  **Returns:** bool


  #### `add_to_history`

  ```python
  add_to_history(self, health: int, total_features: int, critical_issues: int, warnings: int) -> None
  ```

  Add current run to history.

  **Parameters:**

  - `self`
  - `health` (int)
  - `total_features` (int)
  - `critical_issues` (int)
  - `warnings` (int)


  **Returns:** None



---

### AlignmentStateManager

```python
class AlignmentStateManager
```

Manages alignment state persistence and operations.


**Methods:**

  #### `load`

  ```python
  load(self) -> Optional[AlignmentState]
  ```

  Load alignment state from file.

  **Parameters:**

  - `self`


  **Returns:** Optional[AlignmentState]


  #### `save`

  ```python
  save(self, state: AlignmentState) -> bool
  ```

  Save alignment state to file.

  **Parameters:**

  - `self`
  - `state` (AlignmentState)


  **Returns:** bool


  #### `backup`

  ```python
  backup(self) -> bool
  ```

  Create backup of current state.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `detect_context_type`

  ```python
  detect_context_type(self, project_root: Path) -> str
  ```

  Detect if running in admin (CORTEX) or user (dev) context.

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** str


  #### `compute_file_checksums`

  ```python
  compute_file_checksums(self, file_paths: List[Path]) -> Dict[str, Dict[str, Any]]
  ```

  Compute checksums for multiple files.

  **Parameters:**

  - `self`
  - `file_paths` (List[Path])


  **Returns:** Dict[str, Dict[str, Any]]


  #### `detect_file_changes`

  ```python
  detect_file_changes(self, current_checksums: Dict[str, Dict[str, Any]], previous_state: AlignmentState) -> ChangesSummary
  ```

  Detect file changes between current and previous state.

  **Parameters:**

  - `self`
  - `current_checksums` (Dict[str, Dict[str, Any]])
  - `previous_state` (AlignmentState)


  **Returns:** ChangesSummary


  #### `map_files_to_features`

  ```python
  map_files_to_features(self, file_paths: List[str], feature_scores: Dict[str, Dict[str, Any]]) -> Set[str]
  ```

  Map changed files to impacted features.

  **Parameters:**

  - `self`
  - `file_paths` (List[str])
  - `feature_scores` (Dict[str, Dict[str, Any]])


  **Returns:** Set[str]



---
