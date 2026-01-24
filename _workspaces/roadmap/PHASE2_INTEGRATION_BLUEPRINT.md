# Phase 2: Orchestrator Wiring Integration Blueprint

**Status:** READY FOR IMPLEMENTATION  
**Date:** 2026-01-24  
**Effort:** 6-8 hours critical path  
**Blocking:** YES - Phase 1 complete, Phase 2 in progress

---

## Integration Architecture

### Current State
- **WIRE-001:** CoreOrchestratorWiring class, execute_wire_001() function, tests PASSING ✅
- **WIRE-002:** DomainOrchestratorWiring class, execute_wire_002() function, tests PASSING ✅
- **WIRE-003:** SupportOrchestratorWiring class, execute_wire_003() function, tests PASSING ✅
- **MasterOrchestrator.initialize():** Currently calls ensure_bootstrapped() only, doesn't call WIRE modules ❌

### Integration Point
File: `cortex/orchestrators/core/master_orchestrator.py`  
Method: `initialize()` (lines 481-540)

Current flow:
```python
def initialize(self) -> Result[str]:
    # ... validation ...
    bootstrap_result = ensure_bootstrapped()  # ← Only this is called
    # ... return result ...
```

Target flow:
```python
def initialize(self) -> Result[str]:
    # ... validation ...
    bootstrap_result = ensure_bootstrapped()
    
    # WIRE-001: Register core orchestrators
    from cortex.orchestrators.core.wire_001_core_wiring import execute_wire_001
    wire_001_result = execute_wire_001()
    
    # WIRE-002: Register domain orchestrators
    from cortex.orchestrators.core.wire_002_domain_wiring import execute_wire_002
    wire_002_result = execute_wire_002()
    
    # WIRE-003: Register support orchestrators
    from cortex.orchestrators.core.wire_003_support_wiring import execute_wire_003
    wire_003_result = execute_wire_003()
    
    # Validate all 23 orchestrators registered
    registry = get_wiring_registry()
    if registry.get_orchestrator_count() == 23:
        return Ok("All 23 orchestrators wired successfully")
    else:
        return Err(f"Incomplete wiring: {registry.get_orchestrator_count()}/23")
```

---

## Implementation Steps

### Step 1: Add Imports to MasterOrchestrator
Location: Lines 1-60 (import section)

Add:
```python
from cortex.orchestrators.core.wire_001_core_wiring import execute_wire_001
from cortex.orchestrators.core.wire_002_domain_wiring import execute_wire_002
from cortex.orchestrators.core.wire_003_support_wiring import execute_wire_003
from cortex.orchestrators.core.orchestrator_wiring import get_wiring_registry
```

### Step 2: Update initialize() Method
Location: Lines 481-540

Replace the current initialize() implementation with:
- Keep bootstrap_result call (required)
- Add WIRE-001 execution
- Add WIRE-002 execution
- Add WIRE-003 execution
- Add orchestrator count validation
- Add error handling for each WIRE module
- Maintain Result[str] return type
- Maintain audit logging (AC_START/COMPLETE)

### Step 3: Add Helper Method (Optional)
Add validation method to MasterOrchestrator:

```python
def validate_wiring(self) -> Result[Dict[str, int]]:
    """Validate all orchestrators are wired and discoverable"""
    registry = get_wiring_registry()
    orchestrators = registry.get_all_orchestrators()
    stats = {
        "total_wired": len(orchestrators),
        "core_orchestrators": sum(1 for o in orchestrators if o.category == "CORE"),
        "domain_orchestrators": sum(1 for o in orchestrators if o.category == "DOMAIN"),
        "support_orchestrators": sum(1 for o in orchestrators if o.category == "SUPPORT"),
    }
    
    if stats["total_wired"] == 23:
        return Ok(stats)
    else:
        return Err(f"Incomplete wiring: {stats['total_wired']}/23 orchestrators")
```

### Step 4: Update Tests
File: `tests/unit/orchestrators/test_transform_001_wiring.py`

Add integration test:
```python
def test_master_orchestrator_initialization_wires_all_orchestrators():
    """Test that MasterOrchestrator.initialize() wires all 23 orchestrators"""
    master = MasterOrchestrator.instance()
    result = master.initialize()
    
    assert result.is_ok()
    
    registry = get_wiring_registry()
    orchestrators = registry.get_all_orchestrators()
    assert len(orchestrators) == 23
    
    # Verify categories
    core_count = sum(1 for o in orchestrators if o.category == "CORE")
    domain_count = sum(1 for o in orchestrators if o.category == "DOMAIN")
    support_count = sum(1 for o in orchestrators if o.category == "SUPPORT")
    
    assert core_count == 6  # WIRE-001
    assert domain_count >= 5  # WIRE-002
    assert support_count >= 6  # WIRE-003
```

---

## Rollback Plan (CORE-026)

If integration fails:
```bash
git revert 5adaf5677  # Go back to Phase 1
# or
git checkout cortex/orchestrators/core/master_orchestrator.py  # Restore original
```

---

## Validation Checklist

- [ ] WIRE-001 imports added
- [ ] WIRE-002 imports added
- [ ] WIRE-003 imports added
- [ ] initialize() calls execute_wire_001()
- [ ] initialize() calls execute_wire_002()
- [ ] initialize() calls execute_wire_003()
- [ ] Error handling for each WIRE module
- [ ] Orchestrator count validation (== 23)
- [ ] Audit logging maintained
- [ ] Tests pass (test_transform_001_wiring.py)
- [ ] Full test suite runs without errors
- [ ] Git commit with AC_WIRE-INTEGRATION commit message

---

## Success Criteria

✅ All 23 orchestrators initialized and registered  
✅ All WIRE module tests passing  
✅ MasterOrchestrator.initialize() completes successfully  
✅ Orchestrator discovery returns 23 results  
✅ Git history shows clean integration commit  

---

## Next Phase (Phase 3: MCP Tools Exposure)

Once Phase 2 complete:
- Add get_mcp_tools() to all 23 orchestrators
- Wire MCPServer.list_tools() to discover all tools
- Expose 15 MCP tools through unified interface
- Estimated effort: 3-4 hours

---
