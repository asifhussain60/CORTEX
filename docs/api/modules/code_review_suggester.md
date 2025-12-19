# code_review_suggester

Code Review Suggester - Feature 8 Implementation
CORTEX Orchestrator Enhancement Plan v1.0

Automatic code review suggestions after phase completion.
Integrates with response template system and Brain Tier 1.

Author: Asif Hussain
Created: December 13, 2025


## Table of Contents

### Classes
- [CodeReviewSuggester](#codereviewsuggester)

### Functions
- [suggest_code_review](#suggest_code_review)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, json, pathlib, re, src, typing


## Classes

### CodeReviewSuggester

```python
class CodeReviewSuggester
```

Manages code review suggestions based on phase completion.

Features:
- Trigger-based suggestions (phase-4, phase-5, before-deployment)
- User interaction handling (accept/decline)
- Skip tracking in Brain Tier 1
- Deployment reminders for skipped reviews


**Methods:**

  #### `check_should_suggest`

  ```python
  check_should_suggest(self, context: Dict[str, Any]) -> bool
  ```

  Check if code review should be suggested based on context.

Args:
    context: Phase or event information

Returns:
    True if suggestion should be shown

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Phase or event information


  **Returns:** bool
    True if suggestion should be shown


  #### `format_suggestion_message`

  ```python
  format_suggestion_message(self, context: Dict[str, Any]) -> str
  ```

  Format suggestion message based on context.

Args:
    context: Phase or event information

Returns:
    Formatted suggestion message

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Phase or event information


  **Returns:** str
    Formatted suggestion message


  #### `parse_user_response`

  ```python
  parse_user_response(self, response: str) -> str
  ```

  Parse user response to determine action.

Args:
    response: User's response string

Returns:
    'accept', 'decline', or 'unknown'

  **Parameters:**

  - `self`
  - `response` (str): User's response string


  **Returns:** str
    'accept', 'decline', or 'unknown'


  #### `track_skip_decision`

  ```python
  track_skip_decision(self, context: Dict[str, Any], reason: str) -> bool
  ```

  Track skip decision in Brain Tier 1.

Args:
    context: Phase or event information
    reason: Reason for skipping

Returns:
    True if successfully tracked

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Phase or event information
  - `reason` (str): Reason for skipping


  **Returns:** bool
    True if successfully tracked


  #### `get_deployment_reminder`

  ```python
  get_deployment_reminder(self, context: Dict[str, Any]) -> Optional[str]
  ```

  Get deployment reminder if reviews were skipped.

Args:
    context: Deployment event information

Returns:
    Reminder message or None

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Deployment event information


  **Returns:** Optional[str]
    Reminder message or None


  #### `get_trigger_rules`

  ```python
  get_trigger_rules(self) -> Dict[str, Any]
  ```

  Get all trigger rules for documentation/debugging.

Returns:
    Dictionary of trigger rules

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary of trigger rules



---

## Functions

### suggest_code_review

```python
suggest_code_review(context: Dict[str, Any], brain_path: Optional[Path]) -> Optional[str]
```

Convenience function to check and get code review suggestion.

Args:
    context: Phase or event information
    brain_path: Optional Brain Tier 1 path

Returns:
    Suggestion message or None


**Parameters:**

- `context` (Dict[str, Any]): Phase or event information
- `brain_path` (Optional[Path]) = `None`: Optional Brain Tier 1 path


**Returns:** Optional[str]
  Suggestion message or None


---
