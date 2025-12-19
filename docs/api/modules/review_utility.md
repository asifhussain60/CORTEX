# review_utility

Code Review Utility

Fast, lightweight code review management.
Replaces heavy orchestrator (1,029 lines) with focused utility (~600 lines).

Core Operations:
- Create review session
- Analyze file/changes
- Generate review report
- Check quality metrics
- List reviews

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ReviewDepth](#reviewdepth)
- [ReviewStatus](#reviewstatus)
- [CodeIssue](#codeissue)
- [QualityMetrics](#qualitymetrics)
- [ReviewSession](#reviewsession)
- [ReviewResult](#reviewresult)

### Functions
- [create_review](#create_review)
- [load_review](#load_review)
- [analyze_file](#analyze_file)
- [generate_report](#generate_report)
- [list_reviews](#list_reviews)


## Overview

- **Classes:** 6
- **Functions:** 12
- **Dependencies:** dataclasses, datetime, enum, json, logging, pathlib, re, src, typing, yaml


## Classes

### ReviewDepth

```python
class ReviewDepth(Enum)
```

Analysis depth options.



---

### ReviewStatus

```python
class ReviewStatus(Enum)
```

Review status states.



---

### CodeIssue

```python
class CodeIssue
```

**Decorators:** `dataclass`

Single code issue.


**Attributes:**

- `severity`: str
- `category`: str
- `description`: str
- `file`: str
- `line`: int
- `suggestion`: str



---

### QualityMetrics

```python
class QualityMetrics
```

**Decorators:** `dataclass`

Code quality metrics.


**Attributes:**

- `risk_score`: int
- `complexity_score`: int
- `test_coverage`: float
- `lines_of_code`: int
- `files_analyzed`: int
- `issues_count`: Dict[str, int]



---

### ReviewSession

```python
class ReviewSession
```

**Decorators:** `dataclass`

Code review session.


**Attributes:**

- `review_id`: str
- `title`: str
- `description`: str
- `status`: ReviewStatus
- `depth`: ReviewDepth
- `files_reviewed`: List[str]
- `issues`: List[CodeIssue]
- `metrics`: Optional[QualityMetrics]
- `reviewer`: str
- `created_at`: str
- `updated_at`: str
- `completed_at`: Optional[str]



---

### ReviewResult

```python
class ReviewResult
```

**Decorators:** `dataclass`

Result of review operation.


**Attributes:**

- `success`: bool
- `message`: str
- `review_id`: Optional[str]
- `session`: Optional[ReviewSession]
- `report_path`: Optional[Path]
- `errors`: List[str]



---

## Functions

### create_review

```python
create_review(title: str, description: str, depth: ReviewDepth, **kwargs) -> ReviewResult
```

Create new code review session.

Args:
    title: Review title
    description: Review description
    depth: Analysis depth
    **kwargs: Additional session fields
    
Returns:
    ReviewResult with creation outcome


**Parameters:**

- `title` (str): Review title
- `description` (str): Review description
- `depth` (ReviewDepth) = `ReviewDepth.STANDARD`: Analysis depth
- `**kwargs`


**Returns:** ReviewResult
  ReviewResult with creation outcome


---

### load_review

```python
load_review(review_id: str) -> ReviewResult
```

Load existing review session.

Args:
    review_id: Review identifier
    
Returns:
    ReviewResult with loaded session


**Parameters:**

- `review_id` (str): Review identifier


**Returns:** ReviewResult
  ReviewResult with loaded session


---

### analyze_file

```python
analyze_file(review_id: str, file_path: Path, content: Optional[str]) -> ReviewResult
```

Analyze single file for code quality issues.

Args:
    review_id: Review identifier
    file_path: Path to file being analyzed
    content: File content (optional, will read if not provided)
    
Returns:
    ReviewResult with analysis outcome


**Parameters:**

- `review_id` (str): Review identifier
- `file_path` (Path): Path to file being analyzed
- `content` (Optional[str]) = `None`: File content (optional, will read if not provided)


**Returns:** ReviewResult
  ReviewResult with analysis outcome


---

### generate_report

```python
generate_report(review_id: str) -> ReviewResult
```

Generate code review report.

Args:
    review_id: Review identifier
    
Returns:
    ReviewResult with report path


**Parameters:**

- `review_id` (str): Review identifier


**Returns:** ReviewResult
  ReviewResult with report path


---

### list_reviews

```python
list_reviews(status: Optional[ReviewStatus]) -> ReviewResult
```

List code reviews by status.

Args:
    status: Filter by status (None = all)
    
Returns:
    ReviewResult with list of reviews


**Parameters:**

- `status` (Optional[ReviewStatus]) = `None`: Filter by status (None = all)


**Returns:** ReviewResult
  ReviewResult with list of reviews


---
