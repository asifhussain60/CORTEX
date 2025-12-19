# image_detector

Image Attachment Detector for CORTEX

Automatically detects image attachments in user requests and triggers Vision API analysis.
Supports: data URIs, file paths, base64 strings, and GitHub Copilot Chat attachments.

Design Document: cortex-brain/cortex-3.0-design/vision-api-auto-detection.md


## Table of Contents

### Classes
- [ImageAttachment](#imageattachment)
- [ImageDetector](#imagedetector)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** base64, dataclasses, logging, pathlib, re, typing


## Classes

### ImageAttachment

```python
class ImageAttachment
```

**Decorators:** `dataclass`

Represents a detected image attachment.


**Attributes:**

- `source`: str
- `format`: str
- `data`: str
- `size_bytes`: Optional[int]
- `width`: Optional[int]
- `height`: Optional[int]
- `original_reference`: str



---

### ImageDetector

```python
class ImageDetector
```

Detects image attachments in user requests.

Supports multiple attachment formats:
- Data URIs: data:image/png;base64,...
- File paths: /path/to/image.png, C:\images\screenshot.jpg
- Base64 strings: (with format hints)
- URLs: http://example.com/image.png
- GitHub Copilot Chat attachments (special markers)

Example:
    detector = ImageDetector(config)
    images = detector.detect(user_request, attachments)
    
    for img in images:
        print(f"Found {img.format} image from {img.source}")


**Methods:**

  #### `detect`

  ```python
  detect(self, user_request: str, attachments: Optional[List[Dict]]) -> List[ImageAttachment]
  ```

  Detect all images in user request and attachments.

Args:
    user_request: User's text request
    attachments: Optional list of attachment objects from chat interface
    
Returns:
    List of ImageAttachment objects (empty if none found)

  **Parameters:**

  - `self`
  - `user_request` (str): User's text request
  - `attachments` (Optional[List[Dict]]) = `None`: Optional list of attachment objects from chat interface


  **Returns:** List[ImageAttachment]
    List of ImageAttachment objects (empty if none found)


  #### `has_images`

  ```python
  has_images(self, user_request: str, attachments: Optional[List[Dict]]) -> bool
  ```

  Quick check if request has any images.

Args:
    user_request: User's text request
    attachments: Optional list of attachments
    
Returns:
    True if images detected, False otherwise

  **Parameters:**

  - `self`
  - `user_request` (str): User's text request
  - `attachments` (Optional[List[Dict]]) = `None`: Optional list of attachments


  **Returns:** bool
    True if images detected, False otherwise


  #### `get_image_context_summary`

  ```python
  get_image_context_summary(self, images: List[ImageAttachment]) -> str
  ```

  Generate summary of detected images for context injection.

Args:
    images: List of detected images
    
Returns:
    Human-readable summary string

  **Parameters:**

  - `self`
  - `images` (List[ImageAttachment]): List of detected images


  **Returns:** str
    Human-readable summary string



---
