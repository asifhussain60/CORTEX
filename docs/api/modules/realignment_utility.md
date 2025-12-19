# realignment_utility

Realignment Utility

Fast, lightweight policy realignment utility for automatic violation fixes.
Replaces orchestrator with focused utility for policy compliance workflows.

Features:
- Policy violation detection via PolicyValidator integration
- Automatic action generation from violations
- Safe vs approval-required action classification
- Interactive approval prompts for destructive changes
- Realignment report generation with compliance tracking

Operations:
1. realign - Main realignment workflow
2. generate_actions - Create actions from violations
3. create_naming_action - Generate naming violation fixes
4. create_security_action - Generate security violation fixes
5. create_standards_action - Generate standards violation fixes
6. create_architecture_action - Generate architecture violation fixes
7. apply_action - Execute single realignment action
8. generate_report - Create realignment report

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [RealignmentAction](#realignmentaction)
- [RealignmentResult](#realignmentresult)

### Functions
- [realign](#realign)
- [generate_actions](#generate_actions)
- [create_naming_action](#create_naming_action)
- [create_security_action](#create_security_action)
- [create_standards_action](#create_standards_action)
- [create_architecture_action](#create_architecture_action)
- [apply_action](#apply_action)
- [generate_report](#generate_report)
- [align_system_v2](#align_system_v2)


## Overview

- **Classes:** 2
- **Functions:** 23
- **Dependencies:** dataclasses, datetime, inspect, logging, pathlib, shutil, src, typing, yaml


## Classes

### RealignmentAction

```python
class RealignmentAction
```

**Decorators:** `dataclass`

Single realignment action.


**Attributes:**

- `action_type`: str
- `target`: Path
- `description`: str
- `before`: str
- `after`: str
- `severity`: str
- `requires_approval`: bool



---

### RealignmentResult

```python
class RealignmentResult
```

**Decorators:** `dataclass`

Result of realignment operation.


**Attributes:**

- `success`: bool
- `actions_applied`: List[RealignmentAction]
- `actions_skipped`: List[RealignmentAction]
- `errors`: List[str]
- `before_compliance`: float
- `after_compliance`: float
- `report_path`: Optional[Path]



---

## Functions

### realign

```python
realign(project_root: Path, cortex_root: Path, interactive: bool) -> RealignmentResult
```

Execute realignment workflow to fix policy violations automatically.

Steps:
1. Run PolicyValidator to get initial compliance
2. Generate realignment actions from violations
3. Apply automatic actions (no approval needed)
4. Prompt for approval on manual actions (if interactive)
5. Re-run PolicyValidator to measure improvement
6. Generate realignment report

Args:
    project_root: Root directory of user project
    cortex_root: Root directory of CORTEX installation
    interactive: Whether to prompt for approval
    
Returns:
    RealignmentResult with actions taken and compliance improvement


**Parameters:**

- `project_root` (Path): Root directory of user project
- `cortex_root` (Path): Root directory of CORTEX installation
- `interactive` (bool) = `True`: Whether to prompt for approval


**Returns:** RealignmentResult
  RealignmentResult with actions taken and compliance improvement


---

### generate_actions

```python
generate_actions(violations: List) -> List[RealignmentAction]
```

Generate realignment actions from policy violations.

Args:
    violations: List of PolicyViolation objects
    
Returns:
    List of RealignmentAction objects


**Parameters:**

- `violations` (List): List of PolicyViolation objects


**Returns:** List[RealignmentAction]
  List of RealignmentAction objects


---

### create_naming_action

```python
create_naming_action(violation) -> Optional[RealignmentAction]
```

Create action to fix naming violation.

Args:
    violation: PolicyViolation object
    
Returns:
    RealignmentAction or None


**Parameters:**

- `violation`: PolicyViolation object


**Returns:** Optional[RealignmentAction]
  RealignmentAction or None


---

### create_security_action

```python
create_security_action(violation) -> Optional[RealignmentAction]
```

Create action to fix security violation.

Args:
    violation: PolicyViolation object
    
Returns:
    RealignmentAction or None


**Parameters:**

- `violation`: PolicyViolation object


**Returns:** Optional[RealignmentAction]
  RealignmentAction or None


---

### create_standards_action

```python
create_standards_action(violation) -> Optional[RealignmentAction]
```

Create action to fix standards violation.

Args:
    violation: PolicyViolation object
    
Returns:
    RealignmentAction or None


**Parameters:**

- `violation`: PolicyViolation object


**Returns:** Optional[RealignmentAction]
  RealignmentAction or None


---

### create_architecture_action

```python
create_architecture_action(violation) -> Optional[RealignmentAction]
```

Create action to fix architecture violation.

Args:
    violation: PolicyViolation object
    
Returns:
    RealignmentAction or None


**Parameters:**

- `violation`: PolicyViolation object


**Returns:** Optional[RealignmentAction]
  RealignmentAction or None


---

### apply_action

```python
apply_action(action: RealignmentAction) -> bool
```

Apply realignment action.

Args:
    action: Action to apply
    
Returns:
    True if successful, False if skipped


**Parameters:**

- `action` (RealignmentAction): Action to apply


**Returns:** bool
  True if successful, False if skipped


---

### generate_report

```python
generate_report(cortex_root: Path, project_root: Path, applied: List[RealignmentAction], skipped: List[RealignmentAction], errors: List[str], before: float, after: float) -> Path
```

Generate realignment report with compliance tracking.

Args:
    cortex_root: CORTEX root directory
    project_root: Project root directory
    applied: List of applied actions
    skipped: List of skipped actions
    errors: List of errors
    before: Before compliance percentage
    after: After compliance percentage
    
Returns:
    Path to generated report


**Parameters:**

- `cortex_root` (Path): CORTEX root directory
- `project_root` (Path): Project root directory
- `applied` (List[RealignmentAction]): List of applied actions
- `skipped` (List[RealignmentAction]): List of skipped actions
- `errors` (List[str]): List of errors
- `before` (float): Before compliance percentage
- `after` (float): After compliance percentage


**Returns:** Path
  Path to generated report


---

### align_system_v2

```python
align_system_v2(project_root: Path, cortex_root: Path, auto_fix: bool, dry_run: bool) -> Dict[str, Any]
```

CORTEX Align v2.0 - Holistic system alignment with intelligent maintenance.

This is the MOST CRUCIAL validation step. When user says '/CORTEX align',
this function runs comprehensive checks to ensure CORTEX is fully operational.

Features:
- Feature registration validation (all operations in cortex-operations.yaml)
- Auto-discovery and registration of new features
- Intent router coverage check (all operations have triggers)
- Response template validation (all operations have templates)
- Documentation alignment (docs match implementation)
- Obsolete code detection and cleanup
- Test migration to new architecture
- CORTEX.prompt.md optimization validation

Args:
    project_root: Root directory of project to align
    cortex_root: Root directory of CORTEX installation
    auto_fix: Automatically fix issues (default: False, prompt user)
    dry_run: Preview changes without applying (default: False)
    
Returns:
    Dictionary with alignment results and report path


**Parameters:**

- `project_root` (Path): Root directory of project to align
- `cortex_root` (Path): Root directory of CORTEX installation
- `auto_fix` (bool) = `False`: Automatically fix issues (default: False, prompt user)
- `dry_run` (bool) = `False`: Preview changes without applying (default: False)


**Returns:** Dict[str, Any]
  Dictionary with alignment results and report path


---
