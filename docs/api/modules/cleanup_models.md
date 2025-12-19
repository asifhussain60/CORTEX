# cleanup_models

Cleanup Operation Data Models

Data classes for cleanup orchestrator metrics and reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [CleanupMetrics](#cleanupmetrics)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, typing


## Classes

### CleanupMetrics

```python
class CleanupMetrics
```

**Decorators:** `dataclass`

Metrics from cleanup operation


**Attributes:**

- `timestamp`: datetime
- `backups_deleted`: int
- `backups_archived`: int
- `files_reorganized`: int
- `md_files_consolidated`: int
- `root_files_cleaned`: int
- `bloated_files_found`: int
- `archived_docs_removed`: int
- `space_freed_bytes`: int
- `git_commits_created`: int
- `duration_seconds`: float
- `optimization_triggered`: bool
- `warnings`: List[str]
- `errors`: List[str]


**Methods:**

  #### `space_freed_mb`

  *Decorators:* `property`

  ```python
  space_freed_mb(self) -> float
  ```

  #### `space_freed_gb`

  *Decorators:* `property`

  ```python
  space_freed_gb(self) -> float
  ```

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```


---
