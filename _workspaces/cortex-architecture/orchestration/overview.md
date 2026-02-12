# CORTEX Orchestration Overview

**Total Orchestrators:** 60 | **Updated:** 2026-02-11  
**Architecture:** Git-Backed Registry | **Wiring:** YAML-driven dynamic loading

---

## Orchestrator Architecture

CORTEX employs a **neural orchestrator network** where 60 specialized orchestrators work together like regions of a brain, each contributing unique cognitive capabilities.

### Three-Tier Orchestrator Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 MasterOrchestrator                         │
│                 (Executive Decision Center)                      │
│  • Coordinates all orchestrators                                │
│  • Delegates to IntentRouter                                    │
│  • Manages lifecycle & dependencies                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
┌──────────────────┐ ┌──────────────┐ ┌────────────────────┐
│  🧠 Core (11)  │ │ 🎨 Domain (8)│ │ 🔧 Support (41)│
│  Fundamental     │ │  Business    │ │  Infrastructure    │
│  Processing      │ │  Logic       │ │  Utilities         │
└──────────────────┘ └──────────────┘ └────────────────────┘
```

### Orchestrator Categories

| Category | Count | Responsibility |
|----------|-------|----------------|
| **Core** | 11 | Essential processing: routing, TDD, LENS, enforcement |
| **Domain** | 8 | Business capabilities: refactoring, planning, documentation |
| **Support** | 41 | Infrastructure: debugging, dashboards, knowledge, testing |

---

## Core Orchestrators (11)

The cognitive foundation of CORTEX:

### InteractionOrchestrator

**Module:** `cortex.orchestrators.core.interaction_orchestrator`  
**Class:** `InteractionOrchestrator`  
**Status:** active  
**MCP Tools:** 1 exposed

**Exposed Tools:**
- `cortex_interactive_mode`

---

### ArchitectureGuard

**Module:** `cortex.orchestrators.core.architecture_guard`  
**Class:** `ArchitectureGuard`  
**Status:** active  
**MCP Tools:** 1 exposed

**Exposed Tools:**
- `cortex_validate_architecture`

---

### IntentRouter

**Module:** `cortex.orchestrators.core.intent_router`  
**Class:** `IntentRouter`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### ComplexityClassifier

**Module:** `cortex.orchestrators.core.complexity_classifier`  
**Class:** `ComplexityClassifier`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### LENSSynthesis

**Module:** `cortex.orchestrators.core.lens_synthesis`  
**Class:** `LENSSynthesis`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### EnforcementOrchestrator

**Module:** `cortex.orchestrators.core.enforcement_orchestrator`  
**Class:** `EnforcementOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### TDDOrchestrator

**Module:** `cortex.orchestrators.core.tdd_orchestrator`  
**Class:** `TDDOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### IncrementalTaskDecomposer

**Module:** `cortex.orchestrators.planning.incremental_task_decomposer`  
**Class:** `IncrementalTaskDecomposer`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### WorkflowOrchestrator

**Module:** `cortex.orchestrators.core.workflow_orchestrator`  
**Class:** `WorkflowOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### MasterOrchestrator

**Module:** `cortex.orchestrators.core.master_orchestrator`  
**Class:** `MasterOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### ReviewOrchestrator

**Module:** `cortex.orchestrators.core.review_orchestrator`  
**Class:** `ReviewOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---


## Domain Orchestrators (8)

Business logic and workflow specialists:

### CodeLevelPlanner

**Module:** `cortex.orchestrators.domain.code_level_planner`  
**Class:** `CodeLevelPlanner`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### CoherenceValidator

**Module:** `cortex.orchestrators.domain.coherence_validator`  
**Class:** `CoherenceValidator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### RefactoringOrchestrator

**Module:** `cortex.orchestrators.domain.enhanced_refactoring_orchestrator`  
**Class:** `EnhancedRefactoringOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### PlanningOrchestrator

**Module:** `cortex.orchestrators.domain.enhanced_planning_orchestrator`  
**Class:** `EnhancedPlanningOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### DocumentationOrchestrator

**Module:** `cortex.orchestrators.domain.enhanced_documentation_orchestrator`  
**Class:** `EnhancedDocumentationOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### PhaseExecutor

**Module:** `cortex.orchestrators.domain.phase_executor`  
**Class:** `PhaseExecutor`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### AutonomousExecutionEngine

**Module:** `cortex.orchestrators.domain.autonomous_execution_engine`  
**Class:** `AutonomousExecutionEngine`  
**Status:** active  
**MCP Tools:** 0 exposed


---

### ConversationOrchestrator

**Module:** `cortex.orchestrators.conversation_orchestrator`  
**Class:** `ConversationOrchestrator`  
**Status:** active  
**MCP Tools:** 0 exposed


---


## Support Orchestrators (41)

Infrastructure and utility functions:

**Note:** Support orchestrators provide essential infrastructure but are too numerous to list individually. Key categories include:

- **Debugging & Analysis** (10+ orchestrators)
- **Dashboard Generation** (5+ orchestrators)
- **Knowledge Management** (8+ orchestrators)
- **Testing & Validation** (12+ orchestrators)
- **System Utilities** (6+ orchestrators)

For complete details, see [support-orchestrators.md](./support-orchestrators.md).

---

## Orchestrator Request Flow

### Typical Request Lifecycle

```
1. User Request
   ↓
2. MCP Gateway (cortex_process_request)
   ↓
3. MasterOrchestrator
   • Validates environment
   • Checks dependencies
   ↓
4. IntentRouter
   • Classifies: IMPLEMENT | FIX | REFACTOR | ANALYZE | etc.
   • Routes to appropriate orchestrator
   ↓
5. Specialist Orchestrator
   • TDDOrchestrator (IMPLEMENT/FIX)
   • RefactoringOrchestrator (REFACTOR)
   • LENSSynthesis (ANALYZE)
   ↓
6. Cross-Cutting Concerns
   • EnforcementOrchestrator (governance)
   • HolisticValidationOrchestrator (Phase 48 gate)
   • ContextCrystallizationLayer (Phase 49 context)
   ↓
7. Response Generation
   ↓
8. MCP Response (back to AI assistant)
```

### Example: IMPLEMENT Flow

```python
# User: "Implement user authentication"

# Step 1: MCP Entry
cortex_process_request(
    request="Implement user authentication",
    enable_challenge=True
)

# Step 2: MasterOrchestrator delegates to IntentRouter
intent = IntentRouter.classify(request)
# Result: IntentType.IMPLEMENT

# Step 3: Route to TDDOrchestrator
orchestrator = registry.get('TDDOrchestrator')

# Step 4: TDD Orchestrator loads dependencies
orchestrator.load([
    'HolisticValidationOrchestrator',  # Phase 48: Pre-flight
    'ContextCrystallizationLayer',     # Phase 49: Context warming
    'LENSSynthesis',                   # Code intelligence
    'EnforcementOrchestrator'          # Governance
])

# Step 5: Challenge Gate (Phase 48)
challenges = orchestrator.generate_challenges(request)
# Returns 3 alternative approaches

# Step 6: User selects approach → "proceed"

# Step 7: TDD Cycle
orchestrator.execute_tdd_cycle(
    phase='RED',    # Write failing tests
    phase='GREEN',  # Implement minimal code
    phase='REFACTOR' # Apply best practices
)

# Step 8: Governance Validation
EnforcementOrchestrator.validate([
    'CORE-008',  # Tests before code
    'CORE-011',  # Type hints
    'CORE-012',  # Docstrings
])

# Step 9: Audit Trail
# AC_START → AC_COMPLETE markers added

# Result: ✅ Implementation complete with governance compliance
```

---

## Orchestrator Wiring

### Git-Backed Registry

CORTEX uses a **YAML-driven dynamic orchestrator registry** stored in `cortex-registry/_cortex-master/`:

```yaml
# cortex/wiring/specifications/wiring.yaml
orchestrators:
  core:
    - name: MasterOrchestrator
      module: cortex.orchestrators.core.master_orchestrator
      class: MasterOrchestrator
      mcp_tools:
        - cortex_process_request
        - cortex_execute_autonomous
      
  domain:
    - name: TDDOrchestrator
      module: cortex.orchestrators.tdd.tdd_orchestrator
      class: TDDOrchestrator
      mcp_tools:
        - cortex_implement_tdd
        - cortex_run_tests
```

### Dynamic Loading

Orchestrators are loaded **on-demand** using lazy initialization:

```python
from cortex.wiring import GitBackedRegistry

# Initialize registry
registry = GitBackedRegistry()
registry.load()

# Get orchestrator (lazy-loaded)
tdd_orch = registry.get('TDDOrchestrator')

# First access triggers instantiation
tdd_orch.execute_tdd_cycle(...)
```

---

## Key Design Patterns

### 1. Strategy Pattern
Different orchestrators for different intents (IMPLEMENT vs ANALYZE vs REFACTOR)

### 2. Chain of Responsibility
MasterOrchestrator → IntentRouter → Specialist → Cross-Cutting

### 3. Lazy Loading
Orchestrators instantiated only when needed (memory efficient)

### 4. Dependency Injection
Orchestrators declare dependencies in YAML, injected at runtime

### 5. Event-Driven
Orchestrators communicate via events (not direct calls)

---

## Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| **Orchestrator Load Time** | <100ms | ~80ms (cold start) |
| **Routing Decision** | <50ms | ~35ms |
| **TDD Cycle (small)** | <5s | ~3.2s |
| **Holistic Validation** | <200ms | ~150ms |
| **Memory per Orchestrator** | <10MB | ~7MB average |

---

**Last Updated:** 2026-02-11 06:36:38  
**Source:** wiring.yaml + GitBackedRegistry introspection  
**Orchestrators Active:** 60 / 60
