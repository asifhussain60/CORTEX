# load_protection_rules_module

Load protection rules module for brain protection validation.

Part of the Brain Protection operation - loads brain-protection-rules.yaml.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [LoadProtectionRulesModule](#loadprotectionrulesmodule)

### Functions
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** os, pathlib, src, typing, yaml


## Classes

### LoadProtectionRulesModule

```python
class LoadProtectionRulesModule(BaseOperationModule)
```

Load brain protection rules from YAML configuration.

Loads and validates the brain-protection-rules.yaml file that defines
SKULL protection rules and tier protection policies.


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute protection rules loading.

Args:
    context: Operation context
    
Returns:
    OperationResult with loaded rules

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Operation context


  **Returns:** OperationResult
    OperationResult with loaded rules



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register module for discovery.


**Returns:** BaseOperationModule


---
