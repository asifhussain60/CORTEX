# git_analyzer

Git Analyzer Crawler

Extracts development history and activity patterns from Git.


## Table of Contents

### Classes
- [GitAnalyzerCrawler](#gitanalyzercrawler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_crawler, datetime, pathlib, subprocess, typing


## Classes

### GitAnalyzerCrawler

```python
class GitAnalyzerCrawler(BaseCrawler)
```

Analyzes Git repository to extract:
- Total commits, branches, contributors
- Recent activity patterns
- Hot files (most changed)
- Branch health


**Methods:**

  #### `get_name`

  ```python
  get_name(self) -> str
  ```

  #### `crawl`

  ```python
  crawl(self) -> Dict[str, Any]
  ```

  Analyze Git repository history and activity.

Returns:
    Dict containing Git analysis

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing Git analysis



---
