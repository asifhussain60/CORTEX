# auto_registration_orchestrator

Auto-Registration Orchestrator for Discovered Features

Automatically registers discovered orchestrators in cortex-operations.yaml:
- Extracts metadata from discovered features
- Generates natural language triggers from docstrings
- Creates properly formatted YAML entries
- Supports dry-run mode for preview
- Approval workflow for safety

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [RegistrationEntry](#registrationentry)
- [AutoRegistrationOrchestrator](#autoregistrationorchestrator)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, re, src, typing, yaml


## Classes

### RegistrationEntry

```python
class RegistrationEntry
```

**Decorators:** `dataclass`

YAML entry for operation registration


**Attributes:**

- `operation_name`: str
- `display_name`: str
- `deployment_tier`: str
- `category`: str
- `natural_language`: List[str]
- `modules`: List[str]
- `description`: str
- `version`: str
- `author`: str



---

### AutoRegistrationOrchestrator

```python
class AutoRegistrationOrchestrator
```

Orchestrates automatic registration of discovered features


**Methods:**

  #### `extract_natural_language_triggers`

  ```python
  extract_natural_language_triggers(self, docstring: str, operation_name: str) -> List[str]
  ```

  Extract natural language triggers from docstring

Args:
    docstring: Operation docstring
    operation_name: Operation name (e.g., "brain_tuning")

Returns:
    List of natural language trigger phrases

  **Parameters:**

  - `self`
  - `docstring` (str): Operation docstring
  - `operation_name` (str): Operation name (e.g., "brain_tuning")


  **Returns:** List[str]
    List of natural language trigger phrases


  #### `infer_deployment_tier`

  ```python
  infer_deployment_tier(self, module_path: str, docstring: str) -> str
  ```

  Infer deployment tier from module path and docstring

Args:
    module_path: Module path (e.g., "src.operations.modules.brain...")
    docstring: Operation docstring

Returns:
    'user', 'dual', or 'admin'

  **Parameters:**

  - `self`
  - `module_path` (str): Module path (e.g., "src.operations.modules.brain...")
  - `docstring` (str): Operation docstring


  **Returns:** str
    'user', 'dual', or 'admin'


  #### `infer_category`

  ```python
  infer_category(self, operation_name: str, module_path: str) -> str
  ```

  Infer category from operation name and module path

Args:
    operation_name: Operation name
    module_path: Module path

Returns:
    Category name

  **Parameters:**

  - `self`
  - `operation_name` (str): Operation name
  - `module_path` (str): Module path


  **Returns:** str
    Category name


  #### `generate_registration_entry`

  ```python
  generate_registration_entry(self, discovered_feature: Dict) -> RegistrationEntry
  ```

  Generate registration entry from discovered feature

Args:
    discovered_feature: Feature dict from OrchestratorScanner

Returns:
    RegistrationEntry ready for YAML

  **Parameters:**

  - `self`
  - `discovered_feature` (Dict): Feature dict from OrchestratorScanner


  **Returns:** RegistrationEntry
    RegistrationEntry ready for YAML


  #### `format_yaml_entry`

  ```python
  format_yaml_entry(self, entry: RegistrationEntry) -> str
  ```

  Format registration entry as YAML string

Args:
    entry: RegistrationEntry to format

Returns:
    Formatted YAML string

  **Parameters:**

  - `self`
  - `entry` (RegistrationEntry): RegistrationEntry to format


  **Returns:** str
    Formatted YAML string


  #### `register_features`

  ```python
  register_features(self, unregistered_features: List[Dict], dry_run: bool, require_approval: bool) -> Dict
  ```

  Register unregistered features in cortex-operations.yaml

Args:
    unregistered_features: List of discovered features to register
    dry_run: If True, only preview without writing
    require_approval: If True, ask for user approval

Returns:
    Registration result summary

  **Parameters:**

  - `self`
  - `unregistered_features` (List[Dict]): List of discovered features to register
  - `dry_run` (bool) = `True`: If True, only preview without writing
  - `require_approval` (bool) = `True`: If True, ask for user approval


  **Returns:** Dict
    Registration result summary



---

## Functions

### main

```python
main()
```

Entry point for testing


---
