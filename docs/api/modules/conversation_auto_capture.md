# conversation_auto_capture

Automatic Conversation Capture System

Automatically captures high-value conversations to Tier 1 working memory.

Purpose:
    - Identify conversations worth preserving
    - Calculate quality scores automatically
    - Capture conversations with metadata
    - Maintain 70-conversation FIFO buffer optimally

Capture Criteria (should_capture_conversation):
    - Length: >10 messages
    - Has code changes: Files modified during conversation
    - Strategic decisions: Architecture, design, planning discussions
    - Problem resolution: Bugs fixed, issues resolved
    - Complexity: Multi-step workflows, agent coordination

Quality Scoring (0-10):
    - Message count (20%): More messages = more context
    - Code changes (25%): Actual implementation work
    - Strategic value (30%): Architecture, patterns, decisions
    - Resolution success (25%): Problems solved

Target: 49+ conversations (70% FIFO capacity) with avg quality 7.5+

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ConversationAutoCapture](#conversationautocapture)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, logging, os, sqlite3, sys, typing


## Classes

### ConversationAutoCapture

```python
class ConversationAutoCapture
```

Automatic conversation capture with quality scoring.

Monitors conversations and automatically captures high-value ones
to Tier 1 working memory with proper metadata and quality scores.


**Methods:**

  #### `should_capture_conversation`

  ```python
  should_capture_conversation(self, messages: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Tuple[bool, float, str]
  ```

  Determine if conversation should be captured.

Criteria (need 3+ to capture):
1. Length >10 messages
2. Has code changes (files modified)
3. Has strategic decisions (keywords: architecture, design, pattern)
4. Has problem resolution (keywords: fix, bug, issue, error)
5. High complexity (multi-agent coordination, TDD workflow)

Args:
    messages: List of conversation messages
    context: Optional context with metadata

Returns:
    Tuple of (should_capture, quality_score, reason)

  **Parameters:**

  - `self`
  - `messages` (List[Dict[str, Any]]): List of conversation messages
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context with metadata


  **Returns:** Tuple[bool, float, str]
    Tuple of (should_capture, quality_score, reason)


  #### `capture_conversation`

  ```python
  capture_conversation(self, conversation_id: str, title: str, messages: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> bool
  ```

  Capture conversation to Tier 1 with quality scoring.

Args:
    conversation_id: Unique conversation ID
    title: Conversation title
    messages: List of conversation messages
    context: Optional conversation context

Returns:
    True if captured successfully

  **Parameters:**

  - `self`
  - `conversation_id` (str): Unique conversation ID
  - `title` (str): Conversation title
  - `messages` (List[Dict[str, Any]]): List of conversation messages
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional conversation context


  **Returns:** bool
    True if captured successfully


  #### `get_capture_stats`

  ```python
  get_capture_stats(self) -> Dict[str, Any]
  ```

  Get conversation capture statistics.

Returns:
    Dictionary with capture stats

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with capture stats



---
