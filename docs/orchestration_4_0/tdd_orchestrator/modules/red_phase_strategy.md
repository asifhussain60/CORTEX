# red_phase_strategy

CORTEX 4.0 TDD Orchestrator - RED Phase Strategy

Purpose: Generate comprehensive failing tests (RED phase)
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19

Features:
- Edge case analysis
- Domain knowledge integration from Tier 2
- AI-driven test generation
- Parametrized and property-based testing
- Vision API integration for UI testing


## Table of Contents

### Classes
- [REDPhaseStrategy](#redphasestrategy)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, tdd_orchestrator_v4, typing


## Classes

### REDPhaseStrategy

```python
class REDPhaseStrategy(TDDPhaseStrategy)
```

RED Phase: Generate comprehensive tests that MUST fail.

Workflow:
1. Validate DoR (feature defined, no existing tests)
2. Analyze feature requirements
3. Extract edge cases (null, empty, boundaries, errors)
4. Query Tier 2 for domain patterns
5. Generate test suite (unit + parametrized + property-based)
6. Run tests (MUST fail - RED validation)
7. Create git checkpoint
8. Update documentation
9. Feed patterns to brain


**Methods:**

  #### `validate_dor`

  ```python
  validate_dor(self, context: Dict[str, Any]) -> ValidationResult
  ```

  RED DoR Checklist:
- Feature name defined
- Acceptance criteria provided
- No existing tests for this feature
- Git working directory clean
- Test framework detected

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** ValidationResult


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> PhaseResult
  ```

  Execute RED phase test generation.

Returns: PhaseResult with test file, test count, and metrics

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** PhaseResult


  #### `validate_dod`

  ```python
  validate_dod(self, context: Dict[str, Any]) -> ValidationResult
  ```

  RED DoD Checklist:
- Test file created
- Tests run successfully (framework works)
- ALL tests FAIL (RED validation)
- Git checkpoint created
- Documentation generated
- At least 1 edge case covered

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** ValidationResult


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback RED phase changes.

Actions:
- Delete generated test file
- Revert git commit
- Clean up documentation

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool



---
