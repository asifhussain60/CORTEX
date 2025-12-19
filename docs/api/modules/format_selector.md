# format_selector

Plan Format Selector - Intelligent Plan Structure Selection
============================================================

GREEN PHASE - Minimal Implementation

Purpose:
- Decide between single-file vs master/sub-plan structure
- Use cortex-evolution-v3.9 requirements for complex plans
- Match phase count threshold (<=5 single-file, >5 master-plan)

Compliance:
- Master plan requirements (ASCII header, progress tracker, phase tables)
- TDD GREEN_PHASE_VALIDATION

Author: CORTEX TDD System
Date: December 16, 2025
Status: GREEN PHASE


## Table of Contents

### Classes
- [PlanFormatSelector](#planformatselector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, typing


## Classes

### PlanFormatSelector

```python
class PlanFormatSelector
```

Selects appropriate plan format based on complexity.

Rules:
- <=5 phases: Single-file plan
- >5 phases: Master plan + sub-plans
- <3 files affected: Single-file
- >=3 files affected: Master plan


**Methods:**

  #### `select_format`

  ```python
  select_format(self, plan_metadata: Dict[str, Any]) -> Dict[str, Any]
  ```

  Select plan format based on complexity metrics.

Args:
    plan_metadata: Dictionary with keys:
        - complexity_tier (int): 1-4
        - task_count (int): Number of tasks
        - phase_count (int, optional): Number of phases
        - has_subcomponents (bool, optional): Nested dependencies
        - estimated_hours (int, optional): Estimated hours
    
Returns:
    Dictionary with format decision:
    {
        'format': 'single_file' | 'master_subplan',
        'file_pattern': str (for single file),
        'master_file': str (for master plan),
        'subplan_pattern': str (for master plan)
    }

  **Parameters:**

  - `self`
  - `plan_metadata` (Dict[str, Any]): Dictionary with keys:


  **Returns:** Dict[str, Any]
    Dictionary with format decision: { 'format': 'single_file' | 'master_subplan', 'file_pattern': str (for single file), 'master_file': str (for master plan), 'subplan_pattern': str (for master plan) }


  #### `get_format_requirements`

  ```python
  get_format_requirements(self, format_type: Literal['single-file', 'master-plan']) -> Dict[str, Any]
  ```

  Get structure requirements for plan format.

Args:
    format_type: 'single-file' or 'master-plan'
    
Returns:
    Dictionary with structure requirements

  **Parameters:**

  - `self`
  - `format_type` (Literal['single-file', 'master-plan']): 'single-file' or 'master-plan'


  **Returns:** Dict[str, Any]
    Dictionary with structure requirements


  #### `generate_master_plan`

  ```python
  generate_master_plan(self, plan_metadata: Dict[str, Any], output_path) -> str
  ```

  Generate master plan content with ASCII art header.

Args:
    plan_metadata: Plan metadata including feature_name, phase_count, phases
    output_path: Optional path to write file (for testing)
    
Returns:
    Master plan markdown content with ASCII header

  **Parameters:**

  - `self`
  - `plan_metadata` (Dict[str, Any]): Plan metadata including feature_name, phase_count, phases
  - `output_path` = `None`: Optional path to write file (for testing)


  **Returns:** str
    Master plan markdown content with ASCII header



---
