# report_generator

Report Generator for Sanitization

Generates comprehensive audit reports and documentation for sanitization operations.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ReportGenerator](#reportgenerator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, logging, pathlib, typing


## Classes

### ReportGenerator

```python
class ReportGenerator
```

Generates audit reports and documentation.


**Methods:**

  #### `generate_audit_report`

  ```python
  generate_audit_report(self, results: Dict[str, Any]) -> str
  ```

  Generate comprehensive audit report in Markdown.

Args:
    results: Orchestrator execution results

Returns:
    Path to generated report

  **Parameters:**

  - `self`
  - `results` (Dict[str, Any]): Orchestrator execution results


  **Returns:** str
    Path to generated report


  #### `generate_mapping_reference`

  ```python
  generate_mapping_reference(self, mappings: Dict[str, str]) -> str
  ```

  Generate mapping reference file in JSON.

Args:
    mappings: Transformation mappings

Returns:
    Path to mapping reference file

  **Parameters:**

  - `self`
  - `mappings` (Dict[str, str]): Transformation mappings


  **Returns:** str
    Path to mapping reference file



---
