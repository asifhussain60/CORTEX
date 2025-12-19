# ml_context_optimizer

CORTEX Tier 1: ML Context Optimizer
ML-powered context compression using TF-IDF relevance scoring.

Inspired by Cortex Token Optimizer's proven 76% token reduction success.
Achieves 50-70% token reduction while maintaining conversation quality.


## Table of Contents

### Classes
- [MLContextOptimizer](#mlcontextoptimizer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, numpy, sklearn, typing


## Classes

### MLContextOptimizer

```python
class MLContextOptimizer
```

ML-powered context compression using TF-IDF relevance scoring.

Achieves 50-70% token reduction while maintaining conversation quality (>0.9).
Based on Cortex Token Optimizer's proven ML engine approach.

Key Features:
- TF-IDF vectorization for relevance scoring
- Conversation context compression (50-70% reduction)
- Pattern context compression
- Quality scoring (maintains >0.9 quality)
- Performance: <50ms optimization overhead


**Methods:**

  #### `optimize_conversation_context`

  ```python
  optimize_conversation_context(self, conversations: List[Dict[str, Any]], current_intent: str, min_conversations: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]
  ```

  Compress conversation history to most relevant content.

Args:
    conversations: List of conversation dicts with messages
    current_intent: Current user request for relevance scoring
    min_conversations: Minimum conversations to keep (default: 3)

Returns:
    Tuple of (optimized_conversations, metrics)
    
Example:
    >>> optimizer = MLContextOptimizer(target_reduction=0.6)
    >>> conversations = [
    ...     {"id": "1", "messages": [{"content": "Hello"}]},
    ...     {"id": "2", "messages": [{"content": "Debug error"}]},
    ... ]
    >>> optimized, metrics = optimizer.optimize_conversation_context(
    ...     conversations, "Fix the bug"
    ... )
    >>> print(f"Reduced by {metrics['reduction_percentage']:.1f}%")

  **Parameters:**

  - `self`
  - `conversations` (List[Dict[str, Any]]): List of conversation dicts with messages
  - `current_intent` (str): Current user request for relevance scoring
  - `min_conversations` (int) = `3`: Minimum conversations to keep (default: 3)


  **Returns:** Tuple[List[Dict[str, Any]], Dict[str, Any]]
    Tuple of (optimized_conversations, metrics)


  #### `optimize_pattern_context`

  ```python
  optimize_pattern_context(self, patterns: List[Dict[str, Any]], query: str, max_patterns: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]
  ```

  Compress knowledge graph patterns to most relevant subset.

Args:
    patterns: List of pattern dicts from Tier 2
    query: Current query for relevance scoring
    max_patterns: Maximum patterns to return (default: 20)

Returns:
    Tuple of (optimized_patterns, metrics)
    
Example:
    >>> optimizer = MLContextOptimizer()
    >>> patterns = [
    ...     {"description": "Error handling pattern", "confidence": 0.9},
    ...     {"description": "Testing pattern", "confidence": 0.8},
    ... ]
    >>> optimized, metrics = optimizer.optimize_pattern_context(
    ...     patterns, "Fix error handling", max_patterns=10
    ... )

  **Parameters:**

  - `self`
  - `patterns` (List[Dict[str, Any]]): List of pattern dicts from Tier 2
  - `query` (str): Current query for relevance scoring
  - `max_patterns` (int) = `20`: Maximum patterns to return (default: 20)


  **Returns:** Tuple[List[Dict[str, Any]], Dict[str, Any]]
    Tuple of (optimized_patterns, metrics)


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get optimizer statistics.

Returns:
    Dict with optimization statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with optimization statistics



---
