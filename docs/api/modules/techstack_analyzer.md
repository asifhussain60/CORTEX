# techstack_analyzer

Technology Stack Analyzer

Detects frameworks, libraries, dependencies, and language statistics
from project files (requirements.txt, package.json, etc.).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [TechStackAnalyzer](#techstackanalyzer)

### Functions
- [generate_techstack_json](#generate_techstack_json)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** collections, json, logging, pathlib, re, typing


## Classes

### TechStackAnalyzer

```python
class TechStackAnalyzer
```

Analyzes technology stack from project files


**Methods:**

  #### `analyze`

  ```python
  analyze(self) -> Dict[str, Any]
  ```

  Analyze technology stack
Returns comprehensive tech stack data

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### generate_techstack_json

```python
generate_techstack_json(project_path: Path, output_path: Path) -> Dict[str, Any]
```

Generate techstack.json for a project

Args:
    project_path: Path to project to analyze
    output_path: Path to save techstack.json
    
Returns:
    Tech stack data


**Parameters:**

- `project_path` (Path): Path to project to analyze
- `output_path` (Path): Path to save techstack.json


**Returns:** Dict[str, Any]
  Tech stack data


---
