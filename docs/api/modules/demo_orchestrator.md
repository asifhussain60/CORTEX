# demo_orchestrator

CORTEX Demo Orchestrator

Handles discovery and demonstration of CORTEX capabilities.
Routes discovery commands to the appropriate demonstration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [DemoOrchestrator](#demoorchestrator)

### Functions
- [handle_discovery_request](#handle_discovery_request)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, logging, pathlib, typing


## Classes

### DemoOrchestrator

```python
class DemoOrchestrator
```

Orchestrates CORTEX capability discovery and demonstrations.

Handles:
- Introduction and discovery responses
- Live feature demonstrations
- Interactive guided tours
- Learning path recommendations


**Methods:**

  #### `handle_discovery`

  ```python
  handle_discovery(self, user_request: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]
  ```

  Handle discovery request with template-based response.

Args:
    user_request: User's discovery request
    context: Additional context for rendering
    
Returns:
    Response dict with template_id and context

  **Parameters:**

  - `self`
  - `user_request` (str): User's discovery request
  - `context` (Optional[Dict[str, Any]]) = `None`: Additional context for rendering


  **Returns:** Dict[str, Any]
    Response dict with template_id and context



---

## Functions

### handle_discovery_request

```python
handle_discovery_request(user_request: str, brain_path: Optional[Path]) -> Dict[str, Any]
```

Quick handler for discovery requests.

Args:
    user_request: User's discovery request
    brain_path: Path to CORTEX brain
    
Returns:
    Response dict with template_id and context


**Parameters:**

- `user_request` (str): User's discovery request
- `brain_path` (Optional[Path]) = `None`: Path to CORTEX brain


**Returns:** Dict[str, Any]
  Response dict with template_id and context


---
