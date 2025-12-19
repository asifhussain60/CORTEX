# natural_language_interface

CORTEX 3.0 - Feature 1: IDEA Capture System - Natural Language Interface

Purpose: Natural language processing for IDEA capture commands integrated
         with CORTEX's Intent Router and Response Template system.

Architecture:
- Pattern recognition: "idea:", "remember:", "task:", "note:"
- Context extraction: Current file, conversation, operation
- Intent routing: Capture vs. retrieval vs. management
- Response templates: User-friendly feedback and confirmation

Integration Points:
- Intent Router: Extends with IDEA-specific patterns
- Response Templates: IDEA capture and management responses
- Context Provider: Active file, line, operation tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [IdeaCommand](#ideacommand)
- [IdeaNaturalLanguageInterface](#ideanaturallanguageinterface)

### Functions
- [create_idea_interface](#create_idea_interface)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, logging, re, src, typing


## Classes

### IdeaCommand

```python
class IdeaCommand
```

**Decorators:** `dataclass`

Parsed idea command with intent and parameters.


**Attributes:**

- `command_type`: str
- `raw_input`: str
- `idea_text`: Optional[str]
- `idea_id`: Optional[str]
- `filter_type`: Optional[str]
- `filter_value`: Optional[str]
- `priority`: Optional[str]



---

### IdeaNaturalLanguageInterface

```python
class IdeaNaturalLanguageInterface
```

Natural language interface for IDEA capture system.

Recognizes patterns like:
- "idea: add rate limiting"
- "remember: fix the bug in auth"
- "task: update documentation"
- "show ideas"
- "show auth ideas" 
- "work on idea 5"
- "complete idea 3"


**Methods:**

  #### `process_input`

  ```python
  process_input(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]
  ```

  Process user input for IDEA-related commands.

Args:
    user_input: Raw user input text
    context: Optional context (active file, conversation, etc.)
    
Returns:
    Dict with processing results:
    - handled: bool (whether this was an IDEA command)
    - command: IdeaCommand object (if handled)
    - response: str (user-friendly response)
    - idea_id: str (if idea was captured)

  **Parameters:**

  - `self`
  - `user_input` (str): Raw user input text
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context (active file, conversation, etc.)


  **Returns:** Dict[str, Any]
    Dict with processing results: - handled: bool (whether this was an IDEA command) - command: IdeaCommand object (if handled) - response: str (user-friendly response) - idea_id: str (if idea was captured)



---

## Functions

### create_idea_interface

```python
create_idea_interface(config: Optional[Dict[str, Any]]) -> IdeaNaturalLanguageInterface
```

Factory function to create IdeaNaturalLanguageInterface.

Args:
    config: Optional configuration dict
        - idea_queue: IdeaQueue instance (optional)
        
Returns:
    Configured IdeaNaturalLanguageInterface instance


**Parameters:**

- `config` (Optional[Dict[str, Any]]) = `None`: Optional configuration dict


**Returns:** IdeaNaturalLanguageInterface
  Configured IdeaNaturalLanguageInterface instance


---
