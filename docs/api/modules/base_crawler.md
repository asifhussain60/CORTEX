# base_crawler

Base Crawler Class for Discovery Report System

All discovery crawlers inherit from this base class, which provides:
- Standard interface for crawling
- Error handling
- Logging
- Timeout management


## Table of Contents

### Classes
- [BaseCrawler](#basecrawler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** abc, datetime, logging, typing


## Classes

### BaseCrawler

```python
class BaseCrawler(ABC)
```

Abstract base class for all discovery crawlers.

Each crawler analyzes one aspect of the project (files, git, tests, etc.)
and returns structured data for report generation.


**Methods:**

  #### `crawl`

  *Decorators:* `abstractmethod`

  ```python
  crawl(self) -> Dict[str, Any]
  ```

  Execute crawler and return discovery data.

Returns:
    Dict containing crawler-specific discovery data
    
Example structure:
    {
        "success": True,
        "data": {...},
        "errors": [],
        "warnings": []
    }

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing crawler-specific discovery data Example structure: { "success": True, "data": {...}, "errors": [], "warnings": [] }


  #### `get_name`

  *Decorators:* `abstractmethod`

  ```python
  get_name(self) -> str
  ```

  Return crawler name for logging and identification.

Returns:
    Human-readable crawler name (e.g., "File Scanner")

  **Parameters:**

  - `self`


  **Returns:** str
    Human-readable crawler name (e.g., "File Scanner")


  #### `execute`

  ```python
  execute(self) -> Dict[str, Any]
  ```

  Execute crawler with error handling and timing.

This wraps the crawl() method with standard error handling,
logging, and performance tracking.

Returns:
    Dict containing:
        - success: bool
        - data: crawler-specific data
        - crawler_name: str
        - execution_time_ms: float
        - errors: list of error messages

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict containing: - success: bool - data: crawler-specific data - crawler_name: str - execution_time_ms: float - errors: list of error messages


  #### `handle_error`

  ```python
  handle_error(self, error: Exception, execution_time: float) -> Dict[str, Any]
  ```

  Standard error handling for all crawlers.

Args:
    error: Exception that occurred
    execution_time: Time spent before error (ms)
    
Returns:
    Dict with error information in standard format

  **Parameters:**

  - `self`
  - `error` (Exception): Exception that occurred
  - `execution_time` (float): Time spent before error (ms)


  **Returns:** Dict[str, Any]
    Dict with error information in standard format


  #### `log_warning`

  ```python
  log_warning(self, message: str)
  ```

  Log a warning message.

  **Parameters:**

  - `self`
  - `message` (str)


  #### `log_info`

  ```python
  log_info(self, message: str)
  ```

  Log an info message.

  **Parameters:**

  - `self`
  - `message` (str)


  #### `log_error`

  ```python
  log_error(self, message: str)
  ```

  Log an error message.

  **Parameters:**

  - `self`
  - `message` (str)



---
