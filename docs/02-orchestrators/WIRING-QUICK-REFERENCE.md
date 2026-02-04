# CORTEX Orchestrator Wiring Quick Reference
**Purpose:** Template for wiring new orchestrators into `wiring.yaml`  
**Audience:** Developers adding new orchestrators  
**Reference:** Phase 1-8 wiring patterns  

---

## Quick Checklist Before Wiring

- [ ] Orchestrator class implemented (`cortex/orchestrators/...`)
- [ ] Tests created and passing (`tests/unit/orchestrators/...`)
- [ ] MCP adapter created (if needed for API exposure)
- [ ] Health check method implemented
- [ ] Capabilities list documented
- [ ] Dependencies identified and exist in wiring.yaml
- [ ] Priority slot identified (doesn't conflict with others)

---

## Wiring Template

```yaml
# Copy this template and fill in the [BRACKETS]

orchestrators:
  [TIER]:  # core, domain, or support
    - name: "[OrchestratorName]"
      module: "cortex.orchestrators.[category].[module_name]"
      class: "[ClassName]"
      tier: [TIER_NUM]  # 1=core, 2=domain, 3=support
      priority: [NUM]  # See priority allocation below
      dependencies:
        - "[DependentOrchestrator1]"
        - "[DependentOrchestrator2]"
      capabilities:
        - "[capability1]"
        - "[capability2]"
      health_check: "[method_name]"
      mcp_adapter: "cortex.mcp.adapters.[adapter_name]"  # Optional
      metadata:
        icon: "[EMOJI]"
        stages: [NUM]
        intelligence: ["lens", "knowledge"]  # Optional
      description: "[Brief description of purpose]"
      requires_params:  # Optional, for complex initialization
        [param_name]:
          type: "[ParamType]"
          source: "[module.path.ClassName]"
          lazy_create: true
          init_params:
            [key]: value
```

---

## Priority Allocation Strategy

### Core Tier (tier=1)
- **Priority 10-19:** Input/comprehension orchestrators (InteractionOrchestrator)
- **Priority 20-29:** Intent routing/classification (IntentRouter, ComplexityClassifier)
- **Priority 30-40:** Execution orchestrators (TDDOrchestrator, IncrementalTaskDecomposer)
- **Priority 41-50:** Workflow orchestrators (WorkflowOrchestrator)
- **Priority 80-100:** Meta orchestrators (MasterOrchestrator, ReviewOrchestrator)

**Pattern:** First client → middlemen → final coordination

### Domain Tier (tier=2)
- **Priority 49-59:** Planning/refactoring orchestrators
- **Priority 60-79:** Specialized processors

### Support Tier (tier=3)
- **Priority 1-5:** Infrastructure (event bus, registry)
- **Priority 60+:** Tools and utilities

---

## Real Examples from Phase 1-8

### Example 1: ComplexityClassifier (Phase 2)

**Why this structure:**
- Depends on IntentRouter (output classification needed)
- Priority 23 (after intent routing, before planning)
- Core tier (critical path)
- Health check: `classify_complexity` (validates it can classify)

```yaml
- name: "ComplexityClassifier"
  module: "cortex.orchestrators.core.complexity_classifier"
  class: "ComplexityClassifier"
  tier: 1
  priority: 23
  dependencies:
    - "IntentRouter"
  capabilities:
    - complexity_classification
    - orchestrator_routing
    - complexity_analysis
  health_check: "classify_complexity"
  mcp_adapter: "cortex.mcp.adapters.complexity_adapter"
  metadata:
    icon: "📊"
    stages: 3
    intelligence: ["lens"]
  phase: "2"
```

**Implementation checklist for adding this:**
1. ✅ Class in `cortex/orchestrators/core/complexity_classifier.py`
2. ✅ `classify_complexity(request)` method returns (complexity_level, confidence)
3. ✅ Tests verify all 5 levels (TRIVIAL, SIMPLE, MODERATE, COMPLEX, CRITICAL)
4. ✅ MCP adapter in `cortex/mcp/adapters/complexity_adapter.py`
5. ✅ Added to wiring AFTER IntentRouter
6. ✅ Updated LENSSynthesis to depend on it

---

### Example 2: CodeLevelPlanner (Phase 3)

**Why this structure:**
- Depends on ComplexityClassifier (only runs for COMPLEX/CRITICAL)
- Priority 49 (domain tier, mid-range)
- Domain tier (specialized processor)
- No MCP adapter (internal tool, not exposed)

```yaml
- name: "CodeLevelPlanner"
  module: "cortex.orchestrators.domain.code_level_planner"
  class: "CodeLevelPlanner"
  tier: 2
  priority: 49
  dependencies:
    - "ComplexityClassifier"
  capabilities:
    - code_planning
    - file_specification
    - function_specification
    - interface_contracts
  health_check: "analyze_task_scope"
  description: "Generates detailed implementation plans without code generation (Phase 3)"
  mcp_adapter: "cortex.mcp.adapters.planning_adapter"
  metadata:
    icon: "📐"
    stages: 3
    intelligence: ["lens", "knowledge"]
  phase: "3"
```

**Key difference from ComplexityClassifier:**
- Domain tier (2) vs Core tier (1)
- Plan generation capability (vs classification)
- Multiple stages (3 phases of planning)

---

### Example 3: OrchestratorEventBus (Phase 1)

**Why this structure:**
- NO dependencies (infrastructure foundation)
- Priority 1 (runs FIRST, singleton)
- Support tier (infrastructure)
- Special `singleton: true` flag

```yaml
- name: "OrchestratorEventBus"
  module: "cortex.infrastructure.orchestrator_event_bus"
  class: "OrchestratorEventBus"
  tier: 3
  priority: 1
  dependencies: []
  capabilities:
    - event_publishing
    - event_subscription
    - event_history
    - event_replay
    - dead_letter_management
  health_check: "health_check"
  description: "Event-driven communication backbone (Phase 1)"
  mcp_tools: []
  metadata:
    icon: "📡"
    stages: 1
    intelligence: []
  phase: "1"
  singleton: true
```

**Key pattern:**
- ALWAYS define `singleton: true` for infrastructure
- NO intelligence (pure mechanics)
- NO MCP adapter (internal infrastructure)
- Health check just validates existence

---

## Dependency Validation Rules

### ✅ VALID Patterns

```yaml
# A depends on B (B runs first)
- name: A
  dependencies:
    - B

# Multiple dependencies (all run before A)
- name: A
  dependencies:
    - B
    - C
    - D

# No dependencies (foundation layer)
- name: EventBus
  dependencies: []
```

### ❌ INVALID Patterns

```yaml
# Circular dependency (FORBIDDEN)
- name: A
  dependencies:
    - B
- name: B
  dependencies:
    - A

# Forward reference (depends on orchestrator defined later - OK in file but confusing)
- name: A
  dependencies:
    - B  # B defined 50 lines below
```

---

## Testing Wiring Changes

After modifying `wiring.yaml`:

```bash
# 1. Validate syntax
python -c "import yaml; yaml.safe_load(open('cortex/wiring/specifications/wiring.yaml'))"

# 2. Check for circular dependencies
cortex-cli validate-wiring cortex/wiring/specifications/wiring.yaml

# 3. Verify each orchestrator can be instantiated
cortex-cli orchestrator-health --all

# 4. Run E2E tests
pytest tests/e2e/test_cortex_sdlc_e2e.py -k [ORCHESTRATOR_NAME]
```

---

## Common Issues & Solutions

### Issue 1: Priority Conflicts

**Problem:** Two orchestrators same priority
```yaml
- name: A
  priority: 49
- name: B
  priority: 49  # ❌ Conflicts!
```

**Solution:** Use unique priorities within tier
```yaml
- name: A
  priority: 49
- name: B
  priority: 50  # ✅ Unique
```

### Issue 2: Circular Dependencies

**Problem:** A→B→C→A
```yaml
- name: A
  dependencies: [B]
- name: B
  dependencies: [C]
- name: C
  dependencies: [A]  # ❌ Circular!
```

**Solution:** Break cycle with event-driven communication
```yaml
- name: A
  dependencies: []
  capabilities: [publish_to_event_bus]
- name: B
  dependencies: []
  capabilities: [subscribe_to_event_bus]
- name: C
  dependencies: []
  capabilities: [subscribe_to_event_bus]
```

### Issue 3: Missing MCP Adapter

**Problem:** Tool exposed but no adapter
```yaml
- name: MyOrchestrator
  mcp_adapter: "cortex.mcp.adapters.missing_adapter"  # ❌ File doesn't exist!
```

**Solution:** Create adapter or remove if not needed
```yaml
- name: MyOrchestrator
  # No mcp_adapter (internal use only)
  # OR create: cortex/mcp/adapters/my_adapter.py
```

---

## Best Practices

### 1. **Tier Placement**
- **Core (1):** User-facing, request handling, critical path
- **Domain (2):** Specialized processing, business logic
- **Support (3):** Infrastructure, utilities, helpers

### 2. **Priority Numbering**
- Use 10-unit gaps: 10, 20, 30 (leaves room for future orchestrators)
- GroupType together: 20-29 for classification, 30-39 for execution
- Meta orchestrators always highest: 90-100

### 3. **Dependencies**
- Keep flat when possible (reduces startup time)
- Use event bus for decoupling instead of direct dependencies
- Validate no cycles: DAG only!

### 4. **Capabilities**
- Be specific: `complexity_classification` not `analyze`
- Keep list short: 2-5 capabilities per orchestrator
- Match health check method name

### 5. **Health Checks**
- Test core functionality: `classify_complexity`, `generate_tests`, etc.
- Must not access external services (tests won't work in CI)
- Should return boolean: True (healthy) or raise exception

### 6. **MCP Adapters**
- Only add if exposing to external users
- Follow naming: `[orchestrator_name]_adapter.py`
- Document parameters and response format

### 7. **Documentation**
- Add `phase: "X"` tag for new phase orchestrators
- Add `description` for non-obvious orchestrators
- Use icons consistently (see examples)

---

## Phase-Specific Patterns

### Phase 1: Infrastructure
```yaml
# Singleton, no dependencies, high tier priority (1-5)
- name: "EventBus"
  tier: 3
  priority: 1
  singleton: true
  capabilities: [event_publishing, event_subscription]
```

### Phase 2-4: Planning/Validation
```yaml
# Sequential dependencies, domain tier, mid priorities (40-59)
- name: "Planner"
  tier: 2
  priority: 49
  dependencies: [PreviousPhase]
```

### Phase 5+: Review/Meta
```yaml
# Late in pipeline, core tier, high priorities (80-100)
- name: "Reviewer"
  tier: 1
  priority: 99
  dependencies: [MasterOrchestrator]
```

---

## Adding to E2E Tests

After wiring a new orchestrator, add tests:

```python
# tests/e2e/test_cortex_sdlc_e2e.py

def test_e2e_new_orchestrator_integration():
    """Test new orchestrator in pipeline"""
    # 1. Create mock request
    request = {"type": "IMPLEMENT", "complexity": "COMPLEX"}
    
    # 2. Create orchestrator
    orchestrator = NewOrchestrator()
    
    # 3. Execute
    result = orchestrator.process(request)
    
    # 4. Verify
    assert result["status"] == "SUCCESS"
    assert "data" in result
```

---

## Checklist for Adding New Orchestrator

- [ ] **Code**
  - [ ] Class implemented
  - [ ] Methods documented
  - [ ] Type hints added
  - [ ] Tests passing (10+ tests)
  - [ ] Health check method exists

- [ ] **Wiring**
  - [ ] Added to correct tier (core/domain/support)
  - [ ] Priority assigned (unique, no gaps)
  - [ ] Dependencies listed (valid, no cycles)
  - [ ] Capabilities documented (2-5 items)
  - [ ] Health check method named
  - [ ] Phase tag added (if new phase)

- [ ] **Integration**
  - [ ] MCP adapter created (if exposing to users)
  - [ ] E2E test added
  - [ ] Committed to git
  - [ ] Wiring validates: no errors

- [ ] **Documentation**
  - [ ] Purpose documented in description
  - [ ] Dependencies explained
  - [ ] Capabilities listed
  - [ ] Usage example in docs/

---

## Files to Update

When adding a new orchestrator:

1. **Create Orchestrator Code**
   - `cortex/orchestrators/[tier]/[name].py`

2. **Create Tests**
   - `tests/unit/orchestrators/[tier]/test_[name].py`

3. **Update Wiring**
   - `cortex/wiring/specifications/wiring.yaml`

4. **Create MCP Adapter (optional)**
   - `cortex/mcp/adapters/[name]_adapter.py`

5. **Update E2E Tests**
   - `tests/e2e/test_cortex_sdlc_e2e.py`

6. **Update Docs**
   - `docs/02-orchestrators/[name].md`
   - `docs/04-architecture/orchestrator-graph.md`

---

## References

- **Master Wiring:** `cortex/wiring/specifications/wiring.yaml`
- **Phase 1-8 Examples:** Phases 1-8 orchestrator implementations
- **E2E Tests:** `tests/e2e/test_cortex_sdlc_e2e.py`
- **CORTEX SDLC Plan:** `_workspaces/cortex-plan/CORTEX-SELF-IMPROVEMENT-SDLC.yaml`

---

*Last Updated: 2026-02-04 | Based on Phase 1-8 Wiring Integration*
