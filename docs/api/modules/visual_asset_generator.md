# visual_asset_generator

Visual Asset Generator

Generates visual documentation assets including Mermaid diagrams and
AI image prompts to support comprehensive feature documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [MermaidDiagram](#mermaiddiagram)
- [ImagePrompt](#imageprompt)
- [VisualAssets](#visualassets)
- [MermaidDiagramGenerator](#mermaiddiagramgenerator)
- [ImagePromptGenerator](#imagepromptgenerator)
- [VisualAssetGenerator](#visualassetgenerator)


## Overview

- **Classes:** 6
- **Functions:** 0
- **Dependencies:** asyncio, dataclasses, datetime, implementation_discovery_engine, logging, os, pathlib, re, typing


## Classes

### MermaidDiagram

```python
class MermaidDiagram
```

**Decorators:** `dataclass`

Represents a Mermaid diagram


**Attributes:**

- `diagram_type`: str
- `title`: str
- `content`: str
- `description`: str
- `suggested_filename`: str



---

### ImagePrompt

```python
class ImagePrompt
```

**Decorators:** `dataclass`

Represents an AI image generation prompt


**Attributes:**

- `prompt_type`: str
- `title`: str
- `prompt_text`: str
- `style_specifications`: str
- `suggested_filename`: str
- `priority`: str



---

### VisualAssets

```python
class VisualAssets
```

**Decorators:** `dataclass`

Complete collection of visual assets for a feature


**Attributes:**

- `feature_name`: str
- `generation_timestamp`: datetime
- `mermaid_diagrams`: List[MermaidDiagram]
- `image_prompts`: List[ImagePrompt]
- `diagram_files_created`: List[str]
- `image_prompt_files_created`: List[str]
- `diagrams_generated`: int
- `prompts_generated`: int



---

### MermaidDiagramGenerator

```python
class MermaidDiagramGenerator
```

Generates Mermaid diagrams from implementation data


**Methods:**

  #### `generate_class_diagrams`

  ```python
  generate_class_diagrams(self, classes: List[CodeElement]) -> List[MermaidDiagram]
  ```

  Generate class diagrams for new classes

  **Parameters:**

  - `self`
  - `classes` (List[CodeElement])


  **Returns:** List[MermaidDiagram]


  #### `generate_api_sequence_diagrams`

  ```python
  generate_api_sequence_diagrams(self, endpoints: List[APIEndpoint]) -> List[MermaidDiagram]
  ```

  Generate sequence diagrams for API flows

  **Parameters:**

  - `self`
  - `endpoints` (List[APIEndpoint])


  **Returns:** List[MermaidDiagram]


  #### `generate_architecture_diagrams`

  ```python
  generate_architecture_diagrams(self, implementation_data: ImplementationData) -> List[MermaidDiagram]
  ```

  Generate high-level architecture diagrams

  **Parameters:**

  - `self`
  - `implementation_data` (ImplementationData)


  **Returns:** List[MermaidDiagram]



---

### ImagePromptGenerator

```python
class ImagePromptGenerator
```

Generates AI image prompts for visual documentation


**Methods:**

  #### `generate_architecture_prompts`

  ```python
  generate_architecture_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]
  ```

  Generate architecture visualization prompts

  **Parameters:**

  - `self`
  - `implementation_data` (ImplementationData)


  **Returns:** List[ImagePrompt]


  #### `generate_ui_prompts`

  ```python
  generate_ui_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]
  ```

  Generate UI mockup prompts for user-facing features

  **Parameters:**

  - `self`
  - `implementation_data` (ImplementationData)


  **Returns:** List[ImagePrompt]


  #### `generate_concept_prompts`

  ```python
  generate_concept_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]
  ```

  Generate conceptual/metaphorical prompts for abstract features

  **Parameters:**

  - `self`
  - `implementation_data` (ImplementationData)


  **Returns:** List[ImagePrompt]



---

### VisualAssetGenerator

```python
class VisualAssetGenerator
```

Main generator that coordinates Mermaid diagram generation and
AI image prompt creation to create comprehensive visual documentation.


**Methods:**

  #### `generate_visual_assets`

  ```python
  generate_visual_assets(self, implementation_data: ImplementationData) -> VisualAssets
  ```

  Main orchestration method that generates complete visual assets
for an implemented feature.

  **Parameters:**

  - `self`
  - `implementation_data` (ImplementationData)


  **Returns:** VisualAssets



---
