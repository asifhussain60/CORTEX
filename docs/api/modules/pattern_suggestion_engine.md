# pattern_suggestion_engine

Pattern Suggestion Engine

Automatically suggests relevant patterns before task execution to increase utilization.

Purpose:
    - Search for relevant patterns based on task context
    - Rank patterns by relevance (BM25 + confidence + access history)
    - Display top 3 suggestions to user before task execution
    - Track pattern acceptance/rejection for feedback loop

Responsibilities:
    - Pattern retrieval based on intent keywords
    - Relevance scoring with multiple factors
    - Pattern suggestion formatting
    - Usage tracking (acceptance rate, effectiveness)

Integration Points:
    - Called by IntentRouter before agent execution
    - Uses PatternSearch for retrieval
    - Updates pattern access counts via PatternStore

Performance Targets:
    - Suggestion generation: <100ms
    - Pattern search: <50ms
    - Relevance scoring: <30ms

Example:
    >>> from tier2.pattern_suggestion_engine import PatternSuggestionEngine
    >>> engine = PatternSuggestionEngine()
    >>> suggestions = engine.suggest_patterns("implement authentication feature", limit=3)
    >>> for suggestion in suggestions:
    ...     print(f"{suggestion['title']}: {suggestion['relevance_score']:.2f}")

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [PatternSuggestionEngine](#patternsuggestionengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, logging, os, sqlite3, src, sys, typing


## Classes

### PatternSuggestionEngine

```python
class PatternSuggestionEngine
```

Suggests relevant patterns before task execution.

Uses multi-factor relevance scoring:
- BM25 score from FTS5 search (content relevance)
- Confidence score (pattern quality)
- Historical access count (proven usefulness)
- Recency (last accessed timestamp)


**Methods:**

  #### `suggest_patterns`

  ```python
  suggest_patterns(self, task_description: str, intent_type: Optional[str], current_namespace: Optional[str], min_confidence: float, limit: int) -> List[Dict[str, Any]]
  ```

  Suggest relevant patterns for a given task.

Args:
    task_description: Natural language task description
    intent_type: Intent type (PLAN, EXECUTE, TEST, etc.)
    current_namespace: Current application context
    min_confidence: Minimum confidence threshold
    limit: Maximum suggestions to return (default: 3)

Returns:
    List of pattern suggestions with relevance scores

Performance: <100ms

  **Parameters:**

  - `self`
  - `task_description` (str): Natural language task description
  - `intent_type` (Optional[str]) = `None`: Intent type (PLAN, EXECUTE, TEST, etc.)
  - `current_namespace` (Optional[str]) = `None`: Current application context
  - `min_confidence` (float) = `0.6`: Minimum confidence threshold
  - `limit` (int) = `3`: Maximum suggestions to return (default: 3)


  **Returns:** List[Dict[str, Any]]
    List of pattern suggestions with relevance scores Performance: <100ms


  #### `format_suggestion`

  ```python
  format_suggestion(self, pattern: Dict[str, Any]) -> str
  ```

  Format pattern suggestion for display to user.

Args:
    pattern: Pattern dictionary

Returns:
    Formatted suggestion string

  **Parameters:**

  - `self`
  - `pattern` (Dict[str, Any]): Pattern dictionary


  **Returns:** str
    Formatted suggestion string


  #### `display_suggestions`

  ```python
  display_suggestions(self, task_description: str, intent_type: Optional[str], current_namespace: Optional[str]) -> str
  ```

  Display pattern suggestions to user before task execution.

Args:
    task_description: Task description
    intent_type: Intent type
    current_namespace: Current namespace

Returns:
    Formatted suggestions text

  **Parameters:**

  - `self`
  - `task_description` (str): Task description
  - `intent_type` (Optional[str]) = `None`: Intent type
  - `current_namespace` (Optional[str]) = `None`: Current namespace


  **Returns:** str
    Formatted suggestions text


  #### `track_pattern_acceptance`

  ```python
  track_pattern_acceptance(self, pattern_id: str, accepted: bool, task_outcome: Optional[str]) -> bool
  ```

  Track whether user accepted/rejected a pattern suggestion.

Updates:
- Access count (if accepted)
- Last accessed timestamp (if accepted)
- Pattern effectiveness metadata

Args:
    pattern_id: Pattern ID
    accepted: True if user applied pattern
    task_outcome: Task outcome (success/failure/partial)

Returns:
    True if tracking successful

  **Parameters:**

  - `self`
  - `pattern_id` (str): Pattern ID
  - `accepted` (bool): True if user applied pattern
  - `task_outcome` (Optional[str]) = `None`: Task outcome (success/failure/partial)


  **Returns:** bool
    True if tracking successful



---
