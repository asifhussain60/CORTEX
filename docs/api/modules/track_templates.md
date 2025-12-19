# track_templates

CORTEX Multi-Track Design Document Templates

Templates for split and consolidated design documents.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [TrackDocumentTemplates](#trackdocumenttemplates)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, track_config, typing


## Classes

### TrackDocumentTemplates

```python
class TrackDocumentTemplates
```

Templates for multi-track design documents.


**Methods:**

  #### `generate_race_dashboard`

  *Decorators:* `staticmethod`

  ```python
  generate_race_dashboard(config: MultiTrackConfig) -> str
  ```

  Generate race dashboard header for split design docs.

Args:
    config: Multi-track configuration with metrics

Returns:
    Markdown table with live race metrics

  **Parameters:**

  - `config` (MultiTrackConfig): Multi-track configuration with metrics


  **Returns:** str
    Markdown table with live race metrics


  #### `generate_track_section`

  *Decorators:* `staticmethod`

  ```python
  generate_track_section(track: MachineTrack, modules: Dict[str, Dict]) -> str
  ```

  Generate track-specific section for split design doc.

Args:
    track: Track configuration
    modules: Module definitions

Returns:
    Markdown section for this track

  **Parameters:**

  - `track` (MachineTrack): Track configuration
  - `modules` (Dict[str, Dict]): Module definitions


  **Returns:** str
    Markdown section for this track


  #### `generate_split_document`

  *Decorators:* `staticmethod`

  ```python
  generate_split_document(config: MultiTrackConfig, modules: Dict[str, Dict], version: str) -> str
  ```

  Generate complete split design document with race dashboard.

Args:
    config: Multi-track configuration
    modules: Module definitions
    version: CORTEX version

Returns:
    Complete Markdown document

  **Parameters:**

  - `config` (MultiTrackConfig): Multi-track configuration
  - `modules` (Dict[str, Dict]): Module definitions
  - `version` (str) = `'2.0'`: CORTEX version


  **Returns:** str
    Complete Markdown document


  #### `generate_consolidated_document`

  *Decorators:* `staticmethod`

  ```python
  generate_consolidated_document(config: MultiTrackConfig, modules: Dict[str, Dict], version: str) -> str
  ```

  Generate consolidated single-track document after merge.

Args:
    config: Multi-track configuration (for archive reference)
    modules: Module definitions
    version: CORTEX version

Returns:
    Complete consolidated Markdown document

  **Parameters:**

  - `config` (MultiTrackConfig): Multi-track configuration (for archive reference)
  - `modules` (Dict[str, Dict]): Module definitions
  - `version` (str) = `'2.0'`: CORTEX version


  **Returns:** str
    Complete consolidated Markdown document



---
