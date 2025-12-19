# progress_synchronizer

Progress Synchronizer Utility

Purpose: Automatically updates master plans and sub-plans after phase completion,
         maintaining accurate visual progress trackers, elapsed time, and next steps.

Evidence:
- PrevalidationWS: 55 minutes wasted on manual progress updates (11 phases × 5 min)
- Manual updates error-prone (typos, wrong percentages, missed updates)
- Inconsistent visual trackers across plans

Integration:
- Called by orchestrators after phase completion
- Updates markdown files atomically (temp → rename)
- Synchronizes master + all referenced sub-plans

Author: Asif Hussain
Date: December 13, 2025
Version: 1.0.0
Phase: CORTEX Orchestration + AST Enhancement - Phase 2


## Table of Contents

### Classes
- [PhaseStatus](#phasestatus)
- [PhaseInfo](#phaseinfo)
- [ProgressTrackerInfo](#progresstrackerinfo)
- [MarkdownParser](#markdownparser)
- [ASCIIArtGenerator](#asciiartgenerator)
- [TrackerUpdateEngine](#trackerupdateengine)
- [PhaseSummaryBuilder](#phasesummarybuilder)
- [ProgressSynchronizer](#progresssynchronizer)

### Functions
- [update_master_plan_phase](#update_master_plan_phase)
- [update_sub_plan_phase](#update_sub_plan_phase)


## Overview

- **Classes:** 8
- **Functions:** 2
- **Dependencies:** dataclasses, datetime, enum, logging, os, pathlib, re, shutil, tempfile, typing


## Classes

### PhaseStatus

```python
class PhaseStatus(str, Enum)
```

Phase status indicators



---

### PhaseInfo

```python
class PhaseInfo
```

**Decorators:** `dataclass`

Information about a single phase


**Attributes:**

- `phase_id`: str
- `phase_number`: int
- `phase_name`: str
- `status`: PhaseStatus
- `progress_percent`: int
- `start_date`: Optional[datetime]
- `completion_date`: Optional[datetime]
- `elapsed_time`: Optional[timedelta]



---

### ProgressTrackerInfo

```python
class ProgressTrackerInfo
```

**Decorators:** `dataclass`

Complete progress tracker information


**Attributes:**

- `phases`: List[PhaseInfo]
- `overall_progress_percent`: int
- `total_phases`: int
- `completed_phases`: int
- `start_date`: Optional[datetime]
- `target_completion_date`: Optional[datetime]
- `total_elapsed_time`: Optional[timedelta]



---

### MarkdownParser

```python
class MarkdownParser
```

Parses markdown files to extract progress tracker sections.
Preserves markdown structure during updates.


**Methods:**

  #### `load`

  ```python
  load(self) -> bool
  ```

  Load markdown file content

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `extract_progress_tracker`

  ```python
  extract_progress_tracker(self) -> Optional[ProgressTrackerInfo]
  ```

  Extract progress tracker information from markdown

  **Parameters:**

  - `self`


  **Returns:** Optional[ProgressTrackerInfo]



---

### ASCIIArtGenerator

```python
class ASCIIArtGenerator
```

Generates ASCII art progress bars and visual trackers.


**Methods:**

  #### `generate_progress_bar`

  *Decorators:* `staticmethod`

  ```python
  generate_progress_bar(percent: int, width: int) -> str
  ```

  Generate ASCII progress bar [████░░░░]

  **Parameters:**

  - `percent` (int)
  - `width` (int) = `10`


  **Returns:** str


  #### `generate_overall_progress_bar`

  *Decorators:* `staticmethod`

  ```python
  generate_overall_progress_bar(percent: int, width: int) -> str
  ```

  Generate wider progress bar for overall progress

  **Parameters:**

  - `percent` (int)
  - `width` (int) = `30`


  **Returns:** str


  #### `format_status_emoji`

  *Decorators:* `staticmethod`

  ```python
  format_status_emoji(status: PhaseStatus) -> str
  ```

  Get emoji for phase status

  **Parameters:**

  - `status` (PhaseStatus)


  **Returns:** str



---

### TrackerUpdateEngine

```python
class TrackerUpdateEngine
```

Updates progress tracker with new phase status.
Calculates percentages, updates timestamps, manages state transitions.


**Methods:**

  #### `update_phase_status`

  ```python
  update_phase_status(self, phase_number: int, new_status: PhaseStatus, start_date: Optional[datetime], completion_date: Optional[datetime]) -> bool
  ```

  Update a specific phase's status

  **Parameters:**

  - `self`
  - `phase_number` (int)
  - `new_status` (PhaseStatus)
  - `start_date` (Optional[datetime]) = `None`
  - `completion_date` (Optional[datetime]) = `None`


  **Returns:** bool


  #### `get_next_phase`

  ```python
  get_next_phase(self) -> Optional[PhaseInfo]
  ```

  Get the next phase to execute

  **Parameters:**

  - `self`


  **Returns:** Optional[PhaseInfo]



---

### PhaseSummaryBuilder

```python
class PhaseSummaryBuilder
```

Builds phase completion summaries with metrics.


**Methods:**

  #### `build_summary`

  *Decorators:* `staticmethod`

  ```python
  build_summary(phase: PhaseInfo, metrics: Optional[Dict]) -> str
  ```

  Build completion summary for a phase

  **Parameters:**

  - `phase` (PhaseInfo)
  - `metrics` (Optional[Dict]) = `None`


  **Returns:** str



---

### ProgressSynchronizer

```python
class ProgressSynchronizer
```

Main progress synchronizer utility.

Usage:
    sync = ProgressSynchronizer(plan_path)
    sync.update_phase(phase_number=2, status=PhaseStatus.COMPLETE)


**Methods:**

  #### `load`

  ```python
  load(self) -> bool
  ```

  Load plan and extract progress tracker

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `update_phase`

  ```python
  update_phase(self, phase_number: int, status: PhaseStatus, start_date: Optional[datetime], completion_date: Optional[datetime], metrics: Optional[Dict]) -> bool
  ```

  Update a phase's status and synchronize the plan file.

Args:
    phase_number: Phase number to update (e.g., 2 for Phase 2)
    status: New status (PhaseStatus.COMPLETE, etc.)
    start_date: Optional start date (defaults to now if IN_PROGRESS)
    completion_date: Optional completion date (defaults to now if COMPLETE)
    metrics: Optional metrics dict for completion summary

Returns:
    True if update successful, False otherwise

  **Parameters:**

  - `self`
  - `phase_number` (int): Phase number to update (e.g., 2 for Phase 2)
  - `status` (PhaseStatus): New status (PhaseStatus.COMPLETE, etc.)
  - `start_date` (Optional[datetime]) = `None`: Optional start date (defaults to now if IN_PROGRESS)
  - `completion_date` (Optional[datetime]) = `None`: Optional completion date (defaults to now if COMPLETE)
  - `metrics` (Optional[Dict]) = `None`: Optional metrics dict for completion summary


  **Returns:** bool
    True if update successful, False otherwise


  #### `get_current_status`

  ```python
  get_current_status(self) -> Optional[ProgressTrackerInfo]
  ```

  Get current progress tracker status

  **Parameters:**

  - `self`


  **Returns:** Optional[ProgressTrackerInfo]


  #### `get_next_phase`

  ```python
  get_next_phase(self) -> Optional[PhaseInfo]
  ```

  Get the next phase to execute

  **Parameters:**

  - `self`


  **Returns:** Optional[PhaseInfo]



---

## Functions

### update_master_plan_phase

```python
update_master_plan_phase(phase_number: int, status: PhaseStatus, master_plan_path: Optional[Path], metrics: Optional[Dict]) -> bool
```

Update a phase in the master plan.

Args:
    phase_number: Phase number to update
    status: New status
    master_plan_path: Optional path (defaults to MASTER plan)
    metrics: Optional metrics for summary

Returns:
    True if successful


**Parameters:**

- `phase_number` (int): Phase number to update
- `status` (PhaseStatus): New status
- `master_plan_path` (Optional[Path]) = `None`: Optional path (defaults to MASTER plan)
- `metrics` (Optional[Dict]) = `None`: Optional metrics for summary


**Returns:** bool
  True if successful


---

### update_sub_plan_phase

```python
update_sub_plan_phase(sub_plan_path: Path, phase_number: int, status: PhaseStatus, metrics: Optional[Dict]) -> bool
```

Update a phase in a sub-plan


**Parameters:**

- `sub_plan_path` (Path)
- `phase_number` (int)
- `status` (PhaseStatus)
- `metrics` (Optional[Dict]) = `None`


**Returns:** bool


---
