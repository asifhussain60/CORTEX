# plan_sync_manager

CORTEX Planning: Two-Way Sync Manager
Synchronizes active planning files with database tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [PlanningFileWatcher](#planningfilewatcher)
- [PlanSyncManager](#plansyncmanager)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** datetime, json, pathlib, sqlite3, src, threading, time, typing, watchdog


## Classes

### PlanningFileWatcher

```python
class PlanningFileWatcher(FileSystemEventHandler)
```

Watches planning files for changes and triggers sync to database

Monitors:
- cortex-brain/documents/planning/features/active/*.md
- cortex-brain/documents/planning/ado/active/*.md


**Methods:**

  #### `on_modified`

  ```python
  on_modified(self, event: FileModifiedEvent)
  ```

  Handle file modification event

Args:
    event: Watchdog file modification event

  **Parameters:**

  - `self`
  - `event` (FileModifiedEvent): Watchdog file modification event



---

### PlanSyncManager

```python
class PlanSyncManager
```

Two-Way Sync Manager for Planning Files ↔ Database

Features:
- File change monitoring → auto-update database
- Database query → locate and load files
- Conflict resolution (file vs DB divergence)
- Status propagation (approved, blocked, completed)


**Methods:**

  #### `start_file_watcher`

  ```python
  start_file_watcher(self)
  ```

  Start file system watcher for automatic sync

Monitors planning directories and syncs changes to database

  **Parameters:**

  - `self`


  #### `stop_file_watcher`

  ```python
  stop_file_watcher(self)
  ```

  Stop file system watcher

  **Parameters:**

  - `self`


  #### `sync_file_to_database`

  ```python
  sync_file_to_database(self, file_path: Path) -> Dict[str, Any]
  ```

  Sync file changes to database

Extracts metadata from file and updates database record

Args:
    file_path: Path to planning file

Returns:
    Sync result dict with status

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to planning file


  **Returns:** Dict[str, Any]
    Sync result dict with status


  #### `sync_database_to_file`

  ```python
  sync_database_to_file(self, plan_id: str) -> Dict[str, Any]
  ```

  Sync database status to file

Updates file metadata section with database status

Args:
    plan_id: Plan ID to sync

Returns:
    Sync result dict

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan ID to sync


  **Returns:** Dict[str, Any]
    Sync result dict


  #### `resolve_plan_by_name`

  ```python
  resolve_plan_by_name(self, plan_name: str) -> Optional[Dict[str, Any]]
  ```

  Find plan by name (searches both database and filesystem)

Args:
    plan_name: Plan name or partial name

Returns:
    Plan info dict or None if not found

  **Parameters:**

  - `self`
  - `plan_name` (str): Plan name or partial name


  **Returns:** Optional[Dict[str, Any]]
    Plan info dict or None if not found


  #### `validate_sync_integrity`

  ```python
  validate_sync_integrity(self) -> Dict[str, Any]
  ```

  Validate sync integrity between database and files

Checks for:
- Orphaned DB records (file deleted)
- Orphaned files (not in DB)
- Status divergence (file vs DB status differs)

Returns:
    Validation report dict

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Validation report dict



---
