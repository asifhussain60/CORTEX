# recommendations_engine

Recommendations Engine

Generates prioritized recommendations from security, quality, and architecture analysis.
Provides actionable suggestions with effort/impact scoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [Recommendation](#recommendation)
- [RecommendationsEngine](#recommendationsengine)

### Functions
- [generate_recommendations_json](#generate_recommendations_json)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, logging, typing


## Classes

### Recommendation

```python
class Recommendation
```

**Decorators:** `dataclass`

A single recommendation


**Attributes:**

- `id`: str
- `category`: str
- `priority`: str
- `title`: str
- `description`: str
- `rationale`: str
- `impact`: str
- `effort`: str
- `tags`: List[str]
- `resources`: List[str]
- `code_example`: Optional[str]



---

### RecommendationsEngine

```python
class RecommendationsEngine
```

Generates recommendations from analysis results


**Methods:**

  #### `generate_recommendations`

  ```python
  generate_recommendations(self, security_issues: List[Any], quality_issues: List[Any], tech_stack: Dict[str, Any], architecture: Dict[str, Any]) -> List[Dict[str, Any]]
  ```

  Generate comprehensive recommendations

Args:
    security_issues: List of security vulnerabilities
    quality_issues: List of code quality issues
    tech_stack: Technology stack analysis
    architecture: Architecture graph data
    
Returns:
    List of recommendations sorted by priority

  **Parameters:**

  - `self`
  - `security_issues` (List[Any]): List of security vulnerabilities
  - `quality_issues` (List[Any]): List of code quality issues
  - `tech_stack` (Dict[str, Any]): Technology stack analysis
  - `architecture` (Dict[str, Any]): Architecture graph data


  **Returns:** List[Dict[str, Any]]
    List of recommendations sorted by priority



---

## Functions

### generate_recommendations_json

```python
generate_recommendations_json(security_issues: List[Any], quality_issues: List[Any], tech_stack: Dict[str, Any], architecture: Dict[str, Any], output_path) -> List[Dict[str, Any]]
```

Generate recommendations.json

Args:
    security_issues: Security vulnerability list
    quality_issues: Code quality issue list
    tech_stack: Tech stack analysis
    architecture: Architecture graph
    output_path: Path to save recommendations.json
    
Returns:
    List of recommendations


**Parameters:**

- `security_issues` (List[Any]): Security vulnerability list
- `quality_issues` (List[Any]): Code quality issue list
- `tech_stack` (Dict[str, Any]): Tech stack analysis
- `architecture` (Dict[str, Any]): Architecture graph
- `output_path`: Path to save recommendations.json


**Returns:** List[Dict[str, Any]]
  List of recommendations


---
