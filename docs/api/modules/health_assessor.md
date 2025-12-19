# health_assessor

Health Assessor Crawler

Evaluates overall project health and provides recommendations.


## Table of Contents

### Classes
- [HealthAssessorCrawler](#healthassessorcrawler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_crawler, pathlib, typing, yaml


## Classes

### HealthAssessorCrawler

```python
class HealthAssessorCrawler(BaseCrawler)
```

Evaluates project health based on data from other crawlers:
- Overall health score (0-10)
- Risk factors
- Opportunities for improvement
- Strengths
- Actionable recommendations


**Methods:**

  #### `get_name`

  ```python
  get_name(self) -> str
  ```

  #### `crawl`

  ```python
  crawl(self) -> Dict[str, Any]
  ```

  Assess project health based on crawler data.

Returns:
    Dict containing health assessment

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing health assessment



---
