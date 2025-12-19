# master_plan_template

Master Plan Template - Standardized structure for CORTEX master plans.

This module defines the exact section order and structure for master plans,
derived from cortex-3.9-master.md as the canonical reference.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [MasterPlanSection](#masterplansection)
- [MasterPlanTemplate](#masterplantemplate)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, enum, typing


## Classes

### MasterPlanSection

```python
class MasterPlanSection(Enum)
```

Enumeration of master plan sections in canonical order.



---

### MasterPlanTemplate

```python
class MasterPlanTemplate
```

**Decorators:** `dataclass`

Template for generating master plans with standardized structure.

Canonical order from cortex-3.9-master.md:
1. CORTEX Header (ASCII art)
2. Title & Metadata (Plan Name, Type, Status, Created, Last Updated, Completed, Version)
3. Request Context
4. Visual Progress Tracker
5. Phase Status Table
6. Executive Summary
7. Architectural Changes
8. Governance Framework
9. Phase Overview
10. Dependency Graph
11. Success Criteria
12. Deliverables
13. Risk Analysis
14. Related Documentation
15. Execution Strategy
16. Version History
17. Contact & Support


**Methods:**

  #### `get_required_sections`

  *Decorators:* `classmethod`

  ```python
  get_required_sections(cls) -> List[MasterPlanSection]
  ```

  Get list of required sections (always present).

  **Parameters:**

  - `cls`


  **Returns:** List[MasterPlanSection]


  #### `get_optional_sections`

  *Decorators:* `classmethod`

  ```python
  get_optional_sections(cls, tier: str) -> List[MasterPlanSection]
  ```

  Get optional sections based on tier.

  **Parameters:**

  - `cls`
  - `tier` (str)


  **Returns:** List[MasterPlanSection]


  #### `get_section_order`

  *Decorators:* `classmethod`

  ```python
  get_section_order(cls, complexity_tier: int) -> List[MasterPlanSection]
  ```

  Get the canonical section order for a given complexity tier.

Args:
    complexity_tier: Complexity tier (1-4)
    
Returns:
    Ordered list of sections to include

  **Parameters:**

  - `cls`
  - `complexity_tier` (int): Complexity tier (1-4)


  **Returns:** List[MasterPlanSection]
    Ordered list of sections to include


  #### `validate_section_order`

  *Decorators:* `classmethod`

  ```python
  validate_section_order(cls, actual_sections: List[str]) -> Dict[str, Any]
  ```

  Validate that actual sections follow canonical order.

Args:
    actual_sections: List of section identifiers in actual order
    
Returns:
    Validation result with errors if any

  **Parameters:**

  - `cls`
  - `actual_sections` (List[str]): List of section identifiers in actual order


  **Returns:** Dict[str, Any]
    Validation result with errors if any


  #### `get_cortex_header`

  *Decorators:* `staticmethod`

  ```python
  get_cortex_header() -> str
  ```

  Get the standardized CORTEX header ASCII art.

Returns:
    CORTEX header as markdown comment

  **Returns:** str
    CORTEX header as markdown comment



---
