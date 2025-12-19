# user_onboarding_operation

User Onboarding Operation

Connects the EPM onboarding orchestrator to the CORTEX operations system.
Handles the "onboard me" natural language trigger and executes the guided onboarding flow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [UserOnboardingOperation](#useronboardingoperation)

### Functions
- [create_user_onboarding_operation](#create_user_onboarding_operation)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** base_operation_module, datetime, epm, logging, modules, typing, uuid


## Classes

### UserOnboardingOperation

```python
class UserOnboardingOperation(BaseOperationModule)
```

User onboarding operation that leverages the EPM framework.

Natural language triggers:
- "onboard me"
- "new user setup"
- "cortex introduction"
- "getting started"
- "help me get started"


**Methods:**

  #### `execute`

  ```python
  execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Execute user onboarding operation.

Args:
    request: Natural language request (e.g., "onboard me")
    context: Additional context including profile preference
    
Returns:
    Dict with onboarding results and session information

  **Parameters:**

  - `self`
  - `request` (str): Natural language request (e.g., "onboard me")
  - `context` (Dict[str, Any]) = `None`: Additional context including profile preference


  **Returns:** Dict[str, Any]
    Dict with onboarding results and session information



---

## Functions

### create_user_onboarding_operation

```python
create_user_onboarding_operation() -> UserOnboardingOperation
```

Factory function to create user onboarding operation instance


**Returns:** UserOnboardingOperation


---
