# code_analyzer

Code Analyzer for Sanitization

Scans codebases to identify domain-specific terminology, sensitive data,
and structural elements requiring transformation.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CodeAnalyzer](#codeanalyzer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** collections, logging, os, pathlib, re, typing


## Classes

### CodeAnalyzer

```python
class CodeAnalyzer
```

Analyzes codebases to extract domain terminology and structure.


**Methods:**

  #### `scan_file_structure`

  ```python
  scan_file_structure(self) -> Dict[str, Any]
  ```

  Scan directory structure and categorize files.

Returns:
    Dict with file inventory by type and language

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with file inventory by type and language


  #### `extract_domain_terminology`

  ```python
  extract_domain_terminology(self) -> Dict[str, Any]
  ```

  Extract domain-specific terms from code and documentation.

Returns:
    Dict mapping terms to frequency and locations

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict mapping terms to frequency and locations


  #### `extract_namespaces`

  ```python
  extract_namespaces(self) -> Dict[str, List[str]]
  ```

  Extract namespaces/packages from code files.

Returns:
    Dict mapping language to list of namespaces

  **Parameters:**

  - `self`


  **Returns:** Dict[str, List[str]]
    Dict mapping language to list of namespaces


  #### `detect_sensitive_data`

  ```python
  detect_sensitive_data(self) -> Dict[str, Any]
  ```

  Detect potentially sensitive data in codebase.

Returns:
    Dict with sensitive data locations and types

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with sensitive data locations and types


  #### `generate_dependency_graph`

  ```python
  generate_dependency_graph(self) -> Dict[str, List[str]]
  ```

  Generate basic dependency graph (namespace/module dependencies).

Returns:
    Dict mapping files to their dependencies

  **Parameters:**

  - `self`


  **Returns:** Dict[str, List[str]]
    Dict mapping files to their dependencies



---
