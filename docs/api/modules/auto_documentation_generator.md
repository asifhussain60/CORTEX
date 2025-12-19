# auto_documentation_generator

Automatic Documentation Generator - Learning library automation.

Generates comprehensive documentation for all Tier 3/4 operations,
creating learning artifacts in standardized folder structure.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [DocumentationSet](#documentationset)
- [AutoDocumentationGenerator](#autodocumentationgenerator)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, logging, pathlib, typing


## Classes

### DocumentationSet

```python
class DocumentationSet
```

**Decorators:** `dataclass`

Complete documentation set for a component.


**Attributes:**

- `readme`: str
- `context`: str
- `architecture`: str
- `implementation_guide`: str
- `test_strategy`: str
- `research_notes`: str



---

### AutoDocumentationGenerator

```python
class AutoDocumentationGenerator
```

Generate automatic documentation for learning library.


**Methods:**

  #### `generate_documentation`

  ```python
  generate_documentation(self, component_name: str, category: str, context: Dict[str, Any]) -> DocumentationSet
  ```

  Generate complete documentation set for component.

Args:
    component_name: Name of component (e.g., "planning_orchestrator")
    category: Documentation category
    context: Component context (code, design, decisions)
    
Returns:
    Complete documentation set

  **Parameters:**

  - `self`
  - `component_name` (str): Name of component (e.g., "planning_orchestrator")
  - `category` (str): Documentation category
  - `context` (Dict[str, Any]): Component context (code, design, decisions)


  **Returns:** DocumentationSet
    Complete documentation set


  #### `validate_structure`

  ```python
  validate_structure(self) -> bool
  ```

  Validate learning library folder structure.

Returns:
    True if structure is valid

  **Parameters:**

  - `self`


  **Returns:** bool
    True if structure is valid


  #### `list_documented_components`

  ```python
  list_documented_components(self, category: str) -> List[Dict[str, str]]
  ```

  List all documented components.

Args:
    category: Optional category filter
    
Returns:
    List of component info dicts

  **Parameters:**

  - `self`
  - `category` (str) = `None`: Optional category filter


  **Returns:** List[Dict[str, str]]
    List of component info dicts



---
