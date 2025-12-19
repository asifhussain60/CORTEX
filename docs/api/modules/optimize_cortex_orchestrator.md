# optimize_cortex_orchestrator

CORTEX Optimization Orchestrator

Performs holistic review of CORTEX architecture and executes optimizations
with full git tracking and metrics collection.

This orchestrator:
1. Runs all SKULL tests (brain protection validation)
2. Analyzes CORTEX architecture, operation history, patterns learned
3. Generates optimization plan with prioritized actions
4. Executes optimizations with git commits for tracking
5. Collects metrics on improvements achieved

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0.0


## Table of Contents

### Classes
- [OptimizeCortexOrchestrator](#optimizecortexorchestrator)

### Functions
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, json, logging, pathlib, re, sqlite3, src, subprocess, typing, yaml


## Classes

### OptimizeCortexOrchestrator

```python
class OptimizeCortexOrchestrator(BaseOperationModule)
```

Entry point orchestrator for CORTEX optimization.

Coordinates:
- Phase 0: Holistic Instruction Review (CORTEX.prompt.md + copilot-instructions.md)
- Phase 1: Planning Rules Validation
- Phase 2: SKULL test execution (brain protection validation)
- Phase 2.3: Hardcoded path cleanup
- Phase 2.5: Silent system alignment check (admin only)
- Phase 3: Architecture analysis (holistic review)
- Phase 4: Pattern learning (knowledge graph insights)
- Phase 5: Optimization planning (prioritized action generation)
- Phase 6: Optimization execution (with git tracking)
- Phase 6.5: Documentation deduplication
- Phase 7: Metrics collection (improvement tracking)

Usage:
    orchestrator = OptimizeCortexOrchestrator(project_root=Path('/path/to/cortex'))
    result = orchestrator.execute(context={})
    
    # Result includes:
    # - metrics: OptimizationMetrics with full details
    # - git_commits: List of commit hashes for tracking
    # - optimizations_applied: List of applied improvements


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]
  ```

  Validate prerequisites for optimization.

Checks:
- Project root exists
- Git repository present
- Test suite available
- Knowledge graph accessible

Args:
    context: Shared execution context

Returns:
    Tuple of (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared execution context


  **Returns:** tuple[bool, List[str]]
    Tuple of (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute CORTEX optimization workflow.

Workflow:
0. Phase 0: Holistic instruction file review (CORTEX.prompt.md + copilot-instructions.md)
1. Phase 1: Validate planning rules
2. Phase 2: Run SKULL tests (brain protection validation)
3. Phase 2.3: Cleanup hardcoded paths
4. Phase 2.5: Silent system alignment check (admin only)
5. Phase 3: Analyze architecture (holistic review)
6. Phase 4: Generate optimization plan
7. Phase 5: Execute optimizations (with git commits)
8. Phase 6: Collect final metrics
9. Phase 6.5: Documentation deduplication

Args:
    context: Shared execution context

Returns:
    OperationResult with optimization metrics and git commits

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared execution context


  **Returns:** OperationResult
    OperationResult with optimization metrics and git commits


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback optimization changes.

Uses git to revert commits if needed.

Args:
    context: Shared execution context

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared execution context


  **Returns:** bool
    True if successful, False otherwise



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register module with operation factory.


**Returns:** BaseOperationModule


---
