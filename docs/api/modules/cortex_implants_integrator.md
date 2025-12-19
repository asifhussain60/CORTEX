# cortex_implants_integrator

Cortex Implants Integrator

Provides optional integration of cortex-implants into CORTEX orchestrators.
Implements graceful degradation - system works normally without implants.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [CortexImplantsIntegrator](#corteximplantsintegrator)

### Functions
- [get_implants_integrator](#get_implants_integrator)
- [has_cortex_implants](#has_cortex_implants)


## Overview

- **Classes:** 1
- **Functions:** 2
- **Dependencies:** cortex_implants_loader, logging, pathlib, typing


## Classes

### CortexImplantsIntegrator

```python
class CortexImplantsIntegrator
```

Integrates cortex-implants with CORTEX orchestrators.

Features:
- Optional loading (graceful degradation)
- Repo detection (auto-find implants)
- Validation augmentation (add company rules)
- Context enhancement (add company-specific context)

Usage:
    integrator = CortexImplantsIntegrator(repo_path)
    
    # Check if implants present
    if integrator.has_implants():
        # Add company-specific validation
        violations = integrator.validate_against_implants(plan)


**Methods:**

  #### `has_implants`

  ```python
  has_implants(self) -> bool
  ```

  Check if cortex-implants are present.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `get_priority`

  ```python
  get_priority(self) -> str
  ```

  Get implants priority (HIGH/MEDIUM/LOW) or NONE.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `should_override_cortex`

  ```python
  should_override_cortex(self) -> bool
  ```

  Check if implants should override CORTEX rules.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `get_coding_standards`

  ```python
  get_coding_standards(self) -> Optional[Dict[str, Any]]
  ```

  Get coding standards from implants.

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]


  #### `get_architecture_patterns`

  ```python
  get_architecture_patterns(self) -> Optional[Dict[str, Any]]
  ```

  Get architecture patterns from implants.

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]


  #### `get_tech_stack_restrictions`

  ```python
  get_tech_stack_restrictions(self) -> Optional[Dict[str, Any]]
  ```

  Get tech stack restrictions from implants.

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]


  #### `get_business_rules`

  ```python
  get_business_rules(self) -> Optional[List[Dict[str, Any]]]
  ```

  Get business rules from implants.

  **Parameters:**

  - `self`


  **Returns:** Optional[List[Dict[str, Any]]]


  #### `get_security_requirements`

  ```python
  get_security_requirements(self) -> Optional[Dict[str, Any]]
  ```

  Get security requirements from implants.

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]


  #### `validate_tech_stack`

  ```python
  validate_tech_stack(self, dependencies: List[str]) -> List[str]
  ```

  Validate dependencies against implants tech stack.

Args:
    dependencies: List of libraries to validate
    
Returns:
    List of validation errors (empty if all valid)

  **Parameters:**

  - `self`
  - `dependencies` (List[str]): List of libraries to validate


  **Returns:** List[str]
    List of validation errors (empty if all valid)


  #### `validate_architecture`

  ```python
  validate_architecture(self, plan: Dict[str, Any]) -> List[str]
  ```

  Validate plan against architecture patterns.

Args:
    plan: Feature plan to validate
    
Returns:
    List of validation errors (empty if valid)

  **Parameters:**

  - `self`
  - `plan` (Dict[str, Any]): Feature plan to validate


  **Returns:** List[str]
    List of validation errors (empty if valid)


  #### `get_context_summary`

  ```python
  get_context_summary(self) -> str
  ```

  Get summary of implants for context injection.

Returns:
    Markdown summary of active implants

  **Parameters:**

  - `self`


  **Returns:** str
    Markdown summary of active implants



---

## Functions

### get_implants_integrator

```python
get_implants_integrator(repo_path: Optional[Path]) -> CortexImplantsIntegrator
```

Get singleton integrator instance.

Args:
    repo_path: Repository path (optional)
    
Returns:
    CortexImplantsIntegrator instance


**Parameters:**

- `repo_path` (Optional[Path]) = `None`: Repository path (optional)


**Returns:** CortexImplantsIntegrator
  CortexImplantsIntegrator instance


---

### has_cortex_implants

```python
has_cortex_implants(repo_path: Optional[Path]) -> bool
```

Quick check if cortex-implants present.

Args:
    repo_path: Repository path (optional)
    
Returns:
    True if implants found


**Parameters:**

- `repo_path` (Optional[Path]) = `None`: Repository path (optional)


**Returns:** bool
  True if implants found


---
