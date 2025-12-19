# smart_hint_integration

CORTEX 3.0 - Smart Hint Integration

Purpose: Integration layer for conversation capture workflow.
Provides unified interface for quality analysis, hint generation, and vault storage.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [SmartHintSystem](#smarthintsystem)

### Functions
- [get_smart_hint_system](#get_smart_hint_system)
- [analyze_response_for_hint](#analyze_response_for_hint)
- [capture_current_conversation](#capture_current_conversation)


## Overview

- **Classes:** 1
- **Functions:** 3
- **Dependencies:** datetime, os, pathlib, src, typing


## Classes

### SmartHintSystem

```python
class SmartHintSystem
```

Unified interface for CORTEX 3.0 smart hint conversation capture.

Workflow:
1. Analyze conversation quality (semantic scoring)
2. Generate hint if quality threshold met
3. On user request, capture to vault
4. Return hint text for display in response

Usage:
```python
system = SmartHintSystem()

# After generating response
hint = system.analyze_and_generate_hint(user_prompt, assistant_response)

if hint.should_show:
    print(hint.hint_text)  # Display to user

# When user says "capture conversation"
filepath = system.capture_conversation(
    user_prompt, 
    assistant_response,
    hint.conversation_id
)
```


**Methods:**

  #### `analyze_and_generate_hint`

  ```python
  analyze_and_generate_hint(self, user_prompt: str, assistant_response: str) -> SmartHint
  ```

  Analyze conversation and generate hint if needed.

Args:
    user_prompt: User's input
    assistant_response: CORTEX's response
    
Returns:
    SmartHint with conditional display

  **Parameters:**

  - `self`
  - `user_prompt` (str): User's input
  - `assistant_response` (str): CORTEX's response


  **Returns:** SmartHint
    SmartHint with conditional display


  #### `capture_conversation`

  ```python
  capture_conversation(self, user_prompt: str, assistant_response: str, conversation_id: Optional[str]) -> Tuple[Path, ConversationMetadata]
  ```

  Capture conversation to vault.

Args:
    user_prompt: User's input
    assistant_response: CORTEX's response
    conversation_id: Optional ID (uses current if not provided)
    
Returns:
    Tuple of (filepath, metadata)

  **Parameters:**

  - `self`
  - `user_prompt` (str): User's input
  - `assistant_response` (str): CORTEX's response
  - `conversation_id` (Optional[str]) = `None`: Optional ID (uses current if not provided)


  **Returns:** Tuple[Path, ConversationMetadata]
    Tuple of (filepath, metadata)


  #### `capture_multi_turn_conversation`

  ```python
  capture_multi_turn_conversation(self, turns: list[Tuple[str, str]], topic: str) -> Tuple[Path, ConversationMetadata]
  ```

  Capture multi-turn conversation.

Args:
    turns: List of (user_prompt, assistant_response) tuples
    topic: Conversation topic/title
    
Returns:
    Tuple of (filepath, metadata)

  **Parameters:**

  - `self`
  - `turns` (list[Tuple[str, str]]): List of (user_prompt, assistant_response) tuples
  - `topic` (str): Conversation topic/title


  **Returns:** Tuple[Path, ConversationMetadata]
    Tuple of (filepath, metadata)


  #### `get_vault_stats`

  ```python
  get_vault_stats(self) -> Dict
  ```

  Get vault statistics.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `list_recent_conversations`

  ```python
  list_recent_conversations(self, limit: int) -> list
  ```

  List recent captured conversations.

  **Parameters:**

  - `self`
  - `limit` (int) = `5`


  **Returns:** list



---

## Functions

### get_smart_hint_system

```python
get_smart_hint_system(config: Dict) -> SmartHintSystem
```

Get or create global SmartHintSystem instance.

Args:
    config: Optional configuration
    
Returns:
    SmartHintSystem instance


**Parameters:**

- `config` (Dict) = `None`: Optional configuration


**Returns:** SmartHintSystem
  SmartHintSystem instance


---

### analyze_response_for_hint

```python
analyze_response_for_hint(user_prompt: str, assistant_response: str) -> Optional[str]
```

Convenience function for use in response templates.

Returns hint text if should be shown, None otherwise.

Args:
    user_prompt: User's message
    assistant_response: Assistant's response
    
Returns:
    Hint text or None


**Parameters:**

- `user_prompt` (str): User's message
- `assistant_response` (str): Assistant's response


**Returns:** Optional[str]
  Hint text or None


---

### capture_current_conversation

```python
capture_current_conversation(user_prompt: str, assistant_response: str) -> str
```

Convenience function to capture conversation.

Returns confirmation message.

Args:
    user_prompt: User's message
    assistant_response: Assistant's response
    
Returns:
    Confirmation message with filepath


**Parameters:**

- `user_prompt` (str): User's message
- `assistant_response` (str): Assistant's response


**Returns:** str
  Confirmation message with filepath


---
