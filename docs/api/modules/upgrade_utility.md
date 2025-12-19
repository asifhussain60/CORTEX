# upgrade_utility

Upgrade Utility - CORTEX Auto-Upgrade with Brain Preservation

Comprehensive upgrade system with safety-first approach:
- Version checking and comparison
- Brain data backup/restore with verification
- Git operations (pull, merge, rollback)
- Schema migrations with tracking
- Dependency validation
- Operational readiness verification
- What's New feature discovery
- Bootstrap verification

Part of CORTEX 3.2.1 - Upgrade System
Sprint 12b Migration: upgrade_orchestrator (1,115 lines) → upgrade_utility (~1,200 lines)
Author: Asif Hussain

HIGH RISK OPERATIONS - Brain data preservation critical
Zero tolerance for data loss, comprehensive testing required

Operations:
- check_for_updates: Compare current vs remote version
- create_backup: Brain data backup with metadata
- verify_backup: Validate backup integrity
- restore_backup: Rollback to previous state
- execute_upgrade: Complete upgrade workflow
- run_migrations: Apply schema migrations
- validate_dependencies: Verify core/optional dependencies
- validate_operational_readiness: Confirm CORTEX functionality
- validate_test_suite: Verify test discoverability
- generate_whats_new: Feature discovery since last version
- list_backups: Show available backups
- compare_versions: Semantic version comparison


## Table of Contents

### Classes
- [VersionInfo](#versioninfo)
- [BackupMetadata](#backupmetadata)
- [UpgradeResult](#upgraderesult)

### Functions
- [get_current_version](#get_current_version)
- [get_remote_version](#get_remote_version)
- [compare_versions](#compare_versions)
- [check_for_updates](#check_for_updates)
- [create_backup](#create_backup)
- [verify_backup](#verify_backup)
- [restore_backup](#restore_backup)
- [list_backups](#list_backups)
- [run_migrations](#run_migrations)
- [uninstall_unused_packages](#uninstall_unused_packages)
- [validate_dependencies](#validate_dependencies)
- [validate_operational_readiness](#validate_operational_readiness)
- [execute_upgrade](#execute_upgrade)


## Overview

- **Classes:** 3
- **Functions:** 14
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, shutil, sqlite3, subprocess, sys, tempfile, tier1, tier2, tier3, time, typing


## Classes

### VersionInfo

```python
class VersionInfo
```

**Decorators:** `dataclass`

Version information with comparison support.


**Attributes:**

- `version`: str
- `branch`: str
- `timestamp`: str
- `has_updates`: bool


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### BackupMetadata

```python
class BackupMetadata
```

**Decorators:** `dataclass`

Backup metadata with verification info.


**Attributes:**

- `backup_id`: str
- `timestamp`: str
- `version`: str
- `branch`: str
- `items`: List[str]
- `verified`: bool
- `size_bytes`: int


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### UpgradeResult

```python
class UpgradeResult
```

**Decorators:** `dataclass`

Upgrade execution result with complete details.


**Attributes:**

- `success`: bool
- `from_version`: str
- `to_version`: str
- `backup_id`: Optional[str]
- `migrations_applied`: int
- `whats_new`: str
- `validation_results`: Dict[str, Any]
- `message`: str
- `errors`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### get_current_version

```python
get_current_version(cortex_root: Path) -> str
```

Get current CORTEX version from VERSION file.

Args:
    cortex_root: CORTEX root directory

Returns:
    Version string or "unknown"

Example:
    >>> get_current_version(Path("/path/to/CORTEX"))
    '3.2.1'


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** str
  Version string or "unknown"


---

### get_remote_version

```python
get_remote_version(cortex_root: Path) -> str
```

Get remote version from origin/main:VERSION.

Args:
    cortex_root: CORTEX root directory

Returns:
    Remote version string or "unknown"

Example:
    >>> get_remote_version(Path("/path/to/CORTEX"))
    '3.3.0'


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** str
  Remote version string or "unknown"


---

### compare_versions

```python
compare_versions(v1: str, v2: str) -> int
```

Compare semantic version strings.

Args:
    v1: First version (e.g., "3.2.0")
    v2: Second version (e.g., "3.3.0")

Returns:
    -1 if v1 < v2, 0 if equal, 1 if v1 > v2

Example:
    >>> compare_versions("3.2.0", "3.3.0")
    -1
    >>> compare_versions("3.3.0", "3.2.0")
    1
    >>> compare_versions("3.2.0", "3.2.0")
    0


**Parameters:**

- `v1` (str): First version (e.g., "3.2.0")
- `v2` (str): Second version (e.g., "3.3.0")


**Returns:** int
  -1 if v1 < v2, 0 if equal, 1 if v1 > v2


---

### check_for_updates

```python
check_for_updates(cortex_root: Path) -> VersionInfo
```

Check if CORTEX updates are available from origin/main.

Fetches latest from remote and compares versions.

Args:
    cortex_root: CORTEX root directory

Returns:
    VersionInfo with update status

Example:
    >>> info = check_for_updates(Path("/path/to/CORTEX"))
    >>> info.has_updates
    True
    >>> info.version
    '3.2.1'


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** VersionInfo
  VersionInfo with update status


---

### create_backup

```python
create_backup(cortex_root: Path) -> Optional[BackupMetadata]
```

Create backup of brain data and user files.

HIGH RISK OPERATION - Brain data preservation critical.

Backs up:
- cortex-brain/feedback
- cortex-brain/working_memory.db
- cortex-brain/config
- cortex-brain/documents/planning
- logs
- VERSION

Args:
    cortex_root: CORTEX root directory

Returns:
    BackupMetadata or None if failed

Example:
    >>> metadata = create_backup(Path("/path/to/CORTEX"))
    >>> metadata.backup_id
    '20241203_143000'
    >>> metadata.verified
    True


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** Optional[BackupMetadata]
  BackupMetadata or None if failed


---

### verify_backup

```python
verify_backup(cortex_root: Path, backup_id: str) -> bool
```

Verify backup integrity.

Checks that all backed up files exist and are readable.

Args:
    cortex_root: CORTEX root directory
    backup_id: Backup identifier

Returns:
    True if backup is valid, False otherwise

Example:
    >>> verify_backup(Path("/path/to/CORTEX"), "20241203_143000")
    True


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `backup_id` (str): Backup identifier


**Returns:** bool
  True if backup is valid, False otherwise


---

### restore_backup

```python
restore_backup(cortex_root: Path, backup_id: str) -> bool
```

Restore from backup (rollback).

HIGH RISK OPERATION - Restores brain data from backup.

Args:
    cortex_root: CORTEX root directory
    backup_id: Backup identifier to restore

Returns:
    True if restore successful, False otherwise

Example:
    >>> restore_backup(Path("/path/to/CORTEX"), "20241203_143000")
    True


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `backup_id` (str): Backup identifier to restore


**Returns:** bool
  True if restore successful, False otherwise


---

### list_backups

```python
list_backups(cortex_root: Path) -> List[BackupMetadata]
```

List available backups sorted by timestamp.

Args:
    cortex_root: CORTEX root directory

Returns:
    List of BackupMetadata, newest first

Example:
    >>> backups = list_backups(Path("/path/to/CORTEX"))
    >>> len(backups)
    3
    >>> backups[0].version
    '3.2.1'


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** List[BackupMetadata]
  List of BackupMetadata, newest first


---

### run_migrations

```python
run_migrations(cortex_root: Path) -> Tuple[bool, int]
```

Run database schema migrations.

Applies SQL migrations from cortex-brain/migrations/ that haven't
been applied yet. Tracks applied migrations in schema_migrations table.

Args:
    cortex_root: CORTEX root directory

Returns:
    Tuple of (success, migrations_applied_count)

Example:
    >>> success, count = run_migrations(Path("/path/to/CORTEX"))
    >>> success
    True
    >>> count
    3


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** Tuple[bool, int]
  Tuple of (success, migrations_applied_count)


---

### uninstall_unused_packages

```python
uninstall_unused_packages(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]
```

Uninstall packages that were removed in CORTEX 3.9.1 dependency audit.

Removes 67 packages (780 MB) with zero imports in src/:
- Dashboard packages: matplotlib, Flask, networkx (165 MB)
- Browser testing: playwright, selenium, pytest-selenium (170 MB)
- GitHub integration: PyGithub (5 MB)
- Multi-language: esprima, tree-sitter-languages (125 MB)
- Document parsing: python-docx, pypdf (25 MB)
- Other unused: tomli (5 MB)
- Dev tools: pytest-cov, pytest-asyncio (moved to requirements-dev.txt)
- Optional ML: scikit-learn, numpy, send2trash (moved to requirements-optional.txt)

Args:
    cortex_root: CORTEX root directory

Returns:
    Tuple of (success, results_dict)

Example:
    >>> success, results = uninstall_unused_packages(Path("/path/to/CORTEX"))
    >>> success
    True
    >>> results['uninstalled']
    ['matplotlib', 'Flask', 'networkx', ...]


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** Tuple[bool, Dict[str, Any]]
  Tuple of (success, results_dict)


---

### validate_dependencies

```python
validate_dependencies(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]
```

Validate core and optional dependencies are installed.

Core dependencies (MUST be present):
- pytest, PyYAML, python-dateutil, pydantic, watchdog, psutil, requests, parso, sqlparse

Optional dependencies (warn if missing):
- numpy, sklearn, send2trash

Args:
    cortex_root: CORTEX root directory

Returns:
    Tuple of (success, results_dict)

Example:
    >>> success, results = validate_dependencies(Path("/path/to/CORTEX"))
    >>> success
    True
    >>> results['core_installed']
    ['pytest', 'yaml', 'watchdog', 'psutil', 'requests']


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** Tuple[bool, Dict[str, Any]]
  Tuple of (success, results_dict)


---

### validate_operational_readiness

```python
validate_operational_readiness(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]
```

Validate CORTEX is fully operational.

Checks:
- Core imports (tier1, tier2, tier3)
- Database accessibility
- Config validity
- Template validity
- Protection rules validity

Args:
    cortex_root: CORTEX root directory

Returns:
    Tuple of (success, results_dict)

Example:
    >>> success, results = validate_operational_readiness(Path("/path/to/CORTEX"))
    >>> success
    True
    >>> results['imports']
    True


**Parameters:**

- `cortex_root` (Path): CORTEX root directory


**Returns:** Tuple[bool, Dict[str, Any]]
  Tuple of (success, results_dict)


---

### execute_upgrade

```python
execute_upgrade(cortex_root: Path, backup: bool, auto_migrate: bool, force: bool) -> UpgradeResult
```

Execute complete CORTEX upgrade workflow.

HIGH RISK OPERATION - Brain data preservation critical.

Workflow:
1. Check for updates
2. Create backup (if enabled)
3. Pull from origin/main
4. Run migrations (if enabled)
5. Validate dependencies
6. Validate operational readiness
7. Generate What's New report
8. Rollback on failure

Args:
    cortex_root: CORTEX root directory
    backup: Create backup before upgrade (default: True)
    auto_migrate: Run migrations automatically (default: True)
    force: Force upgrade even if no updates (default: False)

Returns:
    UpgradeResult with complete execution details

Example:
    >>> result = execute_upgrade(Path("/path/to/CORTEX"))
    >>> result.success
    True
    >>> result.to_version
    '3.3.0'
    >>> result.migrations_applied
    3


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `backup` (bool) = `True`: Create backup before upgrade (default: True)
- `auto_migrate` (bool) = `True`: Run migrations automatically (default: True)
- `force` (bool) = `False`: Force upgrade even if no updates (default: False)


**Returns:** UpgradeResult
  UpgradeResult with complete execution details


---
