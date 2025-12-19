# analysis_utility

Code Analysis Utility

Lightweight code analysis for detecting issues in code reviews.
Replaces heavy orchestrator (969 lines) with focused utility (~550 lines).

Core analyzers:
- Breaking changes detection
- Security vulnerabilities
- Performance issues
- Code quality checks

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [IssueSeverity](#issueseverity)
- [IssueCategory](#issuecategory)
- [CodeIssue](#codeissue)
- [AnalysisResult](#analysisresult)

### Functions
- [analyze_file](#analyze_file)
- [get_breaking_changes](#get_breaking_changes)
- [check_security](#check_security)
- [check_performance](#check_performance)
- [check_code_quality](#check_code_quality)
- [generate_analysis_report](#generate_analysis_report)


## Overview

- **Classes:** 4
- **Functions:** 11
- **Dependencies:** dataclasses, enum, logging, pathlib, re, src, time, typing


## Classes

### IssueSeverity

```python
class IssueSeverity(Enum)
```

Severity levels for code issues.



---

### IssueCategory

```python
class IssueCategory(Enum)
```

Categories of code issues.



---

### CodeIssue

```python
class CodeIssue
```

**Decorators:** `dataclass`

Single code issue found during analysis.


**Attributes:**

- `category`: IssueCategory
- `severity`: IssueSeverity
- `title`: str
- `description`: str
- `file_path`: str
- `line_number`: int
- `code_snippet`: str
- `fix_suggestion`: str



---

### AnalysisResult

```python
class AnalysisResult
```

**Decorators:** `dataclass`

Results from code analysis.


**Attributes:**

- `analyzer`: str
- `file_path`: str
- `issues`: List[CodeIssue]
- `execution_time`: float


**Methods:**

  #### `critical_count`

  *Decorators:* `property`

  ```python
  critical_count(self) -> int
  ```

  #### `high_count`

  *Decorators:* `property`

  ```python
  high_count(self) -> int
  ```

  #### `medium_count`

  *Decorators:* `property`

  ```python
  medium_count(self) -> int
  ```

  #### `low_count`

  *Decorators:* `property`

  ```python
  low_count(self) -> int
  ```

  #### `total_count`

  *Decorators:* `property`

  ```python
  total_count(self) -> int
  ```


---

## Functions

### analyze_file

```python
analyze_file(file_path: Path, analyzers: Optional[List[str]]) -> AnalysisResult
```

Analyze single file for code issues.

Args:
    file_path: Path to file to analyze
    analyzers: List of analyzer names (default: all)
    
Returns:
    AnalysisResult with findings


**Parameters:**

- `file_path` (Path): Path to file to analyze
- `analyzers` (Optional[List[str]]) = `None`: List of analyzer names (default: all)


**Returns:** AnalysisResult
  AnalysisResult with findings


---

### get_breaking_changes

```python
get_breaking_changes(file_path: Path) -> List[CodeIssue]
```

Detect breaking changes in public APIs.

Args:
    file_path: Path to file to analyze
    
Returns:
    List of breaking change issues


**Parameters:**

- `file_path` (Path): Path to file to analyze


**Returns:** List[CodeIssue]
  List of breaking change issues


---

### check_security

```python
check_security(file_path: Path) -> List[CodeIssue]
```

Check for security vulnerabilities.

Args:
    file_path: Path to file to analyze
    
Returns:
    List of security issues


**Parameters:**

- `file_path` (Path): Path to file to analyze


**Returns:** List[CodeIssue]
  List of security issues


---

### check_performance

```python
check_performance(file_path: Path) -> List[CodeIssue]
```

Check for performance issues.

Args:
    file_path: Path to file to analyze
    
Returns:
    List of performance issues


**Parameters:**

- `file_path` (Path): Path to file to analyze


**Returns:** List[CodeIssue]
  List of performance issues


---

### check_code_quality

```python
check_code_quality(file_path: Path) -> List[CodeIssue]
```

Check general code quality issues.

Args:
    file_path: Path to file to analyze
    
Returns:
    List of code quality issues


**Parameters:**

- `file_path` (Path): Path to file to analyze


**Returns:** List[CodeIssue]
  List of code quality issues


---

### generate_analysis_report

```python
generate_analysis_report(results: List[AnalysisResult], output_path: Path) -> bool
```

Generate markdown analysis report.

Args:
    results: List of analysis results
    output_path: Path to save report
    
Returns:
    True if successful


**Parameters:**

- `results` (List[AnalysisResult]): List of analysis results
- `output_path` (Path): Path to save report


**Returns:** bool
  True if successful


---
