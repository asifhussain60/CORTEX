# onboarding_orchestrator

Onboarding Orchestrator

Manages application onboarding workflow including analysis and dashboard data generation.
Triggered when CORTEX onboards a new user application.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [OnboardingResult](#onboardingresult)
- [OnboardingOrchestrator](#onboardingorchestrator)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** agents, argparse, dataclasses, datetime, graphviz, json, logging, operations, pathlib, plugins, src, sys, time, traceback, typing, use_cases


## Classes

### OnboardingResult

```python
class OnboardingResult
```

**Decorators:** `dataclass`

Result of application onboarding.


**Attributes:**

- `success`: bool
- `project_name`: str
- `analysis_timestamp`: str
- `quality_score`: float
- `security_issues`: int
- `performance_metrics`: int
- `dashboard_url`: str
- `errors`: List[str]
- `output_path`: Optional[Path]



---

### OnboardingOrchestrator

```python
class OnboardingOrchestrator
```

Orchestrates application onboarding workflow.

Workflow:
1. Analyze application (CodeQualityAnalyzer, SecurityScanner, PerformanceMetrics)
2. Transform analyzer outputs to dashboard format (DashboardDataAdapter)
3. Generate dashboard data files
4. Provide dashboard URL to user

Modes:
- Production mode (test_mode=False): Embedded in user repo, standard output paths
- Testing mode (test_mode=True): Standalone CORTEX testing external repos,
  outputs to cortex-brain/documents/onboarded-apps/{project-name}/


**Methods:**

  #### `onboard_application`

  ```python
  onboard_application(self, project_path: Path, project_name: Optional[str]) -> OnboardingResult
  ```

  Onboard user application with full analysis and dashboard generation.

Args:
    project_path: Path to user application to analyze
    project_name: Optional project name (defaults to directory name)

Returns:
    OnboardingResult with success status and dashboard URL

  **Parameters:**

  - `self`
  - `project_path` (Path): Path to user application to analyze
  - `project_name` (Optional[str]) = `None`: Optional project name (defaults to directory name)


  **Returns:** OnboardingResult
    OnboardingResult with success status and dashboard URL



---

## Functions

### main

```python
main()
```

CLI entry point for testing.


---
