# migration_utility

Planning Migration Utility

Lightweight status-based planning document organization.

Core Operations:
- migrate_documents: Full migration workflow with backup and validation
- detect_status: Extract status from frontmatter patterns
- backup_planning_dir: Create timestamped backup
- validate_migration: Verify all files moved correctly
- organize_by_status: Move documents to status subdirectories

Version: 3.0.0 (Migrated from PlanningDocumentMigrator v2.0)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [migrate_documents](#migrate_documents)
- [detect_status](#detect_status)
- [backup_planning_dir](#backup_planning_dir)
- [validate_migration](#validate_migration)
- [organize_by_status](#organize_by_status)


## Overview

- **Classes:** 0
- **Functions:** 6
- **Dependencies:** datetime, os, pathlib, re, shutil, src, time, typing


## Functions

### migrate_documents

```python
migrate_documents(planning_path: str, dry_run: bool, create_backup: bool) -> Dict
```

Migrate planning documents to status-based directories

Args:
    planning_path: Path to planning directory
    dry_run: Preview without moving files
    create_backup: Create backup before migration
    
Returns:
    Dict with migration results
    
Example:
    >>> result = migrate_documents("/path/to/planning", dry_run=False)
    >>> print(result["migrated_count"])
    15


**Parameters:**

- `planning_path` (str): Path to planning directory
- `dry_run` (bool) = `True`: Preview without moving files
- `create_backup` (bool) = `True`: Create backup before migration


**Returns:** Dict
  Dict with migration results


---

### detect_status

```python
detect_status(plan_path: str) -> str
```

Detect plan status from frontmatter

Args:
    plan_path: Path to planning document
    
Returns:
    Status directory name
    
Example:
    >>> status = detect_status("/path/to/plan.md")
    >>> print(status)
    'active'


**Parameters:**

- `plan_path` (str): Path to planning document


**Returns:** str
  Status directory name


---

### backup_planning_dir

```python
backup_planning_dir(planning_dir: Path, plans: List[Path]) -> Path
```

Create timestamped backup

Args:
    planning_dir: Planning directory
    plans: List of plan paths
    
Returns:
    Backup directory path
    
Example:
    >>> backup = backup_planning_dir(Path("/planning"), plans)
    >>> print(backup.name)
    'backup-20250102-143015'


**Parameters:**

- `planning_dir` (Path): Planning directory
- `plans` (List[Path]): List of plan paths


**Returns:** Path
  Backup directory path


---

### validate_migration

```python
validate_migration(planning_dir: Path, original_plans: List[Path], migrations: List[Dict]) -> bool
```

Verify migration completed successfully

Args:
    planning_dir: Planning directory
    original_plans: Original plan paths
    migrations: Migration records
    
Returns:
    True if valid
    
Example:
    >>> valid = validate_migration(planning_dir, plans, migrations)
    >>> print(valid)
    True


**Parameters:**

- `planning_dir` (Path): Planning directory
- `original_plans` (List[Path]): Original plan paths
- `migrations` (List[Dict]): Migration records


**Returns:** bool
  True if valid


---

### organize_by_status

```python
organize_by_status(planning_path: str, document_path: str) -> Optional[str]
```

Organize single document to status subdirectory

Args:
    planning_path: Planning directory
    document_path: Document to organize
    
Returns:
    New path if organized, None if error
    
Example:
    >>> new_path = organize_by_status("/planning", "/planning/plan.md")
    >>> print(new_path)
    '/planning/active/plan.md'


**Parameters:**

- `planning_path` (str): Planning directory
- `document_path` (str): Document to organize


**Returns:** Optional[str]
  New path if organized, None if error


---
