# feedback_agent

Feedback Agent - Issue #3 Fix (P0)
Purpose: Collect structured user feedback about CORTEX issues and improvements
Created: 2025-11-23
Author: Asif Hussain


## Table of Contents

### Classes
- [FeedbackAgent](#feedbackagent)

### Functions
- [handle_feedback_command](#handle_feedback_command)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, feedback, json, pathlib, src, sys, typing, uuid


## Classes

### FeedbackAgent

```python
class FeedbackAgent
```

Handles feedback command routing and structured report generation.
Implements Issue #3 Fix - Missing feedback entry point.


**Methods:**

  #### `create_feedback_report`

  ```python
  create_feedback_report(self, user_input: str, feedback_type: str, severity: str, context: Optional[Dict[str, Any]], auto_upload: bool) -> Dict[str, Any]
  ```

  Create structured feedback report in documents/reports/

Args:
    user_input: User's feedback description
    feedback_type: Type of feedback (bug, gap, improvement, question)
    severity: Severity level (critical, high, medium, low)
    context: Optional context (files, conversation_id, etc.)
    auto_upload: Automatically upload to GitHub Gist (default: True)
    
Returns:
    Dictionary with report metadata and file path

  **Parameters:**

  - `self`
  - `user_input` (str): User's feedback description
  - `feedback_type` (str) = `'general'`: Type of feedback (bug, gap, improvement, question)
  - `severity` (str) = `'medium'`: Severity level (critical, high, medium, low)
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context (files, conversation_id, etc.)
  - `auto_upload` (bool) = `True`: Automatically upload to GitHub Gist (default: True)


  **Returns:** Dict[str, Any]
    Dictionary with report metadata and file path



---

## Functions

### handle_feedback_command

```python
handle_feedback_command(user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]
```

Entry point for feedback command handling.

Args:
    user_input: User's feedback text
    context: Optional context dictionary
    
Returns:
    Result dictionary with success status and file path


**Parameters:**

- `user_input` (str): User's feedback text
- `context` (Optional[Dict[str, Any]]) = `None`: Optional context dictionary


**Returns:** Dict[str, Any]
  Result dictionary with success status and file path


---
