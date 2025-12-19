# narrative_generator

Narrative Intelligence - Context-aware code explanations and storytelling.

Transforms technical AST analysis into human-friendly narratives that
explain code architecture, changes, and impacts.


## Table of Contents

### Classes
- [CodeNarrative](#codenarrative)
- [NarrativeGenerator](#narrativegenerator)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, typing


## Classes

### CodeNarrative

```python
class CodeNarrative
```

**Decorators:** `dataclass`

Human-friendly code explanation.


**Attributes:**

- `title`: str
- `summary`: str
- `details`: List[str]
- `impact_analysis`: str
- `recommendations`: List[str]
- `technical_depth`: str



---

### NarrativeGenerator

```python
class NarrativeGenerator
```

Generate context-aware code narratives.


**Methods:**

  #### `generate_narrative`

  ```python
  generate_narrative(self, narrative_type: str, context: Dict[str, Any], depth: str) -> CodeNarrative
  ```

  Generate narrative for given context.

Args:
    narrative_type: Type of narrative ('architecture_change', 'refactor_explanation', etc.)
    context: Context data (file paths, changes, affected modules, etc.)
    depth: Narrative depth level ('high-level', 'detailed', 'deep-dive')
    
Returns:
    CodeNarrative with human-friendly explanation
    
Raises:
    ValueError: If narrative_type is unknown

  **Parameters:**

  - `self`
  - `narrative_type` (str): Type of narrative ('architecture_change', 'refactor_explanation', etc.)
  - `context` (Dict[str, Any]): Context data (file paths, changes, affected modules, etc.)
  - `depth` (str) = `'detailed'`: Narrative depth level ('high-level', 'detailed', 'deep-dive')


  **Returns:** CodeNarrative
    CodeNarrative with human-friendly explanation


  #### `format_for_master_plan`

  ```python
  format_for_master_plan(self, ast_context: Dict[str, Any], lens_context: Dict[str, Any]) -> str
  ```

  Format AST/Lens analysis for master plan integration.

Target: 200-400 words for master plan "Context" section.
Provides high-level architecture overview and key insights.

Args:
    ast_context: AST analysis results (architecture, dependencies, complexity)
    lens_context: CORTEX Lens analysis results (patterns, smells, metrics)
    
Returns:
    Formatted narrative text (200-400 words)
    
Example Output:
    "The codebase analysis reveals a 4-tier architecture with 23 modules
    across orchestration, routing, and intelligence layers. AST analysis
    identified 12 key components with moderate coupling (avg 3.2 dependencies
    per module). Complexity metrics show 3 high-complexity modules requiring
    attention during implementation..."

  **Parameters:**

  - `self`
  - `ast_context` (Dict[str, Any]): AST analysis results (architecture, dependencies, complexity)
  - `lens_context` (Dict[str, Any]): CORTEX Lens analysis results (patterns, smells, metrics)


  **Returns:** str
    Formatted narrative text (200-400 words) Example Output: "The codebase analysis reveals a 4-tier architecture with 23 modules across orchestration, routing, and intelligence layers. AST analysis identified 12 key components with moderate coupling (avg 3.2 dependencies per module). Complexity metrics show 3 high-complexity modules requiring attention during implementation..."


  #### `format_for_worker_plan`

  ```python
  format_for_worker_plan(self, phase_context: Dict[str, Any], ast_context: Dict[str, Any]) -> str
  ```

  Format phase-specific context for worker plan.

Target: 100-200 words for worker plan "Phase Context" section.
Provides focused, actionable insights for specific phase implementation.

Args:
    phase_context: Phase-specific info (phase_id, focus_area, tasks)
    ast_context: AST analysis relevant to this phase
    
Returns:
    Formatted narrative text (100-200 words)
    
Example Output:
    "Phase 2 focuses on router implementation with 4 modules requiring creation.
    AST analysis shows existing router pattern in tier1/ that can be reused.
    Key dependencies: base_router.py (2 imports), route_analyzer.py (3 imports).
    Complexity: Moderate (avg 8.3 cyclomatic complexity). Recommend TDD approach
    with test coverage target of 85%..."

  **Parameters:**

  - `self`
  - `phase_context` (Dict[str, Any]): Phase-specific info (phase_id, focus_area, tasks)
  - `ast_context` (Dict[str, Any]): AST analysis relevant to this phase


  **Returns:** str
    Formatted narrative text (100-200 words) Example Output: "Phase 2 focuses on router implementation with 4 modules requiring creation. AST analysis shows existing router pattern in tier1/ that can be reused. Key dependencies: base_router.py (2 imports), route_analyzer.py (3 imports). Complexity: Moderate (avg 8.3 cyclomatic complexity). Recommend TDD approach with test coverage target of 85%..."



---
