# mermaid_diagram_validator

Mermaid Diagram Validator - CORTEX Lens Quality Assurance

Validates Mermaid diagrams in generated specifications to ensure they render correctly.
Part of the legacy API specification generation quality gates.

Author: CORTEX
Version: 1.0.0
Date: December 15, 2025


## Table of Contents

### Classes
- [DiagramValidationError](#diagramvalidationerror)
- [DiagramValidationResult](#diagramvalidationresult)
- [MermaidDiagramValidator](#mermaiddiagramvalidator)

### Functions
- [validate_spec_file](#validate_spec_file)
- [print_validation_report](#print_validation_report)


## Overview

- **Classes:** 3
- **Functions:** 2
- **Dependencies:** dataclasses, pathlib, re, sys, typing


## Classes

### DiagramValidationError

```python
class DiagramValidationError
```

**Decorators:** `dataclass`

Represents a validation error in a Mermaid diagram.


**Attributes:**

- `diagram_type`: str
- `line_number`: int
- `error_type`: str
- `message`: str
- `context`: str



---

### DiagramValidationResult

```python
class DiagramValidationResult
```

**Decorators:** `dataclass`

Results of diagram validation.


**Attributes:**

- `is_valid`: bool
- `errors`: List[DiagramValidationError]
- `warnings`: List[str]
- `diagrams_found`: int
- `diagrams_validated`: int



---

### MermaidDiagramValidator

```python
class MermaidDiagramValidator
```

Validates Mermaid diagrams in Markdown files.

Checks for:
- Syntax errors (unclosed brackets, invalid characters)
- Truncated text/identifiers
- Invalid participant names in sequence diagrams
- Malformed node definitions in flowcharts
- Invalid class definitions in class diagrams


**Methods:**

  #### `validate_markdown_file`

  ```python
  validate_markdown_file(self, md_file_path: Path) -> DiagramValidationResult
  ```

  Validate all Mermaid diagrams in a Markdown file.

Args:
    md_file_path: Path to the Markdown file
    
Returns:
    DiagramValidationResult with validation status and errors

  **Parameters:**

  - `self`
  - `md_file_path` (Path): Path to the Markdown file


  **Returns:** DiagramValidationResult
    DiagramValidationResult with validation status and errors



---

## Functions

### validate_spec_file

```python
validate_spec_file(spec_file_path: Path) -> DiagramValidationResult
```

Convenience function to validate a specification file.

Args:
    spec_file_path: Path to business-spec.md file
    
Returns:
    DiagramValidationResult


**Parameters:**

- `spec_file_path` (Path): Path to business-spec.md file


**Returns:** DiagramValidationResult
  DiagramValidationResult


---

### print_validation_report

```python
print_validation_report(result: DiagramValidationResult, file_path: Path)
```

Print a formatted validation report.


**Parameters:**

- `result` (DiagramValidationResult)
- `file_path` (Path)


---
