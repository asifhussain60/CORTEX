# namespace_detector

CORTEX 3.0 - Namespace Detection Engine
======================================

Intelligent detection of conversation context to route questions correctly:
- cortex.* namespace: Questions about CORTEX framework itself
- workspace.* namespace: Questions about user's application code
- Eliminates confusion: "how is the code?" → proper routing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #2 (Week 1)
Effort: 8 hours (namespace detection engine)
Target: ≥90% routing accuracy, <100ms response time


## Table of Contents

### Classes
- [NamespaceType](#namespacetype)
- [ContextCue](#contextcue)
- [NamespaceDetectionResult](#namespacedetectionresult)
- [NamespaceDetector](#namespacedetector)
- [NamespaceResult](#namespaceresult)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** collections, dataclasses, datetime, enum, logging, re, typing


## Classes

### NamespaceType

```python
class NamespaceType(Enum)
```

Detected namespace types



---

### ContextCue

```python
class ContextCue
```

**Decorators:** `dataclass`

A single context detection cue


**Attributes:**

- `pattern`: str
- `namespace`: NamespaceType
- `weight`: float
- `requires_confirmation`: bool



---

### NamespaceDetectionResult

```python
class NamespaceDetectionResult
```

**Decorators:** `dataclass`

Result of namespace detection analysis


**Attributes:**

- `primary_namespace`: NamespaceType
- `confidence`: float
- `contributing_factors`: List[str]
- `alternative_namespace`: Optional[NamespaceType]
- `requires_clarification`: bool
- `suggested_clarification`: Optional[str]



---

### NamespaceDetector

```python
class NamespaceDetector
```

Intelligent namespace detection for question routing.

Analyzes user questions to determine if they're asking about:
- CORTEX framework (brain health, agent performance, etc.)
- User's workspace code (their application, bugs, features)


**Methods:**

  #### `detect_namespace`

  ```python
  detect_namespace(self, user_message: str, conversation_history: Optional[List[str]], current_files: Optional[List[str]]) -> NamespaceDetectionResult
  ```

  Detect the namespace of a user question.

Args:
    user_message: The user's question/message
    conversation_history: Recent conversation for context
    current_files: Files currently open/discussed
    
Returns:
    NamespaceDetectionResult with detected namespace and confidence

  **Parameters:**

  - `self`
  - `user_message` (str): The user's question/message
  - `conversation_history` (Optional[List[str]]) = `None`: Recent conversation for context
  - `current_files` (Optional[List[str]]) = `None`: Files currently open/discussed


  **Returns:** NamespaceDetectionResult
    NamespaceDetectionResult with detected namespace and confidence


  #### `detect`

  ```python
  detect(self, user_message: str, context: Dict) -> 'NamespaceResult'
  ```

  Compatibility method for test suite.
Maps to detect_namespace with simplified result format.

  **Parameters:**

  - `self`
  - `user_message` (str)
  - `context` (Dict) = `None`


  **Returns:** 'NamespaceResult'



---

### NamespaceResult

```python
class NamespaceResult
```

**Decorators:** `dataclass`

Simplified result format for compatibility with test suite


**Attributes:**

- `namespace`: str
- `confidence`: float
- `indicators`: List[str]
- `reasoning`: str



---
