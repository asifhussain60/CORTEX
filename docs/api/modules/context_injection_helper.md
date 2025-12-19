# context_injection_helper

CORTEX Context Injection Helper

Simplified interface for injecting Tier 1 context at CORTEX entry points.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents


### Functions
- [get_context_injector](#get_context_injector)
- [inject_tier1_context](#inject_tier1_context)
- [inject_full_context](#inject_full_context)
- [resolve_pronoun_only](#resolve_pronoun_only)
- [get_context_display](#get_context_display)
- [get_last_injection_time](#get_last_injection_time)
- [is_injection_performance_ok](#is_injection_performance_ok)


## Overview

- **Classes:** 0
- **Functions:** 7
- **Dependencies:** logging, src, typing


## Functions

### get_context_injector

```python
get_context_injector() -> ContextInjector
```

Get or create global context injector instance


**Returns:** ContextInjector


---

### inject_tier1_context

```python
inject_tier1_context(user_request: str, conversation_id: Optional[str]) -> Dict
```

Inject Tier 1 context with automatic pronoun resolution

This is the simplified interface for CORTEX entry points.
Use this at the start of request processing to:
- Load recent conversations
- Extract active entities
- Resolve pronouns ("it" → actual entity)
- Get formatted context summary

Args:
    user_request: User's request text
    conversation_id: Optional conversation UUID

Returns:
    {
        'resolved_request': str,  # Request with pronouns resolved
        'formatted_summary': str,  # Token-efficient context (<500 tokens)
        'active_entities': {...},  # Files, classes, methods, UI components
        'context_display': str,  # User-friendly summary for display
        'injection_time_ms': float  # Performance metric
    }

Example:
    >>> context = inject_tier1_context("Make it purple")
    >>> print(context['resolved_request'])
    "Make the FAB button purple"
    
    >>> print(context['context_display'])
    🧠 **Context Loaded**
    
    📚 **Recent Work:**
       • Added purple FAB button to dashboard
    
    📄 **Active Files:**
       • Dashboard.tsx
       • styles.css


**Parameters:**

- `user_request` (str): User's request text
- `conversation_id` (Optional[str]) = `None`: Optional conversation UUID


**Returns:** Dict
  { 'resolved_request': str,  # Request with pronouns resolved 'formatted_summary': str,  # Token-efficient context (<500 tokens) 'active_entities': {...},  # Files, classes, methods, UI components 'context_display': str,  # User-friendly summary for display 'injection_time_ms': float  # Performance metric }


---

### inject_full_context

```python
inject_full_context(user_request: str, conversation_id: Optional[str], current_file: Optional[str]) -> Dict
```

Inject context from all tiers (1, 2, 3)

Use this for complex operations that benefit from:
- Tier 1: Recent conversations + entities
- Tier 2: Pattern matching from knowledge graph
- Tier 3: Development metrics and git analysis

Args:
    user_request: User's request text
    conversation_id: Optional conversation UUID
    current_file: Optional current file path (for namespace detection)

Returns:
    Complete context from all tiers with performance metrics


**Parameters:**

- `user_request` (str): User's request text
- `conversation_id` (Optional[str]) = `None`: Optional conversation UUID
- `current_file` (Optional[str]) = `None`: Optional current file path (for namespace detection)


**Returns:** Dict
  Complete context from all tiers with performance metrics


---

### resolve_pronoun_only

```python
resolve_pronoun_only(user_request: str) -> str
```

Quick pronoun resolution without full context injection

Use when you only need pronoun resolution (e.g., in message preprocessing)

Args:
    user_request: User's request text

Returns:
    Request with pronouns resolved

Example:
    >>> resolve_pronoun_only("Make it bigger")
    "Make the FAB button bigger"


**Parameters:**

- `user_request` (str): User's request text


**Returns:** str
  Request with pronouns resolved


---

### get_context_display

```python
get_context_display(user_request: str) -> str
```

Get formatted context display for showing to user

Use this to display what CORTEX "remembers" from recent work

Args:
    user_request: User's request text

Returns:
    Formatted context summary with emojis (ready for display)

Example:
    >>> print(get_context_display("Continue work"))
    🧠 **Context Loaded**
    
    📚 **Recent Work:**
       • Added authentication system
    
    📄 **Active Files:**
       • AuthService.cs


**Parameters:**

- `user_request` (str): User's request text


**Returns:** str
  Formatted context summary with emojis (ready for display)


---

### get_last_injection_time

```python
get_last_injection_time() -> float
```

Get the time taken for last context injection (in ms)


**Returns:** float


---

### is_injection_performance_ok

```python
is_injection_performance_ok() -> bool
```

Check if last injection was within performance target (<200ms)


**Returns:** bool


---
