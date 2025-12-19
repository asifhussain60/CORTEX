# tier2_learning

CORTEX 3.0 - Tier 2 Learning Integration for Smart Hints

Purpose: Learn from user acceptance/rejection patterns to improve hint suggestions.
         Adapts quality threshold based on user behavior.

Architecture:
- Tracks user responses (accepted, rejected, ignored)
- Analyzes acceptance patterns by quality level
- Adapts threshold dynamically (6/10 ↔ 8/10 range)
- Stores preferences in Tier 2 knowledge graph
- Implements confidence decay to reduce noise

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [UserResponse](#userresponse)
- [ThresholdRecommendation](#thresholdrecommendation)
- [Tier2LearningIntegration](#tier2learningintegration)

### Functions
- [create_tier2_learning](#create_tier2_learning)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** collections, dataclasses, datetime, json, logging, pathlib, typing


## Classes

### UserResponse

```python
class UserResponse
```

**Decorators:** `dataclass`

User's response to a Smart Hint.


**Attributes:**

- `session_id`: str
- `response`: str
- `quality_score`: int
- `quality_level`: str
- `timestamp`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for JSON serialization.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'UserResponse'
  ```

  Create from dictionary.

  **Parameters:**

  - `cls`
  - `data` (Dict[str, Any])


  **Returns:** 'UserResponse'



---

### ThresholdRecommendation

```python
class ThresholdRecommendation
```

**Decorators:** `dataclass`

Recommendation for threshold adjustment.


**Attributes:**

- `current_threshold`: str
- `recommended_threshold`: str
- `confidence`: float
- `reasoning`: str
- `sample_size`: int



---

### Tier2LearningIntegration

```python
class Tier2LearningIntegration
```

Learns from user hint response patterns and adapts behavior.

Learning Strategy:
- Track acceptance rate by quality level
- If acceptance rate > 70%: Lower threshold (more hints)
- If acceptance rate < 30%: Raise threshold (fewer hints)
- Requires minimum 10 samples before adjusting

Threshold Levels (internal score → quality level):
- EXCELLENT: ≥19 points (strictest)
- GOOD: ≥10 points (default)
- FAIR: ≥2 points (most permissive, not recommended)

Note: We don't go below GOOD in practice (FAIR would be too noisy)


**Methods:**

  #### `record_response`

  ```python
  record_response(self, session_id: str, response: str, quality_score: int, quality_level: str) -> None
  ```

  Record user's response to Smart Hint.

Args:
    session_id: Session identifier
    response: 'accepted', 'rejected', or 'ignored'
    quality_score: Internal quality score
    quality_level: Quality level (EXCELLENT, GOOD, FAIR, LOW)

  **Parameters:**

  - `self`
  - `session_id` (str): Session identifier
  - `response` (str): 'accepted', 'rejected', or 'ignored'
  - `quality_score` (int): Internal quality score
  - `quality_level` (str): Quality level (EXCELLENT, GOOD, FAIR, LOW)


  **Returns:** None


  #### `get_acceptance_rate`

  ```python
  get_acceptance_rate(self, quality_level: Optional[str]) -> float
  ```

  Calculate acceptance rate.

Args:
    quality_level: Optional filter by quality level
    
Returns:
    Acceptance rate (0.0 to 1.0)

  **Parameters:**

  - `self`
  - `quality_level` (Optional[str]) = `None`: Optional filter by quality level


  **Returns:** float
    Acceptance rate (0.0 to 1.0)


  #### `get_response_stats`

  ```python
  get_response_stats(self) -> Dict[str, Any]
  ```

  Get comprehensive response statistics.

Returns:
    Dict with stats by quality level and overall

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with stats by quality level and overall


  #### `recommend_threshold_adjustment`

  ```python
  recommend_threshold_adjustment(self, current_threshold: str) -> Optional[ThresholdRecommendation]
  ```

  Recommend threshold adjustment based on learning.

Args:
    current_threshold: Current quality threshold
    
Returns:
    ThresholdRecommendation or None if insufficient data

  **Parameters:**

  - `self`
  - `current_threshold` (str) = `'GOOD'`: Current quality threshold


  **Returns:** Optional[ThresholdRecommendation]
    ThresholdRecommendation or None if insufficient data


  #### `should_adjust_threshold`

  ```python
  should_adjust_threshold(self, current_threshold: str) -> bool
  ```

  Check if threshold should be adjusted.

Args:
    current_threshold: Current threshold setting
    
Returns:
    True if adjustment recommended

  **Parameters:**

  - `self`
  - `current_threshold` (str) = `'GOOD'`: Current threshold setting


  **Returns:** bool
    True if adjustment recommended


  #### `get_quality_level_preferences`

  ```python
  get_quality_level_preferences(self) -> Dict[str, float]
  ```

  Get user's acceptance rates by quality level.

Returns:
    Dict mapping quality level to acceptance rate

  **Parameters:**

  - `self`


  **Returns:** Dict[str, float]
    Dict mapping quality level to acceptance rate


  #### `reset_learning_data`

  ```python
  reset_learning_data(self) -> None
  ```

  Reset all learning data (for testing or user request).

  **Parameters:**

  - `self`


  **Returns:** None



---

## Functions

### create_tier2_learning

```python
create_tier2_learning(config: Optional[Dict[str, Any]]) -> Tier2LearningIntegration
```

Factory function to create Tier 2 learning integration.

Args:
    config: Optional configuration dict
        - storage_path: Path (default: cortex-brain/tier2/smart-hint-learning.json)
        - min_samples_for_learning: int (default: 10)
        - high_acceptance_threshold: float (default: 0.70)
        - low_acceptance_threshold: float (default: 0.30)
        
Returns:
    Configured Tier2LearningIntegration instance


**Parameters:**

- `config` (Optional[Dict[str, Any]]) = `None`: Optional configuration dict


**Returns:** Tier2LearningIntegration
  Configured Tier2LearningIntegration instance


---
