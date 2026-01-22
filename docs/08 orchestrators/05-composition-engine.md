# Composition Engine & Composed Orchestrator

**Status:** Production Ready | **Version:** 1.0.0 | **Category:** Specialized Orchestrators | **Module:** `cortex/orchestrators/composition/composition_engine.py`

---

## Overview

The **Composition Engine** enables flexible orchestrator composition patterns for building complex workflows from simpler components. It implements four composition patterns (Sequential, Parallel, Conditional, Delegating) for different use cases.

### Purpose

- Compose orchestrators into complex workflows
- Support multiple composition patterns
- Enable error handling at each step
- Manage recovery and rollback
- Generate composition metadata
- Provide orchestrator delegation

---

## Architecture

### Composition Patterns

```
┌────────────────────────────────────────────┐
│        Composition Engine                  │
│    (Pattern Factory & Orchestrator)        │
└────────────────────────────────────────────┘

┌─ SEQUENTIAL
│  Step 1 → Step 2 → Step 3 → Step 4
│  (ETL, data pipelines, batch processing)
│
├─ PARALLEL
│  ├─ Task 1 ─┐
│  ├─ Task 2 ─┼─ Aggregate
│  └─ Task 3 ─┘
│  (Concurrent analysis, bulk operations)
│
├─ CONDITIONAL
│  ├─ IF condition
│  │  └─ Path A
│  └─ ELSE
│     └─ Path B
│  (Decision trees, error handling)
│
└─ DELEGATING
   Parent ──┐
            ├─→ Child 1
            ├─→ Child 2
            └─→ Child 3
   (Hierarchical decomposition)
```

### Key Components

1. **Pattern Selector**
   - Analyzes operation characteristics
   - Recommends appropriate pattern
   - Creates pattern-specific engine

2. **Step Manager**
   - Manages step sequences
   - Tracks step dependencies
   - Coordinates step execution

3. **Error Handler**
   - Step-level error handling
   - Recovery strategies
   - Rollback support

4. **Result Aggregator**
   - Collects step results
   - Merges output
   - Validates completeness

---

## How It Works

### Sequential Pattern

```
Use Case: Extract → Transform → Load (ETL)
          Validate → Process → Archive

┌─────────────────────────────────────────┐
│  Step 1: Extract Data                   │
│  Output: Raw data                       │
└─────────┬─────────────────────────────┘
          │ Pass through
          ▼
┌─────────────────────────────────────────┐
│  Step 2: Transform Data                 │
│  Input: Raw data                        │
│  Output: Transformed data               │
└─────────┬─────────────────────────────┘
          │ Pass through
          ▼
┌─────────────────────────────────────────┐
│  Step 3: Load Data                      │
│  Input: Transformed data                │
│  Output: Load status                    │
└─────────────────────────────────────────┘

Error Handling: If any step fails, rollback to start
Recovery: Retry failed step or skip to next
```

### Parallel Pattern

```
Use Case: Concurrent Analysis
          Bulk Data Loading
          Independent Operations

┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Task 1: Analyze    │     │  Task 2: Analyze    │     │  Task 3: Analyze    │
│  Component A        │     │  Component B        │     │  Component C        │
│  Runtime: 500ms     │     │  Runtime: 300ms     │     │  Runtime: 400ms     │
└──────────┬──────────┘     └──────────┬──────────┘     └──────────┬──────────┘
           │                           │                           │
           └───────────────┬───────────┴──────────────┬───────────┘
                           │                          │
                    ┌──────▼──────────────────┐
                    │ Aggregate Results       │
                    │ Duration: 50ms          │
                    │ Total Time: 500ms       │
                    └────────────────────────┘

Total Duration: MAX(500, 300, 400) + 50 = 550ms
```

### Conditional Pattern

```
Use Case: Error Handling
          Decision Trees
          A/B Testing

┌──────────────────────────┐
│  Evaluate Condition      │
└──────┬───────────────────┘
       │
       ├─ IF condition TRUE ─┐
       │                     └─→ ┌─────────────────┐
       │                        │ Path A Handler  │
       │                        └─────────────────┘
       │
       └─ IF condition FALSE ┐
                             └─→ ┌─────────────────┐
                                │ Path B Handler  │
                                └─────────────────┘

Condition Examples:
  - Error occurred: route to error handler
  - Low risk: execute direct path
  - High complexity: use advanced path
```

### Delegating Pattern

```
Use Case: Hierarchical Task Distribution
          Microservice Orchestration
          Multi-Tenant Operations

┌────────────────────────────────────────┐
│   Parent Orchestrator                  │
│   (Task Distribution)                  │
└──────────────┬───┬──────────┬────┬─────┘
               │   │          │    │
        ┌──────▼┐ ┌┴──────┐ ┌─┴───────┐ ┌──────────┐
        │Child1 │ │Child2 │ │Child3   │ │Child4    │
        │       │ │       │ │         │ │          │
        │Domain1│ │Domain2│ │Domain3  │ │External  │
        └─┬─────┘ └┬──────┘ └──┬──────┘ └────┬─────┘
          │        │           │             │
          └────┬───┴───┬───────┘──────┬──────┘
               │       │              │
          ┌────▼───────▼──────────────▼────┐
          │  Result Aggregation            │
          │  (Merge sub-results)           │
          └────────────────────────────────┘
```

---

## How to Use It

### Basic Usage

```python
from cortex.orchestrators.composition import CompositionEngine, CompositionPattern

# Create engine
engine = CompositionEngine()

# Define composed orchestrator
composed = engine.create_composed_orchestrator(
    name="etl_pipeline",
    pattern=CompositionPattern.SEQUENTIAL,
    steps=[
        "extract_data",
        "transform_data",
        "validate_data",
        "load_data"
    ]
)

# Execute
result = engine.execute_composition(composed)
```

### Pattern 1: Sequential ETL

```python
composed = engine.create_composed_orchestrator(
    name="data_processing",
    pattern=CompositionPattern.SEQUENTIAL,
    steps=[
        "extract_from_source",
        "apply_transformations",
        "validate_output",
        "load_to_warehouse"
    ],
    error_strategy="rollback_on_failure"
)

result = engine.execute_composition(composed)
print(f"Processed: {result.metadata['steps_completed']} steps")
```

### Pattern 2: Parallel Analysis

```python
composed = engine.create_composed_orchestrator(
    name="parallel_analysis",
    pattern=CompositionPattern.PARALLEL,
    steps=[
        "analyze_performance",
        "analyze_security",
        "analyze_coverage"
    ],
    concurrency_level=3,
    timeout_per_step=300
)

result = engine.execute_composition(composed)
```

### Pattern 3: Conditional Workflow

```python
composed = engine.create_composed_orchestrator(
    name="conditional_execution",
    pattern=CompositionPattern.CONDITIONAL,
    condition=lambda ctx: ctx['risk_level'] > 0.8,
    true_path=["rigorous_validation", "manual_review"],
    false_path=["automated_validation"]
)

result = engine.execute_composition(composed)
```

### Pattern 4: Hierarchical Delegation

```python
composed = engine.create_composed_orchestrator(
    name="hierarchical_task",
    pattern=CompositionPattern.DELEGATING,
    steps=[
        "financial_orchestrator:process_payment",
        "audit_orchestrator:log_transaction",
        "notification_orchestrator:notify_user"
    ],
    delegation_strategy="concurrent"
)

result = engine.execute_composition(composed)
```

---

## Error Handling & Recovery

### Recovery Strategies

```python
class RecoveryStrategy(Enum):
    RETRY_FAILED_STEP = "Retry the failed step"
    SKIP_FAILED_STEP = "Skip and continue"
    ROLLBACK_CHECKPOINT = "Rollback to last checkpoint"
    HALT_AND_ALERT = "Stop and alert"
    USE_FALLBACK_VALUE = "Use fallback/default value"
```

### Usage

```python
# Configure error handling
composed.set_error_handling(
    strategy=RecoveryStrategy.ROLLBACK_CHECKPOINT,
    max_retries=3,
    retry_backoff="exponential",
    checkpoint_interval=2
)

result = engine.execute_composition(composed)
```

---

## Best Practices

```python
best_practices = [
    "Define clear step dependencies",
    "Implement comprehensive error handling",
    "Add audit logging to each step",
    "Use meaningful step identifiers",
    "Document composition intent",
    "Plan for rollback scenarios",
    "Test composition paths",
    "Monitor step performance",
    "Set appropriate timeouts",
    "Handle edge cases"
]
```

---

## Integration Points

### Dependencies

- **Individual Orchestrators**: Provide step implementations
- **Audit Logger**: Track composition execution
- **State Manager**: Persist checkpoints

### Dependents

- **MasterOrchestrator**: Uses for complex workflows
- **Workflow Orchestrator**: Composes stages

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `create_composition` | Create new composition |
| `execute_composition` | Execute composition |
| `get_composition_status` | Get execution status |
| `rollback_composition` | Rollback to checkpoint |

---

## Example Workflows

### Workflow 1: ETL Pipeline

```python
pipeline = engine.create_composed_orchestrator(
    name="customer_data_etl",
    pattern=CompositionPattern.SEQUENTIAL,
    steps=[
        "extract_from_crm",
        "clean_and_standardize",
        "validate_integrity",
        "load_to_data_warehouse"
    ]
)
```

### Workflow 2: Concurrent Validation

```python
validation = engine.create_composed_orchestrator(
    name="multi_level_validation",
    pattern=CompositionPattern.PARALLEL,
    steps=[
        "syntax_validation",
        "security_validation",
        "performance_validation"
    ]
)
```

---

## Performance

| Operation | Duration |
|-----------|----------|
| Composition creation | 10-20ms |
| Sequential (4 steps) | 100-500ms |
| Parallel (3 tasks) | ~max(task_durations) |
| Conditional (2 paths) | ~chosen_path_duration |

---

## Testing

- **Coverage:** 93%
- **Pattern validation:** 98%
- **Error recovery:** 91%

---

## Related Documentation

- 📖 [Orchestrator Composition](../patterns/composition-patterns.md)
- 📖 [Error Handling](../patterns/error-handling.md)
- 📖 [Master Orchestrator](01-master-orchestrator.md)

---

## Copyright & License

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

CORTEX Framework - Composition Engine Module
Status: Production Ready | Version: 1.0.0

---

**Last Updated:** 2026-01-22 | **Author:** CORTEX Documentation Generator
