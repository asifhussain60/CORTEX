# git_isolation

CORTEX Git Isolation Enforcement
Prevents CORTEX source code from being committed to user application repositories.

This module:
1. Installs git hooks in user repos to block CORTEX code commits
2. Scans staged files for CORTEX paths
3. Provides clear error messages and alternatives

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file


## Table of Contents

### Classes
- [GitIsolationEnforcer](#gitisolationenforcer)

### Functions
- [install_git_isolation_hooks](#install_git_isolation_hooks)
- [check_git_isolation](#check_git_isolation)


## Overview

- **Classes:** 1
- **Functions:** 2
- **Dependencies:** logging, pathlib, subprocess, sys, typing


## Classes

### GitIsolationEnforcer

```python
class GitIsolationEnforcer
```

Enforces CORTEX code isolation from user application repositories.

Responsibilities:
- Install git hooks in user repos
- Scan commits for CORTEX code
- Block commits that violate isolation
- Provide clear error messages


**Methods:**

  #### `install_hooks`

  ```python
  install_hooks(self) -> bool
  ```

  Install git hooks to prevent CORTEX code commits.

Returns:
    True if hooks installed successfully

  **Parameters:**

  - `self`


  **Returns:** bool
    True if hooks installed successfully


  #### `check_staged_files`

  ```python
  check_staged_files(self) -> Tuple[bool, List[str]]
  ```

  Check if any staged files contain CORTEX code.

Returns:
    (is_safe, violations) where is_safe=False if violations found

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]
    (is_safe, violations) where is_safe=False if violations found


  #### `uninstall_hooks`

  ```python
  uninstall_hooks(self) -> bool
  ```

  Remove CORTEX git hooks (for testing or uninstall).

Returns:
    True if hooks removed successfully

  **Parameters:**

  - `self`


  **Returns:** bool
    True if hooks removed successfully



---

## Functions

### install_git_isolation_hooks

```python
install_git_isolation_hooks(user_repo_path: Path) -> bool
```

Install git hooks to enforce CORTEX isolation.

This is called during 'cortex init' setup process.

Args:
    user_repo_path: Path to user's application repository
    
Returns:
    True if hooks installed successfully


**Parameters:**

- `user_repo_path` (Path): Path to user's application repository


**Returns:** bool
  True if hooks installed successfully


---

### check_git_isolation

```python
check_git_isolation(user_repo_path: Path) -> Tuple[bool, List[str]]
```

Check if staged files violate git isolation.

Args:
    user_repo_path: Path to user's application repository
    
Returns:
    (is_safe, violations) tuple


**Parameters:**

- `user_repo_path` (Path): Path to user's application repository


**Returns:** Tuple[bool, List[str]]
  (is_safe, violations) tuple


---
