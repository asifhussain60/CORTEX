# complexity_analyzer

Complexity Analyzer - Multi-dimensional complexity scoring for tiered routing.

Purpose:
    Analyzes user requests and determines planning complexity to enable
    intelligent routing: HIGH→incremental, MEDIUM→conditional, LOW→skeleton.

Features:
    - 4-dimensional scoring: scope (25), dependencies (25), risk (30), uncertainty (20)
    - Complexity tiers: CRITICAL (90-100), HIGH (70-89), MEDIUM (40-69), LOW (20-39), TRIVIAL (0-19)
    - Auto-routing logic: Security/auth/migrations/APIs→incremental planning
    - Integration with TieredRouter for Planning System 3.0

Author: Asif Hussain
Date: December 2024
Version: 1.0.0


## Table of Contents

### Classes
- [ComplexityTier](#complexitytier)
- [ComplexityScore](#complexityscore)
- [ComplexityAnalyzer](#complexityanalyzer)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, enum, json, logging, pathlib, re, sys, typing


## Classes

### ComplexityTier

```python
class ComplexityTier(Enum)
```

Complexity tiers for planning routing decisions



---

### ComplexityScore

```python
class ComplexityScore
```

**Decorators:** `dataclass`

Result of complexity analysis


**Attributes:**

- `total_score`: int
- `tier`: ComplexityTier
- `dimensions`: Dict[str, int]
- `rationale`: List[str]
- `recommendation`: str
- `triggers`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary for serialization

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### ComplexityAnalyzer

```python
class ComplexityAnalyzer
```

Analyzes planning complexity using 4-dimensional scoring.

Scoring Methodology:
    - Scope Magnitude (25 pts): Files, entities, API endpoints affected
    - Dependencies (25 pts): External services, libraries, breaking changes
    - Risk Level (30 pts): Security, auth, data loss, compliance concerns
    - Uncertainty (20 pts): Ambiguous requirements, unknown tech, R&D needed

Auto-Route Triggers (HIGH complexity):
    - Security patterns: authentication, authorization, encryption
    - Data operations: migrations, schema changes, data loss risk
    - API changes: breaking changes, versioning, contract modifications
    - Critical domains: payment, healthcare, financial calculations

Integration:
    - Called by TieredRouter before classification
    - Influences Tier 3 vs Tier 4 routing decisions
    - Used by Planning Orchestrator for execution mode selection


**Methods:**

  #### `analyze`

  ```python
  analyze(self, user_request: str, codebase_context: Optional[Dict]) -> ComplexityScore
  ```

  Analyze planning complexity of user request.

Args:
    user_request: User's feature request or task description
    codebase_context: Optional codebase analysis from AST (file count, dependencies, etc.)

Returns:
    ComplexityScore with tier, dimensions, and routing recommendation

Example:
    >>> analyzer = ComplexityAnalyzer()
    >>> score = analyzer.analyze("Add JWT authentication to API")
    >>> print(score.tier)  # HIGH (security trigger detected)
    >>> print(score.recommendation)  # "Use incremental planning with TDD"

  **Parameters:**

  - `self`
  - `user_request` (str): User's feature request or task description
  - `codebase_context` (Optional[Dict]) = `None`: Optional codebase analysis from AST (file count, dependencies, etc.)


  **Returns:** ComplexityScore
    ComplexityScore with tier, dimensions, and routing recommendation



---
