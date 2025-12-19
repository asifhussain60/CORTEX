# commit_filter

Commit Filter

Identifies learning-worthy commits using configurable heuristics.
Assigns confidence scores based on line count, test changes, and error keywords.

Features:
- Configurable heuristics (line threshold, keyword patterns, weights)
- Weighted confidence scoring
- Ranked candidate list
- Integration with GitHistoryScanner

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [Candidate](#candidate)
- [CommitFilter](#commitfilter)

### Functions
- [filter_learning_candidates](#filter_learning_candidates)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, git_history_scanner, logging, pathlib, re, src, typing, yaml


## Classes

### Candidate

```python
class Candidate
```

**Decorators:** `dataclass`

Learning-worthy commit candidate.

Attributes:
    commit: Original commit metadata
    confidence_score: Weighted score (0.0-1.0+)
    matched_heuristics: Dict of heuristic_name -> bool
    explanation: Human-readable reason for candidacy


**Attributes:**

- `commit`: CommitMetadata
- `confidence_score`: float
- `matched_heuristics`: Dict[str, bool]
- `explanation`: str



---

### CommitFilter

```python
class CommitFilter
```

Filters commits to identify learning-worthy candidates.

Uses heuristics with weighted scoring:
- line_count: Threshold 100 lines, weight 0.3
- test_changes: Test file modifications, weight 0.4
- error_keywords: fix/bug/error in message, weight 0.5
- refactor_keywords: refactor/cleanup/optimize, weight 0.3

Example:
    filter = CommitFilter()
    commits = scanner.scan_commits(since_hours=24)
    candidates = filter.filter_learning_candidates(commits)
    
    for candidate in candidates:
        print(f"{candidate.commit.sha}: {candidate.confidence_score:.2f}")


**Methods:**

  #### `filter_learning_candidates`

  ```python
  filter_learning_candidates(self, commits: List[CommitMetadata]) -> List[Candidate]
  ```

  Filter commits to identify learning-worthy candidates.

Args:
    commits: List of commit metadata from scanner
    
Returns:
    List of Candidate objects, sorted by confidence descending

  **Parameters:**

  - `self`
  - `commits` (List[CommitMetadata]): List of commit metadata from scanner


  **Returns:** List[Candidate]
    List of Candidate objects, sorted by confidence descending



---

## Functions

### filter_learning_candidates

```python
filter_learning_candidates(commits: List[CommitMetadata], config_path: Optional[Path]) -> List[Candidate]
```

Convenience function to filter commits for learning candidates.

Args:
    commits: List of commit metadata
    config_path: Optional path to heuristics config
    
Returns:
    List of Candidate objects, sorted by confidence


**Parameters:**

- `commits` (List[CommitMetadata]): List of commit metadata
- `config_path` (Optional[Path]) = `None`: Optional path to heuristics config


**Returns:** List[Candidate]
  List of Candidate objects, sorted by confidence


---
