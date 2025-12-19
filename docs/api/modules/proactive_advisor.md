# proactive_advisor

Proactive Advisor - Continuous enhancement recommendations.

Provides actionable recommendations without user prompting based on
code quality analysis, architecture patterns, and historical learnings.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ProactiveRecommendation](#proactiverecommendation)
- [ProactiveAdvisor](#proactiveadvisor)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, typing


## Classes

### ProactiveRecommendation

```python
class ProactiveRecommendation
```

**Decorators:** `dataclass`

Proactive enhancement recommendation.


**Attributes:**

- `category`: str
- `priority`: str
- `title`: str
- `description`: str
- `suggested_action`: str
- `estimated_effort`: str
- `impact`: str



---

### ProactiveAdvisor

```python
class ProactiveAdvisor
```

Generate proactive enhancement recommendations.


**Methods:**

  #### `generate_recommendations`

  ```python
  generate_recommendations(self, context: Optional[Dict[str, Any]]) -> List[ProactiveRecommendation]
  ```

  Generate proactive recommendations based on current codebase state.

Args:
    context: Optional context (current operation, affected files, etc.)
    
Returns:
    List of prioritized recommendations

  **Parameters:**

  - `self`
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context (current operation, affected files, etc.)


  **Returns:** List[ProactiveRecommendation]
    List of prioritized recommendations


  #### `format_recommendations`

  ```python
  format_recommendations(self, recommendations: List[ProactiveRecommendation]) -> str
  ```

  Format recommendations as markdown report.

Args:
    recommendations: List of recommendations
    
Returns:
    Formatted markdown string

  **Parameters:**

  - `self`
  - `recommendations` (List[ProactiveRecommendation]): List of recommendations


  **Returns:** str
    Formatted markdown string



---
