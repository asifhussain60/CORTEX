# schema_migrations

CORTEX Tier 1: Schema Migration System
Zero-downtime schema evolution with version tracking

Author: Asif Hussain
Created: December 2, 2025
Phase: 7.1 - Tier 1 Schema Completion


## Table of Contents

### Classes
- [SchemaMigration](#schemamigration)
- [MigrationManager](#migrationmanager)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** contextlib, dataclasses, datetime, pathlib, sqlite3, typing


## Classes

### SchemaMigration

```python
class SchemaMigration
```

**Decorators:** `dataclass`

Represents a single schema migration


**Attributes:**

- `version`: str
- `name`: str
- `up_sql`: str
- `down_sql`: str
- `description`: Optional[str]



---

### MigrationManager

```python
class MigrationManager
```

Manages schema migrations for Tier 1 database

Features:
- Version tracking
- Forward migrations (up)
- Rollback migrations (down)
- Zero-downtime evolution
- Migration history

Usage:
    manager = MigrationManager(db_path="cortex-brain/tier1/working_memory.db")
    
    # Register migration
    migration = SchemaMigration(
        version="001",
        name="add_working_memory",
        up_sql="CREATE TABLE working_memory (...)",
        down_sql="DROP TABLE working_memory"
    )
    manager.register_migration(migration)
    
    # Apply migration
    manager.apply_migration("001")
    
    # Rollback if needed
    manager.rollback_migration("001")


**Methods:**

  #### `register_migration`

  ```python
  register_migration(self, migration: SchemaMigration)
  ```

  Register a migration for tracking

Args:
    migration: SchemaMigration object to register

  **Parameters:**

  - `self`
  - `migration` (SchemaMigration): SchemaMigration object to register


  #### `apply_migration`

  ```python
  apply_migration(self, version: str) -> bool
  ```

  Apply a migration (forward)

Args:
    version: Migration version to apply
    
Returns:
    True if successful, False if already applied or failed

  **Parameters:**

  - `self`
  - `version` (str): Migration version to apply


  **Returns:** bool
    True if successful, False if already applied or failed


  #### `rollback_migration`

  ```python
  rollback_migration(self, version: str) -> bool
  ```

  Rollback a migration (reverse)

Args:
    version: Migration version to rollback
    
Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `version` (str): Migration version to rollback


  **Returns:** bool
    True if successful, False otherwise


  #### `get_current_version`

  ```python
  get_current_version(self) -> str
  ```

  Get current schema version (highest applied migration)

Returns:
    Version string (e.g., "003") or "000" if no migrations applied

  **Parameters:**

  - `self`


  **Returns:** str
    Version string (e.g., "003") or "000" if no migrations applied


  #### `list_applied_migrations`

  ```python
  list_applied_migrations(self) -> List[Dict[str, Any]]
  ```

  List all applied migrations

Returns:
    List of migration records

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of migration records


  #### `list_pending_migrations`

  ```python
  list_pending_migrations(self) -> List[SchemaMigration]
  ```

  List all registered but not yet applied migrations

Returns:
    List of pending SchemaMigration objects

  **Parameters:**

  - `self`


  **Returns:** List[SchemaMigration]
    List of pending SchemaMigration objects


  #### `apply_all_pending`

  ```python
  apply_all_pending(self) -> Dict[str, bool]
  ```

  Apply all pending migrations in order

Returns:
    Dictionary of {version: success_status}

  **Parameters:**

  - `self`


  **Returns:** Dict[str, bool]
    Dictionary of {version: success_status}


  #### `get_migration_history`

  ```python
  get_migration_history(self) -> List[Dict[str, Any]]
  ```

  Get complete migration history including failures

Returns:
    List of all migration records

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of all migration records



---
