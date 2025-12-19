# report_consolidation_engine

Report Consolidation Engine for CORTEX Cleanup

Consolidates duplicate and redundant reports into single comprehensive documents.
Handles system alignment reports, deployment validation, cleanup reports, etc.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ReportConsolidationEngine](#reportconsolidationengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** collections, datetime, hashlib, json, logging, pathlib, typing


## Classes

### ReportConsolidationEngine

```python
class ReportConsolidationEngine
```

Consolidates duplicate and time-series reports.

Strategies:
1. Time-series consolidation (same type, different dates)
2. Duplicate detection (identical content)
3. Archive old versions (keep N most recent)


**Methods:**

  #### `discover_reports`

  ```python
  discover_reports(self) -> Dict[str, List[Path]]
  ```

  Discover all report files grouped by type.

Returns:
    Dict mapping report_type -> list of report files

  **Parameters:**

  - `self`


  **Returns:** Dict[str, List[Path]]
    Dict mapping report_type -> list of report files


  #### `analyze_consolidation_opportunities`

  ```python
  analyze_consolidation_opportunities(self, report_groups: Dict[str, List[Path]], keep_count: int) -> Dict[str, Dict]
  ```

  Analyze which reports can be consolidated or archived.

Args:
    report_groups: Report files grouped by type
    keep_count: Number of recent reports to keep per type
    
Returns:
    Dict with consolidation recommendations

  **Parameters:**

  - `self`
  - `report_groups` (Dict[str, List[Path]]): Report files grouped by type
  - `keep_count` (int) = `5`: Number of recent reports to keep per type


  **Returns:** Dict[str, Dict]
    Dict with consolidation recommendations


  #### `execute_consolidation`

  ```python
  execute_consolidation(self, recommendations: Dict[str, Dict], dry_run: bool) -> Dict[str, int]
  ```

  Execute consolidation by archiving old reports.

Args:
    recommendations: From analyze_consolidation_opportunities()
    dry_run: If True, only simulate
    
Returns:
    Dict with execution stats

  **Parameters:**

  - `self`
  - `recommendations` (Dict[str, Dict]): From analyze_consolidation_opportunities()
  - `dry_run` (bool) = `True`: If True, only simulate


  **Returns:** Dict[str, int]
    Dict with execution stats


  #### `generate_consolidation_summary`

  ```python
  generate_consolidation_summary(self, report_groups: Dict[str, List[Path]], recommendations: Dict[str, Dict]) -> str
  ```

  Generate human-readable summary of consolidation

  **Parameters:**

  - `self`
  - `report_groups` (Dict[str, List[Path]])
  - `recommendations` (Dict[str, Dict])


  **Returns:** str



---
