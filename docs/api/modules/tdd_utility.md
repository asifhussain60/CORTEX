# tdd_utility

TDD Utility

Fast, lightweight Test-Driven Development workflow management.
Replaces heavy orchestrator (602 lines) with focused utility (~400 lines).

Core Operations:
- State machine (RED → GREEN → REFACTOR → COMPLETE)
- Test execution and validation
- Test file generation
- Implementation tracking

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [TDDPhase](#tddphase)
- [TDDResult](#tddresult)
- [TDDSession](#tddsession)

### Functions
- [start_tdd_session](#start_tdd_session)
- [run_tests](#run_tests)
- [transition_phase](#transition_phase)
- [get_session_status](#get_session_status)
- [generate_test_skeleton](#generate_test_skeleton)
- [update_session_metrics](#update_session_metrics)
- [complete_session](#complete_session)


## Overview

- **Classes:** 3
- **Functions:** 7
- **Dependencies:** dataclasses, datetime, enum, json, logging, pathlib, src, subprocess, typing


## Classes

### TDDPhase

```python
class TDDPhase(Enum)
```

TDD cycle phases.



---

### TDDResult

```python
class TDDResult
```

**Decorators:** `dataclass`

Result of TDD operation.


**Attributes:**

- `success`: bool
- `message`: str
- `phase`: TDDPhase
- `test_passed`: Optional[bool]
- `test_output`: Optional[str]
- `details`: Optional[str]
- `errors`: List[str]



---

### TDDSession

```python
class TDDSession
```

**Decorators:** `dataclass`

TDD session state.


**Attributes:**

- `session_id`: str
- `feature_name`: str
- `test_file`: Path
- `impl_file`: Path
- `current_phase`: TDDPhase
- `tests_written`: int
- `tests_passing`: int
- `created_at`: str
- `updated_at`: str



---

## Functions

### start_tdd_session

```python
start_tdd_session(feature_name: str, test_file: Path, impl_file: Path) -> TDDResult
```

Start new TDD session.

Args:
    feature_name: Name of feature being developed
    test_file: Path to test file
    impl_file: Path to implementation file
    
Returns:
    TDDResult with session creation outcome


**Parameters:**

- `feature_name` (str): Name of feature being developed
- `test_file` (Path): Path to test file
- `impl_file` (Path): Path to implementation file


**Returns:** TDDResult
  TDDResult with session creation outcome


---

### run_tests

```python
run_tests(test_file: Path, test_name: Optional[str]) -> TDDResult
```

Run tests and return results.

Args:
    test_file: Path to test file
    test_name: Optional specific test to run
    
Returns:
    TDDResult with test execution outcome


**Parameters:**

- `test_file` (Path): Path to test file
- `test_name` (Optional[str]) = `None`: Optional specific test to run


**Returns:** TDDResult
  TDDResult with test execution outcome


---

### transition_phase

```python
transition_phase(session_id: str, target_phase: TDDPhase, validation: bool) -> TDDResult
```

Transition TDD session to new phase.

Args:
    session_id: Session identifier
    target_phase: Phase to transition to
    validation: Whether to validate transition is legal
    
Returns:
    TDDResult with transition outcome


**Parameters:**

- `session_id` (str): Session identifier
- `target_phase` (TDDPhase): Phase to transition to
- `validation` (bool) = `True`: Whether to validate transition is legal


**Returns:** TDDResult
  TDDResult with transition outcome


---

### get_session_status

```python
get_session_status(session_id: str) -> TDDResult
```

Get current TDD session status.

Args:
    session_id: Session identifier
    
Returns:
    TDDResult with session status


**Parameters:**

- `session_id` (str): Session identifier


**Returns:** TDDResult
  TDDResult with session status


---

### generate_test_skeleton

```python
generate_test_skeleton(feature_name: str, test_file: Path, impl_file: Path) -> TDDResult
```

Generate test file skeleton.

Args:
    feature_name: Name of feature
    test_file: Path to test file
    impl_file: Path to implementation file
    
Returns:
    TDDResult with skeleton generation outcome


**Parameters:**

- `feature_name` (str): Name of feature
- `test_file` (Path): Path to test file
- `impl_file` (Path): Path to implementation file


**Returns:** TDDResult
  TDDResult with skeleton generation outcome


---

### update_session_metrics

```python
update_session_metrics(session_id: str, tests_written: Optional[int], tests_passing: Optional[int]) -> TDDResult
```

Update TDD session metrics.

Args:
    session_id: Session identifier
    tests_written: Number of tests written (optional)
    tests_passing: Number of tests passing (optional)
    
Returns:
    TDDResult with update outcome


**Parameters:**

- `session_id` (str): Session identifier
- `tests_written` (Optional[int]) = `None`: Number of tests written (optional)
- `tests_passing` (Optional[int]) = `None`: Number of tests passing (optional)


**Returns:** TDDResult
  TDDResult with update outcome


---

### complete_session

```python
complete_session(session_id: str) -> TDDResult
```

Complete TDD session.

Args:
    session_id: Session identifier
    
Returns:
    TDDResult with completion outcome


**Parameters:**

- `session_id` (str): Session identifier


**Returns:** TDDResult
  TDDResult with completion outcome


---
