# vision_orchestrator

Vision API Orchestrator for CORTEX

Coordinates automatic image detection, Vision API analysis, and context injection.
Integrates with intent router to provide seamless image analysis in conversations.

Design Document: cortex-brain/cortex-3.0-design/vision-api-auto-detection.md


## Table of Contents

### Classes
- [VisionOrchestrator](#visionorchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base64, datetime, image_detector, logging, pathlib, typing, vision_api


## Classes

### VisionOrchestrator

```python
class VisionOrchestrator
```

Orchestrates automatic image detection and analysis.

Workflow:
1. Detect images in user request
2. Analyze each image with Vision API
3. Inject analysis results into context
4. Generate summary for response

Example:
    orchestrator = VisionOrchestrator(config)
    
    result = orchestrator.process_request(
        user_request="analyze this screenshot",
        attachments=[{'type': 'image', 'data': '...'}]
    )
    
    if result['images_found']:
        print(f"Analyzed {result['images_analyzed']} images")
        print(result['context_summary'])


**Methods:**

  #### `process_request`

  ```python
  process_request(self, user_request: str, attachments: Optional[List[Dict]], context_type: str, custom_prompt: Optional[str]) -> Dict
  ```

  Process user request with automatic image detection and analysis.

Args:
    user_request: User's text request
    attachments: Optional list of attachment objects
    context_type: Type of analysis ('generic', 'planning', 'debugging', 'ado')
    custom_prompt: Optional custom analysis prompt (overrides context_type)
    
Returns:
    {
        'images_found': bool,
        'images_analyzed': int,
        'images_failed': int,
        'detected_images': List[ImageAttachment],
        'analysis_results': List[Dict],
        'context_summary': str,  # For injection into conversation
        'context_data': Dict,     # Structured data for agents
        'processing_time_ms': float,
        'errors': List[str]
    }

  **Parameters:**

  - `self`
  - `user_request` (str): User's text request
  - `attachments` (Optional[List[Dict]]) = `None`: Optional list of attachment objects
  - `context_type` (str) = `'generic'`: Type of analysis ('generic', 'planning', 'debugging', 'ado')
  - `custom_prompt` (Optional[str]) = `None`: Optional custom analysis prompt (overrides context_type)


  **Returns:** Dict
    { 'images_found': bool, 'images_analyzed': int, 'images_failed': int, 'detected_images': List[ImageAttachment], 'analysis_results': List[Dict], 'context_summary': str,  # For injection into conversation 'context_data': Dict,     # Structured data for agents 'processing_time_ms': float, 'errors': List[str] }


  #### `quick_check`

  ```python
  quick_check(self, user_request: str, attachments: Optional[List[Dict]]) -> bool
  ```

  Quick check if request has images (without full analysis).

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


  #### `get_metrics`

  ```python
  get_metrics(self) -> Dict
  ```

  Get Vision orchestrator usage metrics.

Returns:
    Metrics dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict
    Metrics dictionary


  #### `analyze_specific_image`

  ```python
  analyze_specific_image(self, image_data: str, prompt: str, context_type: str) -> Dict
  ```

  Analyze a specific image with custom prompt (manual analysis).

Args:
    image_data: Image data URI or file path
    prompt: Analysis prompt
    context_type: Context type for logging
    
Returns:
    Analysis result dictionary

  **Parameters:**

  - `self`
  - `image_data` (str): Image data URI or file path
  - `prompt` (str): Analysis prompt
  - `context_type` (str) = `'generic'`: Context type for logging


  **Returns:** Dict
    Analysis result dictionary



---
