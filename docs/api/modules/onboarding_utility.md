# onboarding_utility

Onboarding Utility

Lightweight user profile management for CORTEX onboarding.
Replaces heavy orchestrator (843 lines) with focused utility (~350 lines).

Core Operations:
- Create user profile
- Load existing profile
- Update profile preferences
- Interactive onboarding survey
- Profile validation

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [UserProfile](#userprofile)
- [ProfileResult](#profileresult)

### Functions
- [create_profile](#create_profile)
- [load_profile](#load_profile)
- [update_profile](#update_profile)
- [run_onboarding](#run_onboarding)
- [validate_profile](#validate_profile)


## Overview

- **Classes:** 2
- **Functions:** 9
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, src, typing


## Classes

### UserProfile

```python
class UserProfile
```

**Decorators:** `dataclass`

User profile with preferences.


**Attributes:**

- `user_id`: str
- `experience_level`: str
- `interaction_mode`: str
- `tech_stack`: Optional[str]
- `created_at`: str
- `updated_at`: str


**Methods:**


---

### ProfileResult

```python
class ProfileResult
```

**Decorators:** `dataclass`

Result of profile operation.


**Attributes:**

- `success`: bool
- `message`: str
- `profile`: Optional[UserProfile]
- `errors`: list


**Methods:**


---

## Functions

### create_profile

```python
create_profile(user_id: str, experience_level: str, interaction_mode: str, tech_stack: Optional[str]) -> ProfileResult
```

Create new user profile.

Args:
    user_id: User identifier
    experience_level: junior, mid, senior, expert
    interaction_mode: autonomous, guided, educational, pair
    tech_stack: azure, aws, gcp, custom, none (optional)
    
Returns:
    ProfileResult with creation outcome


**Parameters:**

- `user_id` (str): User identifier
- `experience_level` (str): junior, mid, senior, expert
- `interaction_mode` (str): autonomous, guided, educational, pair
- `tech_stack` (Optional[str]) = `None`: azure, aws, gcp, custom, none (optional)


**Returns:** ProfileResult
  ProfileResult with creation outcome


---

### load_profile

```python
load_profile(user_id: str) -> ProfileResult
```

Load existing user profile.

Args:
    user_id: User identifier
    
Returns:
    ProfileResult with loaded profile


**Parameters:**

- `user_id` (str): User identifier


**Returns:** ProfileResult
  ProfileResult with loaded profile


---

### update_profile

```python
update_profile(user_id: str, experience_level: Optional[str], interaction_mode: Optional[str], tech_stack: Optional[str]) -> ProfileResult
```

Update existing user profile.

Args:
    user_id: User identifier
    experience_level: New experience level (optional)
    interaction_mode: New interaction mode (optional)
    tech_stack: New tech stack (optional)
    
Returns:
    ProfileResult with update outcome


**Parameters:**

- `user_id` (str): User identifier
- `experience_level` (Optional[str]) = `None`: New experience level (optional)
- `interaction_mode` (Optional[str]) = `None`: New interaction mode (optional)
- `tech_stack` (Optional[str]) = `None`: New tech stack (optional)


**Returns:** ProfileResult
  ProfileResult with update outcome


---

### run_onboarding

```python
run_onboarding(user_id: str) -> ProfileResult
```

Run interactive onboarding survey (simplified for testing).
In production, this would be interactive CLI.

Args:
    user_id: User identifier
    
Returns:
    ProfileResult with survey outcome


**Parameters:**

- `user_id` (str): User identifier


**Returns:** ProfileResult
  ProfileResult with survey outcome


---

### validate_profile

```python
validate_profile(user_id: str) -> ProfileResult
```

Validate user profile completeness.

Args:
    user_id: User identifier
    
Returns:
    ProfileResult with validation outcome


**Parameters:**

- `user_id` (str): User identifier


**Returns:** ProfileResult
  ProfileResult with validation outcome


---
