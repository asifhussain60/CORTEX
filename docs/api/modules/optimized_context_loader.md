# optimized_context_loader

Optimized Context Loader

Purpose: Integration layer between CORTEX orchestrator and context optimizer.
Provides optimized context loading with 30% token reduction.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: Phase 4.3 - Context Optimization


## Table of Contents

### Classes
- [OptimizedContextLoader](#optimizedcontextloader)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** context_optimizer, json, pathlib, typing


## Classes

### OptimizedContextLoader

```python
class OptimizedContextLoader
```

Loads and optimizes context for CORTEX orchestrator.

Features:
- Selective tier loading (only what's needed)
- Pattern relevance scoring (best matches first)
- Context compression (30% reduction)
- Dynamic sizing (adjust to query)

Usage:
    loader = OptimizedContextLoader(brain_dir)
    context = loader.load_optimized_context(
        intent="PLAN",
        query="refactor authentication module",
        available_tiers={
            "tier0": instinct_handler,
            "tier1": working_memory,
            "tier2": knowledge_graph,
            "tier3": dev_context
        }
    )


**Methods:**

  #### `load_optimized_context`

  ```python
  load_optimized_context(self, intent: str, query: str, available_tiers: Dict[str, Any], compression_enabled: bool) -> Dict[str, Any]
  ```

  Load optimized context for given intent and query.

Args:
    intent: User intent (PLAN, EXECUTE, TEST, etc.)
    query: User query text
    available_tiers: Dict of available tier instances
    compression_enabled: Enable compression (default True)

Returns:
    Optimized context dict with metadata

  **Parameters:**

  - `self`
  - `intent` (str): User intent (PLAN, EXECUTE, TEST, etc.)
  - `query` (str): User query text
  - `available_tiers` (Dict[str, Any]): Dict of available tier instances
  - `compression_enabled` (bool) = `True`: Enable compression (default True)


  **Returns:** Dict[str, Any]
    Optimized context dict with metadata


  #### `get_metrics`

  ```python
  get_metrics(self) -> Dict[str, Any]
  ```

  Get performance metrics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `reset_metrics`

  ```python
  reset_metrics(self)
  ```

  Reset performance metrics

  **Parameters:**

  - `self`



---
