# context_renderer

CORTEX 3.0 Phase 2 - Context Renderer
====================================

Context-aware response rendering with dynamic template parameter injection.
Renders templates with intelligent context adaptation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Advanced Response Handling (Task 1)
Integration: Template Selector → Context-Aware Response Rendering


## Table of Contents

### Classes
- [RenderResult](#renderresult)
- [ContextRenderer](#contextrenderer)

### Functions
- [render_response_for_question](#render_response_for_question)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, logging, re, src, template_selector, time, traceback, typing


## Classes

### RenderResult

```python
class RenderResult
```

**Decorators:** `dataclass`

Result of context-aware rendering.


**Attributes:**

- `rendered_content`: str
- `template_used`: str
- `context_applied`: Dict[str, Any]
- `render_time_ms`: float
- `warnings`: List[str]
- `success`: bool



---

### ContextRenderer

```python
class ContextRenderer
```

Context-aware response renderer that adapts templates based on user context.

Features:
- Dynamic parameter injection
- Context-aware formatting
- Namespace-specific styling
- Performance optimization


**Methods:**

  #### `render`

  ```python
  render(self, template_result: TemplateSelectionResult, context: Dict[str, Any]) -> RenderResult
  ```

  Render template with context-aware enhancements.

Args:
    template_result: Result from TemplateSelector
    context: Additional rendering context
    
Returns:
    RenderResult with rendered content

  **Parameters:**

  - `self`
  - `template_result` (TemplateSelectionResult): Result from TemplateSelector
  - `context` (Dict[str, Any]) = `None`: Additional rendering context


  **Returns:** RenderResult
    RenderResult with rendered content



---

## Functions

### render_response_for_question

```python
render_response_for_question(question: str, context: Dict[str, Any], brain_path: str) -> RenderResult
```

Integrated function: Select template and render response for a question.

Args:
    question: User's question
    context: Optional context
    brain_path: Optional brain path
    
Returns:
    RenderResult with fully rendered response


**Parameters:**

- `question` (str): User's question
- `context` (Dict[str, Any]) = `None`: Optional context
- `brain_path` (str) = `None`: Optional brain path


**Returns:** RenderResult
  RenderResult with fully rendered response


---
