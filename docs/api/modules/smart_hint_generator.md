# smart_hint_generator

CORTEX 3.0 - Smart Hint Generator

Purpose: Generate contextual hints for valuable conversation capture.
Shows hints only when quality threshold is met (reduces noise).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [SmartHint](#smarthint)
- [SmartHintGenerator](#smarthintgenerator)

### Functions
- [create_hint_generator](#create_hint_generator)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, src, typing


## Classes

### SmartHint

```python
class SmartHint
```

**Decorators:** `dataclass`

Smart hint for conversation capture.


**Attributes:**

- `should_show`: bool
- `hint_text`: str
- `conversation_id`: str
- `suggested_filename`: str
- `quality_level`: str



---

### SmartHintGenerator

```python
class SmartHintGenerator
```

Generates smart hints for conversation capture.

Based on CORTEX 3.0 Hybrid Capture design:
- Shows hints only for GOOD/EXCELLENT conversations
- Provides one-click capture suggestion
- Generates human-readable quality summary
- Stays in chat context (no context switching)


**Methods:**

  #### `generate_hint`

  ```python
  generate_hint(self, quality: QualityScore, user_prompt: str) -> SmartHint
  ```

  Generate smart hint based on conversation quality.

Args:
    quality: Quality score from ConversationQualityAnalyzer
    user_prompt: User's original prompt (for filename generation)
    
Returns:
    SmartHint with conditional display and capture instructions

  **Parameters:**

  - `self`
  - `quality` (QualityScore): Quality score from ConversationQualityAnalyzer
  - `user_prompt` (str): User's original prompt (for filename generation)


  **Returns:** SmartHint
    SmartHint with conditional display and capture instructions


  #### `generate_compact_hint`

  ```python
  generate_compact_hint(self, quality: QualityScore) -> Optional[str]
  ```

  Generate compact hint for inline display.

Args:
    quality: Quality assessment
    
Returns:
    One-line hint text or None if shouldn't show

  **Parameters:**

  - `self`
  - `quality` (QualityScore): Quality assessment


  **Returns:** Optional[str]
    One-line hint text or None if shouldn't show



---

## Functions

### create_hint_generator

```python
create_hint_generator(config: dict) -> SmartHintGenerator
```

Factory function to create hint generator with config.

Args:
    config: Optional configuration dict with 'vault_path' key
    
Returns:
    Configured SmartHintGenerator instance


**Parameters:**

- `config` (dict) = `None`: Optional configuration dict with 'vault_path' key


**Returns:** SmartHintGenerator
  Configured SmartHintGenerator instance


---
