# design_sync_models

Design Sync Models

Data models for Design Sync Orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [ImplementationState](#implementationstate)
- [DesignState](#designstate)
- [GapAnalysis](#gapanalysis)
- [SyncMetrics](#syncmetrics)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, pathlib, typing


## Classes

### ImplementationState

```python
class ImplementationState
```

**Decorators:** `dataclass`

Current implementation reality.


**Attributes:**

- `operations`: Dict[str, Dict]
- `modules`: Dict[str, Path]
- `tests`: Dict[str, int]
- `plugins`: List[str]
- `agents`: List[str]
- `total_modules`: int
- `implemented_modules`: int
- `completion_percentage`: float



---

### DesignState

```python
class DesignState
```

**Decorators:** `dataclass`

Design document state.


**Attributes:**

- `version`: str
- `design_files`: List[Path]
- `status_files`: List[Path]
- `md_documents`: List[Path]
- `yaml_documents`: List[Path]



---

### GapAnalysis

```python
class GapAnalysis
```

**Decorators:** `dataclass`

Gaps between design and implementation.


**Attributes:**

- `overclaimed_completions`: List[str]
- `underclaimed_completions`: List[str]
- `missing_documentation`: List[str]
- `inconsistent_counts`: List[Dict[str, Any]]
- `redundant_status_files`: List[Path]
- `verbose_md_candidates`: List[Path]



---

### SyncMetrics

```python
class SyncMetrics
```

**Decorators:** `dataclass`

Metrics collected during sync.


**Attributes:**

- `sync_id`: str
- `timestamp`: datetime
- `implementation_discovered`: bool
- `gaps_analyzed`: int
- `optimizations_integrated`: int
- `md_to_yaml_converted`: int
- `status_files_consolidated`: int
- `git_commits`: List[str]
- `duration_seconds`: float
- `errors`: List[str]
- `improvements`: Dict[str, Any]



---
