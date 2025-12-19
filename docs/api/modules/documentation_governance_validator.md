# documentation_governance_validator

Documentation Governance Validator
===================================

Validates documentation governance for system alignment.

Author: Asif Hussain


## Table of Contents

### Classes
- [DocumentationGovernanceValidator](#documentationgovernancevalidator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, src, typing


## Classes

### DocumentationGovernanceValidator

```python
class DocumentationGovernanceValidator
```

Validates documentation governance (duplicate/overlapping docs).


**Methods:**

  #### `validate`

  ```python
  validate(self) -> Dict[str, Any]
  ```

  Validate documentation governance (duplicate/overlapping docs).

Checks:
- Duplicate documents across cortex-brain/documents/ and .github/prompts/modules/
- Overlapping content detection (title similarity, keyword overlap)
- Canonical name violations for module guides
- Documents not referenced in index files

Returns:
    Dict with validation results and violations

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with validation results and violations



---
