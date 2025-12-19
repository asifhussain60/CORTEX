# migrate_tier1

CORTEX Tier 1 Migration Script
Migrates conversation data from JSONL to SQLite

Task 0.5.1: Tier 1 Migration Script
Duration: 1-1.5 hours


## Table of Contents

### Classes
- [Tier1Migrator](#tier1migrator)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, datetime, json, pathlib, sqlite3, src, sys, typing


## Classes

### Tier1Migrator

```python
class Tier1Migrator
```

Migrates Tier 1 conversation data from JSONL to SQLite


**Methods:**

  #### `create_schema`

  ```python
  create_schema(self, conn: sqlite3.Connection)
  ```

  Create Tier 1 database schema

  **Parameters:**

  - `self`
  - `conn` (sqlite3.Connection)


  #### `migrate_conversation`

  ```python
  migrate_conversation(self, conn: sqlite3.Connection, conv_data: Dict) -> bool
  ```

  Migrate a single conversation record

Args:
    conn: Database connection
    conv_data: Conversation data from JSONL
    
Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `conn` (sqlite3.Connection): Database connection
  - `conv_data` (Dict): Conversation data from JSONL


  **Returns:** bool
    True if successful, False otherwise


  #### `migrate`

  ```python
  migrate(self) -> Dict
  ```

  Execute migration from JSONL to SQLite

Returns:
    Migration statistics dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict
    Migration statistics dictionary



---

## Functions

### main

```python
main()
```

---
