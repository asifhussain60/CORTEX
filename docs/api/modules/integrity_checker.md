# integrity_checker

CORTEX Brain Integrity Checker

Detects and repairs corruption in brain data structures:
- Conversation history corruption
- Knowledge graph inconsistencies
- Development context staleness
- Cross-tier data leakage

Part of Brain Protection Layer
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11


## Table of Contents

### Classes
- [IntegrityStatus](#integritystatus)
- [IntegrityIssue](#integrityissue)
- [IntegrityReport](#integrityreport)
- [IntegrityChecker](#integritychecker)

### Functions
- [check_brain_integrity](#check_brain_integrity)


## Overview

- **Classes:** 4
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, datetime, enum, hashlib, json, pathlib, sqlite3, src, sys, typing, yaml


## Classes

### IntegrityStatus

```python
class IntegrityStatus(Enum)
```

Integrity check status.



---

### IntegrityIssue

```python
class IntegrityIssue
```

**Decorators:** `dataclass`

An integrity issue discovered.


**Attributes:**

- `component`: str
- `issue_type`: str
- `severity`: str
- `message`: str
- `affected_data`: Optional[str]
- `auto_repairable`: bool
- `repair_action`: Optional[str]



---

### IntegrityReport

```python
class IntegrityReport
```

**Decorators:** `dataclass`

Integrity check report.


**Attributes:**

- `status`: IntegrityStatus
- `timestamp`: str
- `issues`: List[IntegrityIssue]
- `metadata`: Dict[str, Any]
- `auto_repairs_applied`: int



---

### IntegrityChecker

```python
class IntegrityChecker
```

Checks and repairs brain data integrity.

Checks:
1. Data corruption (malformed JSON/YAML)
2. Schema violations (missing required fields)
3. Stale data (outdated timestamps)
4. Cross-tier leakage (data in wrong tier)
5. Orphaned references (broken links)


**Methods:**

  #### `check_all`

  ```python
  check_all(self) -> IntegrityReport
  ```

  Run all integrity checks.

Returns:
    IntegrityReport with findings

  **Parameters:**

  - `self`


  **Returns:** IntegrityReport
    IntegrityReport with findings


  #### `generate_report`

  ```python
  generate_report(self, integrity_report: IntegrityReport) -> str
  ```

  Generate human-readable integrity report.

Args:
    integrity_report: Integrity check results

Returns:
    Formatted report string

  **Parameters:**

  - `self`
  - `integrity_report` (IntegrityReport): Integrity check results


  **Returns:** str
    Formatted report string



---

## Functions

### check_brain_integrity

```python
check_brain_integrity(auto_repair: bool) -> bool
```

Convenience function to check brain integrity.

Args:
    auto_repair: Whether to automatically repair issues

Returns:
    True if brain is healthy


**Parameters:**

- `auto_repair` (bool) = `False`: Whether to automatically repair issues


**Returns:** bool
  True if brain is healthy


---
