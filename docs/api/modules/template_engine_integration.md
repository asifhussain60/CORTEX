# template_engine_integration

CORTEX 3.0 Template Engine Integration
======================================

Integrates real-time data collectors with enhanced question routing templates.
Provides live template rendering with actual metrics instead of mock data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Feature: Quick Win #2+3 Integration - Live Template Rendering


## Table of Contents

### Classes
- [TemplateEngine](#templateengine)
- [EnhancedQuestionHandler](#enhancedquestionhandler)

### Functions
- [test_integration](#test_integration)
- [demo_live_template_rendering](#demo_live_template_rendering)


## Overview

- **Classes:** 2
- **Functions:** 2
- **Dependencies:** datetime, json, os, re, src, sys, typing, yaml


## Classes

### TemplateEngine

```python
class TemplateEngine
```

Template engine that renders response templates with live data


**Methods:**

  #### `render_template`

  ```python
  render_template(self, template_name: str, user_message: str, context: Dict[str, Any], force_refresh: bool) -> Dict[str, Any]
  ```

  Render a template with live data

  **Parameters:**

  - `self`
  - `template_name` (str)
  - `user_message` (str) = `''`
  - `context` (Dict[str, Any]) = `None`
  - `force_refresh` (bool) = `False`


  **Returns:** Dict[str, Any]



---

### EnhancedQuestionHandler

```python
class EnhancedQuestionHandler
```

Enhanced question handler that integrates all components


**Methods:**

  #### `handle_question`

  ```python
  handle_question(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Handle a user question with full CORTEX 3.0 intelligence

  **Parameters:**

  - `self`
  - `user_message` (str)
  - `context` (Dict[str, Any]) = `None`


  **Returns:** Dict[str, Any]



---

## Functions

### test_integration

```python
test_integration()
```

Test the complete integration


---

### demo_live_template_rendering

```python
demo_live_template_rendering()
```

Demo live template rendering with real data


---
