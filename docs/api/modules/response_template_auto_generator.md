# response_template_auto_generator

Response Template Auto-Generator for CORTEX Align v2.0

Automatically generates response templates for operations that don't have them.
Analyzes operation files to create contextually appropriate templates.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [TemplateGenerationResult](#templategenerationresult)
- [ResponseTemplateAutoGenerator](#responsetemplateautogenerator)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, re, typing


## Classes

### TemplateGenerationResult

```python
class TemplateGenerationResult
```

**Decorators:** `dataclass`

Result of template generation.


**Attributes:**

- `success`: bool
- `operation_name`: str
- `template_content`: str
- `error_message`: str



---

### ResponseTemplateAutoGenerator

```python
class ResponseTemplateAutoGenerator
```

Automatically generates response templates for operations.


**Methods:**

  #### `extract_operation_metadata`

  ```python
  extract_operation_metadata(self, operation_name: str) -> Dict[str, str]
  ```

  Extract metadata from operation file.

Args:
    operation_name: Name of the operation

Returns:
    Dictionary with operation metadata

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** Dict[str, str]
    Dictionary with operation metadata


  #### `generate_template`

  ```python
  generate_template(self, operation_name: str) -> str
  ```

  Generate a response template for an operation.

Args:
    operation_name: Name of the operation

Returns:
    YAML template content

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** str
    YAML template content


  #### `add_template`

  ```python
  add_template(self, operation_name: str, dry_run: bool) -> TemplateGenerationResult
  ```

  Add a response template for an operation.

Args:
    operation_name: Name of the operation
    dry_run: If True, don't modify files

Returns:
    TemplateGenerationResult

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation
  - `dry_run` (bool) = `False`: If True, don't modify files


  **Returns:** TemplateGenerationResult
    TemplateGenerationResult


  #### `generate_missing_templates`

  ```python
  generate_missing_templates(self, missing_operations: List[str], dry_run: bool) -> List[TemplateGenerationResult]
  ```

  Generate templates for multiple operations.

Args:
    missing_operations: List of operation names
    dry_run: If True, don't modify files

Returns:
    List of TemplateGenerationResult

  **Parameters:**

  - `self`
  - `missing_operations` (List[str]): List of operation names
  - `dry_run` (bool) = `False`: If True, don't modify files


  **Returns:** List[TemplateGenerationResult]
    List of TemplateGenerationResult



---
