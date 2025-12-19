# vision_context_middleware

Vision Context Middleware for Automatic Image Analysis

Automatically detects images in context and triggers GPT-4V vision analysis
without requiring explicit user prompting. Eliminates the friction of manually
requesting image analysis in Copilot Chat conversations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0

Features:
- Automatic image detection (PNG, JPG, JPEG)
- GPT-4V auto-engagement (<500ms)
- Duplicate image caching
- Skip logic if analysis exists
- API call logging
- Orchestrator integration via decorator

Usage:
    from src.operations.utilities.vision_context_middleware import with_vision_context_middleware
    
    @with_vision_context_middleware
    def my_orchestrator(context):
        # Images automatically analyzed before orchestrator runs
        vision_analysis = context.get('vision_analysis')
        if vision_analysis:
            print(f"Image analysis: {vision_analysis['description']}")
        return context


## Table of Contents

### Classes
- [VisionContextMiddleware](#visioncontextmiddleware)
- [GPT4VisionClient](#gpt4visionclient)

### Functions
- [with_vision_context_middleware](#with_vision_context_middleware)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** functools, hashlib, logging, pathlib, time, typing


## Classes

### VisionContextMiddleware

```python
class VisionContextMiddleware
```

Middleware for automatic vision API engagement on image attachments.

Detects images in context and automatically triggers GPT-4V analysis
without explicit user prompting. Includes caching to prevent duplicate API calls.

Performance: <500ms per image analysis


**Methods:**

  #### `detect_images_in_context`

  ```python
  detect_images_in_context(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
  ```

  Detect images in context attachments.

Args:
    context: Context dictionary with 'attachments' key

Returns:
    List of image attachment dicts with 'type', 'path', 'mime'

Example:
    >>> middleware = VisionContextMiddleware()
    >>> context = {
    ...     'attachments': [
    ...         {'type': 'image', 'path': '/img.png', 'mime': 'image/png'},
    ...         {'type': 'text', 'content': 'Some text'}
    ...     ]
    ... }
    >>> images = middleware.detect_images_in_context(context)
    >>> len(images)
    1

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Context dictionary with 'attachments' key


  **Returns:** List[Dict[str, Any]]
    List of image attachment dicts with 'type', 'path', 'mime'


  #### `process_context`

  ```python
  process_context(self, context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Process context and automatically analyze images.

Args:
    context: Context dictionary

Returns:
    Context with 'vision_analysis' added if images found

Performance: <500ms per image

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Context dictionary


  **Returns:** Dict[str, Any]
    Context with 'vision_analysis' added if images found Performance: <500ms per image



---

### GPT4VisionClient

```python
class GPT4VisionClient
```

Mock GPT-4V client for testing


**Methods:**

  #### `analyze_image`

  ```python
  analyze_image(self, image_path: str) -> Dict[str, Any]
  ```

  Mock image analysis

  **Parameters:**

  - `self`
  - `image_path` (str)


  **Returns:** Dict[str, Any]



---

## Functions

### with_vision_context_middleware

```python
with_vision_context_middleware(func: Callable) -> Callable
```

Decorator to automatically analyze images in context before orchestrator execution.

Detects images in context parameter and adds 'vision_analysis' key
with GPT-4V analysis results before calling the decorated function.

Args:
    func: Orchestrator function to decorate

Returns:
    Decorated function with automatic vision analysis

Example:
    @with_vision_context_middleware
    def my_orchestrator(context):
        vision = context.get('vision_analysis')
        if vision:
            print(f"Image shows: {vision['description']}")
        return context

Performance: <500ms overhead per image


**Parameters:**

- `func` (Callable): Orchestrator function to decorate


**Returns:** Callable
  Decorated function with automatic vision analysis


---
