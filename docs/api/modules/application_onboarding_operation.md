# application_onboarding_operation

Application Onboarding Operation

Handles the "onboard this application" natural language trigger.
Deploys CORTEX to target applications with intelligent codebase discovery,
documentation generation, and contextual questioning capabilities.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ApplicationOnboardingOperation](#applicationonboardingoperation)

### Functions
- [create_application_onboarding_operation](#create_application_onboarding_operation)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** base_operation_module, datetime, epm, logging, modules, pathlib, typing, uuid


## Classes

### ApplicationOnboardingOperation

```python
class ApplicationOnboardingOperation(BaseOperationModule)
```

Application onboarding operation that leverages the EPM framework.

Natural language triggers:
- "onboard this application"
- "analyze my codebase"
- "setup cortex for this project"
- "what can cortex learn about this app"
- "initialize cortex here"
- "deploy cortex"
- "onboard app"
- "application onboarding"


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get operation metadata

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Execute application onboarding operation.

Args:
    request: Natural language request (e.g., "onboard this application")
    context: Additional context including profile preference and project root
    
Returns:
    Dict with onboarding results and session information

  **Parameters:**

  - `self`
  - `request` (str): Natural language request (e.g., "onboard this application")
  - `context` (Dict[str, Any]) = `None`: Additional context including profile preference and project root


  **Returns:** Dict[str, Any]
    Dict with onboarding results and session information



---

## Functions

### create_application_onboarding_operation

```python
create_application_onboarding_operation() -> ApplicationOnboardingOperation
```

Factory function to create application onboarding operation instance


**Returns:** ApplicationOnboardingOperation


---
