# mapping_engine

Mapping Engine for Code Sanitization

Generates domain→generic terminology mappings with conflict detection
and resolution strategies.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [MappingEngine](#mappingengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** collections, logging, re, typing


## Classes

### MappingEngine

```python
class MappingEngine
```

Generates and manages transformation mappings.


**Methods:**

  #### `generate_mappings`

  ```python
  generate_mappings(self, domain_terms: Dict[str, Any], namespaces: Dict[str, List[str]]) -> Dict[str, str]
  ```

  Generate comprehensive transformation mappings.

Args:
    domain_terms: Extracted domain terminology
    namespaces: Detected namespaces by language

Returns:
    Dict mapping original→sanitized terms

  **Parameters:**

  - `self`
  - `domain_terms` (Dict[str, Any]): Extracted domain terminology
  - `namespaces` (Dict[str, List[str]]): Detected namespaces by language


  **Returns:** Dict[str, str]
    Dict mapping original→sanitized terms


  #### `detect_conflicts`

  ```python
  detect_conflicts(self, mappings: Dict[str, str]) -> List[Dict[str, Any]]
  ```

  Detect naming conflicts in mappings.

Args:
    mappings: Proposed transformation mappings

Returns:
    List of conflicts with details

  **Parameters:**

  - `self`
  - `mappings` (Dict[str, str]): Proposed transformation mappings


  **Returns:** List[Dict[str, Any]]
    List of conflicts with details


  #### `resolve_conflicts`

  ```python
  resolve_conflicts(self, mappings: Dict[str, str], conflicts: List[Dict[str, Any]]) -> Dict[str, str]
  ```

  Resolve naming conflicts by adding disambiguators.

Args:
    mappings: Original mappings
    conflicts: Detected conflicts

Returns:
    Resolved mappings

  **Parameters:**

  - `self`
  - `mappings` (Dict[str, str]): Original mappings
  - `conflicts` (List[Dict[str, Any]]): Detected conflicts


  **Returns:** Dict[str, str]
    Resolved mappings


  #### `generate_preview`

  ```python
  generate_preview(self, mappings: Dict[str, str]) -> Dict[str, str]
  ```

  Generate human-readable preview of transformations.

Args:
    mappings: Transformation mappings

Returns:
    Sorted dict for preview display

  **Parameters:**

  - `self`
  - `mappings` (Dict[str, str]): Transformation mappings


  **Returns:** Dict[str, str]
    Sorted dict for preview display



---
