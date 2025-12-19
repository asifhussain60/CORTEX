# cleanup

Workspace Cleanup Operation
CORTEX v3.9 Compatible

Safely removes temporary files, old logs, and cache to free disk space.
Includes safety checks to never delete source code or critical files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0


## Table of Contents

### Classes
- [CleanupCategory](#cleanupcategory)
- [CleanupResult](#cleanupresult)

### Functions
- [is_safe_to_delete](#is_safe_to_delete)
- [find_temp_files](#find_temp_files)
- [find_old_logs](#find_old_logs)
- [find_large_cache_files](#find_large_cache_files)
- [get_size](#get_size)
- [cleanup_workspace](#cleanup_workspace)
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 7
- **Dependencies:** argparse, datetime, enum, logging, os, pathlib, shutil, src, sys, typing


## Classes

### CleanupCategory

```python
class CleanupCategory(Enum)
```

Categories of files that can be cleaned.



---

### CleanupResult

```python
class CleanupResult
```

Result of cleanup operation.


**Methods:**

  #### `add_file`

  ```python
  add_file(self, path: str, size: int)
  ```

  Record file removal.

  **Parameters:**

  - `self`
  - `path` (str)
  - `size` (int)


  #### `add_directory`

  ```python
  add_directory(self, path: str, size: int)
  ```

  Record directory removal.

  **Parameters:**

  - `self`
  - `path` (str)
  - `size` (int)


  #### `add_error`

  ```python
  add_error(self, message: str)
  ```

  Record error.

  **Parameters:**

  - `self`
  - `message` (str)


  #### `add_skip`

  ```python
  add_skip(self, path: str, reason: str)
  ```

  Record skipped item.

  **Parameters:**

  - `self`
  - `path` (str)
  - `reason` (str)


  #### `total_items_removed`

  *Decorators:* `property`

  ```python
  total_items_removed(self) -> int
  ```

  Total files + directories removed.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `space_freed_mb`

  *Decorators:* `property`

  ```python
  space_freed_mb(self) -> float
  ```

  Space freed in MB.

  **Parameters:**

  - `self`


  **Returns:** float



---

## Functions

### is_safe_to_delete

```python
is_safe_to_delete(path: Path, project_root: Path) -> Tuple[bool, str]
```

Check if path is safe to delete.

NEVER deletes:
    - Source code (.py, .js, .ts, .java, .cpp, etc.)
    - Configuration files (.yaml, .json, .toml, .ini)
    - Documentation (.md, .rst, .txt)
    - Git repository (.git/)
    - Brain databases (cortex-brain/*.db)
    - Package manifests (requirements.txt, package.json, etc.)

Args:
    path: Path to check
    project_root: Project root directory

Returns:
    (is_safe, reason)


**Parameters:**

- `path` (Path): Path to check
- `project_root` (Path): Project root directory


**Returns:** Tuple[bool, str]
  (is_safe, reason)


---

### find_temp_files

```python
find_temp_files(project_root: Path, cache_instance) -> List[Path]
```

Find temporary files in project.
Uses ValidationCache to cache scan results.

Targets:
    - *.tmp, *.temp
    - __pycache__ directories
    - *.pyc, *.pyo, *.pyd files
    - .pytest_cache directories
    - *.log files in temp locations

Args:
    project_root: Project root directory
    cache_instance: ValidationCache instance (optional)

Returns:
    List of temporary file/directory paths


**Parameters:**

- `project_root` (Path): Project root directory
- `cache_instance` = `None`: ValidationCache instance (optional)


**Returns:** List[Path]
  List of temporary file/directory paths


---

### find_old_logs

```python
find_old_logs(project_root: Path, days_old: int, cache_instance) -> List[Path]
```

Find log files older than specified days.
Uses ValidationCache to cache scan results.

Args:
    project_root: Project root directory
    days_old: Consider files older than this many days
    cache_instance: ValidationCache instance (optional)

Returns:
    List of old log file paths


**Parameters:**

- `project_root` (Path): Project root directory
- `days_old` (int) = `30`: Consider files older than this many days
- `cache_instance` = `None`: ValidationCache instance (optional)


**Returns:** List[Path]
  List of old log file paths


---

### find_large_cache_files

```python
find_large_cache_files(project_root: Path, min_size_mb: int, cache_instance) -> List[Path]
```

Find large cache files (>10MB by default).
Uses ValidationCache to cache scan results.

Args:
    project_root: Project root directory
    min_size_mb: Minimum file size in MB
    cache_instance: ValidationCache instance (optional)

Returns:
    List of large cache file paths


**Parameters:**

- `project_root` (Path): Project root directory
- `min_size_mb` (int) = `10`: Minimum file size in MB
- `cache_instance` = `None`: ValidationCache instance (optional)


**Returns:** List[Path]
  List of large cache file paths


---

### get_size

```python
get_size(path: Path) -> int
```

Get total size of file or directory in bytes.

Args:
    path: File or directory path

Returns:
    Total size in bytes


**Parameters:**

- `path` (Path): File or directory path


**Returns:** int
  Total size in bytes


---

### cleanup_workspace

```python
cleanup_workspace(project_root: Path, dry_run: bool, categories: List[CleanupCategory], confirm: bool) -> Dict[str, Any]
```

Clean workspace by removing temporary files, old logs, and cache.

Args:
    project_root: Project root directory (auto-detected if None)
    dry_run: If True, only show what would be deleted
    categories: List of cleanup categories (all by default)
    confirm: If True, prompt for confirmation before deleting

Returns:
    Dictionary with cleanup results


**Parameters:**

- `project_root` (Path) = `None`: Project root directory (auto-detected if None)
- `dry_run` (bool) = `True`: If True, only show what would be deleted
- `categories` (List[CleanupCategory]) = `None`: List of cleanup categories (all by default)
- `confirm` (bool) = `True`: If True, prompt for confirmation before deleting


**Returns:** Dict[str, Any]
  Dictionary with cleanup results


---

### main

```python
main()
```

CLI entry point for cleanup operation.


---
