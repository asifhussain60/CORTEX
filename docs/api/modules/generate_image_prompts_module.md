# generate_image_prompts_module

Generate Image Prompts Module - Story Refresh Operation

This module generates Gemini-compatible image prompts for technical system diagrams
based on the CopilotRecommendedDiagrams.md specification.

Author: Asif Hussain
Version: 1.0


## Table of Contents

### Classes
- [GenerateImagePromptsModule](#generateimagepromptsmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, src, typing


## Classes

### GenerateImagePromptsModule

```python
class GenerateImagePromptsModule(BaseOperationModule)
```

Generate Gemini-compatible image prompts for CORTEX system diagrams.

This module reads CopilotRecommendedDiagrams.md and generates single-paragraph
prompts that Gemini's image generator can use to create professional technical
diagrams (flowcharts, sequence diagrams, architecture diagrams).

What it does:
    1. Loads CopilotRecommendedDiagrams.md
    2. Generates 10 technical diagram prompts (single paragraph each)
    3. Saves to docs/story/CORTEX-STORY/Image-Prompts.md
    4. Validates output structure


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]
  ```

  Validate prerequisites.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Generate image prompts file.

Args:
    context: Shared context dictionary
        - Input: project_root (Path)
        - Output: image_prompts_path (Path), prompts_generated (int)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback image prompts generation.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `should_run`

  ```python
  should_run(self, context: Dict[str, Any]) -> bool
  ```

  Determine if module should run.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `get_progress_message`

  ```python
  get_progress_message(self) -> str
  ```

  Get progress message.

  **Parameters:**

  - `self`


  **Returns:** str



---
