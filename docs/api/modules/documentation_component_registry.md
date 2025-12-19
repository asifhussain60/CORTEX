# documentation_component_registry

Documentation Component Registry

Central registry to manage documentation generation components and execute
them individually or as a pipeline. Designed to be extensible as CORTEX evolves.

Author: Asif Hussain
Copyright: © 2024-2025
License: Proprietary - See LICENSE


## Table of Contents

### Classes
- [DocumentationComponent](#documentationcomponent)
- [DocumentationComponentRegistry](#documentationcomponentregistry)

### Functions
- [create_default_registry](#create_default_registry)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** __future__, dataclasses, importlib, logging, pathlib, sys, types, typing


## Classes

### DocumentationComponent

```python
class DocumentationComponent
```

**Decorators:** `dataclass`

**Attributes:**

- `id`: str
- `name`: str
- `module_path`: Path
- `class_name`: str
- `dependencies`: List[str]
- `critical`: bool
- `natural_language`: List[str]



---

### DocumentationComponentRegistry

```python
class DocumentationComponentRegistry
```

Central registry for documentation generation components.


**Methods:**

  #### `register`

  ```python
  register(self, component: DocumentationComponent)
  ```

  #### `list_components`

  ```python
  list_components(self) -> List[Dict[str, Any]]
  ```

  #### `get_dependents`

  ```python
  get_dependents(self, component_id: str) -> List[str]
  ```

  #### `execute`

  ```python
  execute(self, component_id: str, output_path: Optional[Path], profile: str, force_regenerate: bool, validate_output: bool, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]
  ```

  Execute a single documentation component.

  **Parameters:**

  - `self`
  - `component_id` (str)
  - `output_path` (Optional[Path]) = `None`
  - `profile` (str) = `'standard'`
  - `force_regenerate` (bool) = `False`
  - `validate_output` (bool) = `True`
  - `metadata` (Optional[Dict[str, Any]]) = `None`


  **Returns:** Dict[str, Any]


  #### `execute_pipeline`

  ```python
  execute_pipeline(self, component_ids: List[str], output_path: Optional[Path], profile: str, stop_on_failure: bool) -> Dict[str, Any]
  ```

  Execute multiple components in sequence respecting dependencies.

  **Parameters:**

  - `self`
  - `component_ids` (List[str])
  - `output_path` (Optional[Path]) = `None`
  - `profile` (str) = `'standard'`
  - `stop_on_failure` (bool) = `True`


  **Returns:** Dict[str, Any]



---

## Functions

### create_default_registry

```python
create_default_registry(workspace_root: Optional[Path]) -> DocumentationComponentRegistry
```

Create a registry pre-populated with standard CORTEX documentation components.


**Parameters:**

- `workspace_root` (Optional[Path]) = `None`


**Returns:** DocumentationComponentRegistry


---
