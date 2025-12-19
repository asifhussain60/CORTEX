# code_quality_orchestrator

Code Quality Orchestrator.

Provides code review, complexity analysis, and quality scoring.


## Table of Contents

### Classes
- [CodeReviewReport](#codereviewreport)
- [ComplexityReport](#complexityreport)
- [QualityScorecard](#qualityscorecard)
- [CodeQualityOrchestrator](#codequalityorchestrator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** ast, dataclasses, re, typing


## Classes

### CodeReviewReport

```python
class CodeReviewReport
```

**Decorators:** `dataclass`

Code review report.


**Attributes:**

- `issues`: List[Dict[str, Any]]
- `warnings`: int
- `complexity_warnings`: int



---

### ComplexityReport

```python
class ComplexityReport
```

**Decorators:** `dataclass`

Code complexity report.


**Attributes:**

- `functions`: List[Dict[str, Any]]
- `avg_complexity`: float



---

### QualityScorecard

```python
class QualityScorecard
```

**Decorators:** `dataclass`

Quality scorecard.


**Attributes:**

- `overall_score`: int
- `complexity_score`: int
- `style_score`: int
- `recommendations`: List[str]



---

### CodeQualityOrchestrator

```python
class CodeQualityOrchestrator
```

Orchestrator for code quality analysis.


**Methods:**

  #### `run_code_review`

  ```python
  run_code_review(self, source_code: str) -> CodeReviewReport
  ```

  Run automated code review.

  **Parameters:**

  - `self`
  - `source_code` (str)


  **Returns:** CodeReviewReport


  #### `analyze_complexity`

  ```python
  analyze_complexity(self, source_code: str) -> ComplexityReport
  ```

  Analyze code complexity.

  **Parameters:**

  - `self`
  - `source_code` (str)


  **Returns:** ComplexityReport


  #### `generate_scorecard`

  ```python
  generate_scorecard(self, source_code: str) -> QualityScorecard
  ```

  Generate quality scorecard.

  **Parameters:**

  - `self`
  - `source_code` (str)


  **Returns:** QualityScorecard



---
