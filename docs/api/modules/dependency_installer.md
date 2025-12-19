# dependency_installer

Dependency Installer

Handles automated installation of CORTEX dependencies with validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [DependencyResult](#dependencyresult)
- [DependencyInstaller](#dependencyinstaller)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, logging, pathlib, subprocess, sys, typing


## Classes

### DependencyResult

```python
class DependencyResult
```

**Decorators:** `dataclass`

Result of dependency installation.


**Attributes:**

- `success`: bool
- `python_version`: str
- `installed_packages`: List[str]
- `failed_packages`: List[str]
- `venv_created`: bool
- `errors`: List[str]



---

### DependencyInstaller

```python
class DependencyInstaller
```

Handles CORTEX dependency installation and validation.

Features:
- Python version validation (3.8+)
- Virtual environment detection/creation
- Requirements.txt installation
- Package verification
- Rollback on failure


**Methods:**

  #### `install_dependencies`

  ```python
  install_dependencies(self, create_venv: bool, skip_validation: bool) -> DependencyResult
  ```

  Install CORTEX dependencies with validation.

Args:
    create_venv: Create virtual environment if missing
    skip_validation: Skip Python version validation

Returns:
    DependencyResult with installation status

  **Parameters:**

  - `self`
  - `create_venv` (bool) = `True`: Create virtual environment if missing
  - `skip_validation` (bool) = `False`: Skip Python version validation


  **Returns:** DependencyResult
    DependencyResult with installation status


  #### `get_installed_packages`

  ```python
  get_installed_packages(self) -> List[str]
  ```

  Get list of currently installed packages.

  **Parameters:**

  - `self`


  **Returns:** List[str]



---

## Functions

### main

```python
main()
```

CLI entry point for testing.


---
