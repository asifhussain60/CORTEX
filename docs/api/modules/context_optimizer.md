# context_optimizer

CORTEX Context Optimizer

Purpose: Optimize context injection for performance and token efficiency.
Achieves 30% token reduction through intelligent context management.

Features:
- Selective tier loading (only load what's needed)
- Pattern relevance scoring (best first)
- Context compression (30% reduction)
- Dynamic sizing (adjust to query)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: Phase 4.3 - Context Optimization


## Table of Contents

### Classes
- [ContextOptimizer](#contextoptimizer)
- [PatternRelevanceScorer](#patternrelevancescorer)
- [ContextCompressor](#contextcompressor)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** datetime, json, math, pathlib, re, typing


## Classes

### ContextOptimizer

```python
class ContextOptimizer
```

Optimizes context injection for performance and token efficiency.

Reduces context size by 30% while maintaining quality through:
1. Selective tier loading
2. Pattern relevance scoring
3. Intelligent compression
4. Dynamic sizing


**Methods:**

  #### `optimize_context`

  ```python
  optimize_context(self, intent: str, query: str, available_tiers: Dict[str, Any]) -> Dict[str, Any]
  ```

  Optimize context for given intent and query.

Args:
    intent: User intent (PLAN, EXECUTE, TEST, etc.)
    query: User query text
    available_tiers: Dict of available tier instances

Returns:
    Optimized context dict with reduced token count

  **Parameters:**

  - `self`
  - `intent` (str): User intent (PLAN, EXECUTE, TEST, etc.)
  - `query` (str): User query text
  - `available_tiers` (Dict[str, Any]): Dict of available tier instances


  **Returns:** Dict[str, Any]
    Optimized context dict with reduced token count



---

### PatternRelevanceScorer

```python
class PatternRelevanceScorer
```

Scores patterns by relevance to current query.

Ranking factors:
1. Keyword match (40%)
2. Recency (30%)
3. Confidence (20%)
4. Usage frequency (10%)


**Methods:**

  #### `score_patterns`

  ```python
  score_patterns(self, patterns: List[Dict], query: str, limit: int) -> List[Dict]
  ```

  Score and rank patterns by relevance.

Args:
    patterns: List of pattern dicts
    query: Search query
    limit: Max patterns to return

Returns:
    Ranked list of patterns with scores

  **Parameters:**

  - `self`
  - `patterns` (List[Dict]): List of pattern dicts
  - `query` (str): Search query
  - `limit` (int) = `10`: Max patterns to return


  **Returns:** List[Dict]
    Ranked list of patterns with scores



---

### ContextCompressor

```python
class ContextCompressor
```

Compresses context by removing redundancy and using references.

Compression techniques:
1. Summarize long content
2. Use references instead of full text
3. Remove duplicate information
4. Compress metadata


**Methods:**

  #### `compress`

  ```python
  compress(self, context: Dict[str, Any], target_reduction: float) -> Tuple[Dict, Dict]
  ```

  Compress context by target percentage.

Args:
    context: Original context dict
    target_reduction: Target reduction (0.30 = 30%)

Returns:
    (compressed_context, compression_stats)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Original context dict
  - `target_reduction` (float) = `0.3`: Target reduction (0.30 = 30%)


  **Returns:** Tuple[Dict, Dict]
    (compressed_context, compression_stats)



---
