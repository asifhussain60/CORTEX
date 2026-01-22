# Workflow Orchestrator

**Status:** Production Ready | **Version:** 1.0.0 | **Category:** Core Orchestrators | **Module:** `cortex/orchestrators/core/workflow_orchestrator.py`

---

## Overview

The **Workflow Orchestrator** manages the complete **5-Stage Orchestration Pipeline** of CORTEX, coordinating data flow between all five stages while handling errors and maintaining comprehensive execution context.

### Purpose

- Orchestrate all 5 stages of the Master Orchestration pipeline
- Manage data flow between stages
- Handle stage boundary errors
- Maintain execution context across phases
- Aggregate stage results
- Produce final execution output

---

## Architecture

### 5-Stage Pipeline Overview

```
┌────────────────────────────────────────────────────────┐
│                 WORKFLOW ORCHESTRATOR                  │
└────────────────────────────────────────────────────────┘

┌─ STAGE 1: COMPREHENSION
│  └─ Language analysis via LENS Protocol
│     Outputs: Parsed intent, keywords, domain
│
├─ STAGE 2: REPOSITORY SCAN
│  └─ System-wide code analysis
│     Outputs: Code structure, dependencies, affected files
│
├─ STAGE 3: KNOWLEDGE INTEGRATION
│  └─ Merge governance + domain context
│     Outputs: Best practices, applicable rules, knowledge graph
│
├─ STAGE 4: APPROVAL GATES
│  └─ 5 approval gates + implementation planning
│     Outputs: Execution plan, dependencies, resource requirements
│
└─ STAGE 5: EXECUTION
   └─ Execute approved operations
      Outputs: Results, audit trail, state updates
```

### Key Components

1. **Stage Executors**
   - Stage1Executor: Comprehension
   - Stage2Executor: Repository scan
   - Stage3Executor: Knowledge integration
   - Stage4Executor: Approval
   - Stage5Executor: Execution

2. **Context Manager**
   - Maintains execution context across stages
   - Propagates data between stages
   - Handles context enrichment

3. **Error Handler**
   - Stage boundary error handling
   - Fallback options
   - Recovery strategies

4. **Result Aggregator**
   - Collects results from all stages
   - Integrates stage outputs
   - Produces unified result

---

## How It Works

### Execution Flow

```
1. WORKFLOW INITIATED
   ├─ Validate workflow input
   ├─ Initialize context
   └─ Begin stage 1

2. STAGE 1: COMPREHENSION
   ├─ Parse user intent
   ├─ Extract keywords
   ├─ Identify domain
   └─ Output: ComprehensionContext

3. STAGE 2: REPOSITORY SCAN
   ├─ Analyze codebase
   ├─ Map dependencies
   ├─ Identify affected files
   └─ Output: ScanContext

4. STAGE 3: KNOWLEDGE INTEGRATION
   ├─ Load applicable rules
   ├─ Query knowledge graph
   ├─ Extract best practices
   └─ Output: KnowledgeContext

5. STAGE 4: APPROVAL
   ├─ 5 approval gates
   ├─ Generate execution plan
   ├─ Calculate resource needs
   └─ Output: ApprovalContext

6. STAGE 5: EXECUTION
   ├─ Execute approved operations
   ├─ Monitor execution
   ├─ Collect results
   └─ Output: ExecutionResult

7. AGGREGATE RESULTS
   ├─ Merge all stage outputs
   ├─ Create unified response
   └─ Return to user
```

### Stage Characteristics

| Stage | Purpose | Input | Output | Duration |
|-------|---------|-------|--------|----------|
| 1 | Comprehension | User intent | Parsed context | ~100ms |
| 2 | Scan | Parsed context | Code analysis | ~500ms |
| 3 | Knowledge | Code analysis | Rules & practices | ~200ms |
| 4 | Approval | Rules & practices | Execution plan | ~300ms |
| 5 | Execution | Execution plan | Results | ~1-5s |

---

## Stage Details

### Stage 1: Comprehension (LENS Protocol)

```
Input: "Fix race condition in Master Orchestrator"
       └─ Keywords: ["fix", "race condition", "master"]
       └─ Urgency: "high"

Processing:
├─ Language Analysis
│  └─ Tokenize: ["Fix", "race", "condition", ...]
│
├─ Examination (AST)
│  └─ Parse code structure
│  └─ Identify affected modules
│
├─ Navigation (Git)
│  └─ Review change history
│  └─ Find related commits
│
└─ Synthesis (Context)
   └─ Merge signals
   └─ Compute confidence

Output: ComprehensionContext {
  intent_type: "FIX",
  domain: "core",
  confidence: 0.95,
  keywords: ["race", "condition", "synchronization"],
  affected_modules: ["master_orchestrator"]
}
```

### Stage 2: Repository Scan

```
Input: ComprehensionContext
       └─ Domain: "core"
       └─ Affected modules: ["master_orchestrator"]

Processing:
├─ Full codebase scan
├─ Build dependency graph
├─ Identify affected files
├─ Analyze impact scope
└─ Extract test coverage info

Output: ScanContext {
  affected_files: [
    "cortex/orchestrators/core/master_orchestrator.py",
    "tests/unit/orchestrators/test_master_orchestrator.py"
  ],
  impact_scope: "file",
  test_coverage: 95%,
  dependencies: [...]
}
```

### Stage 3: Knowledge Integration

```
Input: ScanContext + Domain rules
       └─ Core domain rules
       └─ Governance tier 0 rules

Processing:
├─ Load TIER 0 rules
├─ Query knowledge graph
├─ Extract best practices
├─ Build rule matrix
└─ Validate against boundaries

Output: KnowledgeContext {
  applicable_rules: [
    "CORE-008: TDD enforcement",
    "CORE-011: Type hints",
    "CORE-012: Docstrings",
    "CORE-013: No bare except"
  ],
  best_practices: [...],
  compliance_requirements: [...]
}
```

### Stage 4: Approval

```
Input: KnowledgeContext
       └─ Applicable rules
       └─ Compliance requirements

5 Approval Gates:
├─ GATE 1: Governance Validation
│  └─ Check TIER 0 rule compliance
│
├─ GATE 2: Impact Assessment
│  └─ Analyze scope and risk
│
├─ GATE 3: Resource Planning
│  └─ Allocate required resources
│
├─ GATE 4: Schedule Approval
│  └─ Plan execution timing
│
└─ GATE 5: Stakeholder Approval
   └─ Notify affected teams

Output: ApprovalContext {
  approval_status: "APPROVED",
  execution_plan: [...],
  resource_requirements: {...},
  schedule: {...}
}
```

### Stage 5: Execution

```
Input: ApprovalContext + Execution plan

Processing:
├─ Initialize execution environment
├─ Execute operation
├─ Monitor progress
├─ Collect results
└─ Perform cleanup

Output: ExecutionResult {
  status: "SUCCESS",
  duration_ms: 2350,
  result: {...},
  audit_trail: [...],
  state_changes: {...}
}
```

---

## How to Use It

### Basic Usage

```python
from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator

# Initialize orchestrator
workflow = WorkflowOrchestrator()

# Create workflow context
context = WorkflowExecutionContext(
    operation="fix_race_condition",
    description="Fix race condition in Master Orchestrator",
    keywords=["fix", "race", "synchronization"],
    domain="core",
    workspace_root=Path("/path/to/workspace")
)

# Execute workflow
result = workflow.execute_workflow(context)

# Check result
if result.success:
    print(f"Workflow completed in {result.duration_ms}ms")
    print(f"Stage results: {result.stage_results}")
else:
    print(f"Workflow failed: {result.error}")
```

### Advanced Usage

#### Pattern 1: Custom Stage Configuration

```python
# Configure specific stages
config = WorkflowConfiguration(
    enable_stage_1=True,
    enable_stage_2=True,
    enable_stage_3=True,
    enable_stage_4=False,  # Skip approval gates
    enable_stage_5=True,
    timeout_per_stage=300
)

result = workflow.execute_workflow(context, config)
```

#### Pattern 2: Stage-by-Stage Execution

```python
# Execute stages manually
stage1_result = workflow.execute_stage(1, context)
stage2_result = workflow.execute_stage(2, stage1_result)
stage3_result = workflow.execute_stage(3, stage2_result)
stage4_result = workflow.execute_stage(4, stage3_result)
stage5_result = workflow.execute_stage(5, stage4_result)
```

#### Pattern 3: Error Recovery

```python
# Execute with recovery
result = workflow.execute_workflow_with_recovery(
    context,
    recovery_strategy="checkpoint",
    max_retries=3
)
```

---

## Integration Points

### Dependencies

- Stage 1: LENS Protocol engine
- Stage 2: Repository scanner
- Stage 3: Knowledge repositories
- Stage 4: Approval gate validators
- Stage 5: Execution orchestrators

### Data Flow Between Stages

```
Stage1Output → Stage2 → Stage2Output → Stage3 → ... → ExecutionResult
  ↓                       ↓
Context                  Context
  ↓                       ↓
Enhanced with:          Enhanced with:
- Parsed intent        - Code analysis
- Keywords             - Dependencies
- Domain               - Affected files
```

---

## Performance Characteristics

| Component | Typical Duration |
|-----------|------------------|
| Stage 1 (Comprehension) | 100-150ms |
| Stage 2 (Scan) | 400-600ms |
| Stage 3 (Knowledge) | 150-250ms |
| Stage 4 (Approval) | 200-400ms |
| Stage 5 (Execution) | 1-10s |
| Aggregation | 50-100ms |
| **Total** | **2-12 seconds** |

---

## Testing

### Test Coverage

- **Stage execution:** 95% coverage
- **Context propagation:** 98% coverage
- **Error handling:** 92% coverage
- **Result aggregation:** 96% coverage
- **E2E workflows:** 88% coverage

---

## Best Practices

### DO ✅

- Execute all 5 stages for comprehensive analysis
- Maintain context across stage boundaries
- Handle errors gracefully at each stage
- Use stage-specific timeouts
- Log stage transitions
- Validate inter-stage data
- Monitor stage performance

### DON'T ❌

- Skip stages without good reason
- Lose context between stages
- Ignore stage errors
- Mix stage output formats
- Assume linear execution
- Neglect stage monitoring
- Over-optimize individual stages

---

## Example Workflows

### Workflow 1: Complete Fix Workflow

```python
context = WorkflowExecutionContext(
    operation="fix_race_condition",
    description="Fix race condition in Master Orchestrator",
    keywords=["fix", "race", "synchronization"],
    domain="core"
)

result = workflow.execute_workflow(context)
# All 5 stages executed
# Complete analysis and approval before execution
```

### Workflow 2: Quick Implementation

```python
# Skip approval gates for urgent implementation
config = WorkflowConfiguration(enable_stage_4=False)
result = workflow.execute_workflow(context, config)
# Stages 1-3, 5 executed
# Approval gates skipped for speed
```

---

## Related Documentation

- 📖 [Master Orchestrator](01-master-orchestrator.md)
- 📖 [Intent Router](02-intent-router.md)
- 📖 [Refactoring Orchestrator](04-refactoring-orchestrator.md)

---

## Copyright & License

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

CORTEX Framework - Workflow Orchestrator Module
Status: Production Ready | Version: 1.0.0

---

**Last Updated:** 2026-01-22 | **Author:** CORTEX Documentation Generator
