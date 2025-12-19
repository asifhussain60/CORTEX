# status_file_consolidator

Status File Consolidator

Consolidates multiple status files into one authoritative document.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [StatusFileConsolidator](#statusfileconsolidator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, re, src, typing


## Classes

### StatusFileConsolidator

```python
class StatusFileConsolidator
```

Consolidates multiple status files into ONE authoritative document.

Responsibilities:
- Select primary status file (CORTEX2-STATUS.MD preferred)
- Update counts from implementation state
- Insert/update recent updates from git history
- Regenerate visual progress bars
- Add sync timestamp with contextual suffix


**Methods:**

  #### `consolidate`

  ```python
  consolidate(self, status_files: List[Path], impl_state: ImplementationState, design_state: DesignState, gaps: GapAnalysis, project_root: Path, metrics: SyncMetrics) -> Optional[Path]
  ```

  Consolidate multiple status files into ONE authoritative document.

Returns:
    Path to consolidated status file

  **Parameters:**

  - `self`
  - `status_files` (List[Path])
  - `impl_state` (ImplementationState)
  - `design_state` (DesignState)
  - `gaps` (GapAnalysis)
  - `project_root` (Path)
  - `metrics` (SyncMetrics)


  **Returns:** Optional[Path]
    Path to consolidated status file



---
