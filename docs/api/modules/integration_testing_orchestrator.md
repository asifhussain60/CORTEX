# integration_testing_orchestrator

Integration Testing Orchestrator.


## Table of Contents

### Classes
- [TestEnvironment](#testenvironment)
- [TestResult](#testresult)
- [IntegrationTestingOrchestrator](#integrationtestingorchestrator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, typing


## Classes

### TestEnvironment

```python
class TestEnvironment
```

**Decorators:** `dataclass`

**Attributes:**

- `name`: str
- `active`: bool



---

### TestResult

```python
class TestResult
```

**Decorators:** `dataclass`

**Attributes:**

- `total_tests`: int
- `passed`: int
- `failed`: int



---

### IntegrationTestingOrchestrator

```python
class IntegrationTestingOrchestrator
```

**Methods:**

  #### `setup_environment`

  ```python
  setup_environment(self, name: str) -> TestEnvironment
  ```

  #### `execute_tests`

  ```python
  execute_tests(self, env: TestEnvironment, tests: List[str]) -> TestResult
  ```

  #### `teardown_environment`

  ```python
  teardown_environment(self, env: TestEnvironment) -> bool
  ```

  #### `aggregate_results`

  ```python
  aggregate_results(self, results: List[TestResult]) -> Dict[str, int]
  ```


---
