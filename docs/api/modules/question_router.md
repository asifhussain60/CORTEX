# question_router

CORTEX 3.0 - Intelligent Question Router
========================================

Routes user questions to appropriate handlers based on namespace detection.
Eliminates confusion between CORTEX framework questions and workspace code questions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #2 (Week 1)  
Effort: 6 hours (response template routing)
Target: ≥90% routing accuracy, <100ms response time


## Table of Contents

### Classes
- [QuestionRoutingResult](#questionroutingresult)
- [RoutingResult](#routingresult)
- [IntelligentQuestionRouter](#intelligentquestionrouter)
- [QuestionRouter](#questionrouter)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** agents, data_collectors, dataclasses, datetime, logging, pathlib, response_templates, typing


## Classes

### QuestionRoutingResult

```python
class QuestionRoutingResult
```

**Decorators:** `dataclass`

Result of question routing with recommended response template


**Attributes:**

- `namespace`: NamespaceType
- `confidence`: float
- `template_category`: str
- `template_name`: str
- `parameters`: Dict[str, Any]
- `requires_clarification`: bool
- `clarification_template`: Optional[str]



---

### RoutingResult

```python
class RoutingResult
```

**Decorators:** `dataclass`

Simplified result format for compatibility with test suite


**Attributes:**

- `template_name`: str
- `confidence`: float
- `parameters`: Dict
- `namespace`: str



---

### IntelligentQuestionRouter

```python
class IntelligentQuestionRouter
```

Routes user questions to appropriate response templates based on namespace detection.

Core routing logic:
- cortex.* namespace → CORTEX framework templates (health, status, brain metrics)
- workspace.* namespace → Workspace analysis templates (code quality, build status) 
- ambiguous → Clarification templates (ask user to specify)
- general → Standard help templates


**Methods:**

  #### `route_question`

  ```python
  route_question(self, user_message: str, conversation_history: Optional[List[str]], current_files: Optional[List[str]]) -> QuestionRoutingResult
  ```

  Route a user question to the appropriate response template.

Args:
    user_message: The user's question
    conversation_history: Recent conversation context
    current_files: Files currently in focus
    
Returns:
    QuestionRoutingResult with routing decision and template info

  **Parameters:**

  - `self`
  - `user_message` (str): The user's question
  - `conversation_history` (Optional[List[str]]) = `None`: Recent conversation context
  - `current_files` (Optional[List[str]]) = `None`: Files currently in focus


  **Returns:** QuestionRoutingResult
    QuestionRoutingResult with routing decision and template info


  #### `route`

  ```python
  route(self, message: str, context: Dict) -> 'RoutingResult'
  ```

  Compatibility method for test suite.
Maps to route_question with simplified result format.

  **Parameters:**

  - `self`
  - `message` (str)
  - `context` (Dict) = `None`


  **Returns:** 'RoutingResult'



---

### QuestionRouter

```python
class QuestionRouter
```

Compatibility wrapper for test suite


**Methods:**

  #### `route`

  ```python
  route(self, message: str, context: Dict) -> 'RoutingResult'
  ```


---
