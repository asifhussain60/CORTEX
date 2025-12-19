# image_context_middleware

Image Context Middleware for CORTEX

Automatically detects image attachments in Copilot Chat context and triggers
Vision API analysis without explicit user request.

Design Goal: Eliminate user friction - "I have to keep explicitly stating this"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0

Features:
- Automatic image attachment detection (<500ms)
- Context-aware Vision API engagement
- Seamless integration with existing infrastructure
- Zero user configuration required

Usage:
    from src.operations.utilities.image_context_middleware import ImageContextMiddleware
    
    middleware = ImageContextMiddleware(config)
    
    # Check for images and auto-engage Vision API
    result = middleware.process_context(
        user_message="What should I do here?",
        attachments=copilot_chat_attachments
    )
    
    if result['vision_engaged']:
        print(f"Analyzed {result['images_analyzed']} images automatically")
        print(result['analysis_summary'])


## Table of Contents

### Classes
- [ImageContextMiddleware](#imagecontextmiddleware)

### Functions
- [get_middleware](#get_middleware)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, json, logging, pathlib, src, time, typing


## Classes

### ImageContextMiddleware

```python
class ImageContextMiddleware
```

Middleware to automatically detect and analyze images in Copilot Chat context.

Integrates with existing Vision API infrastructure:
- src/tier1/vision_orchestrator.py
- src/tier1/image_detector.py
- src/tier1/vision_api.py
- src/cortex_agents/screenshot_analyzer.py

Performance: <500ms engagement time


**Methods:**

  #### `detect_images_in_context`

  ```python
  detect_images_in_context(self, user_message: str, attachments: Optional[List[Dict]], context: Optional[Dict]) -> Dict[str, Any]
  ```

  Detect if images are present in Copilot Chat context.

Checks multiple sources:
1. Explicit attachments parameter
2. Context dictionary (image_base64, image_path, etc.)
3. User message references to images/screenshots

Args:
    user_message: User's text message
    attachments: Optional list of attachment objects
    context: Optional context dictionary

Returns:
    {
        'has_images': bool,
        'image_count': int,
        'image_sources': List[str],  # ['attachment', 'context', 'reference']
        'detection_time_ms': float
    }

  **Parameters:**

  - `self`
  - `user_message` (str): User's text message
  - `attachments` (Optional[List[Dict]]) = `None`: Optional list of attachment objects
  - `context` (Optional[Dict]) = `None`: Optional context dictionary


  **Returns:** Dict[str, Any]
    { 'has_images': bool, 'image_count': int, 'image_sources': List[str],  # ['attachment', 'context', 'reference'] 'detection_time_ms': float }


  #### `infer_analysis_context`

  ```python
  infer_analysis_context(self, user_message: str) -> str
  ```

  Infer what type of image analysis to perform based on user message.

Args:
    user_message: User's text message

Returns:
    Context type: 'generic', 'planning', 'debugging', 'ado'

  **Parameters:**

  - `self`
  - `user_message` (str): User's text message


  **Returns:** str
    Context type: 'generic', 'planning', 'debugging', 'ado'


  #### `process_context`

  ```python
  process_context(self, user_message: str, attachments: Optional[List[Dict]], context: Optional[Dict], force_engage: bool) -> Dict[str, Any]
  ```

  Process Copilot Chat context and auto-engage Vision API if images detected.

This is the main entry point for automatic image analysis.

Args:
    user_message: User's text message
    attachments: Optional list of attachment objects
    context: Optional context dictionary
    force_engage: Force Vision API engagement even if auto_engage disabled

Returns:
    {
        'vision_engaged': bool,
        'images_detected': int,
        'images_analyzed': int,
        'analysis_summary': str,  # Human-readable summary
        'analysis_data': Dict,     # Structured data for agents
        'engagement_time_ms': float,
        'detection_time_ms': float,
        'within_sla': bool,       # <500ms requirement
        'errors': List[str]
    }

  **Parameters:**

  - `self`
  - `user_message` (str): User's text message
  - `attachments` (Optional[List[Dict]]) = `None`: Optional list of attachment objects
  - `context` (Optional[Dict]) = `None`: Optional context dictionary
  - `force_engage` (bool) = `False`: Force Vision API engagement even if auto_engage disabled


  **Returns:** Dict[str, Any]
    { 'vision_engaged': bool, 'images_detected': int, 'images_analyzed': int, 'analysis_summary': str,  # Human-readable summary 'analysis_data': Dict,     # Structured data for agents 'engagement_time_ms': float, 'detection_time_ms': float, 'within_sla': bool,       # <500ms requirement 'errors': List[str] }


  #### `get_metrics`

  ```python
  get_metrics(self) -> Dict[str, Any]
  ```

  Get middleware performance metrics.

Returns:
    {
        'total_requests': int,
        'requests_with_images': int,
        'auto_engagements': int,
        'engagement_rate': float,  # % of requests with images that engaged Vision
        'avg_engagement_time_ms': float,
        'within_sla_rate': float
    }

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    { 'total_requests': int, 'requests_with_images': int, 'auto_engagements': int, 'engagement_rate': float,  # % of requests with images that engaged Vision 'avg_engagement_time_ms': float, 'within_sla_rate': float }



---

## Functions

### get_middleware

```python
get_middleware(config: Optional[Dict]) -> ImageContextMiddleware
```

Get global middleware instance (singleton pattern).

Args:
    config: Optional configuration (only used on first call)

Returns:
    ImageContextMiddleware instance


**Parameters:**

- `config` (Optional[Dict]) = `None`: Optional configuration (only used on first call)


**Returns:** ImageContextMiddleware
  ImageContextMiddleware instance


---
