# user_profile_governance

User Profile Governance Extensions - Sprint 1 Day 3

Adds governance-related fields to user profile system for
first-time acknowledgment tracking.

SCHEMA ADDITIONS:
- acknowledged_rulebook: BOOLEAN flag (0/1)
- rulebook_acknowledged_at: TIMESTAMP of acknowledgment
- onboarding_completed: BOOLEAN flag for full onboarding status

MIGRATION:
This module provides safe migration that:
1. Checks if columns already exist
2. Adds columns only if missing
3. Sets sensible defaults (acknowledged=0 for existing users)
4. Preserves all existing data

USAGE:
    from src.tier1.user_profile_governance import UserProfileGovernance
    
    governance = UserProfileGovernance()
    
    if not governance.has_acknowledged_rulebook():
        # Show onboarding flow
        pass
    
    # Mark as acknowledged
    governance.mark_rulebook_acknowledged()

SPRINT 1 DAY 3-4: First-Time Acknowledgment
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025


## Table of Contents

### Classes
- [UserProfileGovernance](#userprofilegovernance)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, sqlite3, typing


## Classes

### UserProfileGovernance

```python
class UserProfileGovernance
```

Manages governance-related aspects of user profile.

Handles rulebook acknowledgment, onboarding completion,
and governance flag tracking.


**Methods:**

  #### `has_acknowledged_rulebook`

  ```python
  has_acknowledged_rulebook(self) -> bool
  ```

  Check if user has acknowledged the rulebook.

Returns:
    True if acknowledged, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if acknowledged, False otherwise


  #### `mark_rulebook_acknowledged`

  ```python
  mark_rulebook_acknowledged(self) -> bool
  ```

  Mark that user has acknowledged the rulebook.

Sets acknowledged_rulebook=1 and records timestamp.

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if successful, False otherwise


  #### `get_acknowledgment_status`

  ```python
  get_acknowledgment_status(self) -> Dict[str, Any]
  ```

  Get detailed acknowledgment status for user.

Returns:
    Dict with keys:
        - acknowledged: Boolean flag
        - acknowledged_at: Timestamp string or None
        - onboarding_completed: Boolean flag
        - needs_onboarding: Boolean (True if first-time user)

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with keys: - acknowledged: Boolean flag - acknowledged_at: Timestamp string or None - onboarding_completed: Boolean flag - needs_onboarding: Boolean (True if first-time user)


  #### `mark_onboarding_completed`

  ```python
  mark_onboarding_completed(self) -> bool
  ```

  Mark that user has completed full onboarding flow.

This is called after all 3 steps of onboarding are complete.

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if successful, False otherwise


  #### `reset_acknowledgment`

  ```python
  reset_acknowledgment(self) -> bool
  ```

  Reset acknowledgment status (for testing or re-onboarding).

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if successful, False otherwise



---
