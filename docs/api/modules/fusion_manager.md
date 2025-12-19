# fusion_manager

CORTEX 3.0 Milestone 2 - Fusion Integration API

Simple integration layer that makes temporal correlation features
accessible through WorkingMemory and provides higher-level fusion
operations for the dual-channel memory system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [FusionManager](#fusionmanager)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, temporal_correlator, typing


## Classes

### FusionManager

```python
class FusionManager
```

High-level API for CORTEX 3.0 dual-channel memory fusion operations.

Provides simple methods to correlate conversations with ambient events,
generate development narratives, and create unified timelines.


**Methods:**

  #### `correlate_imported_conversation`

  ```python
  correlate_imported_conversation(self, conversation_id: str, auto_correlate: bool) -> Dict[str, Any]
  ```

  Correlate an imported conversation with ambient events.

Args:
    conversation_id: ID of imported conversation
    auto_correlate: If True, run correlation automatically
    
Returns:
    Correlation summary with results and statistics

  **Parameters:**

  - `self`
  - `conversation_id` (str): ID of imported conversation
  - `auto_correlate` (bool) = `True`: If True, run correlation automatically


  **Returns:** Dict[str, Any]
    Correlation summary with results and statistics


  #### `get_conversation_development_story`

  ```python
  get_conversation_development_story(self, conversation_id: str) -> Dict[str, Any]
  ```

  Generate complete development story for a conversation.

Combines conversation content with correlated ambient events
to create a narrative that shows both the planning (WHY) and
execution (WHAT) sides of development.

Args:
    conversation_id: ID of conversation to narrate
    
Returns:
    Development story with timeline and narrative

  **Parameters:**

  - `self`
  - `conversation_id` (str): ID of conversation to narrate


  **Returns:** Dict[str, Any]
    Development story with timeline and narrative


  #### `get_fusion_insights`

  ```python
  get_fusion_insights(self, conversation_id: str, include_recommendations: bool) -> Dict[str, Any]
  ```

  Generate fusion insights for a conversation.

Analyzes correlation patterns to provide insights about
development effectiveness, plan execution, and areas for improvement.

Args:
    conversation_id: ID of conversation to analyze
    include_recommendations: If True, include actionable recommendations
    
Returns:
    Fusion insights and recommendations

  **Parameters:**

  - `self`
  - `conversation_id` (str): ID of conversation to analyze
  - `include_recommendations` (bool) = `True`: If True, include actionable recommendations


  **Returns:** Dict[str, Any]
    Fusion insights and recommendations



---
