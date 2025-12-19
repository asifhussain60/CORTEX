# alignment_models

System Alignment Data Models

Data classes for system alignment validation and reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: IMPLEMENTATION


## Table of Contents

### Classes
- [IntegrationScore](#integrationscore)
- [RemediationSuggestion](#remediationsuggestion)
- [AlignmentReport](#alignmentreport)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, src, typing


## Classes

### IntegrationScore

```python
class IntegrationScore
```

**Decorators:** `dataclass`

Integration depth score for a feature (0-100%).


**Attributes:**

- `feature_name`: str
- `feature_type`: str
- `discovered`: bool
- `imported`: bool
- `instantiated`: bool
- `documented`: bool
- `tested`: bool
- `wired`: bool
- `optimized`: bool


**Methods:**

  #### `score`

  *Decorators:* `property`

  ```python
  score(self) -> int
  ```

  Calculate 0-100 integration score.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `status`

  *Decorators:* `property`

  ```python
  status(self) -> str
  ```

  Get status text based on score.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `issues`

  *Decorators:* `property`

  ```python
  issues(self) -> List[str]
  ```

  List integration issues.

  **Parameters:**

  - `self`


  **Returns:** List[str]



---

### RemediationSuggestion

```python
class RemediationSuggestion
```

**Decorators:** `dataclass`

Auto-remediation suggestion for a feature.


**Attributes:**

- `feature_name`: str
- `suggestion_type`: str
- `content`: str
- `file_path`: Optional[str]



---

### AlignmentReport

```python
class AlignmentReport
```

**Decorators:** `dataclass`

System alignment validation report.


**Attributes:**

- `timestamp`: datetime
- `overall_health`: int
- `critical_issues`: int
- `warnings`: int
- `feature_scores`: Dict[str, IntegrationScore]
- `remediation_suggestions`: List[RemediationSuggestion]
- `orphaned_triggers`: List[str]
- `ghost_features`: List[str]
- `deployment_gate_results`: Optional[Dict[str, Any]]
- `package_purity_results`: Optional[Dict[str, Any]]
- `suggestions`: List[Dict[str, str]]
- `organization_violations`: List[Any]
- `organization_score`: int
- `header_violations`: List[Any]
- `header_compliance_score`: int
- `doc_governance_violations`: List[Any]
- `doc_governance_score`: int
- `conflicts`: List[Conflict]
- `fix_templates`: List[FixTemplate]
- `dashboard_report`: Optional[str]


**Methods:**

  #### `is_healthy`

  *Decorators:* `property`

  ```python
  is_healthy(self) -> bool
  ```

  Check if system is healthy (>80% overall).

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `has_warnings`

  *Decorators:* `property`

  ```python
  has_warnings(self) -> bool
  ```

  Check if system has non-critical warnings.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `has_errors`

  *Decorators:* `property`

  ```python
  has_errors(self) -> bool
  ```

  Check if system has critical errors.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `issues_found`

  *Decorators:* `property`

  ```python
  issues_found(self) -> int
  ```

  Total issues (critical + warnings).

  **Parameters:**

  - `self`


  **Returns:** int



---
