# narrative_intelligence

CORTEX 3.0 Narrative Intelligence Module
Advanced Fusion - Milestone 3

Enhanced story generation with contextual reasoning and development flow analysis.
Generates coherent narratives about development progress using conversation patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX


## Table of Contents

### Classes
- [StoryType](#storytype)
- [NarrativeStyle](#narrativestyle)
- [StoryElement](#storyelement)
- [DevelopmentNarrative](#developmentnarrative)
- [NarrativeIntelligence](#narrativeintelligence)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, json, logging, re, sqlite3, typing, uuid


## Classes

### StoryType

```python
class StoryType(Enum)
```

Types of stories the narrative intelligence can generate



---

### NarrativeStyle

```python
class NarrativeStyle(Enum)
```

Narrative styles for different audiences



---

### StoryElement

```python
class StoryElement
```

**Decorators:** `dataclass`

A single element or event in a development story


**Attributes:**

- `element_id`: str
- `timestamp`: datetime
- `element_type`: str
- `content`: str
- `confidence`: float
- `related_files`: List[str]
- `context_tags`: List[str]
- `metadata`: Dict[str, Any]


**Methods:**


---

### DevelopmentNarrative

```python
class DevelopmentNarrative
```

**Decorators:** `dataclass`

A coherent narrative about development progress


**Attributes:**

- `narrative_id`: str
- `title`: str
- `story_type`: StoryType
- `narrative_style`: NarrativeStyle
- `story_elements`: List[StoryElement]
- `generated_narrative`: str
- `metadata`: Dict[str, Any]
- `created_at`: datetime
- `confidence_score`: float


**Methods:**


---

### NarrativeIntelligence

```python
class NarrativeIntelligence
```

CORTEX 3.0 Narrative Intelligence Module

Generates coherent stories about development progress by analyzing conversation patterns,
file changes, and learning evolution. Provides contextual insights about project development.


**Methods:**

  #### `add_story_element`

  ```python
  add_story_element(self, element: StoryElement) -> bool
  ```

  Add a story element to the narrative database

  **Parameters:**

  - `self`
  - `element` (StoryElement)


  **Returns:** bool


  #### `generate_development_story`

  ```python
  generate_development_story(self, time_range: Tuple[datetime, datetime], story_type: StoryType, narrative_style: NarrativeStyle, focus_files: List[str]) -> DevelopmentNarrative
  ```

  Generate a coherent narrative about development progress.

Args:
    time_range: Tuple of (start_time, end_time) for story scope
    story_type: Type of story to generate
    narrative_style: Style/audience for the narrative
    focus_files: Optional list of files to focus the story on
    
Returns:
    DevelopmentNarrative with generated story

  **Parameters:**

  - `self`
  - `time_range` (Tuple[datetime, datetime]): Tuple of (start_time, end_time) for story scope
  - `story_type` (StoryType) = `StoryType.DEVELOPMENT_PROGRESS`: Type of story to generate
  - `narrative_style` (NarrativeStyle) = `NarrativeStyle.TECHNICAL`: Style/audience for the narrative
  - `focus_files` (List[str]) = `None`: Optional list of files to focus the story on


  **Returns:** DevelopmentNarrative
    DevelopmentNarrative with generated story


  #### `get_recent_narratives`

  ```python
  get_recent_narratives(self, limit: int) -> List[DevelopmentNarrative]
  ```

  Get recently generated narratives

  **Parameters:**

  - `self`
  - `limit` (int) = `10`


  **Returns:** List[DevelopmentNarrative]


  #### `get_narrative_statistics`

  ```python
  get_narrative_statistics(self) -> Dict[str, Any]
  ```

  Get statistics about narrative generation

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `import_conversation_data`

  ```python
  import_conversation_data(self, conversation_data: Dict[str, Any]) -> bool
  ```

  Import conversation data and create story elements

  **Parameters:**

  - `self`
  - `conversation_data` (Dict[str, Any])


  **Returns:** bool



---
