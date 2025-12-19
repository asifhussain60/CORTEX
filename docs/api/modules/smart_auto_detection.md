# smart_auto_detection

CORTEX 3.0 - Feature 5.3: Smart Auto-Detection Integration

Purpose: Integrates Quality Monitor and Smart Hint Generator with response 
         template system for real-time conversation quality detection.

Architecture:
- Monitors conversation quality in real-time 
- Detects valuable conversations (≥7/10 quality score)
- Automatically generates Smart Hints in response templates
- Integrates with Tier 2 for learning user preferences

Week 4 Deliverable:
- Real-time quality monitoring
- Smart hint insertion in responses
- User feedback learning loop

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [SmartAutoDetection](#smartautodetection)

### Functions
- [create_smart_auto_detection](#create_smart_auto_detection)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, logging, src, typing


## Classes

### SmartAutoDetection

```python
class SmartAutoDetection
```

Feature 5.3: Smart Auto-Detection System

Automatically detects valuable conversations and prompts users
with Smart Hints for conversation capture.

Quality Thresholds (mapped to /10 scale for users):
- EXCELLENT (≥19 internal): 9-10/10 → "exceptional strategic value"
- GOOD (≥10 internal): 7-8/10 → "solid strategic conversation" 
- FAIR (≥2 internal): 4-6/10 → "some value"
- LOW (<2 internal): 1-3/10 → "minimal strategic content"

Default hint threshold: GOOD (≥7/10 user scale, ≥10 internal)


**Methods:**

  #### `start_conversation_monitoring`

  ```python
  start_conversation_monitoring(self, session_id: Optional[str]) -> str
  ```

  Start monitoring a new conversation session.

Args:
    session_id: Optional session ID (auto-generated if not provided)
    
Returns:
    Session ID for tracking

  **Parameters:**

  - `self`
  - `session_id` (Optional[str]) = `None`: Optional session ID (auto-generated if not provided)


  **Returns:** str
    Session ID for tracking


  #### `process_conversation_turn`

  ```python
  process_conversation_turn(self, user_message: str, assistant_response: str) -> Dict[str, Any]
  ```

  Process a conversation turn and check for Smart Hint opportunity.

Args:
    user_message: User's input message
    assistant_response: CORTEX's response
    
Returns:
    Dict containing:
    - should_show_hint: bool
    - hint_content: str (if applicable) 
    - quality_info: dict with score details
    - session_info: dict with session details

  **Parameters:**

  - `self`
  - `user_message` (str): User's input message
  - `assistant_response` (str): CORTEX's response


  **Returns:** Dict[str, Any]
    Dict containing: - should_show_hint: bool - hint_content: str (if applicable) - quality_info: dict with score details - session_info: dict with session details


  #### `record_user_feedback`

  ```python
  record_user_feedback(self, feedback: str, session_id: Optional[str]) -> Dict[str, Any]
  ```

  Record user's response to Smart Hint.

Args:
    feedback: User response ('accepted', 'rejected', 'ignored', 'skip')
    session_id: Session ID (optional if current session active)
    
Returns:
    Dict with confirmation and updated statistics

  **Parameters:**

  - `self`
  - `feedback` (str): User response ('accepted', 'rejected', 'ignored', 'skip')
  - `session_id` (Optional[str]) = `None`: Session ID (optional if current session active)


  **Returns:** Dict[str, Any]
    Dict with confirmation and updated statistics


  #### `end_conversation_monitoring`

  ```python
  end_conversation_monitoring(self) -> Optional[Dict[str, Any]]
  ```

  End current conversation monitoring session.

Returns:
    Session summary or None if no active session

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]
    Session summary or None if no active session


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get system performance statistics.

Returns:
    Dict with detection and user interaction statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with detection and user interaction statistics



---

## Functions

### create_smart_auto_detection

```python
create_smart_auto_detection(config: Optional[Dict[str, Any]]) -> SmartAutoDetection
```

Factory function to create Smart Auto-Detection system.

Args:
    config: Optional configuration dict
        - quality_threshold: str (default: "GOOD")
        - min_turns_before_check: int (default: 5)
        - enable_learning: bool (default: True)
        
Returns:
    Configured SmartAutoDetection instance


**Parameters:**

- `config` (Optional[Dict[str, Any]]) = `None`: Optional configuration dict


**Returns:** SmartAutoDetection
  Configured SmartAutoDetection instance


---
