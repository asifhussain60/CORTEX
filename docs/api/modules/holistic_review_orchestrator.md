# holistic_review_orchestrator

Holistic Review Orchestrator - Quality gate validation and learning integration.

Provides comprehensive review of feature execution with quality gates,
recommendations, and learning library documentation.


## Table of Contents

### Classes
- [QualityGate](#qualitygate)
- [ReviewResult](#reviewresult)
- [HolisticReviewOrchestrator](#holisticrevieworchestrator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, typing


## Classes

### QualityGate

```python
class QualityGate
```

**Decorators:** `dataclass`

Quality gate evaluation result.


**Attributes:**

- `gate_name`: str
- `passed`: bool
- `score`: float
- `message`: str
- `metrics`: Dict[str, Any]



---

### ReviewResult

```python
class ReviewResult
```

**Decorators:** `dataclass`

Complete holistic review result.


**Attributes:**

- `overall_passed`: bool
- `gates`: List[QualityGate]
- `recommendations`: List[str]
- `lessons`: Dict[str, Any]
- `patterns`: List[str]


**Methods:**

  #### `failed_gates`

  *Decorators:* `property`

  ```python
  failed_gates(self) -> List[QualityGate]
  ```

  Get failed quality gates.

  **Parameters:**

  - `self`


  **Returns:** List[QualityGate]



---

### HolisticReviewOrchestrator

```python
class HolisticReviewOrchestrator
```

Orchestrates holistic review of feature execution.

Evaluates quality gates:
- Code quality (complexity, maintainability)
- Test coverage (>90% threshold)
- Documentation (docstrings, guides)

Integrates with:
- IncrementalPlanGenerator (Phase 4 auto-addition)
- Learning library (lessons learned documentation)


**Methods:**

  #### `evaluate_code_quality`

  ```python
  evaluate_code_quality(self, context: Dict[str, Any]) -> QualityGate
  ```

  Evaluate code quality metrics.

Args:
    context: Execution context with code metrics
    
Returns:
    QualityGate result

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with code metrics


  **Returns:** QualityGate
    QualityGate result


  #### `evaluate_test_coverage`

  ```python
  evaluate_test_coverage(self, context: Dict[str, Any]) -> QualityGate
  ```

  Evaluate test coverage metrics.

Args:
    context: Execution context with test metrics
    
Returns:
    QualityGate result

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with test metrics


  **Returns:** QualityGate
    QualityGate result


  #### `evaluate_documentation`

  ```python
  evaluate_documentation(self, context: Dict[str, Any]) -> QualityGate
  ```

  Evaluate documentation quality.

Args:
    context: Execution context with doc metrics
    
Returns:
    QualityGate result

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with doc metrics


  **Returns:** QualityGate
    QualityGate result


  #### `run_holistic_review`

  ```python
  run_holistic_review(self, context: Dict[str, Any]) -> ReviewResult
  ```

  Run complete holistic review.

Args:
    context: Execution context with all metrics
    
Returns:
    ReviewResult with gates, recommendations, lessons, patterns

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with all metrics


  **Returns:** ReviewResult
    ReviewResult with gates, recommendations, lessons, patterns


  #### `document_lessons_learned`

  ```python
  document_lessons_learned(self, result: ReviewResult) -> Dict[str, Any]
  ```

  Document lessons learned for learning library.

Args:
    result: ReviewResult from holistic review
    
Returns:
    Structured lessons dictionary

  **Parameters:**

  - `self`
  - `result` (ReviewResult): ReviewResult from holistic review


  **Returns:** Dict[str, Any]
    Structured lessons dictionary


  #### `document_lessons_learned_from_gates`

  ```python
  document_lessons_learned_from_gates(self, gates: List[QualityGate], context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Document lessons from gates and context.

  **Parameters:**

  - `self`
  - `gates` (List[QualityGate])
  - `context` (Dict[str, Any])


  **Returns:** Dict[str, Any]


  #### `extract_patterns`

  ```python
  extract_patterns(self, context: Dict[str, Any]) -> List[str]
  ```

  Extract reusable patterns from execution.

Args:
    context: Execution context
    
Returns:
    List of identified patterns

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context


  **Returns:** List[str]
    List of identified patterns



---
