# obsolete_code_detector

Obsolete Code Detector for CORTEX Align Orchestrator v2.0

This module detects obsolete code across the repository including:
- Orchestrators that have been migrated to utilities
- Tests for deleted orchestrators
- Obsolete scripts (backups, deprecated, temp)
- Files with deprecated import patterns

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [ImportAnalysis](#importanalysis)
- [CleanupPlan](#cleanupplan)
- [ObsoleteCodeDetector](#obsoletecodedetector)

### Functions
- [main](#main)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, logging, pathlib, re, sys, typing


## Classes

### ImportAnalysis

```python
class ImportAnalysis
```

**Decorators:** `dataclass`

Analysis of imports in a file.


**Attributes:**

- `file`: Path
- `has_deprecated`: bool
- `findings`: List[Dict[str, str]]
- `total_deprecated_imports`: int



---

### CleanupPlan

```python
class CleanupPlan
```

**Decorators:** `dataclass`

Comprehensive plan for cleaning up obsolete code.


**Attributes:**

- `obsolete_orchestrators`: List[Path]
- `obsolete_tests`: List[Path]
- `obsolete_scripts`: List[Path]
- `files_with_deprecated_imports`: List[ImportAnalysis]
- `estimated_removal_size_mb`: float
- `safety_checks_required`: bool
- `total_files`: int


**Methods:**

  #### `get_all_files`

  ```python
  get_all_files(self) -> List[Path]
  ```

  Get list of all files in cleanup plan.

  **Parameters:**

  - `self`


  **Returns:** List[Path]



---

### ObsoleteCodeDetector

```python
class ObsoleteCodeDetector
```

Detects obsolete code across the CORTEX repository.


**Methods:**

  #### `has_migrated_utility`

  ```python
  has_migrated_utility(self, orchestrator_name: str) -> bool
  ```

  Check if an orchestrator has a corresponding utility in operations/modules/.

Args:
    orchestrator_name: Name of orchestrator (e.g., 'planning_orchestrator')

Returns:
    True if corresponding utility exists, False otherwise

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of orchestrator (e.g., 'planning_orchestrator')


  **Returns:** bool
    True if corresponding utility exists, False otherwise


  #### `scan_for_obsolete_orchestrators`

  ```python
  scan_for_obsolete_orchestrators(self) -> List[Path]
  ```

  Find orchestrator files that have been migrated to utilities.

Returns:
    List of obsolete orchestrator file paths

  **Parameters:**

  - `self`


  **Returns:** List[Path]
    List of obsolete orchestrator file paths


  #### `scan_for_obsolete_tests`

  ```python
  scan_for_obsolete_tests(self) -> List[Path]
  ```

  Find test files for orchestrators that no longer exist.

Returns:
    List of obsolete test file paths

  **Parameters:**

  - `self`


  **Returns:** List[Path]
    List of obsolete test file paths


  #### `scan_for_obsolete_scripts`

  ```python
  scan_for_obsolete_scripts(self) -> List[Path]
  ```

  Find obsolete scripts (backups, deprecated, temp files).

Returns:
    List of obsolete script file paths

  **Parameters:**

  - `self`


  **Returns:** List[Path]
    List of obsolete script file paths


  #### `analyze_import_usage`

  ```python
  analyze_import_usage(self, file_path: Path) -> ImportAnalysis
  ```

  Analyze a file for deprecated import patterns.

Args:
    file_path: Path to file to analyze

Returns:
    ImportAnalysis with findings

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file to analyze


  **Returns:** ImportAnalysis
    ImportAnalysis with findings


  #### `scan_all_for_deprecated_imports`

  ```python
  scan_all_for_deprecated_imports(self) -> List[ImportAnalysis]
  ```

  Scan all Python files for deprecated imports.

Returns:
    List of ImportAnalysis for files with deprecated imports

  **Parameters:**

  - `self`


  **Returns:** List[ImportAnalysis]
    List of ImportAnalysis for files with deprecated imports


  #### `calculate_total_size`

  ```python
  calculate_total_size(self, files: List[Path]) -> float
  ```

  Calculate total size of files in MB.

Args:
    files: List of file paths

Returns:
    Total size in MB

  **Parameters:**

  - `self`
  - `files` (List[Path]): List of file paths


  **Returns:** float
    Total size in MB


  #### `detect_all`

  ```python
  detect_all(self) -> Dict[str, List[Path]]
  ```

  Detect all types of obsolete code.

This is a simplified version of generate_cleanup_plan() that returns
a dictionary with categorized obsolete files.

Returns:
    Dictionary with keys:
        - deprecated: List of obsolete orchestrator files
        - test_files: List of obsolete test files  
        - temp_files: List of obsolete script/temp files

  **Parameters:**

  - `self`


  **Returns:** Dict[str, List[Path]]
    Dictionary with keys: - deprecated: List of obsolete orchestrator files - test_files: List of obsolete test files - temp_files: List of obsolete script/temp files


  #### `generate_cleanup_plan`

  ```python
  generate_cleanup_plan(self) -> CleanupPlan
  ```

  Generate comprehensive cleanup plan.

Returns:
    CleanupPlan with all detected obsolete code

  **Parameters:**

  - `self`


  **Returns:** CleanupPlan
    CleanupPlan with all detected obsolete code


  #### `generate_report`

  ```python
  generate_report(self, plan: CleanupPlan) -> str
  ```

  Generate formatted report from cleanup plan.

Args:
    plan: CleanupPlan to format

Returns:
    Formatted markdown report

  **Parameters:**

  - `self`
  - `plan` (CleanupPlan): CleanupPlan to format


  **Returns:** str
    Formatted markdown report



---

## Functions

### main

```python
main()
```

CLI entry point for standalone obsolete detection.


---
