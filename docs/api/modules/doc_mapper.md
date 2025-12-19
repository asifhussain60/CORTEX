# doc_mapper

Documentation Mapper Crawler

Maps documentation structure and assesses completeness.


## Table of Contents

### Classes
- [DocMapperCrawler](#docmappercrawler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_crawler, pathlib, re, typing


## Classes

### DocMapperCrawler

```python
class DocMapperCrawler(BaseCrawler)
```

Maps documentation to analyze:
- Total documentation files
- Documentation types (user guides, API docs, design docs)
- Documentation coverage
- README quality
- Help system availability


**Methods:**

  #### `get_name`

  ```python
  get_name(self) -> str
  ```

  #### `crawl`

  ```python
  crawl(self) -> Dict[str, Any]
  ```

  Map and analyze documentation structure.

Returns:
    Dict containing documentation analysis

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing documentation analysis



---
