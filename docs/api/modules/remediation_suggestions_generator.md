# remediation_suggestions_generator

Remediation Suggestions Generator
==================================

Generates auto-remediation suggestions for incomplete features.

Author: Asif Hussain


## Table of Contents

### Classes
- [RemediationSuggestionsGenerator](#remediationsuggestionsgenerator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, src, typing


## Classes

### RemediationSuggestionsGenerator

```python
class RemediationSuggestionsGenerator
```

Generates auto-remediation suggestions for incomplete features.


**Methods:**

  #### `generate`

  ```python
  generate(self, report: AlignmentReport, orchestrators: Dict[str, Dict[str, Any]], agents: Dict[str, Dict[str, Any]]) -> None
  ```

  Generate auto-remediation suggestions for incomplete features.

Args:
    report: AlignmentReport to populate with remediation suggestions
    orchestrators: Discovered orchestrators
    agents: Discovered agents

  **Parameters:**

  - `self`
  - `report` (AlignmentReport): AlignmentReport to populate with remediation suggestions
  - `orchestrators` (Dict[str, Dict[str, Any]]): Discovered orchestrators
  - `agents` (Dict[str, Dict[str, Any]]): Discovered agents


  **Returns:** None



---
