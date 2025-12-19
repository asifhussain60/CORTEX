# duplication_detector

Duplication Detection System (Phase 4)
Searches existing lessons using FTS5 full-text search to prevent duplicates.

Features:
- Keyword extraction from captured lessons
- FTS5 full-text search integration with Tier 2 KnowledgeGraph
- Similarity scoring with configurable threshold
- Ranked duplicate matches with merge suggestions

Author: Asif Hussain
License: Source-Available


## Table of Contents

### Classes
- [DuplicateMatch](#duplicatematch)
- [DuplicationDetector](#duplicationdetector)

### Functions
- [extract_keywords](#extract_keywords)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, logging, pathlib, re, src, typing


## Classes

### DuplicateMatch

```python
class DuplicateMatch
```

**Decorators:** `dataclass`

Represents a potential duplicate lesson match.

Attributes:
    lesson_id: ID of existing lesson in lessons-learned.yaml
    problem: Problem description from existing lesson
    solution: Solution description from existing lesson
    similarity_score: Calculated similarity (0.0-1.0)
    explanation: Human-readable explanation of match


**Attributes:**

- `lesson_id`: str
- `problem`: str
- `solution`: str
- `similarity_score`: float
- `explanation`: str



---

### DuplicationDetector

```python
class DuplicationDetector
```

Detects duplicate lessons using FTS5 full-text search.

Integrates with Tier 2 KnowledgeGraph to search existing lessons
and calculate similarity scores for potential duplicates.


**Methods:**

  #### `find_duplicates`

  ```python
  find_duplicates(self, lesson: CapturedLesson, threshold: float, max_results: int) -> List[DuplicateMatch]
  ```

  Find potential duplicate lessons using FTS5 search.

Args:
    lesson: CapturedLesson to check for duplicates
    threshold: Minimum similarity score to include (0.0-1.0)
    max_results: Maximum number of matches to return
    
Returns:
    List of DuplicateMatch objects sorted by similarity score (descending)

  **Parameters:**

  - `self`
  - `lesson` (CapturedLesson): CapturedLesson to check for duplicates
  - `threshold` (float) = `0.7`: Minimum similarity score to include (0.0-1.0)
  - `max_results` (int) = `5`: Maximum number of matches to return


  **Returns:** List[DuplicateMatch]
    List of DuplicateMatch objects sorted by similarity score (descending)



---

## Functions

### extract_keywords

```python
extract_keywords(lesson: CapturedLesson) -> List[str]
```

Extract keywords from captured lesson for FTS5 search.

Combines keywords from problem, root_cause, and solution fields.
Filters stopwords and extracts meaningful terms.

Args:
    lesson: CapturedLesson to extract keywords from
    
Returns:
    List of unique keywords


**Parameters:**

- `lesson` (CapturedLesson): CapturedLesson to extract keywords from


**Returns:** List[str]
  List of unique keywords


---
