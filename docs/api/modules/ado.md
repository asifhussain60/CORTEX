# ado

ADO CLI - Azure DevOps Work Item Management

Command-line interface for ADO utility operations.

Commands:
  create        - Create new work item
  load          - Load existing work item
  update        - Update work item fields
  summary       - Generate completion summary
  validate-dor  - Validate Definition of Ready
  validate-dod  - Validate Definition of Done
  list          - List work items by status

Usage:
  python -m src.operations.ado create story "My Story" "Description" --priority 1
  python -m src.operations.ado load <work-item-id>
  python -m src.operations.ado update <work-item-id> --status completed
  python -m src.operations.ado summary <work-item-id> --files-created file1.py file2.py
  python -m src.operations.ado validate-dor <work-item-id>
  python -m src.operations.ado validate-dod <work-item-id>
  python -m src.operations.ado list --status active

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [format_work_item_result](#format_work_item_result)
- [format_validation_result](#format_validation_result)
- [cmd_create](#cmd_create)
- [cmd_load](#cmd_load)
- [cmd_update](#cmd_update)
- [cmd_summary](#cmd_summary)
- [cmd_validate_dor](#cmd_validate_dor)
- [cmd_validate_dod](#cmd_validate_dod)
- [cmd_list](#cmd_list)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 10
- **Dependencies:** argparse, json, pathlib, src, sys, typing


## Functions

### format_work_item_result

```python
format_work_item_result(result: WorkItemResult, json_output: bool) -> str
```

Format work item result for display.


**Parameters:**

- `result` (WorkItemResult)
- `json_output` (bool) = `False`


**Returns:** str


---

### format_validation_result

```python
format_validation_result(result: ValidationResult, json_output: bool) -> str
```

Format validation result for display.


**Parameters:**

- `result` (ValidationResult)
- `json_output` (bool) = `False`


**Returns:** str


---

### cmd_create

```python
cmd_create(args: argparse.Namespace) -> int
```

Create work item command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_load

```python
cmd_load(args: argparse.Namespace) -> int
```

Load work item command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_update

```python
cmd_update(args: argparse.Namespace) -> int
```

Update work item command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_summary

```python
cmd_summary(args: argparse.Namespace) -> int
```

Generate summary command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_validate_dor

```python
cmd_validate_dor(args: argparse.Namespace) -> int
```

Validate DoR command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_validate_dod

```python
cmd_validate_dod(args: argparse.Namespace) -> int
```

Validate DoD command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_list

```python
cmd_list(args: argparse.Namespace) -> int
```

List work items command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### main

```python
main()
```

Main CLI entry point.


---
