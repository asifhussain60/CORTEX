# unified_plan_generator

Unified Plan Generator for CORTEX

Shared plan generation logic for all planning orchestrators.
Eliminates duplication across PlanningOrchestrator, TempPlanManager, ADOPlanning.

Author: Asif Hussain
Version: 2.1.0 - Added TaskInjector integration for standard task auto-injection


## Table of Contents

### Classes
- [UnifiedPlanGenerator](#unifiedplangenerator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, master_plan_template, pathlib, re, subprocess, task_injector, token_reduction_tracker, typing


## Classes

### UnifiedPlanGenerator

```python
class UnifiedPlanGenerator
```

Shared plan generation logic for all planning orchestrators.

Eliminates duplication across:
- PlanningOrchestrator
- TempPlanManagerOrchestrator
- ADOPlanningOrchestrator (future: if it needs master plans)


**Methods:**

  #### `standardize_hours`

  ```python
  standardize_hours(self, hours_value: str) -> str
  ```

  Standardize hour format: show hours with days in parentheses if >8h.

Examples:
    "4h" → "4h"
    "16h" → "16h (2d)"
    "2d" → "16h (2d)"
    "24h" → "24h (3d)"
    "1h 30m" → "1.5h"

Args:
    hours_value: Time value in various formats
    
Returns:
    Standardized format: "Xh (Yd)" or "Xh"

  **Parameters:**

  - `self`
  - `hours_value` (str): Time value in various formats


  **Returns:** str
    Standardized format: "Xh (Yd)" or "Xh"


  #### `compress_phase_name`

  ```python
  compress_phase_name(self, phase_name: str, compressed: bool) -> str
  ```

  Compress phase name using abbreviations.

Args:
    phase_name: Original phase name
    compressed: Whether to apply compression
    
Returns:
    Compressed or original phase name

  **Parameters:**

  - `self`
  - `phase_name` (str): Original phase name
  - `compressed` (bool) = `False`: Whether to apply compression


  **Returns:** str
    Compressed or original phase name


  #### `generate_master_plan`

  ```python
  generate_master_plan(self, plan_id: str, phases: List[Dict], metadata: Dict, include_token_tracking: bool, include_visual_tracker: bool, include_continuation_prompt: bool, compressed: bool, manifest_path: Optional[str]) -> str
  ```

  Generate master plan by rendering template with all required sections.

Template sections (7 mandatory):
1. Executive Summary
2. Continuation Prompt
3. Visual Progress Tracker
4. Business Value Summary
5. Phase Breakdown & Execution Status
6. Request Context
7. Definition of Done (DoD)

Args:
    plan_id: Plan identifier
    phases: List of phase dictionaries
    metadata: Plan metadata (date, complexity, etc.)
    include_token_tracking: Include token reduction metrics
    include_visual_tracker: Include ASCII progress bar
    include_continuation_prompt: Include continuation prompt
    compressed: Use compressed format for token optimization
    manifest_path: Path to orchestrator manifest YAML (for continuation prompt context)

Returns:
    Master plan markdown content with all 7 template sections

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `phases` (List[Dict]): List of phase dictionaries
  - `metadata` (Dict): Plan metadata (date, complexity, etc.)
  - `include_token_tracking` (bool) = `True`: Include token reduction metrics
  - `include_visual_tracker` (bool) = `True`: Include ASCII progress bar
  - `include_continuation_prompt` (bool) = `True`: Include continuation prompt
  - `compressed` (bool) = `False`: Use compressed format for token optimization
  - `manifest_path` (Optional[str]) = `None`: Path to orchestrator manifest YAML (for continuation prompt context)


  **Returns:** str
    Master plan markdown content with all 7 template sections


  #### `generate_progress_tracker`

  ```python
  generate_progress_tracker(self, phases: List[Dict], baseline_tokens: int, current_tokens: int, total_files: int, compressed: bool, include_detailed_tracker: bool) -> str
  ```

  Generate visual progress tracker with token metrics.

Args:
    phases: List of phase dictionaries
    baseline_tokens: Baseline token count
    current_tokens: Current token count
    total_files: Total file count
    compressed: Use compressed format
    include_detailed_tracker: Include detailed ASCII box tracker (cortex-3.9 style)

Returns:
    Progress tracker markdown

  **Parameters:**

  - `self`
  - `phases` (List[Dict]): List of phase dictionaries
  - `baseline_tokens` (int): Baseline token count
  - `current_tokens` (int): Current token count
  - `total_files` (int): Total file count
  - `compressed` (bool) = `False`: Use compressed format
  - `include_detailed_tracker` (bool) = `True`: Include detailed ASCII box tracker (cortex-3.9 style)


  **Returns:** str
    Progress tracker markdown


  #### `generate_continuation_prompt`

  ```python
  generate_continuation_prompt(self, plan_id: str, completed_phases: int, total_phases: int, next_phase_number: Optional[int], next_phase_name: Optional[str], progress_percentage: int, manifest_path: Optional[str]) -> str
  ```

  Generate ultra-compact continuation prompt with manifest reference.

Strategy: Link to YAML manifest for full context (phases, DoR/DoD, TDD rules)
rather than repeating information. AI will load manifest on demand.

Args:
    plan_id: Plan identifier
    completed_phases: Number of completed phases
    total_phases: Total number of phases
    next_phase_number: Next phase number (or None if complete)
    next_phase_name: Next phase name
    progress_percentage: Overall progress percentage
    manifest_path: Path to orchestrator manifest (e.g., planning-system-4.0-manifest.yaml)

Returns:
    Ultra-compact continuation prompt (<30 tokens target)

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `completed_phases` (int): Number of completed phases
  - `total_phases` (int): Total number of phases
  - `next_phase_number` (Optional[int]): Next phase number (or None if complete)
  - `next_phase_name` (Optional[str]): Next phase name
  - `progress_percentage` (int): Overall progress percentage
  - `manifest_path` (Optional[str]) = `None`: Path to orchestrator manifest (e.g., planning-system-4.0-manifest.yaml)


  **Returns:** str
    Ultra-compact continuation prompt (<30 tokens target)


  #### `update_phase_status`

  ```python
  update_phase_status(self, master_plan_content: str, phase_number: int, new_status: str, actual_time: Optional[str], tokens_saved: Optional[int], master_plan_path: Optional[Path], auto_commit: bool, commit_message_prefix: Optional[str]) -> str
  ```

  Update phase status in master plan content with optional git commit.

Args:
    master_plan_content: Current master plan markdown
    phase_number: Phase number to update
    new_status: New status (e.g., "IN PROGRESS", "COMPLETE")
    actual_time: Actual time taken (e.g., "2h 15m")
    tokens_saved: Tokens saved in this phase
    master_plan_path: Path to master plan file (required if auto_commit=True)
    auto_commit: Automatically commit changes to git (default: True)
    commit_message_prefix: Optional custom commit message prefix

Returns:
    Updated master plan content

  **Parameters:**

  - `self`
  - `master_plan_content` (str): Current master plan markdown
  - `phase_number` (int): Phase number to update
  - `new_status` (str): New status (e.g., "IN PROGRESS", "COMPLETE")
  - `actual_time` (Optional[str]) = `None`: Actual time taken (e.g., "2h 15m")
  - `tokens_saved` (Optional[int]) = `None`: Tokens saved in this phase
  - `master_plan_path` (Optional[Path]) = `None`: Path to master plan file (required if auto_commit=True)
  - `auto_commit` (bool) = `True`: Automatically commit changes to git (default: True)
  - `commit_message_prefix` (Optional[str]) = `None`: Optional custom commit message prefix


  **Returns:** str
    Updated master plan content


  #### `generate_worker_plan`

  ```python
  generate_worker_plan(self, plan_id: str, phase_number: int, phase_name: str, phase_data: Dict[str, Any], inject_standard_tasks: bool) -> str
  ```

  Generate worker plan (WP##-Phase-Name.md) with optional task injection.

Args:
    plan_id: Plan identifier
    phase_number: Phase number (1-indexed)
    phase_name: Phase name
    phase_data: Phase data dictionary with tasks, deliverables, DoD
    inject_standard_tasks: Whether to inject standard tasks
    
Returns:
    Worker plan markdown content

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `phase_number` (int): Phase number (1-indexed)
  - `phase_name` (str): Phase name
  - `phase_data` (Dict[str, Any]): Phase data dictionary with tasks, deliverables, DoD
  - `inject_standard_tasks` (bool) = `True`: Whether to inject standard tasks


  **Returns:** str
    Worker plan markdown content



---
