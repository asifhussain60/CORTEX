# context_formatter

CORTEX Tier 1 Context Formatter

Converts raw Tier 1 conversation data into LLM-friendly, token-efficient summaries.

Key Responsibilities:
- Format recent conversations into concise summaries (<500 tokens)
- Extract active entities (files, classes, methods) for pronoun resolution
- Resolve pronouns ("it", "that", "this") to actual entities
- Provide temporal context (when work was done)
- Identify current work context

Performance Target: <50ms formatting time

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ContextFormatter](#contextformatter)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, re, typing


## Classes

### ContextFormatter

```python
class ContextFormatter
```

Formats Tier 1 conversation data into token-efficient LLM context

Token Budget: <500 tokens per injection
- Recent conversations: ~300 tokens (3-5 conversations)
- Active entities: ~100 tokens
- Current task: ~100 tokens


**Methods:**

  #### `format_recent_conversations`

  ```python
  format_recent_conversations(self, conversations: List[Dict]) -> str
  ```

  Convert recent conversations into concise summary

Args:
    conversations: List of conversation dicts from Tier 1
        [
            {
                'conversation_id': 'conv_123',
                'summary': 'Added authentication system',
                'created_at': '2025-11-17T14:30:00',
                'entities': ['AuthService.cs', 'LoginController.cs'],
                'intent': 'EXECUTE',
                'status': 'in_progress'
            },
            ...
        ]

Returns:
    Formatted string like:
    ---
    Recent Work Context (Last 5 Conversations):
    
    1. [2 hours ago] Added authentication system
       Files: AuthService.cs, LoginController.cs
       Status: In progress (Phase 2 of 4)
    
    2. [Yesterday] Fixed null reference bug
       Files: UserRepository.cs
       Status: Complete, tests passing
    ---

  **Parameters:**

  - `self`
  - `conversations` (List[Dict]): List of conversation dicts from Tier 1 [ {


  **Returns:** str
    Formatted string like: --- Recent Work Context (Last 5 Conversations): 1. [2 hours ago] Added authentication system Files: AuthService.cs, LoginController.cs Status: In progress (Phase 2 of 4) 2. [Yesterday] Fixed null reference bug Files: UserRepository.cs Status: Complete, tests passing ---


  #### `extract_active_entities`

  ```python
  extract_active_entities(self, conversations: List[Dict]) -> Dict[str, Any]
  ```

  Identify files/classes/methods actively being worked on

Args:
    conversations: Recent conversations from Tier 1

Returns:
    {
        'files': ['AuthService.cs', 'LoginController.cs'],
        'classes': ['AuthService', 'JwtTokenGenerator'],
        'methods': ['ValidateCredentials', 'GenerateToken'],
        'ui_components': ['FAB button', 'login form'],
        'current_task': 'Phase 2: JWT implementation',
        'most_recent_entity': 'AuthService.cs'  # For "it" resolution
    }

  **Parameters:**

  - `self`
  - `conversations` (List[Dict]): Recent conversations from Tier 1


  **Returns:** Dict[str, Any]
    { 'files': ['AuthService.cs', 'LoginController.cs'], 'classes': ['AuthService', 'JwtTokenGenerator'], 'methods': ['ValidateCredentials', 'GenerateToken'], 'ui_components': ['FAB button', 'login form'], 'current_task': 'Phase 2: JWT implementation', 'most_recent_entity': 'AuthService.cs'  # For "it" resolution }


  #### `resolve_pronouns`

  ```python
  resolve_pronouns(self, user_request: str, active_entities: Dict) -> str
  ```

  Resolve "it", "that", "this" to actual entities

Args:
    user_request: User's request text
    active_entities: Dict from extract_active_entities()

Returns:
    Modified request with pronouns resolved

Examples:
    Input: "Make it purple"
    Active entities: {'most_recent_entity': 'FAB button'}
    Output: "Make the FAB button purple"
    
    Input: "Refactor that"
    Active entities: {'most_recent_entity': 'AuthService.cs'}
    Output: "Refactor AuthService.cs"

  **Parameters:**

  - `self`
  - `user_request` (str): User's request text
  - `active_entities` (Dict): Dict from extract_active_entities()


  **Returns:** str
    Modified request with pronouns resolved


  #### `format_context_summary`

  ```python
  format_context_summary(self, conversations: List[Dict], active_entities: Dict, include_header: bool) -> str
  ```

  Create complete context summary for display to user

Args:
    conversations: Recent conversations
    active_entities: Extracted entities
    include_header: Whether to include emoji header

Returns:
    Formatted summary string ready for display

  **Parameters:**

  - `self`
  - `conversations` (List[Dict]): Recent conversations
  - `active_entities` (Dict): Extracted entities
  - `include_header` (bool) = `True`: Whether to include emoji header


  **Returns:** str
    Formatted summary string ready for display



---
