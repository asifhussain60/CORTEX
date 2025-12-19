# review

Code Review CLI

User-friendly command-line interface for code review operations.

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [format_output](#format_output)
- [cmd_create](#cmd_create)
- [cmd_load](#cmd_load)
- [cmd_analyze](#cmd_analyze)
- [cmd_report](#cmd_report)
- [cmd_list](#cmd_list)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 7
- **Dependencies:** argparse, json, pathlib, src, sys, typing, yaml


## Functions

### format_output

```python
format_output(result, json_output: bool)
```

Format operation result for display.


**Parameters:**

- `result`
- `json_output` (bool) = `False`


---

### cmd_create

```python
cmd_create(args)
```

Create new code review.


**Parameters:**

- `args`


---

### cmd_load

```python
cmd_load(args)
```

Load existing review.


**Parameters:**

- `args`


---

### cmd_analyze

```python
cmd_analyze(args)
```

Analyze file for issues.


**Parameters:**

- `args`


---

### cmd_report

```python
cmd_report(args)
```

Generate review report.


**Parameters:**

- `args`


---

### cmd_list

```python
cmd_list(args)
```

List code reviews.


**Parameters:**

- `args`


---

### main

```python
main()
```

Main CLI entry point.


---
