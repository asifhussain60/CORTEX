# schema_version_tracker

Schema Version Tracker

Tracks schema versions for all 3 brain tiers, detects migration needs,
and maintains version history.

Responsibilities:
- Get/set current schema versions per tier
- Detect when migrations are needed
- Track version history
- Log applied migrations
- Define latest available schema versions

Storage:
- Versions stored in Tier 1 metadata table
- Format: JSON with version number and timestamp
- History stored as JSON array

Usage:
    >>> from src.tier0.schema_version_tracker import SchemaVersionTracker
    >>> tracker = SchemaVersionTracker(brain_path="/path/to/cortex-brain")
    >>> version = tracker.get_version('tier2')
    >>> if tracker.needs_migration('tier2', target_version=2):
    ...     # Apply migration
    ...     tracker.record_migration('tier2', 1, 2, 'Add FTS5 support')

Author: Asif Hussain
Phase: 7.3 - Brain Initialization System


## Table of Contents

### Classes
- [SchemaVersionTracker](#schemaversiontracker)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, pathlib, sqlite3, typing


## Classes

### SchemaVersionTracker

```python
class SchemaVersionTracker
```

Tracks schema versions across all 3 brain tiers.

Provides version management, migration detection, and history tracking.


**Methods:**

  #### `get_version`

  ```python
  get_version(self, tier: str) -> int
  ```

  Get current schema version for a tier.

Args:
    tier: Tier name ('tier1', 'tier2', or 'tier3')
    
Returns:
    Version number (integer), 0 if not set

  **Parameters:**

  - `self`
  - `tier` (str): Tier name ('tier1', 'tier2', or 'tier3')


  **Returns:** int
    Version number (integer), 0 if not set


  #### `set_version`

  ```python
  set_version(self, tier: str, version: int)
  ```

  Set schema version for a tier.

Args:
    tier: Tier name ('tier1', 'tier2', or 'tier3')
    version: Version number to set

  **Parameters:**

  - `self`
  - `tier` (str): Tier name ('tier1', 'tier2', or 'tier3')
  - `version` (int): Version number to set


  #### `needs_migration`

  ```python
  needs_migration(self, tier: str, target_version: int) -> bool
  ```

  Check if migration is needed.

Args:
    tier: Tier name
    target_version: Target version to migrate to
    
Returns:
    True if current version < target version

  **Parameters:**

  - `self`
  - `tier` (str): Tier name
  - `target_version` (int): Target version to migrate to


  **Returns:** bool
    True if current version < target version


  #### `get_version_history`

  ```python
  get_version_history(self, tier: str) -> List[Dict[str, Any]]
  ```

  Get version history for a tier.

Args:
    tier: Tier name
    
Returns:
    List of version change records with version and timestamp

  **Parameters:**

  - `self`
  - `tier` (str): Tier name


  **Returns:** List[Dict[str, Any]]
    List of version change records with version and timestamp


  #### `record_migration`

  ```python
  record_migration(self, tier: str, from_version: int, to_version: int, description: str)
  ```

  Record a migration in the log.

Args:
    tier: Tier name
    from_version: Version migrated from
    to_version: Version migrated to
    description: Migration description

  **Parameters:**

  - `self`
  - `tier` (str): Tier name
  - `from_version` (int): Version migrated from
  - `to_version` (int): Version migrated to
  - `description` (str): Migration description


  #### `get_applied_migrations`

  ```python
  get_applied_migrations(self, tier: str) -> List[Dict[str, Any]]
  ```

  Get list of applied migrations for a tier.

Args:
    tier: Tier name
    
Returns:
    List of migration records

  **Parameters:**

  - `self`
  - `tier` (str): Tier name


  **Returns:** List[Dict[str, Any]]
    List of migration records


  #### `get_latest_versions`

  ```python
  get_latest_versions(self) -> Dict[str, int]
  ```

  Get latest available schema versions.

Returns hardcoded schema versions based on actual schema files.

Returns:
    Dict with tier names and latest version numbers

  **Parameters:**

  - `self`


  **Returns:** Dict[str, int]
    Dict with tier names and latest version numbers



---
