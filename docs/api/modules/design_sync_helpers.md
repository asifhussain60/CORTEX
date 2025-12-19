# design_sync_helpers

Design Sync Helpers

Helper functions for design sync orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [RecentUpdatesGenerator](#recentupdatesgenerator)
- [CommitReporter](#commitreporter)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, re, src, subprocess, typing


## Classes

### RecentUpdatesGenerator

```python
class RecentUpdatesGenerator
```

Generates recent updates list from git commit history.

Parses git log for the last N days and extracts meaningful updates
to auto-generate the "Recent Updates" section in status documents.


**Methods:**

  #### `generate`

  ```python
  generate(self, project_root: Path, lookback_days: int) -> List[str]
  ```

  Generate recent updates list from git history.

Args:
    project_root: Project root directory
    lookback_days: Number of days to look back in git history
    
Returns:
    List of update strings with emoji prefixes

  **Parameters:**

  - `self`
  - `project_root` (Path): Project root directory
  - `lookback_days` (int) = `1`: Number of days to look back in git history


  **Returns:** List[str]
    List of update strings with emoji prefixes



---

### CommitReporter

```python
class CommitReporter
```

Commits design sync changes and generates comprehensive report.


**Methods:**

  #### `commit_and_report`

  ```python
  commit_and_report(self, impl_state: ImplementationState, design_state: DesignState, gaps: GapAnalysis, optimizations: Dict[str, Any], transformations: Dict[str, Any], project_root: Path, metrics: SyncMetrics, profile: str) -> Dict[str, Any]
  ```

  Commit changes and generate comprehensive report.

Returns:
    Dict with final report data

  **Parameters:**

  - `self`
  - `impl_state` (ImplementationState)
  - `design_state` (DesignState)
  - `gaps` (GapAnalysis)
  - `optimizations` (Dict[str, Any])
  - `transformations` (Dict[str, Any])
  - `project_root` (Path)
  - `metrics` (SyncMetrics)
  - `profile` (str)


  **Returns:** Dict[str, Any]
    Dict with final report data



---
