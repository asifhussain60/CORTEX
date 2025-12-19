# enhanced_feedback_module

Enhanced Feedback Module - Comprehensive Performance Analytics

Collects 8 categories of metrics from user environments:
1. Application Metrics - Project size, tech stack, complexity
2. Crawler Performance - Discovery stats, cache efficiency
3. CORTEX Performance - Operation timings, memory usage
4. Knowledge Graphs - Entity counts, graph density
5. Development Hygiene - Commit quality, security
6. TDD Mastery - Test coverage, test-first adherence
7. Commit Metrics - Build success, deployment frequency
8. Velocity Metrics - Sprint velocity, cycle time

Supports GitHub Gist integration for effortless sharing.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [EnhancedFeedbackModule](#enhancedfeedbackmodule)

### Functions
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, getpass, github, hashlib, json, logging, pathlib, socket, src, typing, yaml


## Classes

### EnhancedFeedbackModule

```python
class EnhancedFeedbackModule(BaseOperationModule)
```

Enhanced feedback collection with comprehensive metrics and Gist integration.

Features:
    - 8-category metrics collection
    - GitHub Gist upload (optional)
    - Privacy-first sanitization
    - Local report storage
    - Multiple sharing options

Usage:
    # Natural language
    "feedback"
    "generate feedback report"
    "share performance metrics"


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_context`

  ```python
  validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]
  ```

  Validate execution context.

Checks:
    - Project root exists
    - CORTEX brain accessible
    - Feedback reports directory writable

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** tuple[bool, str]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute comprehensive feedback collection.

Args:
    context: Execution context with:
        - project_root: Project root directory
        - share_method: 'local', 'gist', or 'export'
        - github_token: GitHub token for Gist (if share_method='gist')
        - privacy_level: 'full', 'medium', or 'minimal'

Returns:
    OperationResult with feedback report and sharing status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with:


  **Returns:** OperationResult
    OperationResult with feedback report and sharing status



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register module for discovery.


**Returns:** BaseOperationModule


---
