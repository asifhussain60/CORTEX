# governance_drift_checker

Governance Drift Checker for CORTEX System Optimization

Analyzes governance.yaml for rule ordering drift and inefficiencies.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [GovernanceDriftChecker](#governancedriftchecker)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, typing, yaml


## Classes

### GovernanceDriftChecker

```python
class GovernanceDriftChecker
```

Checks governance.yaml for ordering drift and inefficiencies.

Monitors:
- Rule position drift (rules moved from optimal positions)
- Forward reference count (rules referencing later rules)
- File bloat (excessive line count)
- Orphaned rules (never referenced by other rules)
- Missing metadata (copilot_position, reference_count missing)


**Methods:**

  #### `check`

  ```python
  check(self) -> Dict[str, Any]
  ```

  Check governance.yaml for drift and inefficiencies.

Returns:
    Dict with has_issues, issues list, health_score, and recommendations

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with has_issues, issues list, health_score, and recommendations



---
