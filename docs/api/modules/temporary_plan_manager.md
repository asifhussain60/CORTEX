# temporary_plan_manager

Temporary Plan Manager - Interactive Refinement Orchestrator
============================================================

Manages temporary plan creation and iterative refinement workflow.

Purpose:
- Create temporary plans in temp-plans/ folder
- Interactive refinement loop (back-and-forth with user)
- AST/Lens context accumulation across iterations
- DoR validation before approval
- Plan promotion to active/ on approval

Token Optimization:
- Context distillation to ≤3,000 tokens
- AST/Lens graphs externalized to JSON
- Pattern summaries instead of full code
- Quality override if needed (never compromise correctness)

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [RefinementIteration](#refinementiteration)
- [InteractiveRefinementSession](#interactiverefinementsession)
- [TemporaryPlanManager](#temporaryplanmanager)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, src, typing


## Classes

### RefinementIteration

```python
class RefinementIteration
```

**Decorators:** `dataclass`

Single refinement iteration.


**Attributes:**

- `iteration_number`: int
- `timestamp`: str
- `user_input`: str
- `plan_version`: str
- `ast_context`: Optional[Dict[str, Any]]
- `lens_context`: Optional[Dict[str, Any]]
- `dor_score`: float
- `ambiguity_score`: float
- `changes_made`: List[str]



---

### InteractiveRefinementSession

```python
class InteractiveRefinementSession
```

**Decorators:** `dataclass`

Tracks interactive refinement session.


**Attributes:**

- `session_id`: str
- `plan_id`: str
- `user_request`: str
- `created_at`: str
- `complexity_tier`: int
- `iterations`: List[RefinementIteration]
- `current_dor_score`: float
- `status`: str


**Methods:**

  #### `add_iteration`

  ```python
  add_iteration(self, iteration: RefinementIteration)
  ```

  Add refinement iteration.

  **Parameters:**

  - `self`
  - `iteration` (RefinementIteration)



---

### TemporaryPlanManager

```python
class TemporaryPlanManager
```

Manages temporary plan creation and iterative refinement.

Workflow:
1. User request → create temp plan
2. Generate initial draft with AST/Lens analysis
3. Present to user for feedback
4. User provides refinement → update plan + AST/Lens
5. Repeat until DoR satisfied (mutual agreement)
6. User approves → promote to active/

Features:
- Automatic session tracking
- AST/Lens context accumulation
- Token-optimized plan generation
- DoR validation before approval


**Methods:**

  #### `start_refinement_session`

  ```python
  start_refinement_session(self, user_request: str, complexity_tier: int) -> InteractiveRefinementSession
  ```

  Start interactive refinement session.

Args:
    user_request: User's original request
    complexity_tier: Complexity tier (1-4)
    
Returns:
    InteractiveRefinementSession object

  **Parameters:**

  - `self`
  - `user_request` (str): User's original request
  - `complexity_tier` (int): Complexity tier (1-4)


  **Returns:** InteractiveRefinementSession
    InteractiveRefinementSession object


  #### `refine_plan`

  ```python
  refine_plan(self, session_id: str, user_feedback: str) -> Dict[str, Any]
  ```

  Refine plan based on user feedback.

Args:
    session_id: Session ID
    user_feedback: User's feedback/changes
    
Returns:
    Dict with refinement results

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID
  - `user_feedback` (str): User's feedback/changes


  **Returns:** Dict[str, Any]
    Dict with refinement results


  #### `request_approval`

  ```python
  request_approval(self, session_id: str) -> ApprovalResult
  ```

  Request plan approval (DoR gate).

Args:
    session_id: Session ID
    
Returns:
    ApprovalResult from lifecycle manager

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID


  **Returns:** ApprovalResult
    ApprovalResult from lifecycle manager


  #### `approve_plan`

  ```python
  approve_plan(self, session_id: str, approved_by: str) -> Dict[str, Any]
  ```

  Approve plan and promote to active.

Args:
    session_id: Session ID
    approved_by: User who approved
    
Returns:
    Dict with approval results

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID
  - `approved_by` (str): User who approved


  **Returns:** Dict[str, Any]
    Dict with approval results


  #### `reject_plan`

  ```python
  reject_plan(self, session_id: str, reason: str) -> Dict[str, Any]
  ```

  Reject plan and return to drafting.

Args:
    session_id: Session ID
    reason: Rejection reason
    
Returns:
    Dict with rejection results

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID
  - `reason` (str): Rejection reason


  **Returns:** Dict[str, Any]
    Dict with rejection results



---
