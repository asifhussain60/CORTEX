# amnesia

CORTEX Tier 2: Enhanced Amnesia System
Scope-aware selective memory deletion with safety protections.

Features:
- Namespace-scoped deletion (never touch CORTEX-core)
- Generic pattern protection (scope='generic' immune)
- Multi-namespace safety (only delete when all namespaces cleared)
- Confidence-based deletion with safeguards
- Comprehensive audit logging


## Table of Contents

### Classes
- [AmnesiaStats](#amnesiastats)
- [EnhancedAmnesia](#enhancedamnesia)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, knowledge_graph, logging, pathlib, sqlite3, typing


## Classes

### AmnesiaStats

```python
class AmnesiaStats
```

**Decorators:** `dataclass`

Statistics from amnesia operations.


**Attributes:**

- `patterns_deleted`: int
- `relationships_deleted`: int
- `tags_deleted`: int
- `protected_count`: int
- `errors`: List[str]
- `deletion_log`: List[Dict[str, Any]]


**Methods:**


---

### EnhancedAmnesia

```python
class EnhancedAmnesia
```

Enhanced Amnesia System with scope and namespace protection.

CRITICAL SAFETY RULES:
1. NEVER delete scope='generic' patterns (CORTEX core intelligence)
2. NEVER delete patterns with 'CORTEX-core' in namespaces
3. For multi-namespace patterns, only delete when ALL namespaces cleared
4. Always require explicit confirmation for destructive operations
5. Log ALL deletions for audit trail and recovery


**Methods:**

  #### `delete_by_namespace`

  ```python
  delete_by_namespace(self, namespace: str, require_confirmation: bool, dry_run: bool, bypass_safety: bool) -> AmnesiaStats
  ```

  Delete all patterns in a specific namespace.

Safety protections:
- CORTEX-core namespace BLOCKED (cannot delete core intelligence)
- Generic patterns PROTECTED (even if namespace matches)
- Multi-namespace patterns only deleted if this is the LAST namespace
- Confirmation required if deleting >10 patterns

Args:
    namespace: Namespace to clear (e.g., 'KSESSIONS', 'NOOR')
    require_confirmation: If True, check deletion count threshold
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts and protected patterns

Raises:
    ValueError: If trying to delete CORTEX-core namespace
    RuntimeError: If deletion exceeds safety threshold without override

  **Parameters:**

  - `self`
  - `namespace` (str): Namespace to clear (e.g., 'KSESSIONS', 'NOOR')
  - `require_confirmation` (bool) = `True`: If True, check deletion count threshold
  - `dry_run` (bool) = `False`: If True, report what would be deleted without changes
  - `bypass_safety` (bool) = `False`


  **Returns:** AmnesiaStats
    AmnesiaStats with deletion counts and protected patterns


  #### `delete_by_confidence`

  ```python
  delete_by_confidence(self, max_confidence: float, protect_generic: bool, namespace: Optional[str], dry_run: bool) -> AmnesiaStats
  ```

  Delete patterns with confidence below threshold.

Args:
    max_confidence: Delete patterns with confidence <= this value
    protect_generic: Never delete generic patterns (default: True)
    namespace: Limit to specific namespace (optional)
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts

  **Parameters:**

  - `self`
  - `max_confidence` (float): Delete patterns with confidence <= this value
  - `protect_generic` (bool) = `True`: Never delete generic patterns (default: True)
  - `namespace` (Optional[str]) = `None`: Limit to specific namespace (optional)
  - `dry_run` (bool) = `False`: If True, report what would be deleted without changes


  **Returns:** AmnesiaStats
    AmnesiaStats with deletion counts


  #### `delete_by_age`

  ```python
  delete_by_age(self, days_inactive: int, protect_generic: bool, namespace: Optional[str], dry_run: bool) -> AmnesiaStats
  ```

  Delete patterns not accessed in specified days.

Args:
    days_inactive: Delete patterns not accessed in this many days
    protect_generic: Never delete generic patterns (default: True)
    namespace: Limit to specific namespace (optional)
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts

  **Parameters:**

  - `self`
  - `days_inactive` (int): Delete patterns not accessed in this many days
  - `protect_generic` (bool) = `True`: Never delete generic patterns (default: True)
  - `namespace` (Optional[str]) = `None`: Limit to specific namespace (optional)
  - `dry_run` (bool) = `False`: If True, report what would be deleted without changes


  **Returns:** AmnesiaStats
    AmnesiaStats with deletion counts


  #### `clear_application_scope`

  ```python
  clear_application_scope(self, confirmation_code: Optional[str], dry_run: bool) -> AmnesiaStats
  ```

  Delete ALL application-specific patterns (DANGEROUS!).

This is a nuclear option that clears all application knowledge while
preserving CORTEX core intelligence.

Protections:
- Generic patterns IMMUNE (never deleted)
- CORTEX-core namespace IMMUNE
- Requires confirmation code: "DELETE_ALL_APPLICATIONS"
- Dry run available for safety testing

Args:
    confirmation_code: Must be "DELETE_ALL_APPLICATIONS" to proceed
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts

Raises:
    ValueError: If confirmation code is missing or incorrect

  **Parameters:**

  - `self`
  - `confirmation_code` (Optional[str]) = `None`: Must be "DELETE_ALL_APPLICATIONS" to proceed
  - `dry_run` (bool) = `False`: If True, report what would be deleted without changes


  **Returns:** AmnesiaStats
    AmnesiaStats with deletion counts


  #### `get_deletion_preview`

  ```python
  get_deletion_preview(self, namespace: Optional[str], max_confidence: Optional[float], days_inactive: Optional[int]) -> Dict[str, Any]
  ```

  Preview what would be deleted without making changes.

Args:
    namespace: Preview namespace deletion
    max_confidence: Preview confidence threshold deletion
    days_inactive: Preview age-based deletion

Returns:
    Dict with deletion counts and sample patterns

  **Parameters:**

  - `self`
  - `namespace` (Optional[str]) = `None`: Preview namespace deletion
  - `max_confidence` (Optional[float]) = `None`: Preview confidence threshold deletion
  - `days_inactive` (Optional[int]) = `None`: Preview age-based deletion


  **Returns:** Dict[str, Any]
    Dict with deletion counts and sample patterns


  #### `export_deletion_log`

  ```python
  export_deletion_log(self, output_path: Path) -> bool
  ```

  Export deletion log to JSON file for recovery.

Args:
    output_path: Path to save deletion log

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `output_path` (Path): Path to save deletion log


  **Returns:** bool
    True if successful, False otherwise



---
