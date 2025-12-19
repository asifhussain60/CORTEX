# cleanup_test_harness

Cleanup Test Harness - Zero-break guarantee via continuous test validation

This module provides surgical cleanup capabilities with automatic test validation
at each step to ensure no code breakage during cleanup operations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 3.2.1


## Table of Contents

### Classes
- [TestBaseline](#testbaseline)
- [ValidationResult](#validationresult)
- [CleanupTestHarness](#cleanuptestharness)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, shutil, subprocess, typing


## Classes

### TestBaseline

```python
class TestBaseline
```

**Decorators:** `dataclass`

Represents test execution baseline for comparison


**Attributes:**

- `timestamp`: str
- `total_tests`: int
- `passed_tests`: int
- `failed_tests`: int
- `skipped_tests`: int
- `coverage_percent`: float
- `test_duration`: float
- `test_details`: Dict[str, str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict) -> 'TestBaseline'
  ```

  Create from dictionary

  **Parameters:**

  - `cls`
  - `data` (Dict)


  **Returns:** 'TestBaseline'



---

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Result of test validation comparison


**Attributes:**

- `success`: bool
- `baseline`: TestBaseline
- `current`: TestBaseline
- `issues`: List[str]
- `warnings`: List[str]


**Methods:**

  #### `has_failures`

  ```python
  has_failures(self) -> bool
  ```

  Check if validation found failures

  **Parameters:**

  - `self`


  **Returns:** bool



---

### CleanupTestHarness

```python
class CleanupTestHarness
```

Test harness for surgical cleanup with zero-break guarantee.

Provides:
- Pre-cleanup baseline capture
- Category-level test validation
- Automatic rollback on failures
- Detailed validation reporting

Architecture:
    1. Capture baseline (all tests pass, coverage %)
    2. Execute cleanup incrementally by category
    3. Validate after each category deletion
    4. Rollback if tests fail
    5. Generate validation report

Performance:
    - Sequential: 5-10 min (test each file)
    - Category-level: 1-2 min (test each category)
    - 92% time reduction via category batching


**Methods:**

  #### `capture_baseline`

  ```python
  capture_baseline(self) -> TestBaseline
  ```

  Capture test execution baseline before cleanup.

Returns:
    TestBaseline with current test state
    
Raises:
    RuntimeError: If baseline capture fails

  **Parameters:**

  - `self`


  **Returns:** TestBaseline
    TestBaseline with current test state


  #### `validate_category`

  ```python
  validate_category(self, category_name: str) -> ValidationResult
  ```

  Validate tests after category cleanup.

Args:
    category_name: Name of category that was cleaned
    
Returns:
    ValidationResult with comparison to baseline

  **Parameters:**

  - `self`
  - `category_name` (str): Name of category that was cleaned


  **Returns:** ValidationResult
    ValidationResult with comparison to baseline


  #### `backup_files`

  ```python
  backup_files(self, file_paths: List[Path]) -> Path
  ```

  Backup files before deletion.

Args:
    file_paths: List of files to backup
    
Returns:
    Path to backup directory

  **Parameters:**

  - `self`
  - `file_paths` (List[Path]): List of files to backup


  **Returns:** Path
    Path to backup directory


  #### `rollback_category`

  ```python
  rollback_category(self, backup_path: Path) -> bool
  ```

  Rollback category cleanup by restoring from backup.

Args:
    backup_path: Path to backup directory
    
Returns:
    True if rollback succeeded

  **Parameters:**

  - `self`
  - `backup_path` (Path): Path to backup directory


  **Returns:** bool
    True if rollback succeeded


  #### `generate_validation_report`

  ```python
  generate_validation_report(self) -> str
  ```

  Generate detailed validation report.

Returns:
    Markdown formatted report

  **Parameters:**

  - `self`


  **Returns:** str
    Markdown formatted report



---
