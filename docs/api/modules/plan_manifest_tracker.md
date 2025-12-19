# plan_manifest_tracker

Plan Manifest Tracker - Active Plans Registry
=============================================

Manages active-plans-manifest.yaml for tracking all active plans.

Purpose:
- Register approved plans in manifest
- Track plan metadata (status, dates, complexity)
- Enable plan discovery and monitoring
- Support cleanup operations

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [PlanManifestTracker](#planmanifesttracker)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, src, typing, yaml


## Classes

### PlanManifestTracker

```python
class PlanManifestTracker
```

Tracks active plans in manifest file.

Manifest Location:
cortex-brain/documents/planning/active-plans-manifest.yaml

Manifest Structure:
```yaml
version: "1.0"
last_updated: "2025-12-17T10:30:00"
plans:
  - plan_id: "user-auth-v1"
    title: "User Authentication System"
    status: "active"
    complexity_tier: 3
    created_date: "2025-12-15"
    approved_date: "2025-12-15"
    folder: "active/user-auth-v1"
    phases: 4
    estimated_days: 7
```


**Methods:**

  #### `register_plan`

  ```python
  register_plan(self, plan_id: str, title: str, status: str, complexity_tier: int, created_date: str, approved_date: str, folder: str, phases: int, estimated_days: float, metadata: Optional[Dict[str, Any]])
  ```

  Register plan in manifest.

Args:
    plan_id: Plan identifier
    title: Plan title
    status: Plan status (active, in_progress, etc.)
    complexity_tier: Complexity tier (1-4)
    created_date: Creation date (ISO format)
    approved_date: Approval date (ISO format)
    folder: Folder path relative to planning/
    phases: Number of phases
    estimated_days: Estimated duration in days
    metadata: Additional metadata (optional)

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `title` (str): Plan title
  - `status` (str): Plan status (active, in_progress, etc.)
  - `complexity_tier` (int): Complexity tier (1-4)
  - `created_date` (str): Creation date (ISO format)
  - `approved_date` (str): Approval date (ISO format)
  - `folder` (str): Folder path relative to planning/
  - `phases` (int): Number of phases
  - `estimated_days` (float): Estimated duration in days
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional metadata (optional)


  #### `update_plan_status`

  ```python
  update_plan_status(self, plan_id: str, status: str)
  ```

  Update plan status in manifest.

Args:
    plan_id: Plan identifier
    status: New status

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `status` (str): New status


  #### `get_plan`

  ```python
  get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]
  ```

  Get plan metadata from manifest.

Args:
    plan_id: Plan identifier
    
Returns:
    Plan metadata dict, or None if not found

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier


  **Returns:** Optional[Dict[str, Any]]
    Plan metadata dict, or None if not found


  #### `get_all_plans`

  ```python
  get_all_plans(self) -> List[Dict[str, Any]]
  ```

  Get all plans from manifest.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]


  #### `get_plans_by_status`

  ```python
  get_plans_by_status(self, status: str) -> List[Dict[str, Any]]
  ```

  Get plans by status.

Args:
    status: Status filter (active, in_progress, etc.)
    
Returns:
    List of matching plans

  **Parameters:**

  - `self`
  - `status` (str): Status filter (active, in_progress, etc.)


  **Returns:** List[Dict[str, Any]]
    List of matching plans


  #### `remove_plan`

  ```python
  remove_plan(self, plan_id: str)
  ```

  Remove plan from manifest.

Args:
    plan_id: Plan identifier

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier



---
