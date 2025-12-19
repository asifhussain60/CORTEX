# policy_scanner

Policy Scanner - Multi-format policy document detection and parsing

**Purpose:** Detect and parse policy documents from common locations in user repositories
**Supports:** YAML, JSON, Markdown formats
**Graceful Handling:** Works whether policies exist or not

**Author:** Asif Hussain
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
**License:** Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [PolicyFormat](#policyformat)
- [PolicyDocument](#policydocument)
- [PolicyScanner](#policyscanner)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, enum, json, pathlib, src, sys, typing, yaml


## Classes

### PolicyFormat

```python
class PolicyFormat(Enum)
```

Supported policy document formats



---

### PolicyDocument

```python
class PolicyDocument
```

**Decorators:** `dataclass`

Represents a detected policy document


**Attributes:**

- `path`: Path
- `format`: PolicyFormat
- `content`: Dict[str, Any]
- `categories`: List[str]


**Methods:**


---

### PolicyScanner

```python
class PolicyScanner
```

Scans repository for policy documents in multiple formats

**Search Locations:**
1. .github/policies/ (GitHub convention)
2. docs/policies/ (Documentation folder)
3. policies/ (Root policies folder)
4. POLICIES.md / POLICIES.yaml / POLICIES.json (Root files)

**Supported Formats:**
- YAML (.yaml, .yml)
- JSON (.json)
- Markdown (.md) - Parses structured sections


**Methods:**

  #### `scan_for_policies`

  ```python
  scan_for_policies(self) -> List[PolicyDocument]
  ```

  Scan all common locations for policy documents

Returns:
    List of detected PolicyDocument objects (empty if none found)

  **Parameters:**

  - `self`


  **Returns:** List[PolicyDocument]
    List of detected PolicyDocument objects (empty if none found)


  #### `has_policies`

  ```python
  has_policies(self) -> bool
  ```

  Quick check if any policies exist

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `create_starter_policies`

  ```python
  create_starter_policies(self, output_path: Optional[Path]) -> Path
  ```

  Create starter policy template for users without policies

Args:
    output_path: Where to save template (default: repo_root/.github/policies/starter-policies.yaml)
    
Returns:
    Path to created policy file

  **Parameters:**

  - `self`
  - `output_path` (Optional[Path]) = `None`: Where to save template (default: repo_root/.github/policies/starter-policies.yaml)


  **Returns:** Path
    Path to created policy file



---
