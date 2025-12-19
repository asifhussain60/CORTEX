# user_profile_manager

User Profile Manager - Tech Stack Preference System
CORTEX 3.2.1 Phase 1: User Profile System Enhancements

Manages user profile preferences including tech stack configurations.
Provides preset configurations for common cloud platforms and custom options.


## Table of Contents

### Classes
- [TechStackPreset](#techstackpreset)
- [UserProfileManager](#userprofilemanager)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** enum, json, pathlib, sqlite3, typing


## Classes

### TechStackPreset

```python
class TechStackPreset(Enum)
```

Predefined tech stack configurations for common platforms.

Each preset represents a complete, opinionated stack for a specific cloud provider.
NO_PREFERENCE allows CORTEX to recommend best practices without bias.
CUSTOM allows users to mix and match individual tools.


**Methods:**

  #### `get_configuration`

  *Decorators:* `classmethod`

  ```python
  get_configuration(cls, preset: 'TechStackPreset') -> Optional[Dict[str, str]]
  ```

  Get the full configuration dictionary for a preset.

Args:
    preset: TechStackPreset enum value
    
Returns:
    Dict with cloud_provider, container_platform, ci_cd, iac, architecture
    None if preset is NO_PREFERENCE

  **Parameters:**

  - `cls`
  - `preset` ('TechStackPreset'): TechStackPreset enum value


  **Returns:** Optional[Dict[str, str]]
    Dict with cloud_provider, container_platform, ci_cd, iac, architecture None if preset is NO_PREFERENCE



---

### UserProfileManager

```python
class UserProfileManager
```

Manages user profile preferences with focus on tech stack configurations.

Provides high-level interface for tech stack preference management,
wrapping WorkingMemory's user_profile table operations.


**Methods:**

  #### `set_tech_stack_preset`

  ```python
  set_tech_stack_preset(self, preset: TechStackPreset) -> bool
  ```

  Set tech stack preference using a predefined preset.

Args:
    preset: TechStackPreset enum value
    
Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `preset` (TechStackPreset): TechStackPreset enum value


  **Returns:** bool
    True if successful, False otherwise


  #### `set_tech_stack_custom`

  ```python
  set_tech_stack_custom(self, config: Dict[str, str]) -> bool
  ```

  Set custom tech stack configuration.

Args:
    config: Dict with cloud_provider, container_platform, ci_cd, iac, architecture
    
Returns:
    True if successful, False otherwise
    
Raises:
    ValueError: If configuration contains invalid values

  **Parameters:**

  - `self`
  - `config` (Dict[str, str]): Dict with cloud_provider, container_platform, ci_cd, iac, architecture


  **Returns:** bool
    True if successful, False otherwise


  #### `get_tech_stack_preference`

  ```python
  get_tech_stack_preference(self) -> Optional[Dict[str, str]]
  ```

  Get current tech stack preference.

Returns:
    Dict with tech stack configuration, or None if not set/NO_PREFERENCE

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, str]]
    Dict with tech stack configuration, or None if not set/NO_PREFERENCE


  #### `update_tech_stack_preset`

  ```python
  update_tech_stack_preset(self, preset: TechStackPreset) -> bool
  ```

  Update existing tech stack preference to a new preset.

Alias for set_tech_stack_preset for clarity in update scenarios.

Args:
    preset: New TechStackPreset enum value
    
Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `preset` (TechStackPreset): New TechStackPreset enum value


  **Returns:** bool
    True if successful, False otherwise


  #### `clear_tech_stack_preference`

  ```python
  clear_tech_stack_preference(self) -> bool
  ```

  Clear tech stack preference (equivalent to NO_PREFERENCE).

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if successful, False otherwise


  #### `get_profile`

  ```python
  get_profile(self) -> Optional[Dict[str, Any]]
  ```

  Get complete user profile including tech stack preference.

Returns:
    Dict with interaction_mode, experience_level, tech_stack_preference, timestamps
    None if profile doesn't exist

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]
    Dict with interaction_mode, experience_level, tech_stack_preference, timestamps None if profile doesn't exist


  #### `set_response_detail`

  ```python
  set_response_detail(self, detail_level: str) -> bool
  ```

  Set user's response detail preference.

Args:
    detail_level: One of 'concise', 'balanced', 'verbose'

Returns:
    True if successful, False otherwise

Raises:
    ValueError: If detail_level is invalid

  **Parameters:**

  - `self`
  - `detail_level` (str): One of 'concise', 'balanced', 'verbose'


  **Returns:** bool
    True if successful, False otherwise


  #### `get_response_detail`

  ```python
  get_response_detail(self) -> Optional[str]
  ```

  Get user's response detail preference.

Returns:
    'concise', 'balanced', or 'verbose', or None if not set

  **Parameters:**

  - `self`


  **Returns:** Optional[str]
    'concise', 'balanced', or 'verbose', or None if not set


  #### `infer_response_detail_from_mode`

  ```python
  infer_response_detail_from_mode(self, interaction_mode: str) -> str
  ```

  Infer appropriate response_detail from interaction_mode.

Used for migration/backward compatibility.

Args:
    interaction_mode: User's interaction mode

Returns:
    Inferred response detail level

  **Parameters:**

  - `self`
  - `interaction_mode` (str): User's interaction mode


  **Returns:** str
    Inferred response detail level


  #### `set_testing_frameworks`

  ```python
  set_testing_frameworks(self, frameworks: Dict[str, str]) -> bool
  ```

  Set user's preferred testing frameworks for different test types.

Args:
    frameworks: Dict mapping test type to framework name
               e.g., {"unit": "pytest", "e2e_browser": "Playwright"}

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `frameworks` (Dict[str, str]): Dict mapping test type to framework name


  **Returns:** bool
    True if successful, False otherwise


  #### `get_testing_frameworks`

  ```python
  get_testing_frameworks(self) -> Optional[Dict[str, str]]
  ```

  Get user's preferred testing frameworks.

Returns:
    Dict mapping test type to framework name, or None if not set

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, str]]
    Dict mapping test type to framework name, or None if not set


  #### `update_testing_framework`

  ```python
  update_testing_framework(self, test_type: str, framework: str) -> bool
  ```

  Update a single testing framework preference.

Args:
    test_type: Type of test (unit, e2e_browser, etc.)
    framework: Framework name (pytest, Playwright, etc.)

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `test_type` (str): Type of test (unit, e2e_browser, etc.)
  - `framework` (str): Framework name (pytest, Playwright, etc.)


  **Returns:** bool
    True if successful, False otherwise



---
