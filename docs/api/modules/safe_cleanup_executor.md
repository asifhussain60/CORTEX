# safe_cleanup_executor

Safe Cleanup Executor for CORTEX Align Orchestrator v2.0

This module safely removes obsolete files with comprehensive safety checks:
- Git working directory validation
- Automatic backup creation
- Test baseline capture before cleanup
- Category-level cleanup with incremental validation
- Automatic rollback on test failure

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [CleanupCategory](#cleanupcategory)
- [CleanupResult](#cleanupresult)
- [ExecutionReport](#executionreport)
- [SafeCleanupExecutor](#safecleanupexecutor)

### Functions
- [main](#main)


## Overview

- **Classes:** 4
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, datetime, enum, logging, pathlib, shutil, src, subprocess, sys, typing


## Classes

### CleanupCategory

```python
class CleanupCategory(Enum)
```

Categories for incremental cleanup.



---

### CleanupResult

```python
class CleanupResult
```

**Decorators:** `dataclass`

Result of cleanup operation.


**Attributes:**

- `category`: CleanupCategory
- `files_removed`: List[Path]
- `files_failed`: List[Path]
- `backup_path`: Optional[Path]
- `tests_passed_before`: bool
- `tests_passed_after`: bool
- `rolled_back`: bool
- `error`: Optional[str]


**Methods:**

  #### `success`

  *Decorators:* `property`

  ```python
  success(self) -> bool
  ```

  Check if cleanup was successful.

  **Parameters:**

  - `self`


  **Returns:** bool



---

### ExecutionReport

```python
class ExecutionReport
```

**Decorators:** `dataclass`

Complete execution report.


**Attributes:**

- `total_files_removed`: int
- `total_files_failed`: int
- `categories_completed`: List[CleanupCategory]
- `categories_failed`: List[CleanupCategory]
- `backup_paths`: List[Path]
- `results`: List[CleanupResult]


**Methods:**

  #### `success`

  *Decorators:* `property`

  ```python
  success(self) -> bool
  ```

  Check if all cleanup operations succeeded.

  **Parameters:**

  - `self`


  **Returns:** bool



---

### SafeCleanupExecutor

```python
class SafeCleanupExecutor
```

Safely executes cleanup operations with comprehensive safety checks.


**Methods:**

  #### `check_git_status`

  ```python
  check_git_status(self) -> bool
  ```

  Check if git working directory is clean.

Returns:
    True if working directory is clean, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if working directory is clean, False otherwise


  #### `run_tests`

  ```python
  run_tests(self) -> bool
  ```

  Run test suite to capture baseline.

Returns:
    True if all tests pass, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if all tests pass, False otherwise


  #### `create_backup`

  ```python
  create_backup(self, files: List[Path]) -> Path
  ```

  Create backup of files before removal.

Args:
    files: List of files to backup

Returns:
    Path to backup directory

  **Parameters:**

  - `self`
  - `files` (List[Path]): List of files to backup


  **Returns:** Path
    Path to backup directory


  #### `remove_files`

  ```python
  remove_files(self, files: List[Path]) -> tuple[List[Path], List[Path]]
  ```

  Remove files from filesystem.

Args:
    files: List of files to remove

Returns:
    Tuple of (successfully removed files, failed files)

  **Parameters:**

  - `self`
  - `files` (List[Path]): List of files to remove


  **Returns:** tuple[List[Path], List[Path]]
    Tuple of (successfully removed files, failed files)


  #### `restore_backup`

  ```python
  restore_backup(self, backup_path: Path, files: List[Path]) -> bool
  ```

  Restore files from backup.

Args:
    backup_path: Path to backup directory
    files: List of files to restore

Returns:
    True if restore successful, False otherwise

  **Parameters:**

  - `self`
  - `backup_path` (Path): Path to backup directory
  - `files` (List[Path]): List of files to restore


  **Returns:** bool
    True if restore successful, False otherwise


  #### `cleanup_category`

  ```python
  cleanup_category(self, category: CleanupCategory, files: List[Path], run_tests_after: bool) -> CleanupResult
  ```

  Clean up files in a specific category with safety checks.

Args:
    category: Category being cleaned
    files: Files to remove
    run_tests_after: Whether to run tests after cleanup

Returns:
    CleanupResult with details

  **Parameters:**

  - `self`
  - `category` (CleanupCategory): Category being cleaned
  - `files` (List[Path]): Files to remove
  - `run_tests_after` (bool) = `True`: Whether to run tests after cleanup


  **Returns:** CleanupResult
    CleanupResult with details


  #### `execute_cleanup`

  ```python
  execute_cleanup(self, plan: CleanupPlan, dry_run: bool, skip_git_check: bool, skip_tests: bool) -> ExecutionReport
  ```

  Execute complete cleanup with all safety checks.

Args:
    plan: CleanupPlan with files to remove
    dry_run: If True, preview cleanup without executing
    skip_git_check: Skip git working directory check
    skip_tests: Skip test execution (dangerous!)

Returns:
    ExecutionReport with results

  **Parameters:**

  - `self`
  - `plan` (CleanupPlan): CleanupPlan with files to remove
  - `dry_run` (bool) = `False`: If True, preview cleanup without executing
  - `skip_git_check` (bool) = `False`: Skip git working directory check
  - `skip_tests` (bool) = `False`: Skip test execution (dangerous!)


  **Returns:** ExecutionReport
    ExecutionReport with results


  #### `generate_report`

  ```python
  generate_report(self, report: ExecutionReport, dry_run: bool) -> str
  ```

  Generate formatted report from execution.

Args:
    report: ExecutionReport to format
    dry_run: Whether this was a dry run

Returns:
    Formatted markdown report

  **Parameters:**

  - `self`
  - `report` (ExecutionReport): ExecutionReport to format
  - `dry_run` (bool) = `False`: Whether this was a dry run


  **Returns:** str
    Formatted markdown report



---

## Functions

### main

```python
main()
```

CLI entry point for safe cleanup.


---
