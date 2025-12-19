# track_config

CORTEX Multi-Track Configuration Module

Manages machine track assignments with automatic phase distribution,
fun naming, and race metrics tracking.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [TrackMetrics](#trackmetrics)
- [MachineTrack](#machinetrack)
- [MultiTrackConfig](#multitrackconfig)
- [TrackNameGenerator](#tracknamegenerator)
- [PhaseDistributor](#phasedistributor)
- [TrackConfigManager](#trackconfigmanager)


## Overview

- **Classes:** 6
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, hashlib, json, pathlib, random, typing


## Classes

### TrackMetrics

```python
class TrackMetrics
```

**Decorators:** `dataclass`

Real-time metrics for a track.


**Attributes:**

- `track_id`: str
- `modules_total`: int
- `modules_completed`: int
- `velocity`: float
- `estimated_completion`: Optional[datetime]
- `last_activity`: Optional[datetime]
- `streak_count`: int


**Methods:**

  #### `completion_percentage`

  *Decorators:* `property`

  ```python
  completion_percentage(self) -> float
  ```

  Calculate completion percentage.

  **Parameters:**

  - `self`


  **Returns:** float


  #### `status_emoji`

  *Decorators:* `property`

  ```python
  status_emoji(self) -> str
  ```

  Get status emoji based on performance.

  **Parameters:**

  - `self`


  **Returns:** str



---

### MachineTrack

```python
class MachineTrack
```

**Decorators:** `dataclass`

Configuration for a machine's work track.


**Attributes:**

- `track_id`: str
- `track_name`: str
- `emoji`: str
- `color`: str
- `machines`: List[str]
- `phases`: List[str]
- `modules`: List[str]
- `estimated_hours`: float
- `velocity_target`: float
- `metrics`: Optional[TrackMetrics]


**Methods:**


---

### MultiTrackConfig

```python
class MultiTrackConfig
```

**Decorators:** `dataclass`

Multi-track configuration for distributed development.


**Attributes:**

- `mode`: str
- `tracks`: Dict[str, MachineTrack]
- `race_metrics_enabled`: bool
- `display_leaderboard`: bool
- `velocity_window_hours`: int
- `auto_consolidate_threshold`: float


**Methods:**

  #### `is_multi_track`

  *Decorators:* `property`

  ```python
  is_multi_track(self) -> bool
  ```

  Check if multi-track mode is enabled.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `get_track_for_machine`

  ```python
  get_track_for_machine(self, machine_name: str) -> Optional[MachineTrack]
  ```

  Get the track assigned to a specific machine.

  **Parameters:**

  - `self`
  - `machine_name` (str)


  **Returns:** Optional[MachineTrack]


  #### `get_leader`

  ```python
  get_leader(self) -> Optional[MachineTrack]
  ```

  Get the track currently in the lead.

  **Parameters:**

  - `self`


  **Returns:** Optional[MachineTrack]



---

### TrackNameGenerator

```python
class TrackNameGenerator
```

Generates fun, deterministic track names based on machine names.


**Methods:**

  #### `generate`

  *Decorators:* `staticmethod`

  ```python
  generate(machine_name: str, index: int) -> tuple[str, str, str]
  ```

  Generate track name from machine name.

Args:
    machine_name: Name of the machine
    index: Optional index for multiple tracks on same machine

Returns:
    Tuple of (full_name, emoji, color)

  **Parameters:**

  - `machine_name` (str): Name of the machine
  - `index` (int) = `0`: Optional index for multiple tracks on same machine


  **Returns:** tuple[str, str, str]
    Tuple of (full_name, emoji, color)



---

### PhaseDistributor

```python
class PhaseDistributor
```

Intelligent phase distribution across tracks.

Ensures:
- No cross-track dependencies
- Balanced workload by estimated hours
- Logical grouping of related modules


**Methods:**

  #### `distribute`

  *Decorators:* `classmethod`

  ```python
  distribute(cls, modules: Dict[str, Dict], num_tracks: int, track_names: List[str]) -> Dict[str, List[str]]
  ```

  Distribute phases across tracks intelligently.

Args:
    modules: Module definitions from cortex-operations.yaml
    num_tracks: Number of tracks to distribute across
    track_names: List of track IDs

Returns:
    Dict mapping track_id -> list of assigned phases

  **Parameters:**

  - `cls`
  - `modules` (Dict[str, Dict]): Module definitions from cortex-operations.yaml
  - `num_tracks` (int): Number of tracks to distribute across
  - `track_names` (List[str]): List of track IDs


  **Returns:** Dict[str, List[str]]
    Dict mapping track_id -> list of assigned phases



---

### TrackConfigManager

```python
class TrackConfigManager
```

Manages multi-track configuration persistence and loading.


**Methods:**

  #### `load_from_config`

  *Decorators:* `staticmethod`

  ```python
  load_from_config(config_path: Path) -> MultiTrackConfig
  ```

  Load multi-track config from cortex.config.json.

  **Parameters:**

  - `config_path` (Path)


  **Returns:** MultiTrackConfig


  #### `save_to_config`

  *Decorators:* `staticmethod`

  ```python
  save_to_config(config: MultiTrackConfig, config_path: Path) -> None
  ```

  Save multi-track config to cortex.config.json.

  **Parameters:**

  - `config` (MultiTrackConfig)
  - `config_path` (Path)


  **Returns:** None


  #### `create_multi_track_config`

  *Decorators:* `staticmethod`

  ```python
  create_multi_track_config(machines: List[str], modules: Dict[str, Dict], config_path: Path) -> MultiTrackConfig
  ```

  Create new multi-track configuration.

Args:
    machines: List of machine names (from cortex.config.json)
    modules: Module definitions (from cortex-operations.yaml)
    config_path: Path to cortex.config.json

Returns:
    MultiTrackConfig ready to use

  **Parameters:**

  - `machines` (List[str]): List of machine names (from cortex.config.json)
  - `modules` (Dict[str, Dict]): Module definitions (from cortex-operations.yaml)
  - `config_path` (Path): Path to cortex.config.json


  **Returns:** MultiTrackConfig
    MultiTrackConfig ready to use



---
