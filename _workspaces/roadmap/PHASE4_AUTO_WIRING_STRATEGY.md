# Phase 4: Auto-Wiring Infrastructure - Implementation

## Overview
Replace manual WIRE-001/002/003 module calls with YAML-based declarative discovery per CORE-031.

## Implementation Strategy

### Current State (Manual)
```python
# In MasterOrchestrator.initialize():
wire_001_result = execute_wire_001()  # Explicit call
wire_002_result = execute_wire_002()  # Explicit call
wire_003_result = execute_wire_003()  # Explicit call
```

### Target State (Declarative)
```python
# In MasterOrchestrator.initialize():
autowiring = AutowiringOrchestrator()
specs = autowiring.discover_wiring_specs()  # YAML-based discovery
autowiring.apply_wiring_specs(specs)  # Automatic registration
```

## Wiring Specification Format (YAML)

Each orchestrator has a `*_wiring.yaml` spec:

```yaml
# Example: core_wiring.yaml
module_name: core_orchestrators
version: "1.0.0"
description: "Core orchestrators: Interaction, Intent Router, TDD, Workflow"

dependencies:
  - name: governance_registry
    version: ">=1.0.0"
    required: true
  - name: audit_logger
    version: ">=1.0.0"
    required: true

provides:
  - name: InteractionOrchestrator
    category: CORE
    entry_point: "cortex.orchestrators.core.interaction_orchestrator:InteractionOrchestrator"
    
  - name: IntentRouter
    category: CORE
    entry_point: "cortex.orchestrators.core.intent_router:IntentRouter"
    
  - name: TDDOrchestrator
    category: CORE
    entry_point: "cortex.orchestrators.core.tdd_orchestrator:TDDOrchestrator"

initialization_order: 10
```

## Implementation Steps

1. **Create YAML Specs for All Orchestrators** (30 min)
   - Location: `cortex/orchestrators/core/specs/` directory
   - Files: `core_wiring.yaml`, `domain_wiring.yaml`, `support_wiring.yaml`
   - Each lists orchestrators it registers with full metadata

2. **Update AutowiringOrchestrator** (45 min)
   - Enhance `discover_wiring_specs()` to find and parse YAML
   - Add `apply_wiring_specs()` to dynamically import/register
   - Add `validate_dependency_graph()` for circular dependency detection

3. **Update MasterOrchestrator** (45 min)
   - Replace 3 `execute_wire_XXX()` calls with autowiring
   - Call `AutowiringOrchestrator.discover_wiring_specs()`
   - Call `autowiring.apply_wiring_specs()`
   - Maintain same error handling and audit logging

4. **Remove Manual WIRE Modules** (15 min)
   - Comment out or delete `wire_001_core_wiring.py`
   - Comment out or delete `wire_002_domain_wiring.py`
   - Comment out or delete `wire_003_support_wiring.py`
   - Tests remain unchanged (test declarative path instead)

5. **Test & Validation** (30 min)
   - Run existing WIRE tests against new declarative path
   - Add YAML spec validation tests
   - Verify all 23 orchestrators still register correctly

## Benefits

✅ CORE-031 Compliance: Declarative wiring per governance rules
✅ Git-Safe: YAML changes don't require Python code changes
✅ Scalable: Adding new orchestrators requires YAML only
✅ Discoverable: Specs document orchestrator capabilities
✅ Maintainable: Separation of wiring logic and registration

## Timeline
Total: 3 hours
- Discovery: 30 min
- Implementation: 2 hours  
- Testing: 30 min

---
