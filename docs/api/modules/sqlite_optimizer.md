# sqlite_optimizer

SQLite Database Optimization Module

Analyzes and optimizes CORTEX SQLite databases across all tiers.
Performs VACUUM, integrity checks, index analysis, and query optimization.

Copyright © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [SQLiteOptimizer](#sqliteoptimizer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, logging, pathlib, sqlite3, src, typing


## Classes

### SQLiteOptimizer

```python
class SQLiteOptimizer
```

Optimizes SQLite databases for CORTEX tiers.

Features:
- VACUUM to reclaim space and optimize storage
- Integrity check validation
- Index usage analysis
- Query performance analysis
- Fragmentation detection
- Size reporting with before/after comparison


**Methods:**

  #### `optimize_all`

  ```python
  optimize_all(self) -> Dict[str, Any]
  ```

  Optimize all tier databases.

Returns:
    Dictionary with optimization results for each tier

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with optimization results for each tier


  #### `optimize_database`

  ```python
  optimize_database(self, db_path: Path, tier_name: str) -> Dict[str, Any]
  ```

  Optimize a single database.

Args:
    db_path: Path to database file
    tier_name: Name of tier for reporting
    
Returns:
    Dictionary with optimization results

  **Parameters:**

  - `self`
  - `db_path` (Path): Path to database file
  - `tier_name` (str): Name of tier for reporting


  **Returns:** Dict[str, Any]
    Dictionary with optimization results


  #### `generate_report`

  ```python
  generate_report(self, results: Dict[str, Any], output_path: Optional[Path]) -> str
  ```

  Generate optimization report.

Args:
    results: Optimization results from optimize_all()
    output_path: Optional path to save JSON report
    
Returns:
    Formatted report string

  **Parameters:**

  - `self`
  - `results` (Dict[str, Any]): Optimization results from optimize_all()
  - `output_path` (Optional[Path]) = `None`: Optional path to save JSON report


  **Returns:** str
    Formatted report string



---
