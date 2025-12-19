# cleanup_hook

Tier 0: Smart Cleanup Hook (skeleton)

Purpose:
- Enforce CORTEX folder structure hygiene
- Auto-archive safe docs to Git (per Rule PHASE_GIT_CHECKPOINT & Rule #23 design)
- Require approval for potentially breaking moves/archives

Note: This is a skeleton; full implementation will be completed in later phases.


## Table of Contents

### Classes
- [ArchiveDecision](#archivedecision)
- [CleanupAction](#cleanupaction)
- [SmartCleanupHook](#smartcleanuphook)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** __future__, dataclasses, enum, pathlib, typing


## Classes

### ArchiveDecision

```python
class ArchiveDecision(str, Enum)
```


---

### CleanupAction

```python
class CleanupAction
```

**Decorators:** `dataclass`

**Attributes:**

- `path`: Path
- `action`: str
- `target`: Optional[Path]
- `reason`: Optional[str]



---

### SmartCleanupHook

```python
class SmartCleanupHook
```

Tier 0: Folder structure enforcement with Git-aware archival (skeleton).


**Methods:**

  #### `enforce_structure`

  ```python
  enforce_structure(self) -> List[CleanupAction]
  ```

  Detect and propose actions; do not execute destructive operations here.

  **Parameters:**

  - `self`


  **Returns:** List[CleanupAction]


  #### `analyze_file`

  ```python
  analyze_file(self, file_path: Path) -> ArchiveDecision
  ```

  #### `archive_file`

  ```python
  archive_file(self, file_path: Path) -> None
  ```

  #### `move_with_reference_updates`

  ```python
  move_with_reference_updates(self, src: Path, dst: Path) -> None
  ```


---
