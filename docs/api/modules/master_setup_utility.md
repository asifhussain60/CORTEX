# master_setup_utility

Master Setup Utility - Complete CORTEX Setup and Onboarding Operations

Coordinates complete CORTEX setup workflow with project detection, dependency
installation, policy validation, and completion reporting.

Part of CORTEX 3.2.1 - Setup and Onboarding System
Sprint 11 Migration: master_setup_orchestrator (666 lines) → master_setup_utility (~800 lines)
Author: Asif Hussain

Operations:
- detect_project_structure: Analyze project language, framework, build system
- request_user_consent: Interactive consent workflow for setup steps
- install_dependencies: Install CORTEX dependencies with venv management
- validate_policies: Scan and validate project policies
- setup_gitignore: Configure .gitignore to exclude CORTEX/
- generate_copilot_instructions: Create .github/copilot-instructions.md
- create_completion_report: Generate setup completion report with metrics


## Table of Contents

### Classes
- [ProjectDetection](#projectdetection)
- [UserConsent](#userconsent)
- [DependencyInstallation](#dependencyinstallation)
- [PolicyValidation](#policyvalidation)
- [GitIgnoreSetup](#gitignoresetup)
- [SetupResult](#setupresult)

### Functions
- [detect_project_structure](#detect_project_structure)
- [request_user_consent](#request_user_consent)
- [install_dependencies](#install_dependencies)
- [validate_policies](#validate_policies)
- [setup_gitignore](#setup_gitignore)
- [generate_copilot_instructions](#generate_copilot_instructions)
- [create_completion_report](#create_completion_report)


## Overview

- **Classes:** 6
- **Functions:** 9
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, shutil, src, subprocess, sys, tempfile, time, typing


## Classes

### ProjectDetection

```python
class ProjectDetection
```

**Decorators:** `dataclass`

Project structure detection result.


**Attributes:**

- `language`: str
- `framework`: str
- `build_system`: str
- `test_framework`: str
- `files`: int
- `estimated_time`: str
- `metadata`: Dict[str, Any]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### UserConsent

```python
class UserConsent
```

**Decorators:** `dataclass`

User consent for setup steps.


**Attributes:**

- `approved_steps`: List[str]
- `skipped_steps`: List[str]
- `action`: str
- `metadata`: Dict[str, Any]


**Methods:**

  #### `is_step_approved`

  ```python
  is_step_approved(self, step_id: str) -> bool
  ```

  Check if step was approved

  **Parameters:**

  - `self`
  - `step_id` (str)


  **Returns:** bool


  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### DependencyInstallation

```python
class DependencyInstallation
```

**Decorators:** `dataclass`

Dependency installation result.


**Attributes:**

- `success`: bool
- `python_version`: str
- `installed_packages`: List[str]
- `venv_created`: bool
- `venv_path`: Optional[str]
- `errors`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### PolicyValidation

```python
class PolicyValidation
```

**Decorators:** `dataclass`

Policy validation result.


**Attributes:**

- `success`: bool
- `compliant`: bool
- `compliance_percentage`: float
- `total_rules`: int
- `passed`: int
- `failed`: int
- `violations`: List[Dict[str, Any]]
- `report_path`: Optional[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### GitIgnoreSetup

```python
class GitIgnoreSetup
```

**Decorators:** `dataclass`

GitIgnore setup result.


**Attributes:**

- `success`: bool
- `action`: str
- `path`: str
- `error`: Optional[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### SetupResult

```python
class SetupResult
```

**Decorators:** `dataclass`

Complete setup result.


**Attributes:**

- `success`: bool
- `phase_results`: Dict[str, Any]
- `setup_time`: float
- `completion_report_path`: Optional[str]
- `errors`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for reporting

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### detect_project_structure

```python
detect_project_structure(project_root: Path, deep_scan: bool) -> ProjectDetection
```

Analyze project to detect language, framework, and build system.

Scans for project files (package.json, requirements.txt, pom.xml, etc.)
and determines project characteristics.

Args:
    project_root: Project root directory to analyze
    deep_scan: If True, performs deeper analysis (slower)

Returns:
    ProjectDetection with language, framework, build system details

Example:
    >>> detection = detect_project_structure(Path("/path/to/project"))
    >>> detection.language
    'Python'
    >>> detection.framework
    'Django'


**Parameters:**

- `project_root` (Path): Project root directory to analyze
- `deep_scan` (bool) = `False`: If True, performs deeper analysis (slower)


**Returns:** ProjectDetection
  ProjectDetection with language, framework, build system details


---

### request_user_consent

```python
request_user_consent(project_name: str, detection: ProjectDetection, interactive: bool, available_steps: Optional[List[str]]) -> UserConsent
```

Request user consent for setup steps.

In interactive mode, prompts user to approve/skip individual steps.
In non-interactive mode, approves all steps by default.

Args:
    project_name: Name of project being set up
    detection: ProjectDetection result with project details
    interactive: If True, prompts user for consent
    available_steps: List of step IDs to request consent for
        Default: ["dependencies", "policy_validation", "realignment", "gitignore"]

Returns:
    UserConsent with approved/skipped steps

Example:
    >>> consent = request_user_consent("my-project", detection, interactive=True)
    >>> consent.is_step_approved("dependencies")
    True


**Parameters:**

- `project_name` (str): Name of project being set up
- `detection` (ProjectDetection): ProjectDetection result with project details
- `interactive` (bool) = `True`: If True, prompts user for consent
- `available_steps` (Optional[List[str]]) = `None`: List of step IDs to request consent for


**Returns:** UserConsent
  UserConsent with approved/skipped steps


---

### install_dependencies

```python
install_dependencies(cortex_root: Path, force_reinstall: bool) -> DependencyInstallation
```

Install CORTEX dependencies with virtual environment management.

Creates/activates virtual environment and installs required packages
from requirements.txt.

Args:
    cortex_root: CORTEX installation root directory
    force_reinstall: If True, reinstalls even if already installed

Returns:
    DependencyInstallation with success status and details

Example:
    >>> result = install_dependencies(Path("/path/to/CORTEX"))
    >>> result.success
    True
    >>> result.venv_created
    True


**Parameters:**

- `cortex_root` (Path): CORTEX installation root directory
- `force_reinstall` (bool) = `False`: If True, reinstalls even if already installed


**Returns:** DependencyInstallation
  DependencyInstallation with success status and details


---

### validate_policies

```python
validate_policies(project_root: Path, cortex_root: Path, create_starter: bool) -> PolicyValidation
```

Scan and validate project policies.

Searches for policy documents and validates code against policies
using PolicyScanner and PolicyValidator.

Args:
    project_root: Project root directory to validate
    cortex_root: CORTEX installation root
    create_starter: If True and no policies found, creates starter template

Returns:
    PolicyValidation with compliance metrics and violations

Example:
    >>> result = validate_policies(Path("/path/to/project"), Path("/path/to/CORTEX"))
    >>> result.compliance_percentage
    85.5
    >>> result.compliant
    False


**Parameters:**

- `project_root` (Path): Project root directory to validate
- `cortex_root` (Path): CORTEX installation root
- `create_starter` (bool) = `False`: If True and no policies found, creates starter template


**Returns:** PolicyValidation
  PolicyValidation with compliance metrics and violations


---

### setup_gitignore

```python
setup_gitignore(project_root: Path, patterns: Optional[List[str]]) -> GitIgnoreSetup
```

Configure .gitignore to exclude CORTEX/ directory.

Creates or updates .gitignore file to exclude CORTEX directory
from version control.

Args:
    project_root: Project root directory
    patterns: Additional patterns to add (default: ["CORTEX/"])

Returns:
    GitIgnoreSetup with success status and action taken

Example:
    >>> result = setup_gitignore(Path("/path/to/project"))
    >>> result.success
    True
    >>> result.action
    'appended'


**Parameters:**

- `project_root` (Path): Project root directory
- `patterns` (Optional[List[str]]) = `None`: Additional patterns to add (default: ["CORTEX/"])


**Returns:** GitIgnoreSetup
  GitIgnoreSetup with success status and action taken


---

### generate_copilot_instructions

```python
generate_copilot_instructions(project_root: Path, project_name: str, detection: ProjectDetection, force: bool, enable_code_analysis: bool) -> Dict[str, Any]
```

Generate .github/copilot-instructions.md for project.

**CORTEX 3.9.0 Enhancement:** Two-tier AST scanning strategy
- TIER 1 (Setup): Lightweight pattern detection (<3s)
- TIER 2 (Onboarding): Deep analysis via dashboard collectors (30-60s)

Creates GitHub Copilot instructions file with project-specific context,
CORTEX integration guidelines, and detected domain patterns.

Args:
    project_root: Project root directory
    project_name: Name of project
    detection: ProjectDetection with project details
    force: If True, overwrites existing instructions
    enable_code_analysis: If True, run TIER 1 pattern detection

Returns:
    Dictionary with success status, file path, and merge details

Example:
    >>> result = generate_copilot_instructions(
    ...     Path("/path/to/project"),
    ...     "my-project",
    ...     detection,
    ...     enable_code_analysis=True
    ... )
    >>> result["success"]
    True
    >>> result["patterns_detected"]
    4


**Parameters:**

- `project_root` (Path): Project root directory
- `project_name` (str): Name of project
- `detection` (ProjectDetection): ProjectDetection with project details
- `force` (bool) = `False`: If True, overwrites existing instructions
- `enable_code_analysis` (bool) = `True`: If True, run TIER 1 pattern detection


**Returns:** Dict[str, Any]
  Dictionary with success status, file path, and merge details


---

### create_completion_report

```python
create_completion_report(project_name: str, cortex_root: Path, phase_results: Dict[str, Any], start_time: datetime, setup_success: bool) -> str
```

Create setup completion report with all phase results.

Generates comprehensive Markdown report documenting setup process,
phase results, and next steps.

Args:
    project_name: Name of project that was set up
    cortex_root: CORTEX installation root
    phase_results: Dictionary with all phase results
    start_time: Setup start timestamp
    setup_success: Overall setup success status

Returns:
    Path to created report file

Example:
    >>> report_path = create_completion_report(
    ...     "my-project",
    ...     Path("/path/to/CORTEX"),
    ...     phase_results,
    ...     datetime.now()
    ... )
    >>> Path(report_path).exists()
    True


**Parameters:**

- `project_name` (str): Name of project that was set up
- `cortex_root` (Path): CORTEX installation root
- `phase_results` (Dict[str, Any]): Dictionary with all phase results
- `start_time` (datetime): Setup start timestamp
- `setup_success` (bool) = `True`: Overall setup success status


**Returns:** str
  Path to created report file


---
