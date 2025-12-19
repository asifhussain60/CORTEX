# response_context_integration

Response Context Integration - Injects context summaries into CORTEX responses

This module integrates context visibility into standard response templates,
showing users what CORTEX remembers when responding.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ResponseContextIntegration](#responsecontextintegration)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, typing


## Classes

### ResponseContextIntegration

```python
class ResponseContextIntegration
```

Integrates context summaries into CORTEX response templates.

Features:
- Collapsible context summary section
- Quality indicators
- Show only when context is loaded
- Non-intrusive optional display


**Methods:**

  #### `inject_context_summary`

  *Decorators:* `staticmethod`

  ```python
  inject_context_summary(response: str, context_data: Optional[Dict[str, Any]]) -> str
  ```

  Inject context summary into response template.

Args:
    response: Original response text
    context_data: Loaded context data (from context_injector)

Returns:
    Response with context summary injected (if context available)

  **Parameters:**

  - `response` (str): Original response text
  - `context_data` (Optional[Dict[str, Any]]) = `None`: Loaded context data (from context_injector)


  **Returns:** str
    Response with context summary injected (if context available)


  #### `should_show_context`

  *Decorators:* `staticmethod`

  ```python
  should_show_context(context_data: Optional[Dict[str, Any]]) -> bool
  ```

  Determine if context summary should be shown.

Args:
    context_data: Loaded context data

Returns:
    True if context should be displayed

  **Parameters:**

  - `context_data` (Optional[Dict[str, Any]]): Loaded context data


  **Returns:** bool
    True if context should be displayed



---
