# api_doc_generator

API Documentation Generator - Generate comprehensive API docs

Creates structured API documentation from analyzed code:
- Module overview
- Class documentation with methods
- Function documentation
- Type signatures
- Usage examples


## Table of Contents

### Classes
- [APIDocGenerator](#apidocgenerator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** extractors, pathlib, typing


## Classes

### APIDocGenerator

```python
class APIDocGenerator
```

Generates comprehensive API documentation in Markdown format

Creates documentation with:
- Table of contents
- Module overview
- Class documentation
- Method signatures with type hints
- Parameter descriptions
- Return value documentation
- Usage examples


**Methods:**

  #### `generate_module_docs`

  ```python
  generate_module_docs(self, module_info: ModuleInfo, output_path: Path, include_private: bool) -> Path
  ```

  Generate complete documentation for a module

Args:
    module_info: Analyzed module information
    output_path: Where to save the Markdown documentation
    include_private: Whether to document private methods (starting with _)
    
Returns:
    Path to generated Markdown file

  **Parameters:**

  - `self`
  - `module_info` (ModuleInfo): Analyzed module information
  - `output_path` (Path): Where to save the Markdown documentation
  - `include_private` (bool) = `False`: Whether to document private methods (starting with _)


  **Returns:** Path
    Path to generated Markdown file


  #### `generate_multi_module_docs`

  ```python
  generate_multi_module_docs(self, modules: List[ModuleInfo], output_dir: Path, index_name: str) -> Path
  ```

  Generate documentation for multiple modules with index

Args:
    modules: List of analyzed modules
    output_dir: Directory to save documentation
    index_name: Name of the index file
    
Returns:
    Path to index file

  **Parameters:**

  - `self`
  - `modules` (List[ModuleInfo]): List of analyzed modules
  - `output_dir` (Path): Directory to save documentation
  - `index_name` (str) = `'index.md'`: Name of the index file


  **Returns:** Path
    Path to index file


  #### `generate_quick_reference`

  ```python
  generate_quick_reference(self, modules: List[ModuleInfo], output_path: Path) -> Path
  ```

  Generate a quick reference guide

Compact single-page reference with all APIs

Args:
    modules: List of analyzed modules
    output_path: Where to save the quick reference
    
Returns:
    Path to generated file

  **Parameters:**

  - `self`
  - `modules` (List[ModuleInfo]): List of analyzed modules
  - `output_path` (Path): Where to save the quick reference


  **Returns:** Path
    Path to generated file



---
