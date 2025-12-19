# scope_inference_engine

CORTEX Scope Inference Engine

Purpose: Auto-extract feature boundaries from Planning DoR Q3 (functional scope) and Q6 (technical dependencies)
Target: <5 seconds execution time, >70% confidence for auto-proceed
Status: TDD GREEN Phase - Implementation to pass RED tests

Component of: SWAGGER Entry Point Module (Phase 3.2)


## Table of Contents

### Classes
- [ScopeEntities](#scopeentities)
- [ScopeBoundary](#scopeboundary)
- [ScopeInferenceEngine](#scopeinferenceengine)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, logging, pathlib, re, typing


## Classes

### ScopeEntities

```python
class ScopeEntities
```

**Decorators:** `dataclass`

Detected entities from requirements


**Attributes:**

- `tables`: List[str]
- `files`: List[str]
- `services`: List[str]
- `dependencies`: List[str]
- `confidence_scores`: Dict[str, float]



---

### ScopeBoundary

```python
class ScopeBoundary
```

**Decorators:** `dataclass`

Scope boundary with safety limits and user approval tracking


**Attributes:**

- `table_count`: int
- `file_count`: int
- `service_count`: int
- `dependency_depth`: int
- `estimated_complexity`: float
- `confidence`: float
- `gaps`: List[str]
- `user_approved`: bool
- `approval_timestamp`: Optional[str]
- `approval_method`: Optional[str]
- `swagger_context_id`: Optional[str]
- `entities`: Optional['ScopeEntities']


**Methods:**

  #### `approve_scope`

  ```python
  approve_scope(self, method: str) -> None
  ```

  Mark scope as user-approved

  **Parameters:**

  - `self`
  - `method` (str) = `'interactive'`


  **Returns:** None


  #### `is_approval_required`

  ```python
  is_approval_required(self) -> bool
  ```

  Check if user approval is needed

Returns True if:
- Confidence is below HIGH threshold (80%)
- Has ambiguous references (gaps)
- Not yet user-approved

  **Parameters:**

  - `self`


  **Returns:** bool



---

### ScopeInferenceEngine

```python
class ScopeInferenceEngine
```

Extract scope boundaries from Planning DoR answers

Key Innovation: Zero new questions for 80% of cases - scope extracted from
requirements already collected during DoR validation (Q3 + Q6)


**Methods:**

  #### `parse_dor_answers`

  ```python
  parse_dor_answers(self, dor_responses: Dict[str, str]) -> str
  ```

  Extract and combine text from DoR Q3 and Q6

Args:
    dor_responses: Dict with 'Q3' and/or 'Q6' keys
    
Returns:
    Combined requirements text for entity extraction

  **Parameters:**

  - `self`
  - `dor_responses` (Dict[str, str]): Dict with 'Q3' and/or 'Q6' keys


  **Returns:** str
    Combined requirements text for entity extraction


  #### `extract_entities`

  ```python
  extract_entities(self, requirements_text: str) -> ScopeEntities
  ```

  Extract tables, files, services, dependencies from requirements

Args:
    requirements_text: Requirements from DoR Q3 + Q6
    
Returns:
    ScopeEntities with detected entities and confidence scores

  **Parameters:**

  - `self`
  - `requirements_text` (str): Requirements from DoR Q3 + Q6


  **Returns:** ScopeEntities
    ScopeEntities with detected entities and confidence scores


  #### `calculate_confidence`

  ```python
  calculate_confidence(self, entities: ScopeEntities, requirements_text: str) -> float
  ```

  Calculate confidence score based on entity clarity and completeness

Confidence factors:
- Explicit entity names (high confidence)
- Quantified scope "15 tables" (high confidence)
- Vague references "some tables" (low confidence)
- Empty entities (low confidence)

Args:
    entities: Extracted entities
    requirements_text: Original requirements (optional, for vague keyword detection)

Returns:
    Confidence score (0.0-1.0)

  **Parameters:**

  - `self`
  - `entities` (ScopeEntities): Extracted entities
  - `requirements_text` (str) = `''`: Original requirements (optional, for vague keyword detection)


  **Returns:** float
    Confidence score (0.0-1.0)


  #### `generate_scope_boundary`

  ```python
  generate_scope_boundary(self, entities: ScopeEntities, confidence: float) -> ScopeBoundary
  ```

  Create scope boundary with safety limits

Args:
    entities: Detected entities
    confidence: Calculated confidence score (0.0-1.0)
    
Returns:
    ScopeBoundary with counts, complexity estimate, and gaps

  **Parameters:**

  - `self`
  - `entities` (ScopeEntities): Detected entities
  - `confidence` (float): Calculated confidence score (0.0-1.0)


  **Returns:** ScopeBoundary
    ScopeBoundary with counts, complexity estimate, and gaps



---
