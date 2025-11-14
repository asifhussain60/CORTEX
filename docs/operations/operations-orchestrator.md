# Operations Orchestrator Operation

**Auto-generated:** 2025-11-14 11:19:45

---

## Overview

Universal Operations Orchestrator - CORTEX 2.0

This orchestrator coordinates ALL CORTEX operations (setup, story refresh, cleanup, etc.)
by executing modules in dependency-resolved order across defined phases.

Design Principles:
    - Single orchestrator for all operations
    - YAML-driven operation definitions
    - Topological sort for dependency resolution
    - Phase-based execution with priorities
    - Parallel execution of independent modules
    - Comprehensive error handling and rollback

Author: Asif Hussain
Version: 2.1 (Parallel Execution Optimization)

## Usage

```python
from src.operations.operations_orchestrator import OperationExecutionReport

operation = OperationExecutionReport()
result = operation.execute()
```

## Methods
