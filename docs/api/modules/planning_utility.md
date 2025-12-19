# planning_utility

Planning Utility

Fast, lightweight planning management for feature planning workflows.
Replaces heavy orchestrator (2,693 lines) with focused utility (~800 lines).

Core Operations:
- Create plan with metadata
- Load/Save YAML plans
- Validate plans (DoR/DoD)
- Generate Markdown views
- Approve/Complete lifecycle

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [PlanResult](#planresult)
- [ValidationResult](#validationresult)

### Functions
- [detect_execution_mode](#detect_execution_mode)
- [analyze_risks](#analyze_risks)
- [detect_plan_complexity](#detect_plan_complexity)
- [create_plan](#create_plan)
- [load_plan](#load_plan)
- [save_plan](#save_plan)
- [validate_plan](#validate_plan)
- [generate_markdown](#generate_markdown)
- [approve_plan](#approve_plan)
- [complete_plan](#complete_plan)


## Overview

- **Classes:** 2
- **Functions:** 15
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, re, src, typing, yaml


## Classes

### PlanResult

```python
class PlanResult
```

**Decorators:** `dataclass`

Result of planning operation.


**Attributes:**

- `success`: bool
- `message`: str
- `plan_path`: Optional[Path]
- `plan_data`: Optional[Dict[str, Any]]
- `errors`: List[str]
- `details`: Optional[str]



---

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Result of plan validation.


**Attributes:**

- `valid`: bool
- `errors`: List[str]
- `warnings`: List[str]



---

## Functions

### detect_execution_mode

```python
detect_execution_mode(user_input: str) -> str
```

Detect if user wants autonomous (chained) or approval-gated execution.

Autonomous Triggers (case-insensitive):
- "execute all phases autonomously"
- "auto chained"
- "execute all phases auto chained"
- "all phases without user intervention"
- "without user intervention"
- "autonomous execution"
- "end to end"
- "run autonomously"
- "auto execute all"

Args:
    user_input: User's request/command text
    
Returns:
    "autonomous" if triggers detected, "approval_gated" otherwise
    
Examples:
    >>> detect_execution_mode("execute all phases autonomously")
    'autonomous'
    >>> detect_execution_mode("create plan for authentication")
    'approval_gated'


**Parameters:**

- `user_input` (str): User's request/command text


**Returns:** str
  "autonomous" if triggers detected, "approval_gated" otherwise


---

### analyze_risks

```python
analyze_risks(plan_data: Dict[str, Any]) -> List[Dict[str, str]]
```

Analyze plan for potential risks using heuristic patterns.

Risk Categories:
- Technical: Complexity, dependencies, architecture
- Timeline: Duration estimates, resource availability
- Security: Data handling, authentication, authorization
- Quality: Testing coverage, code review, validation
- Operational: Deployment, monitoring, rollback

Args:
    plan_data: Plan dictionary to analyze
    
Returns:
    List of risk dictionaries with category, description, severity, mitigation


**Parameters:**

- `plan_data` (Dict[str, Any]): Plan dictionary to analyze


**Returns:** List[Dict[str, str]]
  List of risk dictionaries with category, description, severity, mitigation


---

### detect_plan_complexity

```python
detect_plan_complexity(feature_name: str, description: str, user_input: str) -> Tuple[str, bool, str]
```

Detect if feature requires incremental plan generation.

Complexity Indicators:
- HIGH: Authentication, security, data migration, external APIs, multi-phase
- MEDIUM: Refactoring, new endpoints, UI changes, database changes
- LOW: Bug fixes, small enhancements, config changes

Args:
    feature_name: Feature name
    description: Feature description
    user_input: Original user request
    
Returns:
    Tuple of (complexity_level, use_incremental, reason)
    
Examples:
    >>> detect_plan_complexity("JWT Authentication", "Add JWT auth", "plan auth")
    ('high', True, 'Security-critical authentication feature')
    >>> detect_plan_complexity("Fix typo", "Fix typo in UI", "plan fix")
    ('low', False, 'Simple bug fix')


**Parameters:**

- `feature_name` (str): Feature name
- `description` (str): Feature description
- `user_input` (str): Original user request


**Returns:** Tuple[str, bool, str]
  Tuple of (complexity_level, use_incremental, reason)


---

### create_plan

```python
create_plan(feature_name: str, description: str, author: str, complexity: str, user_input: str) -> PlanResult
```

Create new plan with metadata.

Automatically detects complexity and delegates to incremental generator for:
- HIGH complexity: Security, auth, migrations, external APIs, multi-phase
- MEDIUM complexity: Refactoring, endpoints, UI, DB changes (with detailed description)
- LOW complexity: Simple features (uses skeleton generation)

Args:
    feature_name: Name of feature being planned
    description: Feature description
    author: Plan author name
    complexity: Complexity level (low, medium, high) - overridden by auto-detection
    user_input: Original user request (used to detect execution mode and complexity)
    
Returns:
    PlanResult with plan creation outcome


**Parameters:**

- `feature_name` (str): Name of feature being planned
- `description` (str) = `''`: Feature description
- `author` (str) = `'CORTEX'`: Plan author name
- `complexity` (str) = `'medium'`: Complexity level (low, medium, high) - overridden by auto-detection
- `user_input` (str) = `''`: Original user request (used to detect execution mode and complexity)


**Returns:** PlanResult
  PlanResult with plan creation outcome


---

### load_plan

```python
load_plan(plan_path: Path) -> PlanResult
```

Load plan from YAML file.

Args:
    plan_path: Path to plan YAML file
    
Returns:
    PlanResult with loaded plan data


**Parameters:**

- `plan_path` (Path): Path to plan YAML file


**Returns:** PlanResult
  PlanResult with loaded plan data


---

### save_plan

```python
save_plan(plan_data: Dict[str, Any], plan_path: Optional[Path]) -> PlanResult
```

Save plan to YAML file.

Args:
    plan_data: Plan dictionary to save
    plan_path: Optional custom path (auto-generated if None)
    
Returns:
    PlanResult with save outcome


**Parameters:**

- `plan_data` (Dict[str, Any]): Plan dictionary to save
- `plan_path` (Optional[Path]) = `None`: Optional custom path (auto-generated if None)


**Returns:** PlanResult
  PlanResult with save outcome


---

### validate_plan

```python
validate_plan(plan_data: Dict[str, Any]) -> ValidationResult
```

Validate plan structure and content.

Args:
    plan_data: Plan dictionary to validate
    
Returns:
    ValidationResult with validation outcome


**Parameters:**

- `plan_data` (Dict[str, Any]): Plan dictionary to validate


**Returns:** ValidationResult
  ValidationResult with validation outcome


---

### generate_markdown

```python
generate_markdown(plan_data: Dict[str, Any]) -> str
```

Generate Markdown view from plan data.

Args:
    plan_data: Plan dictionary
    
Returns:
    Markdown-formatted string


**Parameters:**

- `plan_data` (Dict[str, Any]): Plan dictionary


**Returns:** str
  Markdown-formatted string


---

### approve_plan

```python
approve_plan(plan_filename: str) -> PlanResult
```

Approve plan and move to active directory.

Args:
    plan_filename: Name of plan file to approve
    
Returns:
    PlanResult with approval outcome


**Parameters:**

- `plan_filename` (str): Name of plan file to approve


**Returns:** PlanResult
  PlanResult with approval outcome


---

### complete_plan

```python
complete_plan(plan_filename: str) -> PlanResult
```

Complete plan and move to completed directory.

Args:
    plan_filename: Name of plan file to complete
    
Returns:
    PlanResult with completion outcome


**Parameters:**

- `plan_filename` (str): Name of plan file to complete


**Returns:** PlanResult
  PlanResult with completion outcome


---
