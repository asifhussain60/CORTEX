# gap_remediation_validator

Gap Remediation Validator
==========================

Validates Phase 1-4 gap remediation components for system alignment.

Author: Asif Hussain


## Table of Contents

### Classes
- [GapRemediationValidator](#gapremediationvalidator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, src, typing, yaml


## Classes

### GapRemediationValidator

```python
class GapRemediationValidator
```

Validates Phase 1-4 gap remediation components.


**Methods:**

  #### `validate`

  ```python
  validate(self, report: AlignmentReport) -> None
  ```

  Validate Phase 1-4 gap remediation components.

Validates:
- GitHub Actions workflows (feedback-aggregation.yml)
- Template format compliance (H1 headers, Challenge field)
- Brain protection rule severity (NO_ROOT_FILES blocked enforcement)
- Configuration schemas (plan-schema.yaml, lint-rules.yaml)

Args:
    report: AlignmentReport to populate with gap remediation validation results

  **Parameters:**

  - `self`
  - `report` (AlignmentReport): AlignmentReport to populate with gap remediation validation results


  **Returns:** None



---
