# setup_utility

Setup Utility

Fast, lightweight setup management for CORTEX shared environment.
Replaces orchestrator with focused utility for shared venv management.

Features:
- Shared tooling environment at ~/.cortex/venv/
- Project-specific dependency isolation
- 10x setup time reduction
- Version conflict resolution
- Automatic Python executable detection

Operations:
1. create_shared_venv - Create shared virtual environment
2. install_cortex_tooling - Install pytest, pyyaml, requests, playwright
3. link_project - Link project to shared environment
4. install_project_deps - Install project-specific dependencies
5. get_python_path - Get Python executable path
6. get_project_env_vars - Get environment variables with PYTHONPATH

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [create_versioned_shared_venv](#create_versioned_shared_venv)
- [create_shared_venv](#create_shared_venv)
- [install_cortex_tooling](#install_cortex_tooling)
- [link_project](#link_project)
- [install_project_deps](#install_project_deps)
- [get_python_path](#get_python_path)
- [get_project_env_vars](#get_project_env_vars)


## Overview

- **Classes:** 0
- **Functions:** 8
- **Dependencies:** json, pathlib, subprocess, sys, typing, venv


## Functions

### create_versioned_shared_venv

```python
create_versioned_shared_venv(python_version: Optional[str], home_dir: Optional[Path]) -> Dict[str, Any]
```

Create version-specific shared CORTEX environment at ~/.cortex/venv-X.Y/

This integrates with PythonEnvironmentModule's shared environment detection.

Args:
    python_version: Python version string (e.g., "3.11"). Auto-detects if None.
    home_dir: Home directory path (defaults to user home)
    
Returns:
    Dict with operation result:
        - success: bool
        - venv_path: str (path to created venv)
        - python_version: str (version used)
        - message: str
        
Example:
    >>> result = create_versioned_shared_venv()
    >>> print(result['venv_path'])  # ~/.cortex/venv-3.11/


**Parameters:**

- `python_version` (Optional[str]) = `None`: Python version string (e.g., "3.11"). Auto-detects if None.
- `home_dir` (Optional[Path]) = `None`: Home directory path (defaults to user home)


**Returns:** Dict[str, Any]
  Dict with operation result: - success: bool - venv_path: str (path to created venv) - python_version: str (version used) - message: str


---

### create_shared_venv

```python
create_shared_venv(home_dir: Optional[Path]) -> Dict[str, Any]
```

Create shared CORTEX virtual environment at ~/.cortex/venv/

DEPRECATED: Use create_versioned_shared_venv() for Python version isolation.
This function is maintained for backward compatibility only.

Args:
    home_dir: Home directory path (defaults to user home)
    
Returns:
    Dict with operation result:
        - success: bool
        - venv_path: str (path to created venv)
        - message: str


**Parameters:**

- `home_dir` (Optional[Path]) = `None`: Home directory path (defaults to user home)


**Returns:** Dict[str, Any]
  Dict with operation result: - success: bool - venv_path: str (path to created venv) - message: str


---

### install_cortex_tooling

```python
install_cortex_tooling(venv_path: Path) -> Dict[str, Any]
```

Install CORTEX tooling packages into shared environment.

Args:
    venv_path: Path to shared virtual environment
    
Returns:
    Dict with operation result:
        - success: bool
        - packages: list of installed packages
        - message: str


**Parameters:**

- `venv_path` (Path): Path to shared virtual environment


**Returns:** Dict[str, Any]
  Dict with operation result: - success: bool - packages: list of installed packages - message: str


---

### link_project

```python
link_project(project_dir: Path, venv_path: Path) -> Dict[str, Any]
```

Link project to shared CORTEX environment.

Updates project's cortex.config.json with shared venv reference.

Args:
    project_dir: Path to project directory
    venv_path: Path to shared virtual environment
    
Returns:
    Dict with operation result:
        - success: bool
        - config_path: str
        - message: str


**Parameters:**

- `project_dir` (Path): Path to project directory
- `venv_path` (Path): Path to shared virtual environment


**Returns:** Dict[str, Any]
  Dict with operation result: - success: bool - config_path: str - message: str


---

### install_project_deps

```python
install_project_deps(project_dir: Path, python_path: Path) -> Dict[str, Any]
```

Install project-specific dependencies separately from shared tooling.

Args:
    project_dir: Path to project directory
    python_path: Path to Python executable in shared venv
    
Returns:
    Dict with operation result:
        - success: bool
        - packages: list of installed packages
        - message: str


**Parameters:**

- `project_dir` (Path): Path to project directory
- `python_path` (Path): Path to Python executable in shared venv


**Returns:** Dict[str, Any]
  Dict with operation result: - success: bool - packages: list of installed packages - message: str


---

### get_python_path

```python
get_python_path(venv_path: Path) -> Path
```

Get Python executable path within virtual environment.

Args:
    venv_path: Path to virtual environment directory
    
Returns:
    Path to Python executable (platform-specific)


**Parameters:**

- `venv_path` (Path): Path to virtual environment directory


**Returns:** Path
  Path to Python executable (platform-specific)


---

### get_project_env_vars

```python
get_project_env_vars(project_dir: Path) -> Dict[str, str]
```

Get environment variables for running Python with project dependencies.

Returns PYTHONPATH including project-specific site-packages directory.

Args:
    project_dir: Path to project directory
    
Returns:
    Dict of environment variables with PYTHONPATH configuration


**Parameters:**

- `project_dir` (Path): Path to project directory


**Returns:** Dict[str, str]
  Dict of environment variables with PYTHONPATH configuration


---
