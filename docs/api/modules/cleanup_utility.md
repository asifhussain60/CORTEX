# cleanup_utility

Cleanup Utility

Fast, lightweight cleanup management for Phase 8 integration cleanup.
Replaces cleanup_strategy.py with focused utility for file cleanup.

Features:
- Profile-based cleanup strategies (quick/standard/comprehensive)
- Safe file detection with critical file protection
- Age-based filtering for backups and logs
- Dry-run mode for preview

Operations:
1. get_cleanup_strategy - Get strategy description
2. detect_quick_files - Detect temp/cache files only
3. detect_standard_files - Detect temp/cache/old backups (>30 days)
4. detect_comprehensive_files - Detect all obsolete files
5. execute_cleanup - Remove files safely

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [get_cleanup_strategy](#get_cleanup_strategy)
- [detect_quick_files](#detect_quick_files)
- [detect_standard_files](#detect_standard_files)
- [detect_comprehensive_files](#detect_comprehensive_files)
- [execute_cleanup](#execute_cleanup)


## Overview

- **Classes:** 0
- **Functions:** 5
- **Dependencies:** datetime, pathlib, typing


## Functions

### get_cleanup_strategy

```python
get_cleanup_strategy(profile: str) -> Dict[str, Any]
```

Get cleanup strategy description for profile.

Args:
    profile: Profile name (quick|standard|comprehensive)
    
Returns:
    Dict with strategy info:
        - profile: str
        - description: str
        - targets: list of cleanup targets


**Parameters:**

- `profile` (str): Profile name (quick|standard|comprehensive)


**Returns:** Dict[str, Any]
  Dict with strategy info: - profile: str - description: str - targets: list of cleanup targets


---

### detect_quick_files

```python
detect_quick_files(brain_path: Path) -> List[Path]
```

Detect files for quick cleanup (temp and cache only).

Args:
    brain_path: Path to CORTEX brain directory
    
Returns:
    List of files to clean


**Parameters:**

- `brain_path` (Path): Path to CORTEX brain directory


**Returns:** List[Path]
  List of files to clean


---

### detect_standard_files

```python
detect_standard_files(brain_path: Path, cutoff_days: int) -> List[Path]
```

Detect files for standard cleanup (temp, cache, old backups).

Args:
    brain_path: Path to CORTEX brain directory
    cutoff_days: Age threshold for old backups (default: 30 days)
    
Returns:
    List of files to clean


**Parameters:**

- `brain_path` (Path): Path to CORTEX brain directory
- `cutoff_days` (int) = `30`: Age threshold for old backups (default: 30 days)


**Returns:** List[Path]
  List of files to clean


---

### detect_comprehensive_files

```python
detect_comprehensive_files(brain_path: Path, cutoff_days: int) -> List[Path]
```

Detect files for comprehensive cleanup (all obsolete files).

Args:
    brain_path: Path to CORTEX brain directory
    cutoff_days: Age threshold for logs (default: 30 days)
    
Returns:
    List of files to clean


**Parameters:**

- `brain_path` (Path): Path to CORTEX brain directory
- `cutoff_days` (int) = `30`: Age threshold for logs (default: 30 days)


**Returns:** List[Path]
  List of files to clean


---

### execute_cleanup

```python
execute_cleanup(files: List[Path], dry_run: bool) -> Dict[str, Any]
```

Execute cleanup by removing files safely.

Args:
    files: List of files to remove
    dry_run: If True, show what would be removed without executing
    
Returns:
    Dict with cleanup results:
        - success: bool
        - files_removed: int
        - dry_run: bool
        - message: str


**Parameters:**

- `files` (List[Path]): List of files to remove
- `dry_run` (bool) = `False`: If True, show what would be removed without executing


**Returns:** Dict[str, Any]
  Dict with cleanup results: - success: bool - files_removed: int - dry_run: bool - message: str


---
