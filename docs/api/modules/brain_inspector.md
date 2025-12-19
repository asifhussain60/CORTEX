# brain_inspector

Brain Inspector Crawler

Analyzes CORTEX brain state across all tiers (Tier 1, 2, 3).


## Table of Contents

### Classes
- [BrainInspectorCrawler](#braininspectorcrawler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_crawler, datetime, pathlib, sqlite3, typing, yaml


## Classes

### BrainInspectorCrawler

```python
class BrainInspectorCrawler(BaseCrawler)
```

Inspects CORTEX brain to analyze:
- Tier 1: Conversation memory (working memory)
- Tier 2: Knowledge graph (learned patterns)
- Tier 3: Development context (project metrics)
- Brain health and protection rules


**Methods:**

  #### `get_name`

  ```python
  get_name(self) -> str
  ```

  #### `crawl`

  ```python
  crawl(self) -> Dict[str, Any]
  ```

  Analyze CORTEX brain state across all tiers.

Returns:
    Dict containing brain analysis

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing brain analysis



---
