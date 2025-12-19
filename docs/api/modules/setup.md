# setup

Environment Setup Operation - CORTEX 3.0 Phase 1.1
Monolithic MVP Implementation (~350 lines)

Detects platform, validates dependencies, creates virtual environment,
installs packages, initializes CORTEX brain databases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [Platform](#platform)
- [SetupResult](#setupresult)

### Functions
- [detect_platform](#detect_platform)
- [validate_python](#validate_python)
- [validate_git](#validate_git)
- [validate_vscode](#validate_vscode)
- [create_virtual_environment](#create_virtual_environment)
- [install_dependencies](#install_dependencies)
- [configure_gitignore](#configure_gitignore)
- [initialize_brain_databases](#initialize_brain_databases)
- [setup_environment](#setup_environment)


## Overview

- **Classes:** 2
- **Functions:** 9
- **Dependencies:** argparse, enum, os, pathlib, sqlite3, subprocess, sys, typing


## Classes

### Platform

```python
class Platform(Enum)
```

Supported platforms.



---

### SetupResult

```python
class SetupResult
```

Result of setup operation.


**Methods:**

  #### `add_error`

  ```python
  add_error(self, message: str)
  ```

  Add error message.

  **Parameters:**

  - `self`
  - `message` (str)


  #### `add_warning`

  ```python
  add_warning(self, message: str)
  ```

  Add warning message.

  **Parameters:**

  - `self`
  - `message` (str)


  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### detect_platform

```python
detect_platform() -> Platform
```

Detect current operating system platform.

Returns:
    Platform enum value


**Returns:** Platform
  Platform enum value


---

### validate_python

```python
validate_python() -> Tuple[bool, str]
```

Validate Python installation and version.

Returns:
    (is_valid, version_string)


**Returns:** Tuple[bool, str]
  (is_valid, version_string)


---

### validate_git

```python
validate_git() -> Tuple[bool, str]
```

Validate Git installation.

Returns:
    (is_installed, version_string)


**Returns:** Tuple[bool, str]
  (is_installed, version_string)


---

### validate_vscode

```python
validate_vscode() -> bool
```

Check if VS Code is installed.

Returns:
    True if VS Code found


**Returns:** bool
  True if VS Code found


---

### create_virtual_environment

```python
create_virtual_environment(project_root: Path) -> Tuple[bool, str]
```

Create Python virtual environment if it doesn't exist.

Args:
    project_root: CORTEX project root directory

Returns:
    (success, message)


**Parameters:**

- `project_root` (Path): CORTEX project root directory


**Returns:** Tuple[bool, str]
  (success, message)


---

### install_dependencies

```python
install_dependencies(project_root: Path) -> Tuple[bool, int, str]
```

Install Python dependencies from requirements.txt.

Args:
    project_root: CORTEX project root directory

Returns:
    (success, packages_installed, message)


**Parameters:**

- `project_root` (Path): CORTEX project root directory


**Returns:** Tuple[bool, int, str]
  (success, packages_installed, message)


---

### configure_gitignore

```python
configure_gitignore(project_root: Path) -> Tuple[bool, str]
```

Add CORTEX folder to .gitignore to prevent committing CORTEX internals.

Creates .gitignore if it doesn't exist, or appends CORTEX exclusion if missing.

Args:
    project_root: CORTEX project root directory

Returns:
    (success, message)


**Parameters:**

- `project_root` (Path): CORTEX project root directory


**Returns:** Tuple[bool, str]
  (success, message)


---

### initialize_brain_databases

```python
initialize_brain_databases(project_root: Path) -> Tuple[bool, str]
```

Initialize CORTEX brain SQLite databases.

Creates:
    - cortex-brain/tier1/conversations.db
    - cortex-brain/tier2/knowledge-graph.db
    - cortex-brain/tier3/context-intelligence.db

Args:
    project_root: CORTEX project root directory

Returns:
    (success, message)


**Parameters:**

- `project_root` (Path): CORTEX project root directory


**Returns:** Tuple[bool, str]
  (success, message)


---

### setup_environment

```python
setup_environment(profile: str, project_root: Path) -> Dict[str, Any]
```

Main setup operation - configures CORTEX development environment.

Steps:
    1. Detect platform (Windows/Mac/Linux)
    2. Validate dependencies (Python 3.9+, Git, VS Code)
    3. Create virtual environment
    4. Install Python packages from requirements.txt
    5. Initialize brain databases (Tier 1-3)
    6. Validate setup completion

Args:
    profile: Setup profile ('minimal', 'standard', 'full')
    project_root: Project root path (auto-detected if None)

Returns:
    Result dictionary with success status and details


**Parameters:**

- `profile` (str) = `'standard'`: Setup profile ('minimal', 'standard', 'full')
- `project_root` (Path) = `None`: Project root path (auto-detected if None)


**Returns:** Dict[str, Any]
  Result dictionary with success status and details


---
