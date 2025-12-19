# risk_assessor

Risk Assessor - Pre-execution impact analysis.

Analyzes proposed changes to identify potential breaking changes,
data loss risks, and security vulnerabilities before execution.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [RiskLevel](#risklevel)
- [RiskAssessment](#riskassessment)
- [RiskAssessor](#riskassessor)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, domain_classifier, enum, logging, pathlib, typing


## Classes

### RiskLevel

```python
class RiskLevel(Enum)
```

Risk severity levels.



---

### RiskAssessment

```python
class RiskAssessment
```

**Decorators:** `dataclass`

Risk assessment result.


**Attributes:**

- `risk_level`: RiskLevel
- `category`: str
- `description`: str
- `affected_components`: List[str]
- `mitigation_steps`: List[str]
- `requires_manual_review`: bool



---

### RiskAssessor

```python
class RiskAssessor
```

Assess execution risks before changes are applied.


**Methods:**

  #### `assess_risk`

  ```python
  assess_risk(self, operation: str, context: Dict[str, Any]) -> List[RiskAssessment]
  ```

  Assess risks of proposed operation.

Args:
    operation: Operation description
    context: Operation context (files, changes, etc.)
    
Returns:
    List of identified risks

  **Parameters:**

  - `self`
  - `operation` (str): Operation description
  - `context` (Dict[str, Any]): Operation context (files, changes, etc.)


  **Returns:** List[RiskAssessment]
    List of identified risks


  #### `should_block_execution`

  ```python
  should_block_execution(self, risks: List[RiskAssessment]) -> bool
  ```

  Determine if execution should be blocked based on risks.

Args:
    risks: List of risk assessments
    
Returns:
    True if execution should be blocked

  **Parameters:**

  - `self`
  - `risks` (List[RiskAssessment]): List of risk assessments


  **Returns:** bool
    True if execution should be blocked


  #### `format_risk_report`

  ```python
  format_risk_report(self, risks: List[RiskAssessment]) -> str
  ```

  Format risk assessments as markdown report.

Args:
    risks: List of risk assessments
    
Returns:
    Formatted markdown string

  **Parameters:**

  - `self`
  - `risks` (List[RiskAssessment]): List of risk assessments


  **Returns:** str
    Formatted markdown string



---
