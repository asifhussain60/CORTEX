# feature_auto_registrar

Feature Auto-Registrar for CORTEX Align Orchestrator v2.0

This module automatically discovers and registers new features in cortex-operations.yaml.
Extracts metadata from Python files and generates properly formatted YAML entries.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [OperationMetadata](#operationmetadata)
- [RegistrationResult](#registrationresult)
- [FeatureAutoRegistrar](#featureautoregistrar)

### Functions
- [main](#main)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** ast, dataclasses, datetime, logging, pathlib, re, sys, typing, yaml


## Classes

### OperationMetadata

```python
class OperationMetadata
```

**Decorators:** `dataclass`

Metadata extracted from an operation file.


**Attributes:**

- `name`: str
- `display_name`: str
- `description`: str
- `deployment_tier`: str
- `natural_language`: List[str]
- `category`: str
- `modules`: List[str]
- `examples`: List[str]
- `version`: str
- `author`: str



---

### RegistrationResult

```python
class RegistrationResult
```

**Decorators:** `dataclass`

Result from feature registration.


**Attributes:**

- `success`: bool
- `operation_name`: str
- `yaml_entry`: str
- `dry_run`: bool
- `error_message`: str
- `file_path`: Optional[Path]



---

### FeatureAutoRegistrar

```python
class FeatureAutoRegistrar
```

Automatically registers discovered features in cortex-operations.yaml.


**Methods:**

  #### `extract_module_docstring`

  ```python
  extract_module_docstring(self, content: str) -> str
  ```

  Extract module-level docstring from Python file.

Args:
    content: Python file content

Returns:
    Module docstring or empty string

  **Parameters:**

  - `self`
  - `content` (str): Python file content


  **Returns:** str
    Module docstring or empty string


  #### `extract_natural_language_triggers`

  ```python
  extract_natural_language_triggers(self, content: str, docstring: str) -> List[str]
  ```

  Extract natural language triggers from file content and docstring.

Looks for:
- Patterns like: "plan feature", "start tdd", "commit and push"
- Command strings in comments
- Usage examples in docstrings

Args:
    content: Python file content
    docstring: Module docstring

Returns:
    List of natural language trigger phrases

  **Parameters:**

  - `self`
  - `content` (str): Python file content
  - `docstring` (str): Module docstring


  **Returns:** List[str]
    List of natural language trigger phrases


  #### `infer_deployment_tier`

  ```python
  infer_deployment_tier(self, file_path: Path, content: str) -> str
  ```

  Infer deployment tier from file location and content.

Args:
    file_path: Path to the operation file
    content: File content

Returns:
    'user_facing', 'dual_context', or 'admin_only'

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to the operation file
  - `content` (str): File content


  **Returns:** str
    'user_facing', 'dual_context', or 'admin_only'


  #### `infer_category`

  ```python
  infer_category(self, file_path: Path) -> str
  ```

  Infer operation category from file path and name.

Args:
    file_path: Path to the operation file

Returns:
    Category name

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to the operation file


  **Returns:** str
    Category name


  #### `extract_usage_examples`

  ```python
  extract_usage_examples(self, docstring: str) -> List[str]
  ```

  Extract usage examples from docstring.

Args:
    docstring: Module docstring

Returns:
    List of usage examples

  **Parameters:**

  - `self`
  - `docstring` (str): Module docstring


  **Returns:** List[str]
    List of usage examples


  #### `find_related_modules`

  ```python
  find_related_modules(self, operation_name: str) -> List[str]
  ```

  Find modules related to an operation.

Args:
    operation_name: Name of the operation

Returns:
    List of module names/paths

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** List[str]
    List of module names/paths


  #### `analyze_operation_file`

  ```python
  analyze_operation_file(self, file_path: Path) -> OperationMetadata
  ```

  Extract metadata from an operation file.

Args:
    file_path: Path to operation file

Returns:
    OperationMetadata with extracted information

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to operation file


  **Returns:** OperationMetadata
    OperationMetadata with extracted information


  #### `format_triggers`

  ```python
  format_triggers(self, triggers: List[str]) -> str
  ```

  Format natural language triggers for YAML.

  **Parameters:**

  - `self`
  - `triggers` (List[str])


  **Returns:** str


  #### `format_examples`

  ```python
  format_examples(self, examples: List[str]) -> str
  ```

  Format examples for YAML.

  **Parameters:**

  - `self`
  - `examples` (List[str])


  **Returns:** str


  #### `generate_yaml_entry`

  ```python
  generate_yaml_entry(self, metadata: OperationMetadata) -> str
  ```

  Generate YAML entry for an operation.

Args:
    metadata: OperationMetadata to convert to YAML

Returns:
    Formatted YAML string

  **Parameters:**

  - `self`
  - `metadata` (OperationMetadata): OperationMetadata to convert to YAML


  **Returns:** str
    Formatted YAML string


  #### `insert_yaml_entry`

  ```python
  insert_yaml_entry(self, yaml_entry: str) -> None
  ```

  Insert YAML entry into cortex-operations.yaml.
Inserts at the end of the operations section, before the modules section.

Args:
    yaml_entry: Formatted YAML string to insert

  **Parameters:**

  - `self`
  - `yaml_entry` (str): Formatted YAML string to insert


  **Returns:** None


  #### `update_statistics`

  ```python
  update_statistics(self) -> None
  ```

  Update statistics section in cortex-operations.yaml.

  **Parameters:**

  - `self`


  **Returns:** None


  #### `add_changelog_entry`

  ```python
  add_changelog_entry(self, operation_name: str) -> None
  ```

  Add changelog entry for newly registered operation.

Args:
    operation_name: Name of the operation

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** None


  #### `register_feature`

  ```python
  register_feature(self, operation_name: str, dry_run: bool) -> RegistrationResult
  ```

  Register a new feature in cortex-operations.yaml.

Args:
    operation_name: Name of the operation to register
    dry_run: If True, generate YAML but don't write to file

Returns:
    RegistrationResult with status and details

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation to register
  - `dry_run` (bool) = `False`: If True, generate YAML but don't write to file


  **Returns:** RegistrationResult
    RegistrationResult with status and details


  #### `batch_register`

  ```python
  batch_register(self, operation_names: List[str], dry_run: bool) -> Dict[str, RegistrationResult]
  ```

  Register multiple operations.

Args:
    operation_names: List of operation names to register
    dry_run: If True, don't write to file

Returns:
    Dict mapping operation names to RegistrationResults

  **Parameters:**

  - `self`
  - `operation_names` (List[str]): List of operation names to register
  - `dry_run` (bool) = `False`: If True, don't write to file


  **Returns:** Dict[str, RegistrationResult]
    Dict mapping operation names to RegistrationResults



---

## Functions

### main

```python
main()
```

CLI entry point for standalone registration.


---
