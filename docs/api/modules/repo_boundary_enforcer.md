# repo_boundary_enforcer

Repo Boundary Enforcer

Enforces strict isolation between repositories in multi-repo workspaces.
Prevents cross-repo imports, state sharing, and cortex-implants leakage.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [RepoBoundaryViolation](#repoboundaryviolation)
- [RepoBoundaryEnforcer](#repoboundaryenforcer)

### Functions
- [get_repo_boundary_enforcer](#get_repo_boundary_enforcer)
- [validate_cross_repo_operation](#validate_cross_repo_operation)


## Overview

- **Classes:** 2
- **Functions:** 2
- **Dependencies:** json, logging, pathlib, typing


## Classes

### RepoBoundaryViolation

```python
class RepoBoundaryViolation(Exception)
```

Exception raised when repo boundary is violated.



---

### RepoBoundaryEnforcer

```python
class RepoBoundaryEnforcer
```

Enforces forbidden boundaries between repositories.

Rules:
1. No cross-repo imports (cannot import code from another repo)
2. No shared state between repos (no shared files/databases)
3. Each repo's .cortex-implants is invisible to other repos
4. CORTEX repo is read-only for user repos (can use, can't modify)
5. No hardcoded paths to other repos

Features:
- Auto-detection of repo boundaries
- Import path validation
- File operation interception
- Violation logging and reporting

Usage:
    enforcer = RepoBoundaryEnforcer(workspace_root)
    enforcer.validate_operation(
        source_repo=Path("/workspace/frontend"),
        target_path=Path("/workspace/backend/src/models.py"),
        operation="import"
    )


**Methods:**

  #### `get_repo_root`

  ```python
  get_repo_root(self, path: Path) -> Optional[Path]
  ```

  Get the repository root for a given path.

Args:
    path: File or directory path
    
Returns:
    Repository root path or None if not in any repo

  **Parameters:**

  - `self`
  - `path` (Path): File or directory path


  **Returns:** Optional[Path]
    Repository root path or None if not in any repo


  #### `validate_operation`

  ```python
  validate_operation(self, source_repo: Path, target_path: Path, operation: str) -> bool
  ```

  Validate if operation crosses repo boundary.

Args:
    source_repo: Source repository path
    target_path: Target file/directory path
    operation: Operation type (import, read, write, access)
    
Returns:
    True if operation allowed
    
Raises:
    RepoBoundaryViolation: If operation crosses boundary

  **Parameters:**

  - `self`
  - `source_repo` (Path): Source repository path
  - `target_path` (Path): Target file/directory path
  - `operation` (str) = `'access'`: Operation type (import, read, write, access)


  **Returns:** bool
    True if operation allowed


  #### `validate_import`

  ```python
  validate_import(self, source_file: Path, import_path: str) -> bool
  ```

  Validate Python import statement.

Args:
    source_file: File containing the import
    import_path: Import path (e.g., "src.models.user")
    
Returns:
    True if import allowed
    
Raises:
    RepoBoundaryViolation: If import crosses boundary

  **Parameters:**

  - `self`
  - `source_file` (Path): File containing the import
  - `import_path` (str): Import path (e.g., "src.models.user")


  **Returns:** bool
    True if import allowed


  #### `check_cortex_implants_leakage`

  ```python
  check_cortex_implants_leakage(self, source_repo: Path, search_path: Path) -> bool
  ```

  Check if operation would leak cortex-implants between repos.

Args:
    source_repo: Source repository
    search_path: Path being searched
    
Returns:
    True if no leakage
    
Raises:
    RepoBoundaryViolation: If leakage detected

  **Parameters:**

  - `self`
  - `source_repo` (Path): Source repository
  - `search_path` (Path): Path being searched


  **Returns:** bool
    True if no leakage


  #### `get_violations_report`

  ```python
  get_violations_report(self) -> str
  ```

  Generate report of all violations.

Returns:
    Human-readable report

  **Parameters:**

  - `self`


  **Returns:** str
    Human-readable report


  #### `save_violations_log`

  ```python
  save_violations_log(self, output_file: Path) -> None
  ```

  Save violations log to JSON file.

  **Parameters:**

  - `self`
  - `output_file` (Path)


  **Returns:** None


  #### `get_repo_inventory`

  ```python
  get_repo_inventory(self) -> Dict[str, any]
  ```

  Get inventory of all repos in workspace.

Returns:
    Dictionary with repo information

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]
    Dictionary with repo information


  #### `print_repo_inventory`

  ```python
  print_repo_inventory(self) -> None
  ```

  Print repo inventory to console.

  **Parameters:**

  - `self`


  **Returns:** None



---

## Functions

### get_repo_boundary_enforcer

```python
get_repo_boundary_enforcer(workspace_root: Path) -> RepoBoundaryEnforcer
```

Get singleton enforcer instance.


**Parameters:**

- `workspace_root` (Path)


**Returns:** RepoBoundaryEnforcer


---

### validate_cross_repo_operation

```python
validate_cross_repo_operation(source_repo: Path, target_path: Path, operation: str) -> bool
```

Convenience function to validate cross-repo operation.

Args:
    source_repo: Source repository path
    target_path: Target file/directory path
    operation: Operation type
    
Returns:
    True if allowed
    
Raises:
    RepoBoundaryViolation: If operation forbidden


**Parameters:**

- `source_repo` (Path): Source repository path
- `target_path` (Path): Target file/directory path
- `operation` (str) = `'access'`: Operation type


**Returns:** bool
  True if allowed


---
