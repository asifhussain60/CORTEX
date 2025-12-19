# documentation_generator

CORTEX 3.0 - EPM Documentation Generator (Feature 4 - Phase 4.2)
================================================================

⚠️ DEPRECATED - Use Enterprise Documentation Orchestrator instead
Location: cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py

This module is kept for backward compatibility but will be removed in v4.0.
For new documentation generation, use the Enterprise Documentation Orchestrator:
- Unified entry point for ALL doc generation
- Includes Discovery Engine, DALL-E prompts, narratives, story, executive summary
- Admin-only (not packaged for production)

Documentation generation pipeline that converts code analysis results
into comprehensive, readable documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Feature 4 - Phase 4.2 (Week 2)
Effort: 15 hours (documentation generation pipeline)
Dependencies: Phase 4.1 (Code Analysis Engine) - COMPLETED
Status: DEPRECATED (use Enterprise Documentation Orchestrator)


## Table of Contents

### Classes
- [DocumentationConfig](#documentationconfig)
- [DocumentSection](#documentsection)
- [DocumentationGenerator](#documentationgenerator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, jinja2, json, markdown, os, pathlib, re, sys, typing, yaml


## Classes

### DocumentationConfig

```python
class DocumentationConfig
```

**Decorators:** `dataclass`

Configuration for documentation generation


**Attributes:**

- `output_format`: str
- `include_code_examples`: bool
- `include_diagrams`: bool
- `include_metrics`: bool
- `template_style`: str
- `output_directory`: str



---

### DocumentSection

```python
class DocumentSection
```

**Decorators:** `dataclass`

A section of generated documentation


**Attributes:**

- `title`: str
- `content`: str
- `level`: int
- `order`: int
- `section_type`: str
- `metadata`: Dict[str, Any]



---

### DocumentationGenerator

```python
class DocumentationGenerator
```

Generates comprehensive documentation from code analysis results.

Features:
- Multiple output formats (Markdown, HTML, RST)
- Configurable templates and styles
- Code example extraction and formatting
- Automatic table of contents generation
- Cross-reference linking
- Metrics and statistics integration


**Methods:**

  #### `generate_from_analysis`

  ```python
  generate_from_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, str]
  ```

  Generate documentation from code analysis results.

Args:
    analysis_results: Results from Phase 4.1 code analysis engine
    
Returns:
    Dictionary mapping document names to file paths

  **Parameters:**

  - `self`
  - `analysis_results` (Dict[str, Any]): Results from Phase 4.1 code analysis engine


  **Returns:** Dict[str, str]
    Dictionary mapping document names to file paths



---
