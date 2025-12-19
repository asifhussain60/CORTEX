# user_consent_manager

User Consent Manager

Handles interactive user consent for CORTEX setup operations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ConsentAction](#consentaction)
- [ConsentResult](#consentresult)
- [UserConsentManager](#userconsentmanager)

### Functions
- [main](#main)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, enum, logging, pathlib, sys, typing


## Classes

### ConsentAction

```python
class ConsentAction(Enum)
```

User consent actions.



---

### ConsentResult

```python
class ConsentResult
```

**Decorators:** `dataclass`

Result of user consent interaction.


**Attributes:**

- `action`: ConsentAction
- `approved_steps`: List[str]
- `skipped_steps`: List[str]
- `customizations`: Dict[str, Any]
- `user_notes`: Optional[str]



---

### UserConsentManager

```python
class UserConsentManager
```

Manages interactive user consent for CORTEX onboarding.

Features:
- Interactive prompts with clear explanations
- Step-by-step confirmation
- Customization options
- Consent tracking


**Methods:**

  #### `request_onboarding_consent`

  ```python
  request_onboarding_consent(self, detected_info: Dict[str, Any]) -> ConsentResult
  ```

  Request user consent for full onboarding workflow.

Args:
    detected_info: Detected project information

Returns:
    ConsentResult with user decisions

  **Parameters:**

  - `self`
  - `detected_info` (Dict[str, Any]): Detected project information


  **Returns:** ConsentResult
    ConsentResult with user decisions


  #### `request_dashboard_consent`

  ```python
  request_dashboard_consent(self) -> bool
  ```

  Request specific consent for dashboard generation.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `request_policy_validation_consent`

  ```python
  request_policy_validation_consent(self, policy_path: str) -> bool
  ```

  Request consent to validate against policy documents.

  **Parameters:**

  - `self`
  - `policy_path` (str)


  **Returns:** bool


  #### `confirm_action`

  ```python
  confirm_action(self, action: str, consequences: List[str], default: bool) -> bool
  ```

  Confirm potentially destructive action with clear consequences.

  **Parameters:**

  - `self`
  - `action` (str)
  - `consequences` (List[str])
  - `default` (bool) = `True`


  **Returns:** bool


  #### `request_policy_validation_consent`

  ```python
  request_policy_validation_consent(self, policy_path: Optional[Path]) -> bool
  ```

  Request consent for policy validation

Args:
    policy_path: Path to detected policy document (or None if none found)

Returns:
    True if user approves, False otherwise

  **Parameters:**

  - `self`
  - `policy_path` (Optional[Path]) = `None`: Path to detected policy document (or None if none found)


  **Returns:** bool
    True if user approves, False otherwise



---

## Functions

### main

```python
main()
```

CLI entry point for testing.


---
