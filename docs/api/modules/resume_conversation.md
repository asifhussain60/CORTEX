# resume_conversation

CORTEX Operation: Resume Conversation
Resume previous conversation from new chat session

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [ResumeConversationOperation](#resumeconversationoperation)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** json, logging, pathlib, re, typing


## Classes

### ResumeConversationOperation

```python
class ResumeConversationOperation
```

Resume conversation from new chat session

Features:
    - Keyword-based conversation search
    - Multiple match selection
    - Auto-resume for single matches
    - Planning document opening
    - Full context restoration
    - Next steps suggestions

Usage:
    operation = ResumeConversationOperation(conversation_manager)
    result = operation.execute("resume authentication work")


**Methods:**

  #### `execute`

  ```python
  execute(self, user_query: str) -> Dict[str, Any]
  ```

  Resume conversation based on user query

Args:
    user_query: Natural language query (e.g., "resume authentication work")
    
Returns:
    Resume context dictionary with:
        - action: 'resumed', 'select_conversation', or 'error'
        - conversation_id: ID of resumed conversation (if resumed)
        - title: Conversation title
        - summary: Generated summary
        - recent_messages: Last 5 messages
        - entities: Entities discussed
        - files: Files modified
        - next_steps: Suggested next steps
        - options: List of conversations to choose from (if select_conversation)
        - error: Error message (if error)

  **Parameters:**

  - `self`
  - `user_query` (str): Natural language query (e.g., "resume authentication work")


  **Returns:** Dict[str, Any]
    Resume context dictionary with: - action: 'resumed', 'select_conversation', or 'error' - conversation_id: ID of resumed conversation (if resumed) - title: Conversation title - summary: Generated summary - recent_messages: Last 5 messages - entities: Entities discussed - files: Files modified - next_steps: Suggested next steps - options: List of conversations to choose from (if select_conversation) - error: Error message (if error)


  #### `resume_by_id`

  ```python
  resume_by_id(self, conversation_id: str) -> Dict[str, Any]
  ```

  Resume specific conversation by ID

Args:
    conversation_id: Conversation ID to resume
    
Returns:
    Resume context dictionary

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID to resume


  **Returns:** Dict[str, Any]
    Resume context dictionary



---
