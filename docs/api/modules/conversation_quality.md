# conversation_quality

CORTEX 3.0 - Conversation Quality Analyzer

Purpose: Semantic analysis of conversations to detect strategic value.
Scores conversations based on planning depth, reasoning, and decision rationale.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [SemanticElements](#semanticelements)
- [QualityScore](#qualityscore)
- [ConversationQualityAnalyzer](#conversationqualityanalyzer)

### Functions
- [create_analyzer](#create_analyzer)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, re, typing


## Classes

### SemanticElements

```python
class SemanticElements
```

**Decorators:** `dataclass`

Detected semantic elements in a conversation.


**Attributes:**

- `multi_phase_planning`: bool
- `phase_count`: int
- `challenge_accept_flow`: bool
- `design_decisions`: bool
- `file_references`: int
- `code_blocks`: int
- `next_steps_provided`: bool
- `code_implementation`: bool
- `architectural_discussion`: bool
- `security_discussion`: bool
- `code_review`: bool



---

### QualityScore

```python
class QualityScore
```

**Decorators:** `dataclass`

Conversation quality assessment.


**Attributes:**

- `total_score`: int
- `level`: str
- `elements`: SemanticElements
- `reasoning`: str
- `should_show_hint`: bool



---

### ConversationQualityAnalyzer

```python
class ConversationQualityAnalyzer
```

Analyzes conversation quality using CORTEX 3.0 semantic scoring.

Scoring Matrix (from HYBRID-CAPTURE-SIMULATION-REPORT.md):
- Multi-phase planning: 3 points per phase
- Challenge/Accept flow: 3 points
- Design decisions: 2 points
- File references: 1 point per file (max 3)
- Next steps provided: 2 points
- Code implementation: 1 point
- Architectural discussion: 2 points

Quality Thresholds:
- EXCELLENT: 10+ points (high strategic value)
- GOOD: 6-9 points (moderate strategic context)
- FAIR: 3-5 points (some strategic context)
- LOW: 0-2 points (minimal strategic content)


**Methods:**

  #### `analyze_conversation`

  ```python
  analyze_conversation(self, user_prompt: str, assistant_response: str) -> QualityScore
  ```

  Analyze a single conversation turn for strategic value.

Args:
    user_prompt: User's input message
    assistant_response: CORTEX's response
    
Returns:
    QualityScore with semantic analysis and hint recommendation

  **Parameters:**

  - `self`
  - `user_prompt` (str): User's input message
  - `assistant_response` (str): CORTEX's response


  **Returns:** QualityScore
    QualityScore with semantic analysis and hint recommendation


  #### `analyze_multi_turn_conversation`

  ```python
  analyze_multi_turn_conversation(self, turns: List[Tuple[str, str]]) -> QualityScore
  ```

  Analyze a multi-turn conversation.

Args:
    turns: List of (user_prompt, assistant_response) tuples
    
Returns:
    Aggregated quality score for entire conversation

  **Parameters:**

  - `self`
  - `turns` (List[Tuple[str, str]]): List of (user_prompt, assistant_response) tuples


  **Returns:** QualityScore
    Aggregated quality score for entire conversation



---

## Functions

### create_analyzer

```python
create_analyzer(config: Dict) -> ConversationQualityAnalyzer
```

Factory function to create analyzer with config.

Args:
    config: Optional configuration dict with 'hint_threshold' key
    
Returns:
    Configured ConversationQualityAnalyzer instance


**Parameters:**

- `config` (Dict) = `None`: Optional configuration dict with 'hint_threshold' key


**Returns:** ConversationQualityAnalyzer
  Configured ConversationQualityAnalyzer instance


---
