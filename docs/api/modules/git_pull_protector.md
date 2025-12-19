# git_pull_protector

Git Pull Protector

Protects locally aligned files from being overwritten by git pull operations.
Uses stash-based protection with intelligent conflict resolution.

Author: Asif Hussain
Version: 3.8.1


## Table of Contents

### Classes
- [GitPullProtector](#gitpullprotector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** alignment_state_tracker, datetime, pathlib, subprocess, typing


## Classes

### GitPullProtector

```python
class GitPullProtector
```

Protects aligned files during git pull operations.

Workflow:
1. Pre-Pull: Check for aligned files that would be overwritten
2. Stash: Automatically stash aligned changes
3. Pull: Execute git pull
4. Reconcile: Merge stashed alignment with pulled code
5. Restore: Apply alignment where possible


**Methods:**

  #### `check_pull_safety`

  ```python
  check_pull_safety(self) -> Tuple[bool, Dict[str, Any]]
  ```

  Check if git pull is safe (won't overwrite aligned files).

Returns:
    Tuple of (is_safe, report)

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, Dict[str, Any]]
    Tuple of (is_safe, report)


  #### `protect_and_pull`

  ```python
  protect_and_pull(self, auto_stash: bool, preserve_alignment: bool) -> Dict[str, Any]
  ```

  Execute protected git pull.

Args:
    auto_stash: Automatically stash aligned changes
    preserve_alignment: Try to preserve alignment after pull
    
Returns:
    Result dictionary with pull status and protection actions

  **Parameters:**

  - `self`
  - `auto_stash` (bool) = `True`: Automatically stash aligned changes
  - `preserve_alignment` (bool) = `True`: Try to preserve alignment after pull


  **Returns:** Dict[str, Any]
    Result dictionary with pull status and protection actions


  #### `get_protection_status`

  ```python
  get_protection_status(self) -> Dict[str, Any]
  ```

  Get current protection status.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
