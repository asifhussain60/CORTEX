# version_manager

Version Manager for CORTEX

Centralized version management system that:
- Reads version information from cortex.config.json
- Provides API for version queries across codebase
- Supports orchestrator-specific version tracking
- Validates version consistency

Phase 15 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [VersionInfo](#versioninfo)
- [VersionManager](#versionmanager)

### Functions
- [get_version_manager](#get_version_manager)
- [get_cortex_version](#get_cortex_version)
- [get_planning_system_version](#get_planning_system_version)


## Overview

- **Classes:** 2
- **Functions:** 3
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, typing


## Classes

### VersionInfo

```python
class VersionInfo
```

**Decorators:** `dataclass`

Version information container.


**Attributes:**

- `cortex_version`: str
- `planning_system_version`: str
- `orchestrator_versions`: Dict[str, str]
- `config_path`: Path
- `last_read`: datetime


**Methods:**


---

### VersionManager

```python
class VersionManager
```

Centralized version management for CORTEX.

Reads version from cortex.config.json and provides consistent
version information across all orchestrators and modules.

Usage:
    vm = VersionManager()
    cortex_version = vm.get_cortex_version()
    planning_version = vm.get_planning_system_version()
    orchestrator_version = vm.get_orchestrator_version("planning_orchestrator")


**Attributes:**

- `_instance`: Optional['VersionManager']


**Methods:**

  #### `get_cortex_version`

  ```python
  get_cortex_version(self) -> str
  ```

  Get CORTEX version.

Returns:
    CORTEX version string (e.g., "3.9.0")

  **Parameters:**

  - `self`


  **Returns:** str
    CORTEX version string (e.g., "3.9.0")


  #### `get_planning_system_version`

  ```python
  get_planning_system_version(self) -> str
  ```

  Get Planning System version.

Returns:
    Planning System version string (e.g., "3.0")

  **Parameters:**

  - `self`


  **Returns:** str
    Planning System version string (e.g., "3.0")


  #### `get_orchestrator_version`

  ```python
  get_orchestrator_version(self, orchestrator_name: str) -> str
  ```

  Get version for specific orchestrator.

Args:
    orchestrator_name: Name of orchestrator
                     (e.g., "planning_orchestrator", "ado_orchestrator")

Returns:
    Orchestrator version string or "unknown" if not registered

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of orchestrator (e.g., "planning_orchestrator", "ado_orchestrator")


  **Returns:** str
    Orchestrator version string or "unknown" if not registered


  #### `register_orchestrator_version`

  ```python
  register_orchestrator_version(self, orchestrator_name: str, version: str) -> None
  ```

  Register orchestrator-specific version.

Args:
    orchestrator_name: Name of orchestrator
    version: Version string (e.g., "3.0", "2.5")

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of orchestrator
  - `version` (str): Version string (e.g., "3.0", "2.5")


  **Returns:** None


  #### `get_version_info`

  ```python
  get_version_info(self) -> VersionInfo
  ```

  Get complete version information.

Returns:
    VersionInfo object with all version data

  **Parameters:**

  - `self`


  **Returns:** VersionInfo
    VersionInfo object with all version data


  #### `refresh`

  ```python
  refresh(self) -> None
  ```

  Reload version information from config file.

Useful after config file updates.

  **Parameters:**

  - `self`


  **Returns:** None


  #### `validate_consistency`

  ```python
  validate_consistency(self) -> Dict[str, Any]
  ```

  Validate version consistency across system.

Checks:
- Config file exists and is readable
- Required version fields present
- Version format validity (semantic versioning)

Returns:
    Dictionary with validation results:
    {
        'valid': bool,
        'errors': List[str],
        'warnings': List[str],
        'cortex_version': str,
        'planning_version': str,
        'orchestrators': Dict[str, str]
    }

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with validation results: { 'valid': bool, 'errors': List[str], 'warnings': List[str], 'cortex_version': str, 'planning_version': str, 'orchestrators': Dict[str, str] }


  #### `get_version_string`

  ```python
  get_version_string(self, include_orchestrators: bool) -> str
  ```

  Get formatted version string for display.

Args:
    include_orchestrators: Include registered orchestrator versions

Returns:
    Formatted version string

  **Parameters:**

  - `self`
  - `include_orchestrators` (bool) = `False`: Include registered orchestrator versions


  **Returns:** str
    Formatted version string



---

## Functions

### get_version_manager

```python
get_version_manager(config_path: Optional[Path]) -> VersionManager
```

Get global VersionManager instance (singleton).

Args:
    config_path: Optional path to cortex.config.json

Returns:
    VersionManager instance


**Parameters:**

- `config_path` (Optional[Path]) = `None`: Optional path to cortex.config.json


**Returns:** VersionManager
  VersionManager instance


---

### get_cortex_version

```python
get_cortex_version() -> str
```

Convenience function to get CORTEX version.

Returns:
    CORTEX version string


**Returns:** str
  CORTEX version string


---

### get_planning_system_version

```python
get_planning_system_version() -> str
```

Convenience function to get Planning System version.

Returns:
    Planning System version string


**Returns:** str
  Planning System version string


---
