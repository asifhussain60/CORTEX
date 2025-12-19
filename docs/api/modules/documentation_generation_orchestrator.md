# documentation_generation_orchestrator

Documentation Generation Orchestrator.

Provides automatic documentation generation from Python code using AST parsing.


## Table of Contents

### Classes
- [DocstringInfo](#docstringinfo)
- [APIReference](#apireference)
- [UsageGuide](#usageguide)
- [DocumentationGenerationOrchestrator](#documentationgenerationorchestrator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** ast, dataclasses, pathlib, typing


## Classes

### DocstringInfo

```python
class DocstringInfo
```

**Decorators:** `dataclass`

Information about a docstring.


**Attributes:**

- `name`: str
- `type`: str
- `docstring`: str
- `lineno`: int



---

### APIReference

```python
class APIReference
```

**Decorators:** `dataclass`

Generated API reference documentation.


**Attributes:**

- `module_name`: str
- `markdown`: str
- `sections`: List[str]



---

### UsageGuide

```python
class UsageGuide
```

**Decorators:** `dataclass`

Generated usage guide documentation.


**Attributes:**

- `module_name`: str
- `markdown`: str
- `examples`: List[Dict[str, str]]



---

### DocumentationGenerationOrchestrator

```python
class DocumentationGenerationOrchestrator
```

Orchestrator for automatic documentation generation.

Features:
- Extract docstrings from Python source code
- Generate API reference documentation
- Create usage guides with examples
- Markdown formatting


**Methods:**

  #### `extract_docstrings`

  ```python
  extract_docstrings(self, source_code: str) -> List[DocstringInfo]
  ```

  Extract docstrings from Python source code.

Args:
    source_code: Python source code as string
    
Returns:
    List of DocstringInfo objects

  **Parameters:**

  - `self`
  - `source_code` (str): Python source code as string


  **Returns:** List[DocstringInfo]
    List of DocstringInfo objects


  #### `generate_api_reference`

  ```python
  generate_api_reference(self, docstrings: List[DocstringInfo], module_name: str) -> APIReference
  ```

  Generate API reference documentation.

Args:
    docstrings: List of extracted docstrings
    module_name: Name of the module
    
Returns:
    APIReference with markdown documentation

  **Parameters:**

  - `self`
  - `docstrings` (List[DocstringInfo]): List of extracted docstrings
  - `module_name` (str) = `'Module'`: Name of the module


  **Returns:** APIReference
    APIReference with markdown documentation


  #### `create_usage_guide`

  ```python
  create_usage_guide(self, module_name: str, examples: List[Dict[str, str]], description: str) -> UsageGuide
  ```

  Create usage guide with examples.

Args:
    module_name: Name of the module
    examples: List of example dicts with 'title' and 'code' keys
    description: Optional module description
    
Returns:
    UsageGuide with markdown documentation

  **Parameters:**

  - `self`
  - `module_name` (str): Name of the module
  - `examples` (List[Dict[str, str]]): List of example dicts with 'title' and 'code' keys
  - `description` (str) = `''`: Optional module description


  **Returns:** UsageGuide
    UsageGuide with markdown documentation



---
