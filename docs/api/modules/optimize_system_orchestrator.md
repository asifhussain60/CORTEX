# optimize_system_orchestrator

CORTEX System Optimizer - Meta-Level Orchestrator

Comprehensive system optimization from all angles:
1. Design-Implementation Synchronization (design_sync)
2. Code Health & Obsolete Tests (optimize_cortex)
3. Brain Tier Tuning & Knowledge Graph Optimization
4. Entry Point Alignment (orchestrator consistency)
5. Test Suite Optimization (SKULL-007 compliance)
6. Comprehensive Health Report

This meta-orchestrator coordinates ALL optimization operations to ensure:
- Maximum inbuilt tooling leverage
- Design-implementation alignment
- Brain protection layer integrity
- Knowledge graph quality
- Test suite health (100% pass rate)
- Entry point consistency

Configuration is loaded from cortex-brain/operations-config.yaml under system_optimization section.
No hardcoded limits or thresholds.

Natural Language Triggers:
- "optimize cortex system"
- "optimize everything"
- "run comprehensive optimization"
- "system health check comprehensive"
- "align all components"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Version: 3.0.0
Date: November 12, 2025


## Table of Contents

### Classes
- [OptimizeSystemOrchestrator](#optimizesystemorchestrator)

### Functions
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, json, logging, pathlib, re, src, subprocess, typing, yaml


## Classes

### OptimizeSystemOrchestrator

```python
class OptimizeSystemOrchestrator(BaseOperationModule)
```

Meta-level orchestrator for comprehensive CORTEX system optimization.

Coordinates 8 optimization phases:

Phase 0: Instruction File Review
    - Holistic review of CORTEX.prompt.md + copilot-instructions.md
    - Detect redundancy, outdated references, bloat
    - Validate trigger coverage and consistency
    - Optimize for token efficiency

Phase 1: Design Sync
    - Run design_sync_orchestrator
    - Resolve design-implementation drift
    - Consolidate status files
    - Update module counts

Phase 2: Code Health
    - Run optimize_cortex_orchestrator
    - Identify obsolete tests
    - Detect dead code
    - Analyze test coverage gaps

Phase 3: Brain Tuning
    - Validate tier boundaries (Tier 0, 1, 2, 3)
    - Prune low-confidence patterns (<0.50)
    - Detect and merge duplicate patterns
    - Validate brain protection rules (YAML)

Phase 4: Entry Point Alignment
    - Validate all orchestrator headers use HeaderFormatter
    - Sync command registry with natural language triggers
    - Update CORTEX.prompt.md with discovered commands
    - Ensure consistent copyright attribution

Phase 5: Test Suite Optimization
    - Execute obsolete test removal (from Phase 2)
    - Fix failing tests using recommendations
    - Validate 100% pass rate (SKULL-007 compliance)
    - Generate test coverage report

Phase 6: Comprehensive Report
    - Consolidate metrics from all phases
    - Calculate overall health score
    - Generate recommendations
    - Save to cortex-brain/system-optimization-report.md

Phase 7: Governance Health Check
    - Check rule position drift vs optimal ordering
    - Count forward references (target: <3)
    - Detect file bloat (target: <1200 lines)
    - Identify orphaned rules (never referenced)
    - Validate metadata (copilot_position, reference_count)
    - Calculate governance health score (0-100)

Phase 8: SKULL Test Discovery & Validation
    - Scan CORTEX system holistically for governance enforcement points
    - Identify missing SKULL tests for brain protection rules
    - Detect outdated SKULL tests (rules removed/refactored)
    - Validate SKULL test coverage (all Tier 0 instincts tested)
    - Recommend new SKULL tests based on governance drift
    - Execute existing SKULL tests and report failures

Usage:
    orchestrator = OptimizeSystemOrchestrator(project_root=Path('/path/to/cortex'))
    result = orchestrator.execute(context={'profile': 'comprehensive', 'mode': 'live'})


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return metadata for this operation module.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> OperationResult
  ```

  Validate prerequisites for system optimization.

Checks:
- CORTEX project root exists
- Required orchestrators available
- Git repository initialized
- Python environment configured

Args:
    context: Execution context

Returns:
    OperationResult with validation status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context


  **Returns:** OperationResult
    OperationResult with validation status


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute comprehensive system optimization.

Args:
    context: Execution context with keys:
        - profile: Optimization profile ('comprehensive', 'focused', 'minimal')
        - mode: Execution mode (always 'live')
        - skip_phases: Optional list of phases to skip

Returns:
    OperationResult with optimization status and metrics

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with keys:


  **Returns:** OperationResult
    OperationResult with optimization status and metrics



---

## Functions

### register

```python
register() -> OptimizeSystemOrchestrator
```

Register this module with the operations system.

Returns:
    Instance of OptimizeSystemOrchestrator


**Returns:** OptimizeSystemOrchestrator
  Instance of OptimizeSystemOrchestrator


---
