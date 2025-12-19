# pattern_learning_engine

CORTEX 3.0 Pattern Learning Engine
Advanced Fusion - Milestone 3

Learns from successful temporal correlations to improve future suggestions.
Core component of CORTEX's adaptive fusion layer.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX


## Table of Contents

### Classes
- [PatternType](#patterntype)
- [CorrelationPattern](#correlationpattern)
- [LearningSession](#learningsession)
- [PatternLearningEngine](#patternlearningengine)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** collections, dataclasses, datetime, enum, json, logging, re, sqlite3, typing, uuid


## Classes

### PatternType

```python
class PatternType(Enum)
```

Types of patterns the learning engine can recognize and learn from



---

### CorrelationPattern

```python
class CorrelationPattern
```

**Decorators:** `dataclass`

A learned pattern from successful correlations


**Attributes:**

- `pattern_id`: str
- `pattern_type`: PatternType
- `pattern_data`: Dict[str, Any]
- `confidence`: float
- `usage_count`: int
- `success_rate`: float
- `created_at`: datetime
- `last_used`: datetime


**Methods:**


---

### LearningSession

```python
class LearningSession
```

**Decorators:** `dataclass`

A session where patterns were learned from correlations


**Attributes:**

- `session_id`: str
- `conversation_id`: str
- `patterns_learned`: int
- `patterns_applied`: int
- `improvement_score`: float
- `created_at`: datetime


**Methods:**


---

### PatternLearningEngine

```python
class PatternLearningEngine
```

CORTEX 3.0 Pattern Learning Engine

Learns from successful temporal correlations to improve future suggestions.
Builds patterns that help predict files, sequences, and optimal correlation windows.


**Methods:**

  #### `learn_from_correlation`

  ```python
  learn_from_correlation(self, correlation_result: Dict[str, Any]) -> LearningSession
  ```

  Learn patterns from a successful temporal correlation result.

Args:
    correlation_result: Result from TemporalCorrelator with correlation data
    
Returns:
    LearningSession with details of what was learned

  **Parameters:**

  - `self`
  - `correlation_result` (Dict[str, Any]): Result from TemporalCorrelator with correlation data


  **Returns:** LearningSession
    LearningSession with details of what was learned


  #### `suggest_files_for_conversation`

  ```python
  suggest_files_for_conversation(self, conversation_text: str, conversation_metadata: Dict[str, Any]) -> List[Dict[str, Any]]
  ```

  Predict likely implementation files based on conversation content using learned patterns.

Args:
    conversation_text: Text content of the conversation
    conversation_metadata: Optional metadata (timestamp, participants, etc.)
    
Returns:
    List of file suggestions with confidence scores

  **Parameters:**

  - `self`
  - `conversation_text` (str): Text content of the conversation
  - `conversation_metadata` (Dict[str, Any]) = `None`: Optional metadata (timestamp, participants, etc.)


  **Returns:** List[Dict[str, Any]]
    List of file suggestions with confidence scores


  #### `boost_confidence_from_patterns`

  ```python
  boost_confidence_from_patterns(self, correlation_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]
  ```

  Use learned patterns to boost correlation confidence scores.

Args:
    correlation_candidates: List of potential correlations with base confidence
    
Returns:
    Same list with updated confidence scores based on patterns

  **Parameters:**

  - `self`
  - `correlation_candidates` (List[Dict[str, Any]]): List of potential correlations with base confidence


  **Returns:** List[Dict[str, Any]]
    Same list with updated confidence scores based on patterns


  #### `get_learning_statistics`

  ```python
  get_learning_statistics(self) -> Dict[str, Any]
  ```

  Get statistics about pattern learning progress

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `export_patterns`

  ```python
  export_patterns(self, output_file: str) -> bool
  ```

  Export learned patterns to a JSON file for backup or analysis

  **Parameters:**

  - `self`
  - `output_file` (str)


  **Returns:** bool



---
