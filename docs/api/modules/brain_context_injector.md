# brain_context_injector

Brain Context Injector

Lightweight context injection system for brain-assisted responses.
Queries all 3 brain tiers and returns relevant context with performance <100ms.

Responsibilities:
- Inject context from Tier 1 (recent conversations)
- Inject context from Tier 2 (learned patterns)
- Inject context from Tier 3 (development metrics)
- Rank results by relevance
- Manage token budgets
- Performance monitoring

Usage:
    >>> from src.tier0.brain_context_injector import BrainContextInjector
    >>> injector = BrainContextInjector(brain_path="/path/to/cortex-brain")
    >>> context = injector.inject_full_context("implement authentication")
    >>> print(f"Loaded {context['tier1']['conversation_count']} conversations")

Author: Asif Hussain
Phase: 7.4 - Context Injection System


## Table of Contents

### Classes
- [BrainContextInjector](#braincontextinjector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, pathlib, sqlite3, time, typing


## Classes

### BrainContextInjector

```python
class BrainContextInjector
```

Injects context from all 3 brain tiers for brain-assisted responses.

Provides fast (<100ms) multi-tier context loading with relevance ranking.


**Methods:**

  #### `inject_tier1_context`

  ```python
  inject_tier1_context(self, user_request: str, max_conversations: int) -> Dict[str, Any]
  ```

  Inject context from Tier 1 (Working Memory).

Loads recent conversations and ranks them by relevance to user request.

Args:
    user_request: User's current request
    max_conversations: Maximum conversations to return
    
Returns:
    Dict with conversations, count, and metadata

  **Parameters:**

  - `self`
  - `user_request` (str): User's current request
  - `max_conversations` (int) = `5`: Maximum conversations to return


  **Returns:** Dict[str, Any]
    Dict with conversations, count, and metadata


  #### `inject_tier2_context`

  ```python
  inject_tier2_context(self, user_request: str, max_patterns: int) -> Dict[str, Any]
  ```

  Inject context from Tier 2 (Knowledge Graph).

Loads relevant learned patterns ranked by relevance.

Args:
    user_request: User's current request
    max_patterns: Maximum patterns to return
    
Returns:
    Dict with patterns, count, and metadata

  **Parameters:**

  - `self`
  - `user_request` (str): User's current request
  - `max_patterns` (int) = `5`: Maximum patterns to return


  **Returns:** Dict[str, Any]
    Dict with patterns, count, and metadata


  #### `inject_tier3_context`

  ```python
  inject_tier3_context(self, current_file: Optional[str]) -> Dict[str, Any]
  ```

  Inject context from Tier 3 (Development Context).

Loads file metrics and git activity for current file if provided,
or general project metrics otherwise.

Args:
    current_file: Current file being worked on
    
Returns:
    Dict with file metrics and git activity

  **Parameters:**

  - `self`
  - `current_file` (Optional[str]) = `None`: Current file being worked on


  **Returns:** Dict[str, Any]
    Dict with file metrics and git activity


  #### `inject_full_context`

  ```python
  inject_full_context(self, user_request: str, current_file: Optional[str], max_tokens: int) -> Dict[str, Any]
  ```

  Inject context from all 3 tiers.

Performance target: <100ms for full context injection.

Args:
    user_request: User's current request
    current_file: Current file being worked on
    max_tokens: Maximum tokens to return (for budget management)
    
Returns:
    Dict with tier1, tier2, tier3 contexts and performance metrics

  **Parameters:**

  - `self`
  - `user_request` (str): User's current request
  - `current_file` (Optional[str]) = `None`: Current file being worked on
  - `max_tokens` (int) = `500`: Maximum tokens to return (for budget management)


  **Returns:** Dict[str, Any]
    Dict with tier1, tier2, tier3 contexts and performance metrics



---
