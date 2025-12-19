# obsolete_code_auto_cleaner

Obsolete Code Auto-Cleanup for CORTEX Align v2.0

Safely removes obsolete files with automatic backup creation.
Handles deletion of orphaned tests, deprecated scripts, and obsolete orchestrators.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [CleanupResult](#cleanupresult)
- [ObsoleteCodeAutoCleaner](#obsoletecodeautocleaner)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, logging, pathlib, shutil, typing


## Classes

### CleanupResult

```python
class CleanupResult
```

**Decorators:** `dataclass`

Result of cleanup operation.


**Attributes:**

- `success`: bool
- `files_removed`: List[Path]
- `files_backed_up`: List[Path]
- `errors`: List[str]
- `backup_dir`: Optional[Path]
- `space_freed_mb`: float



---

### ObsoleteCodeAutoCleaner

```python
class ObsoleteCodeAutoCleaner
```

Automatically removes obsolete code with safety backups.


**Methods:**

  #### `create_backup_dir`

  ```python
  create_backup_dir(self) -> Path
  ```

  Create timestamped backup directory.

Returns:
    Path to backup directory

  **Parameters:**

  - `self`


  **Returns:** Path
    Path to backup directory


  #### `is_safe_to_delete`

  ```python
  is_safe_to_delete(self, file_path: Path) -> tuple[bool, str]
  ```

  Check if file is safe to delete.

Args:
    file_path: Path to file

Returns:
    Tuple of (is_safe, reason)

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file


  **Returns:** tuple[bool, str]
    Tuple of (is_safe, reason)


  #### `backup_file`

  ```python
  backup_file(self, file_path: Path, backup_dir: Path) -> Optional[Path]
  ```

  Backup a file before deletion.

Args:
    file_path: Path to file to backup
    backup_dir: Directory to store backup

Returns:
    Path to backed up file or None on error

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file to backup
  - `backup_dir` (Path): Directory to store backup


  **Returns:** Optional[Path]
    Path to backed up file or None on error


  #### `delete_file`

  ```python
  delete_file(self, file_path: Path) -> bool
  ```

  Delete a file.

Args:
    file_path: Path to file to delete

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file to delete


  **Returns:** bool
    True if successful, False otherwise


  #### `cleanup_files`

  ```python
  cleanup_files(self, files_to_remove: List[Path], dry_run: bool) -> CleanupResult
  ```

  Clean up obsolete files with backup.

Args:
    files_to_remove: List of files to remove
    dry_run: If True, don't actually delete files

Returns:
    CleanupResult with details

  **Parameters:**

  - `self`
  - `files_to_remove` (List[Path]): List of files to remove
  - `dry_run` (bool) = `False`: If True, don't actually delete files


  **Returns:** CleanupResult
    CleanupResult with details


  #### `cleanup_obsolete_tests`

  ```python
  cleanup_obsolete_tests(self, obsolete_tests: List[Path], dry_run: bool) -> CleanupResult
  ```

  Clean up obsolete test files.

Args:
    obsolete_tests: List of test files to remove
    dry_run: If True, don't actually delete files

Returns:
    CleanupResult

  **Parameters:**

  - `self`
  - `obsolete_tests` (List[Path]): List of test files to remove
  - `dry_run` (bool) = `False`: If True, don't actually delete files


  **Returns:** CleanupResult
    CleanupResult


  #### `cleanup_obsolete_scripts`

  ```python
  cleanup_obsolete_scripts(self, obsolete_scripts: List[Path], dry_run: bool) -> CleanupResult
  ```

  Clean up obsolete script files.

Args:
    obsolete_scripts: List of script files to remove
    dry_run: If True, don't actually delete files

Returns:
    CleanupResult

  **Parameters:**

  - `self`
  - `obsolete_scripts` (List[Path]): List of script files to remove
  - `dry_run` (bool) = `False`: If True, don't actually delete files


  **Returns:** CleanupResult
    CleanupResult


  #### `cleanup_obsolete_orchestrators`

  ```python
  cleanup_obsolete_orchestrators(self, obsolete_orchestrators: List[Path], dry_run: bool) -> CleanupResult
  ```

  Clean up obsolete orchestrator files.

Args:
    obsolete_orchestrators: List of orchestrator files to remove
    dry_run: If True, don't actually delete files

Returns:
    CleanupResult

  **Parameters:**

  - `self`
  - `obsolete_orchestrators` (List[Path]): List of orchestrator files to remove
  - `dry_run` (bool) = `False`: If True, don't actually delete files


  **Returns:** CleanupResult
    CleanupResult


  #### `rollback_cleanup`

  ```python
  rollback_cleanup(self, backup_dir: Path) -> bool
  ```

  Rollback a cleanup operation by restoring from backup.

Args:
    backup_dir: Path to backup directory

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `backup_dir` (Path): Path to backup directory


  **Returns:** bool
    True if successful, False otherwise



---
