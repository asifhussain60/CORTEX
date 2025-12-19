# governance_engine

CORTEX Tier 0: Governance Engine
Enforces immutable governance rules and protects system integrity.


## Table of Contents

### Classes
- [Severity](#severity)
- [ViolationType](#violationtype)
- [GovernanceEngine](#governanceengine)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** datetime, enum, pathlib, src, typing, yaml


## Classes

### Severity

```python
class Severity(Enum)
```

Rule severity levels



---

### ViolationType

```python
class ViolationType(Enum)
```

Types of governance violations



---

### GovernanceEngine

```python
class GovernanceEngine
```

Tier 0 Governance Engine

Responsibilities:
- Load and validate governance rules
- Check for rule violations
- Create challenges for risky changes
- Validate Definition of Done/Ready
- Enforce tier boundaries


**Methods:**

  #### `get_rule`

  ```python
  get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]
  ```

  Get a governance rule by ID.

Args:
    rule_id: Rule identifier (e.g., 'TEST_FIRST_TDD')

Returns:
    Rule dictionary or None if not found

  **Parameters:**

  - `self`
  - `rule_id` (str): Rule identifier (e.g., 'TEST_FIRST_TDD')


  **Returns:** Optional[Dict[str, Any]]
    Rule dictionary or None if not found


  #### `get_all_rules`

  ```python
  get_all_rules(self) -> List[Dict[str, Any]]
  ```

  Get all governance rules.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]


  #### `get_rules_by_severity`

  ```python
  get_rules_by_severity(self, severity: Severity) -> List[Dict[str, Any]]
  ```

  Get all rules of a specific severity.

Args:
    severity: Severity level to filter by

Returns:
    List of rules matching the severity

  **Parameters:**

  - `self`
  - `severity` (Severity): Severity level to filter by


  **Returns:** List[Dict[str, Any]]
    List of rules matching the severity


  #### `check_tdd_violation`

  ```python
  check_tdd_violation(self, has_new_code: bool, has_new_test: bool, test_written_first: bool) -> Optional[Dict[str, Any]]
  ```

  Check for TDD (Test-First Development) violations.

Args:
    has_new_code: Whether new production code was added
    has_new_test: Whether new test was added
    test_written_first: Whether test was written before code

Returns:
    Violation details or None if no violation

  **Parameters:**

  - `self`
  - `has_new_code` (bool): Whether new production code was added
  - `has_new_test` (bool): Whether new test was added
  - `test_written_first` (bool): Whether test was written before code


  **Returns:** Optional[Dict[str, Any]]
    Violation details or None if no violation


  #### `validate_definition_of_done`

  ```python
  validate_definition_of_done(self, compilation_clean: bool, tests_pass: bool, new_tests_created: bool, tdd_cycle_complete: bool, code_formatted: bool, no_lint_violations: bool, docs_updated: bool, app_runs: bool, no_exceptions: bool, functionality_verified: bool) -> Dict[str, Any]
  ```

  Validate Definition of Done criteria.

Returns:
    Validation result with status and failed criteria

  **Parameters:**

  - `self`
  - `compilation_clean` (bool) = `True`
  - `tests_pass` (bool) = `True`
  - `new_tests_created` (bool) = `True`
  - `tdd_cycle_complete` (bool) = `True`
  - `code_formatted` (bool) = `True`
  - `no_lint_violations` (bool) = `True`
  - `docs_updated` (bool) = `True`
  - `app_runs` (bool) = `True`
  - `no_exceptions` (bool) = `True`
  - `functionality_verified` (bool) = `True`


  **Returns:** Dict[str, Any]
    Validation result with status and failed criteria


  #### `validate_definition_of_ready`

  ```python
  validate_definition_of_ready(self, user_story_clear: bool, acceptance_criteria_defined: bool, testable_outcomes: bool, scope_bounded: bool, dependencies_identified: bool, estimate_possible: bool, files_known: bool, architecture_clear: bool, no_blocking_dependencies: bool) -> Dict[str, Any]
  ```

  Validate Definition of Ready criteria.

Returns:
    Validation result with status and failed criteria

  **Parameters:**

  - `self`
  - `user_story_clear` (bool) = `True`
  - `acceptance_criteria_defined` (bool) = `True`
  - `testable_outcomes` (bool) = `True`
  - `scope_bounded` (bool) = `True`
  - `dependencies_identified` (bool) = `True`
  - `estimate_possible` (bool) = `True`
  - `files_known` (bool) = `True`
  - `architecture_clear` (bool) = `True`
  - `no_blocking_dependencies` (bool) = `True`


  **Returns:** Dict[str, Any]
    Validation result with status and failed criteria


  #### `check_tier_boundary_violation`

  ```python
  check_tier_boundary_violation(self, tier: int, data_type: str) -> Optional[Dict[str, Any]]
  ```

  Check if data is in the correct tier.

Args:
    tier: Tier number (0-3)
    data_type: Type of data (e.g., 'conversation', 'pattern', 'governance')

Returns:
    Violation details or None if no violation

  **Parameters:**

  - `self`
  - `tier` (int): Tier number (0-3)
  - `data_type` (str): Type of data (e.g., 'conversation', 'pattern', 'governance')


  **Returns:** Optional[Dict[str, Any]]
    Violation details or None if no violation


  #### `create_challenge`

  ```python
  create_challenge(self, proposed_change: str, risks: List[str], alternatives: Optional[List[str]]) -> Dict[str, Any]
  ```

  Create a challenge for a risky user-proposed change.

Args:
    proposed_change: Description of what user wants to change
    risks: List of identified risks
    alternatives: Optional list of safer alternatives

Returns:
    Challenge details to present to user

  **Parameters:**

  - `self`
  - `proposed_change` (str): Description of what user wants to change
  - `risks` (List[str]): List of identified risks
  - `alternatives` (Optional[List[str]]) = `None`: Optional list of safer alternatives


  **Returns:** Dict[str, Any]
    Challenge details to present to user


  #### `get_violations`

  ```python
  get_violations(self, severity: Optional[Severity], limit: Optional[int]) -> List[Dict[str, Any]]
  ```

  Get logged violations.

Args:
    severity: Filter by severity level
    limit: Maximum number of violations to return

Returns:
    List of violations

  **Parameters:**

  - `self`
  - `severity` (Optional[Severity]) = `None`: Filter by severity level
  - `limit` (Optional[int]) = `None`: Maximum number of violations to return


  **Returns:** List[Dict[str, Any]]
    List of violations


  #### `clear_violations`

  ```python
  clear_violations(self) -> None
  ```

  Clear the violations log.

  **Parameters:**

  - `self`


  **Returns:** None



---
