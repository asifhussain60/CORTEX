# planning_intelligence_coordinator

Planning Intelligence Coordinator
Combines complexity analysis with test value scoring for intelligent planning decisions.

Purpose:
    Coordinates ComplexityAnalyzer (planning tier routing) with TestValueScorer
    (test necessity) to provide comprehensive planning recommendations.

Decision Matrix:
    HIGH Complexity + CRITICAL Test Value → Incremental + Full TDD
    HIGH Complexity + LOW Test Value → Incremental + Skip Tests
    LOW Complexity + CRITICAL Test Value → Skeleton + Targeted Tests
    LOW Complexity + LOW Test Value → Direct Execution + No Tests

Author: Asif Hussain
Date: December 2024
Version: 1.0.0


## Table of Contents

### Classes
- [PlanningMode](#planningmode)
- [TestStrategy](#teststrategy)
- [PlanningDecision](#planningdecision)
- [PlanningIntelligenceCoordinator](#planningintelligencecoordinator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, enum, json, logging, pathlib, src, sys, typing


## Classes

### PlanningMode

```python
class PlanningMode(Enum)
```

Recommended planning execution mode



---

### TestStrategy

```python
class TestStrategy(Enum)
```

Test generation strategy



---

### PlanningDecision

```python
class PlanningDecision
```

**Decorators:** `dataclass`

Comprehensive planning recommendation


**Attributes:**

- `planning_mode`: PlanningMode
- `test_strategy`: TestStrategy
- `complexity_score`: ComplexityScore
- `test_value_score`: Optional[TestValueScore]
- `rationale`: List[str]
- `recommendation`: str
- `estimated_hours`: Tuple[float, float]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### PlanningIntelligenceCoordinator

```python
class PlanningIntelligenceCoordinator
```

Coordinates complexity analysis and test value scoring for planning decisions.

Workflow:
    1. User provides feature request
    2. Analyze planning complexity (ComplexityAnalyzer)
    3. If code exists, analyze test value (TestValueScorer)
    4. Combine scores to recommend planning mode + test strategy
    5. Provide time estimates based on combined analysis

Decision Matrix:
    ┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐
    │ Complexity      │ CRITICAL Tests   │ HIGH/MEDIUM Tests│ LOW/TRIVIAL Tests│
    ├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
    │ CRITICAL/HIGH   │ Incremental+Full │ Incremental+Some │ Incremental+Skip │
    │ MEDIUM          │ Skeleton+Targeted│ Skeleton+Targeted│ Skeleton+Skip    │
    │ LOW/TRIVIAL     │ Skeleton+Targeted│ Direct+Skip      │ Direct+Skip      │
    └─────────────────┴──────────────────┴──────────────────┴──────────────────┘

Integration:
    - Called by Planning Orchestrator before execution
    - Informs TDD Orchestrator whether to generate tests
    - Used by response templates to explain decisions


**Methods:**

  #### `analyze_request`

  ```python
  analyze_request(self, user_request: str, codebase_context: Optional[Dict], target_files: Optional[List[Path]]) -> PlanningDecision
  ```

  Analyze user request and determine optimal planning approach.

Args:
    user_request: User's feature request or task description
    codebase_context: Optional AST analysis results (file count, dependencies, etc.)
    target_files: Optional list of files to be modified (for test value scoring)

Returns:
    PlanningDecision with mode, test strategy, and rationale

Example:
    >>> coordinator = PlanningIntelligenceCoordinator()
    >>> decision = coordinator.analyze_request(
    ...     "Add JWT authentication to API",
    ...     target_files=[Path("src/auth/jwt_handler.py")]
    ... )
    >>> print(decision.planning_mode)  # INCREMENTAL_FULL_TDD
    >>> print(decision.test_strategy)  # FULL_SUITE

  **Parameters:**

  - `self`
  - `user_request` (str): User's feature request or task description
  - `codebase_context` (Optional[Dict]) = `None`: Optional AST analysis results (file count, dependencies, etc.)
  - `target_files` (Optional[List[Path]]) = `None`: Optional list of files to be modified (for test value scoring)


  **Returns:** PlanningDecision
    PlanningDecision with mode, test strategy, and rationale



---
