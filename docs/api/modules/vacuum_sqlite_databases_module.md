# vacuum_sqlite_databases_module

Vacuum SQLite Databases Module

Optimizes SQLite databases to recover space and improve performance.

SOLID Principles:
- Single Responsibility: Only handles SQLite optimization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [VacuumSQLiteDatabasesModule](#vacuumsqlitedatabasesmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, pathlib, sqlite3, src, typing


## Classes

### VacuumSQLiteDatabasesModule

```python
class VacuumSQLiteDatabasesModule(BaseOperationModule)
```

Cleanup module for optimizing SQLite databases.

Responsibilities:
1. Vacuum CORTEX brain databases
2. Calculate space recovered
3. Report optimization results


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]
  ```

  Validate prerequisites for database optimization.

Checks:
1. Project root available
2. Brain directory exists

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute SQLite database optimization.

Steps:
1. Find all SQLite databases in cortex-brain
2. Get size before vacuum
3. Run VACUUM on each database
4. Calculate space recovered

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---
