# conversation_capture_module

Conversation Capture Module

Enables manual conversation capture to Tier 1 Working Memory via natural language commands.

Natural Language Triggers:
- "remember this"
- "capture conversation" 
- "save chat"
- "store this conversation"
- "save context"

SOLID Principles:
- Single Responsibility: Only handles manual conversation capture
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on abstractions (WorkingMemory interface)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ConversationCaptureModule](#conversationcapturemodule)

### Functions
- [capture_conversation](#capture_conversation)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, pathlib, re, src, typing, uuid


## Classes

### ConversationCaptureModule

```python
class ConversationCaptureModule(BaseOperationModule)
```

Captures current conversation to Tier 1 Working Memory on user request.

Responsibilities:
1. Detect natural language capture triggers
2. Extract conversation history from context
3. Identify entities (files, classes, methods)
4. Detect conversation intent (PLAN, EXECUTE, FIX, etc.)
5. Store to Tier 1 database
6. Return confirmation with conversation ID


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]
  ```

  Validate prerequisites for conversation capture.

Checks:
1. Brain initialized (Tier 1 database exists)
2. User request contains capture trigger
3. Conversation history available in context

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `should_capture`

  ```python
  should_capture(self, user_request: str) -> bool
  ```

  Check if user request contains a capture trigger.

Args:
    user_request: The user's input text
    
Returns:
    True if capture was requested, False otherwise

  **Parameters:**

  - `self`
  - `user_request` (str): The user's input text


  **Returns:** bool
    True if capture was requested, False otherwise


  #### `detect_intent`

  ```python
  detect_intent(self, conversation_text: str) -> str
  ```

  Detect the primary intent of the conversation.

Args:
    conversation_text: Combined text from all messages
    
Returns:
    Intent string (PLAN, EXECUTE, FIX, etc.) or 'GENERAL'

  **Parameters:**

  - `self`
  - `conversation_text` (str): Combined text from all messages


  **Returns:** str
    Intent string (PLAN, EXECUTE, FIX, etc.) or 'GENERAL'


  #### `extract_entities`

  ```python
  extract_entities(self, conversation_text: str) -> Dict[str, List[str]]
  ```

  Extract entities (files, classes, methods) from conversation.

Args:
    conversation_text: Combined text from all messages
    
Returns:
    Dict with entity categories and lists of entity names

  **Parameters:**

  - `self`
  - `conversation_text` (str): Combined text from all messages


  **Returns:** Dict[str, List[str]]
    Dict with entity categories and lists of entity names


  #### `create_conversation_summary`

  ```python
  create_conversation_summary(self, conversation_history: List[Dict[str, str]], max_length: int) -> str
  ```

  Create a concise summary of the conversation.

Args:
    conversation_history: List of message dicts with 'role' and 'content'
    max_length: Maximum summary length in characters
    
Returns:
    Summary string

  **Parameters:**

  - `self`
  - `conversation_history` (List[Dict[str, str]]): List of message dicts with 'role' and 'content'
  - `max_length` (int) = `200`: Maximum summary length in characters


  **Returns:** str
    Summary string


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute conversation capture.

Steps:
1. Extract conversation history from context
2. Generate conversation ID
3. Extract entities from conversation
4. Detect conversation intent
5. Create summary
6. Store to Tier 1 database
7. Return confirmation

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---

## Functions

### capture_conversation

```python
capture_conversation(user_request: str, conversation_history: List[Dict[str, str]], project_root: Optional[Path]) -> Dict[str, Any]
```

Convenience function to capture a conversation.

Args:
    user_request: The user's request (checked for capture trigger)
    conversation_history: List of messages with 'role' and 'content'
    project_root: Project root path (defaults to current directory)
    
Returns:
    Dict with capture results or None if capture not requested


**Parameters:**

- `user_request` (str): The user's request (checked for capture trigger)
- `conversation_history` (List[Dict[str, str]]): List of messages with 'role' and 'content'
- `project_root` (Optional[Path]) = `None`: Project root path (defaults to current directory)


**Returns:** Dict[str, Any]
  Dict with capture results or None if capture not requested


---
