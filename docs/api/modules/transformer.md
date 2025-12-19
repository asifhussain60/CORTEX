# transformer

Code Transformer for Sanitization

Applies transformation mappings to codebase files while preserving
structure and functionality.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CodeTransformer](#codetransformer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, os, pathlib, re, shutil, typing


## Classes

### CodeTransformer

```python
class CodeTransformer
```

Applies sanitization transformations to codebase.


**Methods:**

  #### `transform_codebase`

  ```python
  transform_codebase(self, source_directory: str, output_directory: str, mappings: Dict[str, str]) -> Dict[str, Any]
  ```

  Transform entire codebase using mappings.

Args:
    source_directory: Source codebase path
    output_directory: Destination for sanitized code
    mappings: Transformation mappings (original→generic)

Returns:
    Transformation log with statistics

  **Parameters:**

  - `self`
  - `source_directory` (str): Source codebase path
  - `output_directory` (str): Destination for sanitized code
  - `mappings` (Dict[str, str]): Transformation mappings (original→generic)


  **Returns:** Dict[str, Any]
    Transformation log with statistics



---
