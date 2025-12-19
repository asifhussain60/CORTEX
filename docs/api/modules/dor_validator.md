# dor_validator

CORTEX DoR (Definition of Ready) Validator

Validates that feature requirements meet the Definition of Ready (DoR) checklist
before allowing timeframe estimates. CORTEX NEVER provides estimates without complete DoR.

Author: Asif Hussain
Copyright: (c) 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [DoRStatus](#dorstatus)
- [DoRCriterion](#dorcriterion)
- [DoRCriterionStatus](#dorcriterionstatus)
- [DoRValidationResult](#dorvalidationresult)
- [DoRValidator](#dorvalidator)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, re, typing


## Classes

### DoRStatus

```python
class DoRStatus(Enum)
```

Status of DoR validation



---

### DoRCriterion

```python
class DoRCriterion(Enum)
```

DoR checklist criteria (8 items from planning guide)



---

### DoRCriterionStatus

```python
class DoRCriterionStatus
```

**Decorators:** `dataclass`

Status of a single DoR criterion


**Attributes:**

- `criterion`: DoRCriterion
- `satisfied`: bool
- `evidence`: str
- `notes`: str
- `clarifying_question`: str



---

### DoRValidationResult

```python
class DoRValidationResult
```

**Decorators:** `dataclass`

Result of DoR validation


**Attributes:**

- `status`: DoRStatus
- `criteria`: Dict[DoRCriterion, DoRCriterionStatus]
- `missing_count`: int
- `complete_count`: int
- `total_count`: int
- `can_estimate`: bool
- `blocking_reason`: str
- `clarifying_questions`: List[str]
- `timestamp`: str


**Methods:**

  #### `completion_percentage`

  *Decorators:* `property`

  ```python
  completion_percentage(self) -> float
  ```

  Calculate completion percentage

  **Parameters:**

  - `self`


  **Returns:** float


  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### DoRValidator

```python
class DoRValidator
```

Validates Definition of Ready (DoR) before allowing timeframe estimates.

CRITICAL: CORTEX NEVER provides estimates if DoR is not complete.

DoR Checklist (8 items):
1. Requirements documented with zero ambiguity
2. All vague terms replaced with specific metrics
3. Dependencies identified and validated
4. Technical design approach agreed upon
5. Test strategy defined
6. Acceptance criteria are measurable
7. Security review completed (OWASP checklist)
8. User approval on scope and approach


**Methods:**

  #### `validate_dor`

  ```python
  validate_dor(self, requirements: str, context: Optional[Dict[str, Any]]) -> DoRValidationResult
  ```

  Validate requirements against DoR checklist.

Args:
    requirements: Feature requirements text
    context: Optional context dict with additional info:
        - dependencies: List of known dependencies
        - acceptance_criteria: List of AC items
        - security_notes: Security review notes
        - user_approved: Boolean for user approval
        - technical_design: Design notes
        - test_strategy: Test strategy notes

Returns:
    DoRValidationResult with status and missing items

  **Parameters:**

  - `self`
  - `requirements` (str): Feature requirements text
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context dict with additional info:


  **Returns:** DoRValidationResult
    DoRValidationResult with status and missing items


  #### `get_dor_checklist_display`

  ```python
  get_dor_checklist_display(self, result: DoRValidationResult) -> str
  ```

  Generate formatted DoR checklist display.

Args:
    result: DoRValidationResult from validate_dor()

Returns:
    Formatted markdown string showing checklist status

  **Parameters:**

  - `self`
  - `result` (DoRValidationResult): DoRValidationResult from validate_dor()


  **Returns:** str
    Formatted markdown string showing checklist status


  #### `is_ready_for_estimation`

  ```python
  is_ready_for_estimation(self, result: DoRValidationResult) -> bool
  ```

  Check if DoR validation allows estimation

  **Parameters:**

  - `self`
  - `result` (DoRValidationResult)


  **Returns:** bool


  #### `get_missing_criteria`

  ```python
  get_missing_criteria(self, result: DoRValidationResult) -> List[str]
  ```

  Get list of missing criteria labels

  **Parameters:**

  - `self`
  - `result` (DoRValidationResult)


  **Returns:** List[str]


  #### `get_clarifying_questions`

  ```python
  get_clarifying_questions(self, result: DoRValidationResult) -> List[str]
  ```

  Get list of clarifying questions for missing criteria

  **Parameters:**

  - `self`
  - `result` (DoRValidationResult)


  **Returns:** List[str]


  #### `update_criterion`

  ```python
  update_criterion(self, criterion: DoRCriterion, satisfied: bool, evidence: str, notes: str) -> None
  ```

  Manually update a criterion status (after user provides answer).

Args:
    criterion: The DoR criterion to update
    satisfied: Whether the criterion is now satisfied
    evidence: Evidence supporting the status
    notes: Additional notes

  **Parameters:**

  - `self`
  - `criterion` (DoRCriterion): The DoR criterion to update
  - `satisfied` (bool): Whether the criterion is now satisfied
  - `evidence` (str) = `''`: Evidence supporting the status
  - `notes` (str) = `''`: Additional notes


  **Returns:** None


  #### `revalidate`

  ```python
  revalidate(self) -> DoRValidationResult
  ```

  Re-run validation with current criteria status

  **Parameters:**

  - `self`


  **Returns:** DoRValidationResult



---
