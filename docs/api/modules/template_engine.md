# template_engine

CORTEX 3.0 - EPM Template Engine (Feature 4 - Phase 4.3)
========================================================

Advanced template engine for flexible documentation generation
with Jinja2 integration and multiple output formats.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Feature 4 - Phase 4.3 (Week 2)
Effort: 10 hours (template system)
Dependencies: Phase 4.2 (Documentation Generator) - JUST COMPLETED


## Table of Contents

### Classes
- [TemplateConfig](#templateconfig)
- [TemplateContext](#templatecontext)
- [TemplateEngine](#templateengine)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, jinja2, json, os, pathlib, re, sys, typing, yaml


## Classes

### TemplateConfig

```python
class TemplateConfig
```

**Decorators:** `dataclass`

Configuration for template engine


**Attributes:**

- `template_directory`: str
- `output_format`: str
- `custom_filters`: Dict[str, Any]
- `auto_escape`: bool
- `trim_blocks`: bool
- `lstrip_blocks`: bool



---

### TemplateContext

```python
class TemplateContext
```

**Decorators:** `dataclass`

Context data for template rendering


**Attributes:**

- `project_info`: Dict[str, Any]
- `analysis_results`: Dict[str, Any]
- `generation_metadata`: Dict[str, Any]
- `custom_variables`: Dict[str, Any]



---

### TemplateEngine

```python
class TemplateEngine
```

Advanced template engine for documentation generation.

Features:
- Jinja2 template processing with custom filters
- Multiple output formats (Markdown, HTML, RST)
- Template inheritance and composition
- Auto-escaping for security
- Custom template functions and filters
- Template validation and error handling


**Methods:**

  #### `render_template`

  ```python
  render_template(self, template_name: str, context: Union[TemplateContext, Dict[str, Any]]) -> str
  ```

  Render a template with the provided context.

Args:
    template_name: Name of template file (with extension)
    context: Template context data
    
Returns:
    Rendered template content
    
Raises:
    TemplateNotFound: If template file doesn't exist
    TemplateError: If template has syntax errors

  **Parameters:**

  - `self`
  - `template_name` (str): Name of template file (with extension)
  - `context` (Union[TemplateContext, Dict[str, Any]]): Template context data


  **Returns:** str
    Rendered template content


  #### `render_string`

  ```python
  render_string(self, template_string: str, context: Union[TemplateContext, Dict[str, Any]]) -> str
  ```

  Render a template from string content.

Args:
    template_string: Template content as string
    context: Template context data
    
Returns:
    Rendered content

  **Parameters:**

  - `self`
  - `template_string` (str): Template content as string
  - `context` (Union[TemplateContext, Dict[str, Any]]): Template context data


  **Returns:** str
    Rendered content


  #### `list_templates`

  ```python
  list_templates(self, pattern: Optional[str]) -> List[str]
  ```

  List available templates, optionally filtered by pattern.

Args:
    pattern: Optional regex pattern to filter template names
    
Returns:
    List of template filenames

  **Parameters:**

  - `self`
  - `pattern` (Optional[str]) = `None`: Optional regex pattern to filter template names


  **Returns:** List[str]
    List of template filenames


  #### `validate_template`

  ```python
  validate_template(self, template_name: str) -> Dict[str, Any]
  ```

  Validate a template for syntax errors.

Args:
    template_name: Name of template to validate
    
Returns:
    Validation results with errors/warnings

  **Parameters:**

  - `self`
  - `template_name` (str): Name of template to validate


  **Returns:** Dict[str, Any]
    Validation results with errors/warnings


  #### `create_template`

  ```python
  create_template(self, template_name: str, content: str, overwrite: bool) -> bool
  ```

  Create a new template file.

Args:
    template_name: Name for the new template
    content: Template content
    overwrite: Whether to overwrite existing template
    
Returns:
    True if created successfully, False otherwise

  **Parameters:**

  - `self`
  - `template_name` (str): Name for the new template
  - `content` (str): Template content
  - `overwrite` (bool) = `False`: Whether to overwrite existing template


  **Returns:** bool
    True if created successfully, False otherwise



---
