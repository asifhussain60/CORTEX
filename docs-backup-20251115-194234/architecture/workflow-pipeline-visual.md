# Workflow Pipeline System - Visual Architecture

**Last Updated:** 2025-11-10

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                                   │
│  "Add authentication with threat modeling, DoD validation, and docs"    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   CORTEX Entry Point     │
                    │   (cortex_entry.py)      │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   Intent Router          │
                    │   Detects: PLAN intent   │
                    │   Risk: HIGH (auth)      │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │  Workflow Selector        │
                    │  Selects: secure_feature_ │
                    │          creation.yaml    │
                    └────────────┬──────────────┘
                                 │
                ┌────────────────▼──────────────────────┐
                │   Workflow Orchestrator               │
                │                                       │
                │  1. Load YAML definition              │
                │  2. Validate DAG (no cycles)          │
                │  3. Inject context ONCE (Tier 1-3)    │
                │  4. Execute stages in order           │
                │  5. Manage state between stages       │
                │  6. Log to Tier 1                     │
                └────────────────┬──────────────────────┘
                                 │
         ┌───────────────────────┴─────────────────────────────┐
         │                 Stage Execution (in order)          │
         │                                                      │
┌────────▼─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ 1. Threat Model  │──▶│ 2. DoD/  │──▶│ 3. Plan  │──▶│ 4. TDD   │
│                  │  │    DoR   │  │          │  │  Cycle   │
│ Outputs:         │  │          │  │          │  │          │
│ - threats: [...]│  │ Outputs: │  │ Outputs: │  │ Outputs: │
│ - risk: HIGH    │  │ - dor OK │  │ - phases │  │ - files  │
│                  │  │ - dod OK │  │ - tasks  │  │ - tests  │
└──────────────────┘  └──────────┘  └──────────┘  └──────────┘
                                                        │
         ┌──────────────────────────────────────────────┘
         │
┌────────▼─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ 5. Run Tests     │──▶│ 6. DoD   │──▶│ 7. Code  │──▶│ 8. Doc   │
│                  │  │  Validate│  │  Cleanup │  │  Generate│
│ Outputs:         │  │          │  │          │  │          │
│ - passing: TRUE │  │ Outputs: │  │ Outputs: │  │ Outputs: │
│ - coverage: 95% │  │ - passed │  │ - cleaned│  │ - docs   │
│                  │  │          │  │          │  │          │
└──────────────────┘  └──────────┘  └──────────┘  └──────────┘
         │                                              │
         └──────────────────┬───────────────────────────┘
                            │
                   ┌────────▼─────────┐
                   │  Workflow State  │
                   │                  │
                   │ ✅ All stages OK │
                   │ ⏱️  Duration: 45s │
                   │ 📁 Files: 8      │
                   │ ✓ Tests: 23      │
                   └────────┬─────────┘
                            │
                   ┌────────▼─────────┐
                   │ Response to User │
                   │                  │
                   │ "✅ Feature      │
                   │  complete with   │
                   │  security checks"│
                   └──────────────────┘
```

---

## 🔄 State Flow Diagram

```
WorkflowState (Shared Between All Stages)
═══════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────┐
│ workflow_id: "wf-abc123"                                 │
│ conversation_id: "conv-456"                              │
│ user_request: "Add authentication..."                    │
├──────────────────────────────────────────────────────────┤
│ context: {                                               │
│   tier1: {conversations: [...], recent: [...]}          │
│   tier2: {patterns: [...], similar: [...]}              │
│   tier3: {hotspots: [...], velocity: {...}}             │
│ }  ← INJECTED ONCE AT START (not per-stage)             │
├──────────────────────────────────────────────────────────┤
│ stage_outputs: {                                         │
│   "threat_model": {                                      │
│     threats: [                                           │
│       {category: "Spoofing", risk: 6, ...},             │
│       {category: "Tampering", risk: 4, ...}             │
│     ],                                                   │
│     risk_level: "high"                                   │
│   },                                                     │
│   "clarify_dod_dor": {                                   │
│     dor: {ready: true, ...},                            │
│     dod: {build_clean: true, ...},                      │
│     questions: []                                        │
│   },                                                     │
│   "plan": {                                              │
│     phases: [{phase: 1, tasks: [...]}, ...],           │
│     estimated_hours: 8                                   │
│   },                                                     │
│   "tdd_cycle": {                                         │
│     files_modified: ["auth.py", "test_auth.py"],       │
│     tests_passing: true                                  │
│   },                                                     │
│   ...                                                    │
│ }                                                        │
├──────────────────────────────────────────────────────────┤
│ stage_statuses: {                                        │
│   "threat_model": SUCCESS,                               │
│   "clarify_dod_dor": SUCCESS,                           │
│   "plan": SUCCESS,                                       │
│   "tdd_cycle": SUCCESS,                                  │
│   "run_tests": SUCCESS,                                  │
│   "validate_dod": SUCCESS,                               │
│   "cleanup": SUCCESS,                                    │
│   "document": SUCCESS                                    │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Dependency Graph Example

```
Workflow: secure_feature_creation
══════════════════════════════════════════════════════════

    START
      │
      ▼
┌───────────────┐
│ threat_model  │  (no dependencies)
└───────┬───────┘
        │
        ▼
┌────────────────┐
│ clarify_dod_dor│  depends_on: ["threat_model"]
└───────┬────────┘
        │
        ▼
┌───────────┐
│   plan    │  depends_on: ["clarify_dod_dor"]
└─────┬─────┘
      │
      ▼
┌───────────┐
│ tdd_cycle │  depends_on: ["plan"]
└─────┬─────┘
      │
      ▼
┌────────────┐
│ run_tests  │  depends_on: ["tdd_cycle"]
└─────┬──────┘
      │
      ▼
┌──────────────┐
│ validate_dod │  depends_on: ["run_tests"]
└──────┬───────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────┐    ┌──────────┐
│ cleanup  │    │ document │
└────┬─────┘    └─────┬────┘
     │ (optional)     │
     │                │
     └────────┬───────┘
              │
              ▼
            END

Execution Order (Topological Sort):
1. threat_model
2. clarify_dod_dor
3. plan
4. tdd_cycle
5. run_tests
6. validate_dod
7. cleanup
8. document

Validation: ✅ No cycles, all dependencies satisfied
```

---

## ⚡ Performance Comparison

```
❌ Without Orchestrator (Old Approach)
═══════════════════════════════════════════════════════════

Stage 1: Query Tier 1-3 (200ms) + Execute (50ms) = 250ms
Stage 2: Query Tier 1-3 (200ms) + Execute (30ms) = 230ms
Stage 3: Query Tier 1-3 (200ms) + Execute (100ms) = 300ms
Stage 4: Query Tier 1-3 (200ms) + Execute (5000ms) = 5200ms
Stage 5: Query Tier 1-3 (200ms) + Execute (200ms) = 400ms
Stage 6: Query Tier 1-3 (200ms) + Execute (50ms) = 250ms
Stage 7: Query Tier 1-3 (200ms) + Execute (80ms) = 280ms
Stage 8: Query Tier 1-3 (200ms) + Execute (120ms) = 320ms
──────────────────────────────────────────────────────────
TOTAL: 7,230ms (7.2 seconds)
Context overhead: 1,600ms (8 × 200ms)


✅ With Orchestrator (New Approach)
═══════════════════════════════════════════════════════════

Initial: Inject context (200ms) - ONCE
Stage 1: Execute (50ms)
Stage 2: Execute (30ms)
Stage 3: Execute (100ms)
Stage 4: Execute (5000ms)
Stage 5: Execute (200ms)
Stage 6: Execute (50ms)
Stage 7: Execute (80ms)
Stage 8: Execute (120ms)
──────────────────────────────────────────────────────────
TOTAL: 5,830ms (5.8 seconds)
Context overhead: 200ms (1 × 200ms)

SAVINGS: 1,400ms (19% faster) ⚡
```

---

## 🧩 Stage Interface Contract

```python
class WorkflowStage(Protocol):
    """Every stage must implement this interface"""
    
    def execute(self, state: WorkflowState) -> StageResult:
        """
        Main execution logic
        
        Receives:
        - state.user_request (original request)
        - state.context (Tier 1-3 data)
        - state.stage_outputs (outputs from previous stages)
        
        Returns:
        - StageResult with status, outputs, errors
        """
        pass
    
    def validate_input(self, state: WorkflowState) -> bool:
        """
        Pre-execution validation
        
        Returns:
        - True if inputs are valid
        - False if missing required data
        """
        pass
    
    def on_failure(self, state: WorkflowState, error: Exception):
        """
        Failure handler
        
        Called when:
        - Exception raised during execute()
        - Validation fails
        - Timeout exceeded
        
        Use for:
        - Cleanup
        - Logging
        - Rollback
        """
        pass
```

---

## 📋 YAML Workflow Definition Schema

```yaml
# Workflow definition schema

workflow_id: string (required)
  # Unique identifier for this workflow
  # Example: "secure_feature_creation"

name: string (required)
  # Human-readable workflow name
  # Example: "Secure Feature Creation"

description: string (optional)
  # Multi-line description of workflow purpose

stages: array (required)
  # List of stages in workflow
  
  - id: string (required)
      # Unique stage identifier
      # Example: "threat_model"
    
    script: string (required)
      # Python module name (without .py)
      # Example: "threat_modeler"
      # Loads from: src/workflows/stages/threat_modeler.py
    
    required: boolean (default: true)
      # If true, stage failure aborts workflow
      # If false, stage failure logged but workflow continues
    
    depends_on: array (default: [])
      # List of stage IDs this stage depends on
      # Must complete successfully before this stage runs
      # Example: ["threat_model", "clarify_dod_dor"]
    
    retryable: boolean (default: false)
      # If true, stage will retry on failure
    
    max_retries: integer (default: 3)
      # Maximum retry attempts (if retryable: true)
    
    timeout_seconds: integer (default: 300)
      # Stage execution timeout in seconds
```

---

## 🔒 Security Integration

```
Workflow Pipeline + Security Model
═══════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────┐
│               Workflow Orchestrator                      │
│                                                          │
│  For each stage:                                        │
│    1. Validate stage script (whitelist check)           │
│    2. Load stage module in sandboxed environment        │
│    3. Check stage permissions (capabilities)            │
│    4. Enforce resource limits (timeout, memory)         │
│    5. Execute stage with monitoring                     │
│    6. Log security events to audit trail               │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│ Input        │ │ Sandbox     │ │ Audit        │
│ Validation   │ │ Enforcement │ │ Logging      │
│              │ │             │ │              │
│ • Schema OK? │ │ • Timeout   │ │ • Stage exec │
│ • Safe paths?│ │ • Memory    │ │ • Failures   │
│ • No SQL inj?│ │ • Queries   │ │ • Anomalies  │
└──────────────┘ └─────────────┘ └──────────────┘

Integration Points:
- threat_modeler.py uses security threat model (STRIDE)
- dod_validator.py checks security DoD (if high-risk)
- All stages run with resource monitoring
- Audit log tracks all stage executions
```

---

## 🚀 Quick Reference

### Create New Stage

```python
# src/workflows/stages/my_new_stage.py

from src.workflows.workflow_pipeline import (
    WorkflowStage, WorkflowState, StageResult, StageStatus
)

class MyNewStage:
    def execute(self, state: WorkflowState) -> StageResult:
        # Your logic here
        return StageResult(
            stage_id="my_stage",
            status=StageStatus.SUCCESS,
            duration_ms=0,
            output={"key": "value"}
        )
    
    def validate_input(self, state: WorkflowState) -> bool:
        return bool(state.user_request)
    
    def on_failure(self, state: WorkflowState, error: Exception):
        print(f"Failed: {error}")

def create_stage() -> WorkflowStage:
    return MyNewStage()
```

### Add Stage to Workflow

```yaml
# src/workflows/definitions/my_workflow.yaml

stages:
  - id: "my_stage"
    script: "my_new_stage"
    required: true
    depends_on: ["previous_stage"]
```

### Execute Workflow

```python
from src.workflows.workflow_pipeline import (
    WorkflowDefinition, WorkflowOrchestrator
)

workflow_def = WorkflowDefinition.from_yaml("my_workflow.yaml")
orchestrator = WorkflowOrchestrator(workflow_def, context_injector, tier1)

state = orchestrator.execute(
    user_request="Do something",
    conversation_id="conv-123"
)
```

---

**Status:** ✅ Architecture Designed and Documented  
**Next Steps:** Implement remaining stages (cleanup, document, etc.)  
**Reference:** `docs/guides/workflow-pipeline-guide.md`
