# plugin_registry

Plugin Registry Crawler

Inventories CORTEX plugin ecosystem and capabilities.


## Table of Contents

### Classes
- [PluginRegistryCrawler](#pluginregistrycrawler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_crawler, importlib, pathlib, sys, typing


## Classes

### PluginRegistryCrawler

```python
class PluginRegistryCrawler(BaseCrawler)
```

Inventories CORTEX plugin system to analyze:
- Registered plugins (active/inactive)
- Natural language patterns
- Command registry entries
- Plugin health and initialization


**Methods:**

  #### `get_name`

  ```python
  get_name(self) -> str
  ```

  #### `crawl`

  ```python
  crawl(self) -> Dict[str, Any]
  ```

  Inventory plugin ecosystem.

Returns:
    Dict containing plugin analysis

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing plugin analysis



---
