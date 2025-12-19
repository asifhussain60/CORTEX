# alignment_state_tracker

Alignment State Tracker

Tracks which files have been aligned, optimized, or reviewed on the current machine.
State is machine-local (not shared via git) to prevent conflicts across machines.

Author: Asif Hussain
Version: 3.8.1


## Table of Contents

### Classes
- [FileAlignmentState](#filealignmentstate)
- [AlignmentStateTracker](#alignmentstatetracker)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, hashlib, json, pathlib, socket, typing


## Classes

### FileAlignmentState

```python
class FileAlignmentState
```

**Decorators:** `dataclass`

State of a single file's alignment.


**Attributes:**

- `path`: str
- `last_aligned`: str
- `alignment_hash`: str
- `operations`: List[str]
- `score`: Optional[int]
- `issues_fixed`: int


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
  from_dict(cls, data: Dict[str, Any]) -> 'FileAlignmentState'
  ```

  Create from dictionary.

  **Parameters:**

  - `cls`
  - `data` (Dict[str, Any])


  **Returns:** 'FileAlignmentState'



---

### AlignmentStateTracker

```python
class AlignmentStateTracker
```

Tracks alignment state for files on the current machine.

State file is in .gitignore to prevent cross-machine conflicts.
Each machine maintains its own alignment state independently.


**Methods:**

  #### `mark_aligned`

  ```python
  mark_aligned(self, file_path: Path, operation: str, issues_fixed: int, score: Optional[int]) -> None
  ```

  Mark a file as aligned/optimized/reviewed.

Args:
    file_path: Path to file
    operation: Operation performed ('align', 'optimize', 'review')
    issues_fixed: Number of issues fixed
    score: Review score if available

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file
  - `operation` (str): Operation performed ('align', 'optimize', 'review')
  - `issues_fixed` (int) = `0`: Number of issues fixed
  - `score` (Optional[int]) = `None`: Review score if available


  **Returns:** None


  #### `is_aligned`

  ```python
  is_aligned(self, file_path: Path) -> bool
  ```

  Check if file is currently aligned.

  **Parameters:**

  - `self`
  - `file_path` (Path)


  **Returns:** bool


  #### `get_aligned_files`

  ```python
  get_aligned_files(self) -> List[Path]
  ```

  Get list of all aligned files.

  **Parameters:**

  - `self`


  **Returns:** List[Path]


  #### `get_modified_aligned_files`

  ```python
  get_modified_aligned_files(self) -> List[Path]
  ```

  Get aligned files that have been modified since alignment.

  **Parameters:**

  - `self`


  **Returns:** List[Path]


  #### `get_alignment_info`

  ```python
  get_alignment_info(self, file_path: Path) -> Optional[FileAlignmentState]
  ```

  Get alignment information for a file.

  **Parameters:**

  - `self`
  - `file_path` (Path)


  **Returns:** Optional[FileAlignmentState]


  #### `clear_state`

  ```python
  clear_state(self, file_path: Optional[Path]) -> None
  ```

  Clear alignment state.

Args:
    file_path: Specific file to clear, or None to clear all

  **Parameters:**

  - `self`
  - `file_path` (Optional[Path]) = `None`: Specific file to clear, or None to clear all


  **Returns:** None


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get alignment statistics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
