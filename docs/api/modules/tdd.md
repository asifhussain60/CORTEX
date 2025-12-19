# tdd

TDD CLI - Test-Driven Development Workflow

Command-line interface for TDD utility operations.

Commands:
  start     - Start new TDD session
  test      - Run tests
  pass      - Transition to GREEN phase (tests passing)
  refactor  - Transition to REFACTOR phase
  complete  - Complete TDD session
  status    - Get current session status
  skeleton  - Generate test skeleton

Usage:
  python -m src.operations.tdd start "Feature Name" tests/test_feature.py src/feature.py
  python -m src.operations.tdd test tests/test_feature.py
  python -m src.operations.tdd pass <session-id>
  python -m src.operations.tdd refactor <session-id>
  python -m src.operations.tdd complete <session-id>
  python -m src.operations.tdd status <session-id>
  python -m src.operations.tdd skeleton "Feature Name" tests/test_feature.py src/feature.py

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [format_result](#format_result)
- [cmd_start](#cmd_start)
- [cmd_test](#cmd_test)
- [cmd_pass](#cmd_pass)
- [cmd_refactor](#cmd_refactor)
- [cmd_complete](#cmd_complete)
- [cmd_status](#cmd_status)
- [cmd_skeleton](#cmd_skeleton)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 9
- **Dependencies:** argparse, json, pathlib, src, sys, typing


## Functions

### format_result

```python
format_result(result: TDDResult, json_output: bool) -> str
```

Format TDD result for display.

Args:
    result: TDDResult to format
    json_output: Whether to output as JSON
    
Returns:
    Formatted string


**Parameters:**

- `result` (TDDResult): TDDResult to format
- `json_output` (bool) = `False`: Whether to output as JSON


**Returns:** str
  Formatted string


---

### cmd_start

```python
cmd_start(args: argparse.Namespace) -> int
```

Start TDD session command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_test

```python
cmd_test(args: argparse.Namespace) -> int
```

Run tests command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_pass

```python
cmd_pass(args: argparse.Namespace) -> int
```

Transition to GREEN phase command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_refactor

```python
cmd_refactor(args: argparse.Namespace) -> int
```

Transition to REFACTOR phase command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_complete

```python
cmd_complete(args: argparse.Namespace) -> int
```

Complete session command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_status

```python
cmd_status(args: argparse.Namespace) -> int
```

Get session status command.


**Parameters:**

- `args` (argparse.Namespace)


**Returns:** int


---

### cmd_skeleton

```python
cmd_skeleton(args: argparse.Namespace) -> int
```

Generate test skeleton command.


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
