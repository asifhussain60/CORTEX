# smart_recommendations

CORTEX 3.0 - Smart Recommendations API
Advanced Fusion Features - Milestone 3

Intelligent file prediction service that leverages learned patterns from the Pattern Learning Engine
to suggest relevant files based on conversation content and development context.

Features:
- Context-aware file suggestions based on conversation analysis
- Pattern-driven recommendations using learned correlations
- File grouping by relevance and development phase
- Adaptive learning from user interaction feedback
- Integration with both conversational and traditional memories

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Version: 3.0.0


## Table of Contents

### Classes
- [FileRecommendation](#filerecommendation)
- [RecommendationContext](#recommendationcontext)
- [RecommendationFeedback](#recommendationfeedback)
- [SmartRecommendations](#smartrecommendations)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** collections, dataclasses, datetime, json, logging, math, pathlib, re, sqlite3, typing


## Classes

### FileRecommendation

```python
class FileRecommendation
```

**Decorators:** `dataclass`

A recommended file with confidence score and reasoning


**Attributes:**

- `file_path`: str
- `confidence_score`: float
- `reasoning`: str
- `recommendation_type`: str
- `supporting_evidence`: List[str]
- `last_accessed`: Optional[datetime]
- `frequency_score`: float
- `recency_score`: float
- `pattern_strength`: float
- `metadata`: Dict[str, Any]


**Methods:**


---

### RecommendationContext

```python
class RecommendationContext
```

**Decorators:** `dataclass`

Context information for generating recommendations


**Attributes:**

- `current_conversation`: str
- `user_intent`: str
- `mentioned_files`: List[str]
- `development_phase`: str
- `keywords`: List[str]
- `conversation_id`: str
- `timestamp`: datetime
- `session_context`: Dict[str, Any]


**Methods:**


---

### RecommendationFeedback

```python
class RecommendationFeedback
```

**Decorators:** `dataclass`

User feedback on recommendation quality


**Attributes:**

- `recommendation_id`: str
- `file_path`: str
- `user_action`: str
- `timestamp`: datetime
- `context`: str
- `effectiveness_rating`: Optional[float]



---

### SmartRecommendations

```python
class SmartRecommendations
```

Advanced file recommendation engine using pattern learning and context analysis.

This system learns from conversation patterns, file access history, and user feedback
to provide intelligent file suggestions that improve development workflow efficiency.


**Methods:**

  #### `get_recommendations`

  ```python
  get_recommendations(self, context: RecommendationContext, max_results: int) -> List[FileRecommendation]
  ```

  Generate intelligent file recommendations based on conversation context.

Args:
    context: RecommendationContext with conversation details
    max_results: Maximum number of recommendations to return
    
Returns:
    List of FileRecommendation objects sorted by confidence score

  **Parameters:**

  - `self`
  - `context` (RecommendationContext): RecommendationContext with conversation details
  - `max_results` (int) = `10`: Maximum number of recommendations to return


  **Returns:** List[FileRecommendation]
    List of FileRecommendation objects sorted by confidence score


  #### `record_file_access`

  ```python
  record_file_access(self, file_path: str, conversation_id: str, access_type: str, context: str)
  ```

  Record file access for learning and recommendations

  **Parameters:**

  - `self`
  - `file_path` (str)
  - `conversation_id` (str)
  - `access_type` (str)
  - `context` (str) = `None`


  #### `record_feedback`

  ```python
  record_feedback(self, feedback: RecommendationFeedback)
  ```

  Record user feedback on recommendation quality

  **Parameters:**

  - `self`
  - `feedback` (RecommendationFeedback)


  #### `get_recommendation_analytics`

  ```python
  get_recommendation_analytics(self, days: int) -> Dict[str, Any]
  ```

  Get analytics on recommendation effectiveness and patterns

  **Parameters:**

  - `self`
  - `days` (int) = `30`


  **Returns:** Dict[str, Any]


  #### `optimize_recommendations`

  ```python
  optimize_recommendations(self)
  ```

  Optimize recommendation system based on collected data and feedback

  **Parameters:**

  - `self`



---
