# vision_api

Vision API Integration for CORTEX

Provides image analysis capabilities using GitHub Copilot's built-in vision API.
Includes token budgeting, image preprocessing, and result caching.

Design Document: cortex-brain/cortex-2.0-design/31-vision-api-integration.md


## Table of Contents

### Classes
- [VisionAPI](#visionapi)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** PIL, base64, datetime, hashlib, io, json, logging, pathlib, re, time, typing


## Classes

### VisionAPI

```python
class VisionAPI
```

GitHub Copilot Vision API integration with token management.

Features:
- Image preprocessing (downscale, compress)
- Token cost estimation
- Budget enforcement (500 token hard limit)
- Result caching (24 hour TTL)
- Graceful fallback on errors

Example:
    vision = VisionAPI(config)
    result = vision.analyze_image(
        image_data="data:image/png;base64,...",
        prompt="Extract button colors and labels"
    )
    
    if result['success']:
        print(f"Analysis: {result['analysis']}")
        print(f"Tokens used: {result['tokens_used']}")


**Methods:**

  #### `analyze_image`

  ```python
  analyze_image(self, image_data: str, prompt: str) -> Dict
  ```

  Analyze image using GitHub Copilot vision API.

Args:
    image_data: Base64-encoded image (data URI format)
    prompt: Natural language analysis request
    
Returns:
    {
        'success': bool,
        'analysis': str,           # Natural language response
        'extracted_data': dict,    # Structured data
        'tokens_used': int,
        'processing_time_ms': int,
        'cached': bool,
        'error': str (if failed)
    }

  **Parameters:**

  - `self`
  - `image_data` (str): Base64-encoded image (data URI format)
  - `prompt` (str): Natural language analysis request


  **Returns:** Dict
    { 'success': bool, 'analysis': str,           # Natural language response 'extracted_data': dict,    # Structured data 'tokens_used': int, 'processing_time_ms': int, 'cached': bool, 'error': str (if failed) }


  #### `get_metrics`

  ```python
  get_metrics(self) -> Dict
  ```

  Get Vision API usage metrics.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `clear_cache`

  ```python
  clear_cache(self)
  ```

  Clear cached results.

  **Parameters:**

  - `self`



---
