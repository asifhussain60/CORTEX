# phase8_utility

Phase 8 Operations Utility

Lightweight Phase 8 operations for final integration and cleanup.

Core Operations:
- handle_integration_cleanup: Final cleanup before deployment
- handle_completion_report: Generate Phase 8 completion report
- handle_phase8_status: Show Phase 8 progress
- calculate_cleanup_metrics: File size and category analysis
- generate_completion_report: Report content generation

Version: 3.0.0 (Migrated from Phase8OperationHandler)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [calculate_cleanup_metrics](#calculate_cleanup_metrics)
- [generate_completion_report](#generate_completion_report)
- [handle_integration_cleanup](#handle_integration_cleanup)
- [handle_completion_report](#handle_completion_report)
- [handle_phase8_status](#handle_phase8_status)


## Overview

- **Classes:** 0
- **Functions:** 5
- **Dependencies:** datetime, pathlib, tempfile, time, typing


## Functions

### calculate_cleanup_metrics

```python
calculate_cleanup_metrics(files: List[Path]) -> Dict[str, Any]
```

Calculate cleanup metrics for files

Args:
    files: List of files to analyze
    
Returns:
    Dict with size, count, categories
    
Example:
    >>> metrics = calculate_cleanup_metrics([Path("test.log")])
    >>> print(metrics["total_files"])
    1


**Parameters:**

- `files` (List[Path]): List of files to analyze


**Returns:** Dict[str, Any]
  Dict with size, count, categories


---

### generate_completion_report

```python
generate_completion_report() -> str
```

Generate Phase 8 completion report content

Returns:
    Markdown formatted report
    
Example:
    >>> report = generate_completion_report()
    >>> print("Phase 8" in report)
    True


**Returns:** str
  Markdown formatted report


---

### handle_integration_cleanup

```python
handle_integration_cleanup(brain_path: str, dry_run: bool, profile: str) -> Dict[str, Any]
```

Handle integration cleanup operation

Args:
    brain_path: Path to CORTEX brain directory
    dry_run: If True, no actual changes
    profile: Cleanup profile (quick/standard/comprehensive)
    
Returns:
    Dict with cleanup results
    
Example:
    >>> result = handle_integration_cleanup("/path/to/brain")
    >>> print(result["dry_run"])
    True


**Parameters:**

- `brain_path` (str): Path to CORTEX brain directory
- `dry_run` (bool) = `True`: If True, no actual changes
- `profile` (str) = `'standard'`: Cleanup profile (quick/standard/comprehensive)


**Returns:** Dict[str, Any]
  Dict with cleanup results


---

### handle_completion_report

```python
handle_completion_report(brain_path: str, output_path: str) -> Dict[str, Any]
```

Handle completion report generation

Args:
    brain_path: Path to CORTEX brain
    output_path: Optional custom output path
    
Returns:
    Dict with report path and success status
    
Example:
    >>> result = handle_completion_report("/path/to/brain")
    >>> print(result["success"])
    True


**Parameters:**

- `brain_path` (str): Path to CORTEX brain
- `output_path` (str) = `None`: Optional custom output path


**Returns:** Dict[str, Any]
  Dict with report path and success status


---

### handle_phase8_status

```python
handle_phase8_status() -> Dict[str, Any]
```

Handle Phase 8 status query

Returns:
    Dict with progress information
    
Example:
    >>> status = handle_phase8_status()
    >>> print(status["total_deliverables"])
    13


**Returns:** Dict[str, Any]
  Dict with progress information


---
